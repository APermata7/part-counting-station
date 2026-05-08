from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models.inspection import Inspection
from app.models.part import Part
from app.schemas.detection import DetectionResponse
from app.services.sensor_fusion import determine_status

router = APIRouter(prefix="/detection", tags=["Detection"])

@router.post("/inspect", response_model=DetectionResponse)
async def inspect_part(
    part_id: int = Form(...),
    operator_username: str = Form(...),
    n_cv: int = Form(...),
    weight_gram: float = Form(...),
    db: Session = Depends(get_db)
):
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    n_weight = int(round(weight_gram / float(part.weight_per_unit)))
    difference = abs(n_cv - n_weight)
    status = determine_status(difference, part.threshold)

    inspection_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"

    new_inspection = Inspection(
        inspection_id=inspection_id,
        part_id=part.id,
        operator_username=operator_username,
        qty_label=part.target_qty,
        n_cv=n_cv,
        n_weight=n_weight,
        difference=difference,
        status=status,
        threshold_used=part.threshold
    )
    db.add(new_inspection)
    db.commit()
    db.refresh(new_inspection)

    return DetectionResponse(
        inspection_id=inspection_id,
        part_id=part.id,
        part_name=part.part_name,
        qty_label=part.target_qty,
        n_cv=n_cv,
        n_weight=n_weight,
        difference=difference,
        status=status.value,
        threshold_used=part.threshold,
        timestamp=datetime.now().isoformat()
    )