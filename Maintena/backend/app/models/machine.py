
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    machine_code = Column(String, unique=True, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, default="Operational")
    health = Column(Integer, nullable=True)
    last_maintenance = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
