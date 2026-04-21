from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Event
from database import SessionLocal
from .auth import get_current_user

router = APIRouter(prefix="/events", tags=["events"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class EventRequest(BaseModel):
    title: str = Field(min_length=3)
    location: str = Field(min_length=3)
    total_seats: int = Field(gt=0)


@router.get("/", status_code=status.HTTP_200_OK)
async def list_events(db: db_dependency):
    return db.query(Event).all()


@router.get("/{event_id}", status_code=status.HTTP_200_OK)
async def get_event(
    db: db_dependency,
    event_id: int = Path(gt=0)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(
    event_request: EventRequest,
    user: user_dependency,
    db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    event = Event(
        title=event_request.title,
        location=event_request.location,
        total_seats=event_request.total_seats,
        available_seats=event_request.total_seats,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event
