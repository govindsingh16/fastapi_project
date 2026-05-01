from fastapi import HTTPException
from models import Event
from repositories import events as event_repository


def list_events(db):
    return event_repository.list_events(db)


def get_events(db, page: int, limit: int, search: str, location: str, sort: str):
    return event_repository.get_events(db, page, limit, search, location, sort)


def create_event(db, user, event_request):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    event = Event(
        title=event_request.title,
        location=event_request.location,
        total_seats=event_request.total_seats,
        available_seats=event_request.total_seats,
    )

    return event_repository.create_event(db, event)
