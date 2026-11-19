
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models.machine import Machine

router = APIRouter(
    prefix="/machines",
    tags=["Machine Management"]
)


class MachineCreate(BaseModel):
    name: str
    machine_code: str
    location: str
    status: str = "Operational"


class MachineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    machine_code: str
    location: str
    status: str
    last_maintenance: Optional[datetime]
    created_at: datetime


@router.post("/", response_model=MachineResponse)
def create_machine(machine: MachineCreate, db: Session = Depends(get_db)):

    existing = db.query(Machine).filter(
        Machine.machine_code == machine.machine_code
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Machine code already exists")

    new_machine = Machine(**machine.model_dump())

    db.add(new_machine)
    db.commit()
    db.refresh(new_machine)

    return new_machine


@router.get("/", response_model=list[MachineResponse])
def get_machines(db: Session = Depends(get_db)):
    return db.query(Machine).all()


@router.get("/{machine_id}", response_model=MachineResponse)
def get_machine(machine_id: int, db: Session = Depends(get_db)):

    machine = db.query(Machine).filter(
        Machine.id == machine_id
    ).first()

    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    return machine


@router.put("/{machine_id}", response_model=MachineResponse)
def update_machine(
    machine_id: int,
    updated_data: MachineCreate,
    db: Session = Depends(get_db)
):

    machine = db.query(Machine).filter(
        Machine.id == machine_id
    ).first()

    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    for key, value in updated_data.model_dump().items():
        setattr(machine, key, value)

    db.commit()
    db.refresh(machine)

    return machine


@router.delete("/{machine_id}")
def delete_machine(machine_id: int, db: Session = Depends(get_db)):

    machine = db.query(Machine).filter(
        Machine.id == machine_id
    ).first()

    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    db.delete(machine)
    db.commit()

    return {"message": "Machine deleted successfully"}
