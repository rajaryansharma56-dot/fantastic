from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)

    machine_id = Column(
        Integer,
        ForeignKey("machines.id"),
        nullable=False,
        index=True
    )

    temperature = Column(Float, nullable=True)
    vibration = Column(Float, nullable=True)
    operating_hours = Column(Float, nullable=True)

    recorded_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
