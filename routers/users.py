from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path
from starlette import status
from exception import CustomException
from models import Users
from database import SessionLocal
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix='/user',
    tags=['user']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserVerification(BaseModel):
    password: str = Field(min_length=6, max_length=72)
    new_password: str = Field(min_length=6)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise CustomException('Authentication Failed', 401)
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency,
                          user_verification: UserVerification):
    if user is None:
        raise CustomException('Authentication Failed', 401)
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise CustomException('User not found.', 404)

    try:
        if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
            raise CustomException('Error on password change', 401)
    except ValueError:
        raise CustomException('Password too long; must be <=72 bytes when UTF-8 encoded', 400)

    new_pw_bytes = user_verification.new_password.encode('utf-8')
    if len(new_pw_bytes) > 72:
        raise CustomException('New password too long; must be <=72 bytes when UTF-8 encoded', 400)

    hashed_password = bcrypt_context.hash(user_verification.new_password)
    user_model.hashed_password = hashed_password
    db.add(user_model)
    db.commit()

@router.get("/test-error")
def test_error():
    raise CustomException("Something went wrong",400)






