
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal

from app.database import get_db
from app.models.machine import Machine
from app.models.maintenance import Maintenance


router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance Management"]
)


# ---------------- REQUEST SCHEMA ----------------

class MaintenanceCreate(BaseModel):
    machine_id: int
    title: str = Field(min_length=3, max_length=150)
    description: Optional[str] = None

    maintenance_type: Literal["Preventive", "Corrective"] = "Preventive"

    priority: Literal["Low", "Medium", "High", "Critical"] = "Medium"

    status: Literal[
        "Scheduled",
        "In Progress",
        "Completed",
        "Cancelled"
    ] = "Scheduled"

    scheduled_date: datetime
    cost: Optional[Decimal] = Field(default=None, ge=0)


# ---------------- RESPONSE SCHEMA ----------------

class MaintenanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: int
    title: str
    description: Optional[str]
    maintenance_type: str
    priority: str
    status: str
    scheduled_date: datetime
    completed_date: Optional[datetime]
    cost: Optional[Decimal]
    created_at: datetime


# ---------------- CREATE MAINTENANCE ----------------

@router.post(
    "/",
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_maintenance(
    data: MaintenanceCreate,
    db: Session = Depends(get_db)
):
    machine = db.query(Machine).filter(
        Machine.id == data.machine_id
    ).first()

    if not machine:
        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )

    if data.status == "Completed":
        raise HTTPException(
            status_code=400,
            detail="Create maintenance as Scheduled or In Progress, then complete it"
        )

    new_maintenance = Maintenance(**data.model_dump())

    try:
        db.add(new_maintenance)
        db.commit()
        db.refresh(new_maintenance)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create maintenance record"
        )

    return new_maintenance


# ---------------- GET ALL MAINTENANCE ----------------

@router.get(
    "/",
    response_model=list[MaintenanceResponse]
)
def get_maintenances(
    db: Session = Depends(get_db)
):
    return db.query(Maintenance).order_by(
        Maintenance.created_at.desc()
    ).all()


# ---------------- GET MAINTENANCE BY ID ----------------

@router.get(
    "/{maintenance_id}",
    response_model=MaintenanceResponse
)
def get_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db)
):
    maintenance = db.query(Maintenance).filter(
        Maintenance.id == maintenance_id
    ).first()

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    return maintenance


# ---------------- UPDATE MAINTENANCE ----------------

@router.put(
    "/{maintenance_id}",
    response_model=MaintenanceResponse
)
def update_maintenance(
    maintenance_id: int,
    data: MaintenanceCreate,
    db: Session = Depends(get_db)
):
    maintenance = db.query(Maintenance).filter(
        Maintenance.id == maintenance_id
    ).first()

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    if maintenance.status == "Completed":
        raise HTTPException(
            status_code=400,
            detail="Completed maintenance cannot be updated"
        )

    machine = db.query(Machine).filter(
        Machine.id == data.machine_id
    ).first()

    if not machine:
        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )

    if data.status == "Completed":
        raise HTTPException(
            status_code=400,
            detail="Use the complete endpoint to complete maintenance"
        )

    try:
        for key, value in data.model_dump().items():
            setattr(maintenance, key, value)

        db.commit()
        db.refresh(maintenance)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to update maintenance record"
        )

    return maintenance


# ---------------- COMPLETE MAINTENANCE ----------------

@router.patch(
    "/{maintenance_id}/complete",
    response_model=MaintenanceResponse
)
def complete_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db)
):
    maintenance = db.query(Maintenance).filter(
        Maintenance.id == maintenance_id
    ).first()

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    if maintenance.status == "Completed":
        raise HTTPException(
            status_code=400,
            detail="Maintenance is already completed"
        )

    if maintenance.status == "Cancelled":
        raise HTTPException(
            status_code=400,
            detail="Cancelled maintenance cannot be completed"
        )

    maintenance.status = "Completed"
    maintenance.completed_date = datetime.utcnow()

    try:
        db.commit()
        db.refresh(maintenance)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to complete maintenance"
        )

    return maintenance


# ---------------- DELETE MAINTENANCE ----------------

@router.delete("/{maintenance_id}")
def delete_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db)
):
    maintenance = db.query(Maintenance).filter(
        Maintenance.id == maintenance_id
    ).first()

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    try:
        db.delete(maintenance)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to delete maintenance record"
        )

    return {
        "message": "Maintenance record deleted successfully",
        "id": maintenance_id
    }
