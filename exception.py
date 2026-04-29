from fastapi import Request
from fastapi.responses import JSONResponse

class CustomException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code


async def custom_exception_handler(request: Request, exc: CustomException):
    print("Custom handler triggered")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )