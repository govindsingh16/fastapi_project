from models import Users


def get_user_by_username(db, username: str):
    return db.query(Users).filter(Users.username == username).first()


def get_user_by_id(db, user_id: int):
    return db.query(Users).filter(Users.id == user_id).first()


def create_user(db, user: Users):
    db.add(user)
    db.commit()
    return user


def update_user(db, user: Users):
    db.add(user)
    db.commit()
    return user
