from fastapi import FastAPI
import models
from database import engine
from routers import events, booking, admin, users
from routers import auth

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(booking.router)
app.include_router(admin.router)
app.include_router(users.router)