import json
from pathlib import Path
from typing import Any
from copy import deepcopy
from .database import Database
from .errors import (
    TableNotFoundError,
    TableExistsError,
    InvalidStorageDataError,
    StorageError,
)
from .table import Table


class FileDatabase(Database):
    def __init__(self, directory: str = "data"):
        self.directory = Path(directory)
        self._tables_cache: dict[str, Table] = {}
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise StorageError(f"Не удалось создать папку '{directory}': {e}")

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.json"

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table_from_file(self, table_name: str) -> Table:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        try:
            with table_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidStorageDataError(
                f"Файл таблицы '{table_name}' содержит некорректный JSON: {e}"
            )
        except OSError as e:
            raise StorageError(f"Ошибка при чтении файла '{table_name}': {e}")
        if "schema" not in data or "records" not in data:
            raise InvalidStorageDataError(
                f"Файл таблицы '{table_name}' имеет некорректную структуру"
            )
        schema = {}
        for field_name, field_type in data["schema"].items():
            if field_type == "int":
                schema[field_name] = int
            elif field_type == "str":
                schema[field_name] = str
            elif field_type == "bool":
                schema[field_name] = bool
            else:
                schema[field_name] = str
        table = Table(table_name, schema)
        for record in data["records"]:
            for key, value in record.items():
                if key in schema and schema[key] is int:
                    record[key] = int(value) if value is not None else None
                elif key in schema and schema[key] is bool:
                    record[key] = bool(value) if value is not None else False
            table._records.append(deepcopy(record))
        if table._records:
            max_id = max(r.get("id", 0) for r in table._records)
            table._next_id = max_id + 1
        return table

    def _save_table_to_file(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)
        schema_info = {}
        for field_name, field_type in table.schema.items():
            schema_info[field_name] = field_type.__name__
        data = {"schema": schema_info, "records": table.get_all()}
        try:
            with table_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except OSError as e:
            raise StorageError(f"Ошибка при сохранении таблицы '{table_name}': {e}")

    def create_table(self, table_name: str, schema: dict[str, type]) -> None:
        if self._table_exists(table_name):
            raise TableExistsError(f"Таблица '{table_name}' уже существует")
        table = Table(table_name, schema)
        self._save_table_to_file(table_name, table)
        self._tables_cache[table_name] = table

    def insert_record(self, table_name: str, record: dict[str, Any]) -> dict[str, Any]:
        table = self._load_table_from_file(table_name)
        result = table.create(record)
        self._save_table_to_file(table_name, table)
        self._tables_cache[table_name] = table
        return result

    def select_records(
        self,
        table_name: str,
        filters: dict[str, Any] | None = None,
        sort_by: str | None = None,
        reverse: bool = False,
    ) -> list[dict[str, Any]]:
        table = self._load_table_from_file(table_name)
        return table.select(filters, sort_by, reverse)

    def update_record(
        self, table_name: str, record_id: Any, updates: dict[str, Any]
    ) -> dict[str, Any]:
        table = self._load_table_from_file(table_name)
        result = table.update(record_id, updates)
        self._save_table_to_file(table_name, table)
        self._tables_cache[table_name] = table
        return result

    def delete_record(self, table_name: str, record_id: Any) -> dict[str, Any]:
        table = self._load_table_from_file(table_name)
        result = table.delete(record_id)
        self._save_table_to_file(table_name, table)
        self._tables_cache[table_name] = table
        return result

    def get_table_names(self) -> list[str]:
        return [f.stem for f in self.directory.glob("*.json")]

    def drop_table(self, table_name: str) -> None:
        table_path = self._get_table_path(table_name)
        if table_path.exists():
            try:
                table_path.unlink()
            except OSError as e:
                raise StorageError(f"Не удалось удалить таблицу '{table_name}': {e}")
            if table_name in self._tables_cache:
                del self._tables_cache[table_name]
        else:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
