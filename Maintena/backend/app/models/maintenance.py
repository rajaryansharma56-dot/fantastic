
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from datetime import datetime

from app.database import Base


class Maintenance(Base):
    __tablename__ = "maintenances"

    id = Column(Integer, primary_key=True, index=True)

    machine_id = Column(
        Integer,
        ForeignKey("machines.id"),
        nullable=False,
        index=True
    )

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    maintenance_type = Column(String, default="Preventive")
    priority = Column(String, default="Medium")
    status = Column(String, default="Scheduled")

    scheduled_date = Column(DateTime, nullable=False)
    completed_date = Column(DateTime, nullable=True)

    cost = Column(Numeric(10, 2), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
