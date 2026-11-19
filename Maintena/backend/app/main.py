from fastapi import FastAPI

from app.database import Base, engine

from app.models.machine import Machine
from app.models.maintenance import Maintenance
from app.models.sensor_reading import SensorReading

from app.routers import machines, maintenance, dashboard, chatbot, risk

from fastapi.middleware.cors import CORSMiddleware



Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Maintena API",
    description="Industrial Maintenance Management System",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(machines.router)
app.include_router(maintenance.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Maintena API",
        "status": "running"
    }

app.include_router(chatbot.router)
app.include_router(risk.router)


