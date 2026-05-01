from models import Booking


def list_bookings(db):
    return db.query(Booking).all()


def get_booking_by_id(db, booking_id: int):
    return db.query(Booking).filter(Booking.id == booking_id).first()


def create_booking(db, booking: Booking):
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def delete_booking(db, booking: Booking):
    db.delete(booking)
    db.commit()
