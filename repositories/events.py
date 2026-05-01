from models import Event


def list_events(db):
    return db.query(Event).all()


def get_events(db, page: int, limit: int, search: str, location: str, sort: str):
    query = db.query(Event)

    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))

    if location:
        query = query.filter(Event.location.ilike(f"%{location}%"))

    if sort == "created_at":
        query = query.order_by(Event.created_at.asc())

    offset = (page - 1) * limit
    return query.offset(offset).limit(limit).all()


def get_event_by_id(db, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()


def get_event_by_id_for_update(db, event_id: int):
    return db.query(Event).filter(Event.id == event_id).with_for_update().first()


def create_event(db, event: Event):
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def update_event(db, event: Event):
    db.add(event)
    db.commit()
    return event


def delete_event(db, event_id: int):
    db.query(Event).filter(Event.id == event_id).delete()
    db.commit()
