from fastapi import HTTPException
from repositories import bookings as booking_repository
from repositories import events as event_repository


def _ensure_admin(user):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')


def list_events(db, user):
    _ensure_admin(user)
    return event_repository.list_events(db)


def list_bookings(db, user):
    _ensure_admin(user)
    return booking_repository.list_bookings(db)


def delete_event(db, user, event_id: int):
    _ensure_admin(user)
    event = event_repository.get_event_by_id(db, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail='Event not found.')
    event_repository.delete_event(db, event_id)
