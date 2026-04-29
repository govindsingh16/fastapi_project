from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path
from starlette import status
from exception import CustomException
from models import Event, Booking
from database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/events", status_code=status.HTTP_200_OK)
async def list_events(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise CustomException('Authentication Failed', 401)
    return db.query(Event).all()


@router.get('/bookings', status_code=status.HTTP_200_OK)
async def list_bookings(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise CustomException('Authentication Failed', 401)
    return db.query(Booking).all()


@router.delete('/event/{event_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(user: user_dependency, db: db_dependency, event_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise CustomException('Authentication Failed', 401)
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise CustomException('Event not found.', 404)
    db.query(Event).filter(Event.id == event_id).delete()
    db.commit()







