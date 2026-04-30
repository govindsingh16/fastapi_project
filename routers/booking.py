from time import time
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Event, Booking
from .auth import get_current_user
from utils.redis_lock import acquire_lock, release_lock
import time
from logger import logger
router = APIRouter(prefix="/booking", tags=["booking"]) 




def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def book_seat(event_id: int, seats: int, db: db_dependency , user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    lock_key = f"lock:event:{event_id}"

    if not acquire_lock(lock_key):
        raise HTTPException(status_code=429, detail="Another booking in progress")
    time.sleep(2)
    logger.info(f"User {user.get('id')} booking event {event_id}")

    try:
        # lock row for update to avoid race conditions (Postgres supports FOR UPDATE)
        event = db.query(Event).filter(Event.id == event_id).with_for_update().first()

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if seats <= 0:
            raise HTTPException(status_code=400, detail="Seats must be > 0")

        if event.available_seats < seats:
            raise HTTPException(status_code=400, detail="Not enough seats available")

        event.available_seats -= seats

        booking = Booking(
            user_id=user.get("id"),
            event_id=event_id,
            seats_booked=seats
        )

        db.add(booking)
        db.add(event)
        db.commit()
        db.refresh(booking)

        return {"message": "Booking successful", "booking_id": booking.id}

    finally:
        release_lock(lock_key)


@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: int,
    db: db_dependency,
    user: user_dependency
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    if booking.user_id != user.get("id"):
        raise HTTPException(status_code=403, detail="Not authorized")

    event = db.query(Event).filter(Event.id == booking.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Associated event not found")

    event.available_seats += booking.seats_booked

    db.delete(booking)
    db.commit()

    return {"message": "Booking cancelled"}