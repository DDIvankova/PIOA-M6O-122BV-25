from abc import ABC, abstractmethod
from typing import Any


class Database(ABC):
    @abstractmethod
    def create_table(self, table_name: str, schema: dict[str, type]) -> None:
        pass

    @abstractmethod
    def drop_table(self, table_name: str) -> None:
        pass

    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        pass

    @abstractmethod
    def insert_record(self, table_name: str, record: dict[str, Any]) -> dict[str, Any]:
        pass

    @abstractmethod
    def select_records(
        self,
        table_name: str,
        filters: dict[str, Any] | None = None,
        sort_by: str | None = None,
        reverse: bool = False,
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def update_record(
        self, table_name: str, record_id: Any, updates: dict[str, Any]
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def delete_record(self, table_name: str, record_id: Any) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_table_names(self) -> list[str]:
        pass