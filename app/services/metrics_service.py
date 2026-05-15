from sqlalchemy.orm import Session
from app.repositories import metrics_repository as repo

class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    def get_avg_execution_time(self) -> float | None:
        avg_time = repo.get_average_execution_time(self.db)

        if avg_time is None:
            return None

        return avg_time.total_seconds()