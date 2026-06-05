from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.part import Part
from app.schemas.part import PartResponse

router = APIRouter(prefix="/parts", tags=["Parts"])

@router.get("/", response_model=List[PartResponse])
def get_parts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Part).offset(skip).limit(limit).all()

@router.get("/{part_id}", response_model=PartResponse)
def get_part(part_id: int, db: Session = Depends(get_db)):
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return part