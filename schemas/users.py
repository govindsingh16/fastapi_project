from pydantic import BaseModel, Field


class UserVerification(BaseModel):
    password: str = Field(min_length=6, max_length=72)
    new_password: str = Field(min_length=6)
