from fastapi import APIRouter
from starlette import status
from routers.dependencies import db_dependency, user_dependency
from services import bookings as booking_service

router = APIRouter(prefix="/booking", tags=["booking"]) 


@router.post("/", status_code=status.HTTP_201_CREATED)
def book_seat(event_id: int, seats: int, db: db_dependency , user: user_dependency):
    return booking_service.book_seat(db, user, event_id, seats)


@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: int,
    db: db_dependency,
    user: user_dependency
):
    return booking_service.cancel_booking(db, user, booking_id)
