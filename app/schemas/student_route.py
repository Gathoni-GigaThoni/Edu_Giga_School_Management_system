from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from app.models.enums import TransportDirection


class StudentRouteAssign(BaseModel):
    route_id: int
    direction: TransportDirection
    use_daily_rate: bool = False


class StudentRouteRead(BaseModel):
    id: int
    student_id: int
    route_id: int
    direction: TransportDirection
    use_daily_rate: bool
    active: bool
    start_date: date

    model_config = ConfigDict(from_attributes=True)
