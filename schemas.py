from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CompanyCreate(BaseModel):
    name: str
    group_name: Optional[str] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    group_name: Optional[str] = None

class Company(BaseModel):
    id: int
    name: str
    group_name: Optional[str] = None

    class Config:
        from_attributes = True

class AvailableDesk(BaseModel):
    desk_id: int
    label: str
    equipment: str
    floor_level: int
    building_name: str
    city: str

class ReservationCreate(BaseModel):
    desk_id: int
    employee_id: int
    start_time: datetime
    end_time: datetime
    status: str = "reserved"

class Reservation(BaseModel):
    id: int
    desk_id: int
    employee_id: int
    start_time: datetime
    end_time: datetime
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True