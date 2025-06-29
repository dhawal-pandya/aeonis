from abc import ABC, abstractmethod
from typing import List, Dict, Any
import uuid

class TraceRepository(ABC):

    @abstractmethod
    def get_project_by_api_key(self, api_key: str) -> Any:
        pass

    @abstractmethod
    def add_spans(self, spans: List[Dict[str, Any]], project_id: uuid.UUID):
        pass

    @abstractmethod
    def get_traces_by_project_id(self, project_id: uuid.UUID, limit: int = 100) -> List[Any]:
        pass

    @abstractmethod
    def delete_traces_by_project_id(self, project_id: uuid.UUID) -> int:
        pass
