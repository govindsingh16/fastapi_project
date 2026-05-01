from fastapi import APIRouter
from starlette import status
from routers.dependencies import db_dependency, user_dependency
from schemas.users import UserVerification
from services import users as user_service

router = APIRouter(
    prefix='/user',
    tags=['user']
)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    return user_service.get_user(db, user)


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency,
                          user_verification: UserVerification):
    user_service.change_password(db, user, user_verification)







