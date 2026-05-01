from fastapi import APIRouter, Path
from starlette import status
from routers.dependencies import db_dependency, user_dependency
from services import admin as admin_service

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


@router.get("/events", status_code=status.HTTP_200_OK)
async def list_events(user: user_dependency, db: db_dependency):
    return admin_service.list_events(db, user)


@router.get('/bookings', status_code=status.HTTP_200_OK)
async def list_bookings(user: user_dependency, db: db_dependency):
    return admin_service.list_bookings(db, user)


@router.delete('/event/{event_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(user: user_dependency, db: db_dependency, event_id: int = Path(gt=0)):
    admin_service.delete_event(db, user, event_id)







