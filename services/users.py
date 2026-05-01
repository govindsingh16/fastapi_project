from fastapi import HTTPException
from passlib.context import CryptContext
from repositories import users as user_repository

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_user(db, user):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return user_repository.get_user_by_id(db, user.get('id'))


def change_password(db, user, user_verification):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = user_repository.get_user_by_id(db, user.get('id'))
    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found.')

    try:
        if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
            raise HTTPException(status_code=401, detail='Error on password change')
    except ValueError:
        raise HTTPException(status_code=400, detail='Password too long; must be <=72 bytes when UTF-8 encoded')

    new_pw_bytes = user_verification.new_password.encode('utf-8')
    if len(new_pw_bytes) > 72:
        raise HTTPException(status_code=400, detail='New password too long; must be <=72 bytes when UTF-8 encoded')

    hashed_password = bcrypt_context.hash(user_verification.new_password)
    user_model.hashed_password = hashed_password
    return user_repository.update_user(db, user_model)
