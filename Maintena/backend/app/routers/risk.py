from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.machine import Machine
from app.models.maintenance import Maintenance
from app.models.sensor_reading import SensorReading

from app.services.risk_engine import assess_machine_risk

router = APIRouter(
    prefix="/api/risk",
    tags=["Machine Risk Assessment"]
)


@router.get("/")
def get_all_machine_risks(db: Session = Depends(get_db)):

    machines = db.query(Machine).all()

    results = []

    for machine in machines:

        readings = (
            db.query(SensorReading)
            .filter(SensorReading.machine_id == machine.id)
            .all()
        )

        maintenance_records = (
            db.query(Maintenance)
            .filter(Maintenance.machine_id == machine.id)
            .all()
        )

        result = assess_machine_risk(
            machine,
            readings,
            maintenance_records
        )

        results.append(result)

    return {
        "total_machines": len(results),
        "risk_assessments": results
    }


@router.get("/{machine_id}")
def get_machine_risk(
    machine_id: int,
    db: Session = Depends(get_db)
):

    machine = db.query(Machine).filter(
        Machine.id == machine_id
    ).first()

    if not machine:
        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )

    readings = (
        db.query(SensorReading)
        .filter(SensorReading.machine_id == machine_id)
        .all()
    )

    maintenance_records = (
        db.query(Maintenance)
        .filter(Maintenance.machine_id == machine_id)
        .all()
    )

    return assess_machine_risk(
        machine,
        readings,
        maintenance_records
    )
