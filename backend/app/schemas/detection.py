from pydantic import BaseModel

class DetectionResponse(BaseModel):
    inspection_id: str
    part_id: int
    part_name: str
    qty_label: int
    n_cv: int
    n_weight: int
    difference: int
    status: str
    threshold_used: int
    timestamp: str