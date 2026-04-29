from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path
from starlette import status
from exception import CustomException
from models import Event
from database import SessionLocal
from .auth import get_current_user
from fastapi import Query

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


@router.get("/list", status_code=status.HTTP_200_OK)
async def list_events(db: db_dependency):
    return db.query(Event).all()


@router.get("/")
def get_events(
    db: db_dependency,
    page: int = 1,
    limit: int = 10,
    search: str = "",
    location: str = "",
    sort: str = "created_at"
):
    query = db.query(Event)

    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))

    if location:
        query = query.filter(Event.location.ilike(f"%{location}%"))

    if sort == "created_at":
        query = query.order_by(Event.created_at.asc())

    offset = (page - 1) * limit

    events = query.offset(offset).limit(limit).all()

    return events


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(
    event_request: EventRequest,
    user: user_dependency,
    db: db_dependency
):
    if user is None:
        raise CustomException('Authentication Failed', 401)

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
