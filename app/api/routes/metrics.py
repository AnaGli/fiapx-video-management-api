from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.services.metrics_service import MetricsService

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
)

def get_metrics_service(db: Session = Depends(get_db)):
    return MetricsService(db)

@router.get("/average-execution-time")
def average_execution_time(service: MetricsService = Depends(get_metrics_service)):
    avg_seconds = service.get_avg_execution_time()
    return {
        "average_execution_time_seconds": avg_seconds
    }