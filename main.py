from fastapi import FastAPI
from database import engine
from models import Base
from routers import events, booking, admin, users
from routers import auth
import redis
from config import settings
from fastapi import Request
import time
from logger import logger

app = FastAPI()


Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(booking.router)
app.include_router(admin.router)
app.include_router(users.router)

r = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=settings.redis_decode_responses
)

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



# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     start_time = time.time()

#     response = await call_next(request)

#     process_time = round((time.time() - start_time) * 1000, 2)

#     logger.info(
#         f"{request.method} {request.url.path} "
#         f"status={response.status_code} "
#         f"time={process_time}ms"
#     )

#     return response
