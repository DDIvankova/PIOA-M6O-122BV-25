from typing import Any
from .database import Database
from .errors import TableNotFoundError, TableExistsError
from .table import Table


class MemoryDatabase(Database):
    def __init__(self):
        self._tables: dict[str, Table] = {}

    def create_table(self, table_name: str, schema: dict[str, type]) -> None:
        if table_name in self._tables:
            raise TableExistsError(f"Таблица '{table_name}' уже существует")
        self._tables[table_name] = Table(table_name, schema)

    def drop_table(self, table_name: str) -> None:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        del self._tables[table_name]

    def table_exists(self, table_name: str) -> bool:
        return table_name in self._tables

    def insert_record(self, table_name: str, record: dict[str, Any]) -> dict[str, Any]:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        return self._tables[table_name].create(record)

    def select_records(
        self,
        table_name: str,
        filters: dict[str, Any] | None = None,
        sort_by: str | None = None,
        reverse: bool = False,
    ) -> list[dict[str, Any]]:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        return self._tables[table_name].select(filters, sort_by, reverse)

    def update_record(
        self, table_name: str, record_id: Any, updates: dict[str, Any]
    ) -> dict[str, Any]:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        return self._tables[table_name].update(record_id, updates)

    def delete_record(self, table_name: str, record_id: Any) -> dict[str, Any]:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        return self._tables[table_name].delete(record_id)

    def get_table_names(self) -> list[str]:
        return list(self._tables.keys())
