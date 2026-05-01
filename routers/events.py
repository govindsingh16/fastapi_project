from fastapi import APIRouter
from starlette import status
from routers.dependencies import db_dependency, user_dependency
from schemas.events import EventRequest
from services import events as event_service

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/list", status_code=status.HTTP_200_OK)
async def list_events(db: db_dependency):
    return event_service.list_events(db)


@router.get("/")
def get_events(
    db: db_dependency,
    page: int = 1,
    limit: int = 10,
    search: str = "",
    location: str = "",
    sort: str = "created_at"
):
    return event_service.get_events(db, page, limit, search, location, sort)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(
    event_request: EventRequest,
    user: user_dependency,
    db: db_dependency
):
    return event_service.create_event(db, user, event_request)
