from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.service_order import ServiceOrder 

def get_average_execution_time(db: Session):
    return db.query(
        func.avg(
            ServiceOrder.execution_finished_at - ServiceOrder.execution_started_at
        )
    ).filter(
        ServiceOrder.execution_started_at.isnot(None),
        ServiceOrder.execution_finished_at.isnot(None),
    ).scalar()