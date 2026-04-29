from time import time
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from exception import CustomException
from database import SessionLocal
from models import Event, Booking
from .auth import get_current_user
from utils.redis_lock import acquire_lock, release_lock
import time

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
        raise CustomException('Authentication Failed', 401)

    lock_key = f"lock:event:{event_id}"

    if not acquire_lock(lock_key):
        raise CustomException("Another booking in progress", 429)
    time.sleep(2)

    try:
        # lock row for update to avoid race conditions (Postgres supports FOR UPDATE)
        event = db.query(Event).filter(Event.id == event_id).with_for_update().first()

        if not event:
            raise CustomException("Event not found", 404)

        if seats <= 0:
            raise CustomException("Seats must be > 0", 400)

        if event.available_seats < seats:
            raise CustomException("Not enough seats available", 400)

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
        raise CustomException("Booking not found", 404)

    if user is None:
        raise CustomException('Authentication Failed', 401)

    if booking.user_id != user.get("id"):
        raise CustomException("Not authorized", 403)

    event = db.query(Event).filter(Event.id == booking.event_id).first()
    if not event:
        raise CustomException("Associated event not found", 404)

    event.available_seats += booking.seats_booked

    db.delete(booking)
    db.commit()

    return {"message": "Booking cancelled"}
