from pydantic import BaseModel, Field


class EventRequest(BaseModel):
    title: str = Field(min_length=3)
    location: str = Field(min_length=3)
    total_seats: int = Field(gt=0)
