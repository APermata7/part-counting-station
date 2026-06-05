from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.models.inspection import Inspection
from app.schemas.inspection import InspectionResponse

router = APIRouter(prefix="/inspections", tags=["Inspections"])

@router.get("/", response_model=List[InspectionResponse])
def get_inspections(
    skip: int = 0,
    limit: int = 100,
    part_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Inspection)
    if part_id:
        query = query.filter(Inspection.part_id == part_id)
    if status:
        query = query.filter(Inspection.status == status)
    if start_date:
        query = query.filter(Inspection.inspection_time >= start_date)
    if end_date:
        query = query.filter(Inspection.inspection_time <= end_date)
    return query.order_by(Inspection.inspection_time.desc()).offset(skip).limit(limit).all()

@router.get("/{inspection_id}", response_model=InspectionResponse)
def get_inspection(inspection_id: str, db: Session = Depends(get_db)):
    insp = db.query(Inspection).filter(Inspection.inspection_id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return insp