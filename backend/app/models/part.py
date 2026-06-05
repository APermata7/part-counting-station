from sqlalchemy import Column, Integer, String, DECIMAL
from app.core.database import Base

class Part(Base):
    __tablename__ = "part"

    id = Column(Integer, primary_key=True, index=True)
    part_code = Column(String(50), unique=True, index=True, nullable=False)
    part_name = Column(String(100), nullable=False)
    weight_per_unit = Column(DECIMAL(10, 4), nullable=False)
    target_qty = Column(Integer, nullable=False)
    threshold = Column(Integer, default=5)