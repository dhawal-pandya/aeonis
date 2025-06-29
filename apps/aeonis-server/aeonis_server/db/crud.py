from typing import List, Dict, Any
import uuid
from sqlalchemy.orm import Session
from . import models
from .repository import TraceRepository

class PostgresTraceRepository(TraceRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_project_by_api_key(self, api_key: str) -> models.Project:
        return self.db.query(models.Project).filter(models.Project.api_key == api_key).first()

    def add_spans(self, spans: List[Dict[str, Any]], project_id: uuid.UUID):
        db_spans = [models.Span(**span, project_id=project_id) for span in spans]
        self.db.add_all(db_spans)
        self.db.commit()

    def get_traces_by_project_id(self, project_id: uuid.UUID, limit: int = 100) -> List[models.Span]:
        return (
            self.db.query(models.Span)
            .filter(models.Span.project_id == project_id)
            .order_by(models.Span.start_time.desc())
            .limit(limit)
            .all()
        )

    def delete_traces_by_project_id(self, project_id: uuid.UUID) -> int:
        num_deleted = self.db.query(models.Span).filter(models.Span.project_id == project_id).delete()
        self.db.commit()
        return num_deleted
