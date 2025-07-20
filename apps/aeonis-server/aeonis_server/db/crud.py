from sqlalchemy import func, text
from typing import List, Dict, Any
import uuid
from sqlalchemy.orm import Session
from . import models
from .repository import TraceRepository

from .database import Base, engine

import logging

# Get a logger
logger = logging.getLogger(__name__)


class PostgresTraceRepository(TraceRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_project_by_api_key(self, api_key: str) -> models.Project:
        return (
            self.db.query(models.Project)
            .filter(models.Project.api_key == api_key)
            .first()
        )

    def add_spans(self, spans: List[Dict[str, Any]], project_id: uuid.UUID):

        db_spans = []
        for span_data in spans:
            try:
                # The Span model will now correctly map commit_id and sdk_version from the top level
                # while also preserving the attributes dictionary.
                db_spans.append(models.Span(**span_data, project_id=project_id))
            except Exception as e:
                logger.error(f"Error processing span data: {span_data}", exc_info=True)
                # Optionally, decide if you want to skip this span or fail the whole batch
                continue

        if not db_spans:
            logger.warning("No spans were successfully processed.")
            return

        try:
            self.db.add_all(db_spans)
            self.db.commit()
            logger.info(
                f"Successfully committed {len(db_spans)} spans to the database."
            )
        except Exception as e:
            logger.error("Failed to commit spans to database", exc_info=True)
            self.db.rollback()

    def get_traces_by_project_id(
        self, project_id: uuid.UUID, limit: int = 100
    ) -> List[models.Span]:
        """
        Retrieves the most recent traces for a given project ID.
        This is a multi-step query to avoid ambiguity in DISTINCT + ORDER BY.
        """
        # Step 1: Find the latest start_time for each trace_id
        latest_spans_subquery = (
            self.db.query(
                models.Span.trace_id,
                func.max(models.Span.start_time).label("latest_start_time"),
            )
            .filter(models.Span.project_id == project_id)
            .group_by(models.Span.trace_id)
            .subquery()
        )

        # Step 2: Get the top N trace_ids ordered by that latest start_time
        recent_trace_ids_query = (
            self.db.query(latest_spans_subquery.c.trace_id)
            .order_by(latest_spans_subquery.c.latest_start_time.desc())
            .limit(limit)
        )

        recent_trace_ids = [row[0] for row in recent_trace_ids_query.all()]

        if not recent_trace_ids:
            return []

        # Step 3: Fetch all spans belonging to those trace_ids
        return (
            self.db.query(models.Span)
            .filter(models.Span.trace_id.in_(recent_trace_ids))
            .order_by(models.Span.start_time.asc())
            .all()
        )

    def delete_traces_by_project_id(self, project_id: uuid.UUID) -> int:
        num_deleted = (
            self.db.query(models.Span)
            .filter(models.Span.project_id == project_id)
            .delete()
        )
        self.db.commit()
        return num_deleted

    def get_spans_by_trace_id(self, trace_id: str) -> List[models.Span]:
        return (
            self.db.query(models.Span)
            .filter(models.Span.trace_id == trace_id)
            .order_by(models.Span.start_time.asc())
            .all()
        )

    def get_project_by_id(self, project_id: uuid.UUID) -> models.Project:
        return (
            self.db.query(models.Project)
            .filter(models.Project.id == project_id)
            .first()
        )

    def get_all_projects(self) -> List[models.Project]:
        return self.db.query(models.Project).all()

    def create_project(
        self,
        name: str,
        git_repo_url: str = None,
        is_private: bool = False,
        git_ssh_key: str = None,
    ) -> models.Project:
        import secrets

        # TODO: Implement actual encryption for the SSH key before storing it.
        # For now, it's stored in plaintext which is NOT secure.
        project = models.Project(
            id=uuid.uuid4(),
            name=name,
            api_key=secrets.token_urlsafe(32),
            git_repo_url=git_repo_url,
            is_private=is_private,
            git_ssh_key=git_ssh_key,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_project(self, project_id: uuid.UUID) -> int:
        # First, delete all traces for the project
        self.delete_traces_by_project_id(project_id)

        # Then, delete the project itself
        project = (
            self.db.query(models.Project)
            .filter(models.Project.id == project_id)
            .first()
        )
        if not project:
            return 0

        self.db.delete(project)
        self.db.commit()
        return 1

    def delete_all_data(self) -> int:
        """Drops all tables from the database."""
        try:
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            return 1  # Return a success indicator
        except Exception as e:
            print(f"Error clearing database: {e}")
            return -1

    def execute_sql(self, query: str, params: dict = None) -> List[Dict[str, Any]]:
        """Executes a read-only SQL query and returns the results as a list of dicts."""
        try:
            result = self.db.execute(text(query), params)
            # The .mappings().all() method returns a list of dictionary-like objects
            return [row for row in result.mappings().all()]
        except Exception as e:
            logger.error(
                f"Database query failed. Query: {query}, Params: {params}",
                exc_info=True,
            )
            raise e
