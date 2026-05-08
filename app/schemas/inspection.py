from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class StatusEnum(str, Enum):
    OK = "OK"
    NG = "NG"

class InspectionBase(BaseModel):
    inspection_id: str
    part_id: int
    operator_username: str
    qty_label: int
    n_cv: int
    n_weight: int
    difference: int
    status: StatusEnum
    threshold_used: int

class InspectionCreate(InspectionBase):
    pass

class InspectionResponse(InspectionBase):
    id: int
    inspection_time: datetime

    class Config:
        from_attributes = True