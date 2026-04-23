from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class StatusEnum(str, enum.Enum):
    OK = "OK"
    NG = "NG"

class Inspection(Base):
    __tablename__ = "inspection"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(String(50), unique=True, index=True, nullable=False)
    part_id = Column(Integer, ForeignKey("part.id"), nullable=False)
    operator_username = Column(String(50), nullable=False)
    qty_label = Column(Integer, nullable=False)
    n_cv = Column(Integer, nullable=False)
    n_weight = Column(Integer, nullable=False)
    difference = Column(Integer, nullable=False)
    status = Column(Enum(StatusEnum), nullable=False)
    threshold_used = Column(Integer, nullable=False)
    inspection_time = Column(DateTime(timezone=True), server_default=func.now())