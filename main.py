from fastapi import FastAPI
import models
from database import engine
from routers import events, booking, admin, users
from routers import auth
import redis

app = FastAPI()


models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(booking.router)
app.include_router(admin.router)
app.include_router(users.router)

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

@app.get("/redis-test")
def redis_test():
    r.set("test_key", "hello_govind")
    return {
        "value": r.get("test_key")
    }

@app.get("/user/{user_id}")
def get_user(user_id: int):
    key = f"user:{user_id}"

    cached = r.get(key)
    if cached:
        return {"source": "cache", "data": cached}

    # simulate DB delay
    import time
    time.sleep(2)

    data = f"user_{user_id}_data"

    r.setex(key, 60, data)

    return {"source": "db", "data": data}