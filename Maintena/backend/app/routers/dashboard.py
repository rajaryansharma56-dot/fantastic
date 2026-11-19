from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.database import get_db
from app.models.machine import Machine
from app.models.maintenance import Maintenance
from app.models.sensor_reading import SensorReading

from app.services.risk_engine import assess_machine_risk

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):

    total_machines = db.query(Machine).count()

    machine_status = (
        db.query(Machine.status, func.count(Machine.id))
        .group_by(Machine.status)
        .all()
    )

    machine_breakdown = {
        status: count for status, count in machine_status
    }

    total_maintenance = db.query(Maintenance).count()

    scheduled = db.query(Maintenance).filter(
        Maintenance.status == "Scheduled"
    ).count()

    in_progress = db.query(Maintenance).filter(
        Maintenance.status == "In Progress"
    ).count()

    completed = db.query(Maintenance).filter(
        Maintenance.status == "Completed"
    ).count()

    cancelled = db.query(Maintenance).filter(
        Maintenance.status == "Cancelled"
    ).count()

    overdue = db.query(Maintenance).filter(
        Maintenance.scheduled_date < datetime.utcnow(),
        Maintenance.status.in_(["Scheduled", "In Progress"])
    ).count()

    total_cost = db.query(
        func.coalesce(func.sum(Maintenance.cost), 0)
    ).scalar()

    # Calculate actual risk for every machine
    risk_assessments = []

    for machine in db.query(Machine).all():

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

        assessment = assess_machine_risk(
            machine,
            readings,
            maintenance_records
        )

        risk_assessments.append(assessment)

    # Risk level summary
    risk_breakdown = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
        "INSUFFICIENT_DATA": 0
    }

    for assessment in risk_assessments:

        level = assessment["risk_level"]

        if level in risk_breakdown:
            risk_breakdown[level] += 1

    return {
        "machines": {
            "total": total_machines,
            "status_breakdown": machine_breakdown
        },
        "maintenance": {
            "total": total_maintenance,
            "scheduled": scheduled,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": cancelled,
            "overdue": overdue
        },
        "total_maintenance_cost": total_cost,
        "risk": {
            "total_assessed": len(risk_assessments),
            "risk_breakdown": risk_breakdown,
            "assessments": risk_assessments
        },
        "generated_at": datetime.utcnow()
    }


@router.get("/recent-maintenance")
def get_recent_maintenance(db: Session = Depends(get_db)):

    return (
        db.query(Maintenance)
        .order_by(Maintenance.created_at.desc())
        .limit(5)
        .all()
    )
