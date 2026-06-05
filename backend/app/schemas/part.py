from pydantic import BaseModel

class PartBase(BaseModel):
    part_code: str
    part_name: str
    weight_per_unit: float
    target_qty: int
    threshold: int

class PartResponse(PartBase):
    id: int