from typing import Annotated
from fastapi import APIRouter, Depends
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm
from routers.dependencies import db_dependency
from schemas.auth import CreateUserRequest, Token
from services import auth as auth_service

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

get_current_user = auth_service.get_current_user


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    auth_service.create_user(db, create_user_request)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    return auth_service.login_for_access_token(db, form_data)







