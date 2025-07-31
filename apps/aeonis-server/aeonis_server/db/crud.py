from sqlalchemy import func, text
from typing import List, Dict, Any
import uuid
from sqlalchemy.orm import Session
from . import models
from .repository import TraceRepository

from .database import Base, engine

import logging

# get a logger
logger = logging.getLogger(__name__)


class PostgresTraceRepository(TraceRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_project_by_api_key(self, api_key: str) -> models.Project:
        logger.info(f"Querying for project with API key: {api_key}")
        return (
            self.db.query(models.Project)
            .filter(models.Project.api_key == api_key)
            .first()
        )

    def add_spans(self, spans: List[Dict[str, Any]], project_id: uuid.UUID):
        logger.info(f"Processing {len(spans)} spans for project_id: {project_id}")
        db_spans = []
        for span_data in spans:
            try:
                # manually map the span data to the span model
                # to avoid any unexpected keyword arguments.
                db_span = models.Span(
                    project_id=project_id,
                    trace_id=span_data.get("trace_id"),
                    span_id=span_data.get("span_id"),
                    parent_span_id=span_data.get("parent_span_id"),
                    name=span_data.get("name"),
                    commit_id=span_data.get("commit_id"),
                    sdk_version=span_data.get("sdk_version"),
                    start_time=span_data.get("start_time"),
                    end_time=span_data.get("end_time"),
                    attributes=span_data.get("attributes"),
                    error=span_data.get("error"),
                )
                db_spans.append(db_span)
            except Exception as e:
                logger.error(f"Error processing span data: {span_data}", exc_info=True)
                # optionally, skip span or fail batch
                continue

        if not db_spans:
            logger.warning("No spans were successfully processed.")
            return

        try:
            logger.info(f"Committing {len(db_spans)} spans to the database.")
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
    ) -> List[Dict[str, Any]]:
        """
        retrieves recent traces for a project id.
        multi-step query to avoid ambiguity.
        """
        # step 1: find latest start_time for each trace_id
        latest_spans_subquery = (
            self.db.query(
                models.Span.trace_id,
                func.max(models.Span.start_time).label("latest_start_time"),
            )
            .filter(models.Span.project_id == project_id)
            .group_by(models.Span.trace_id)
            .subquery()
        )

        # step 2: get top n trace_ids by latest start_time
        recent_trace_ids_query = (
            self.db.query(latest_spans_subquery.c.trace_id)
            .order_by(latest_spans_subquery.c.latest_start_time.desc())
            .limit(limit)
        )

        recent_trace_ids = [row[0] for row in recent_trace_ids_query.all()]

        if not recent_trace_ids:
            return []

        # step 3: fetch all spans for those trace_ids
        spans = (
            self.db.query(models.Span)
            .filter(models.Span.trace_id.in_(recent_trace_ids))
            .order_by(models.Span.start_time.asc())
            .all()
        )
        return [span.to_dict() for span in spans]

    def delete_traces_by_project_id(self, project_id: uuid.UUID) -> int:
        num_deleted = (
            self.db.query(models.Span)
            .filter(models.Span.project_id == project_id)
            .delete()
        )
        self.db.commit()
        return num_deleted

    def get_spans_by_trace_id(self, trace_id: str) -> List[Dict[str, Any]]:
        spans = (
            self.db.query(models.Span)
            .filter(models.Span.trace_id == trace_id)
            .order_by(models.Span.start_time.asc())
            .all()
        )
        return [span.to_dict() for span in spans]

    def get_project_by_id(self, project_id: uuid.UUID) -> models.Project:
        return (
            self.db.query(models.Project)
            .filter(models.Project.id == project_id)
            .first()
        )

    def get_all_projects(self) -> List[Dict[str, Any]]:
        projects = self.db.query(models.Project).all()
        return [project.to_dict() for project in projects]

    def create_project(
        self,
        name: str,
        git_repo_url: str = None,
        is_private: bool = False,
        git_ssh_key: str = None,
    ) -> models.Project:
        import secrets

        # todo: encrypt ssh key before storing.
        # currently stored in plaintext, not secure.
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
        # first, delete all traces for the project
        self.delete_traces_by_project_id(project_id)

        # then, delete the project itself
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
        """drops all tables from database."""
        try:
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            return 1  # Return a success indicator
        except Exception as e:
            print(f"Error clearing database: {e}")
            return -1

    def execute_sql(self, query: str, params: dict = None) -> List[Dict[str, Any]]:
        """executes read-only sql query, returns list of dicts."""
        try:
            result = self.db.execute(text(query), params)
            # .mappings().all() returns list of dictionary-like objects
            return [row for row in result.mappings().all()]
        except Exception as e:
            logger.error(
                f"Database query failed. Query: {query}, Params: {params}",
                exc_info=True,
            )
            raise e
