from pydantic import BaseModel
from typing import Optional

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