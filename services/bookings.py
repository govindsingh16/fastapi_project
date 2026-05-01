import time

from fastapi import HTTPException
from logger import logger
from models import Booking
from repositories import bookings as booking_repository
from repositories import events as event_repository
from utils.redis_lock import acquire_lock, release_lock


def book_seat(db, user, event_id: int, seats: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    lock_key = f"lock:event:{event_id}"

    if not acquire_lock(lock_key):
        raise HTTPException(status_code=429, detail="Another booking in progress")
    time.sleep(2)
    logger.info(f"User {user.get('id')} booking event {event_id}")

    try:
        event = event_repository.get_event_by_id_for_update(db, event_id)

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


def cancel_booking(db, user, booking_id: int):
    booking = booking_repository.get_booking_by_id(db, booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    if booking.user_id != user.get("id"):
        raise HTTPException(status_code=403, detail="Not authorized")

    event = event_repository.get_event_by_id(db, booking.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Associated event not found")

    event.available_seats += booking.seats_booked

    db.delete(booking)
    db.commit()

    return {"message": "Booking cancelled"}
