import json
from pathlib import Path
from typing import Any, Dict, Type
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
        self._tables_cache: Dict[str, Table] = {}
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise StorageError(f"Не удалось создать папку '{directory}': {e}")

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.json"

    def table_exists(self, table_name: str) -> bool:
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

        schema: Dict[str, Type] = {}
        for field_name, field_type in data["schema"].items():
            if field_type == "int":
                schema[field_name] = int
            elif field_type == "str":
                schema[field_name] = str
            elif field_type == "bool":
                schema[field_name] = bool
            else:
                raise InvalidStorageDataError(
                    f"Неизвестный тип поля '{field_name}': {field_type}"
                )

        table = Table(table_name, schema)
        restored_records = []

        for record in data["records"]:
            converted_record: Dict[str, Any] = {}
            for key, value in record.items():
                try:
                    field_type = schema.get(key)
                    if field_type is int:
                        converted_record[key] = (
                            int(value) if value is not None else None
                        )
                    elif field_type is bool:
                        converted_record[key] = (
                            bool(value) if value is not None else False
                        )
                    else:
                        converted_record[key] = value
                except (TypeError, ValueError) as e:
                    raise InvalidStorageDataError(
                        f"Некорректное значение поля '{key}' в таблице '{table_name}': {e}"
                    )
            restored_records.append(converted_record)

        table.restore_records(restored_records)
        return table

    def _save_table_to_file(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)
        schema_info: Dict[str, str] = {}
        for field_name, field_type in table.schema.items():
            schema_info[field_name] = field_type.__name__
        data = {"schema": schema_info, "records": table.get_all()}
        try:
            with table_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except OSError as e:
            raise StorageError(f"Ошибка при сохранении таблицы '{table_name}': {e}")

    def create_table(self, table_name: str, schema: Dict[str, Type]) -> None:
        if self.table_exists(table_name):
            raise TableExistsError(f"Таблица '{table_name}' уже существует")
        table = Table(table_name, schema)
        self._save_table_to_file(table_name, table)
        self._tables_cache[table_name] = table

    def insert_record(self, table_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
        table = self._load_table_from_file(table_name)
        result = table.create(record)
        self._save_table_to_file(table_name, table)
        self._tables_cache[table_name] = table
        return result

    def select_records(
        self,
        table_name: str,
        filters: Dict[str, Any] | None = None,
        sort_by: str | None = None,
        reverse: bool = False,
    ) -> list[Dict[str, Any]]:
        table = self._load_table_from_file(table_name)
        return table.select(filters, sort_by, reverse)

    def update_record(
        self, table_name: str, record_id: Any, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        table = self._load_table_from_file(table_name)
        result = table.update(record_id, updates)
        self._save_table_to_file(table_name, table)
        self._tables_cache[table_name] = table
        return result

    def delete_record(self, table_name: str, record_id: Any) -> Dict[str, Any]:
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
