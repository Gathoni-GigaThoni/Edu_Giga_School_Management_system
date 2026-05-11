from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class RouteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    one_way_morning_price: float = Field(..., ge=0)
    one_way_evening_price: float = Field(..., ge=0)
    two_way_price: float = Field(..., ge=0)
    daily_rate: float = Field(..., ge=0)


class RouteUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    one_way_morning_price: Optional[float] = Field(default=None, ge=0)
    one_way_evening_price: Optional[float] = Field(default=None, ge=0)
    two_way_price: Optional[float] = Field(default=None, ge=0)
    daily_rate: Optional[float] = Field(default=None, ge=0)


class RouteRead(BaseModel):
    id: int
    name: str
    one_way_morning_price: float
    one_way_evening_price: float
    two_way_price: float
    daily_rate: float

    model_config = ConfigDict(from_attributes=True)
