from typing import Any, Optional
from copy import deepcopy
from .errors import (
    DuplicateIDError,
    ValidationError,
    RecordNotFoundError,
    InvalidFieldError,
    InvalidSortError,
)


class Table:
    def __init__(self, name: str, schema: dict[str, type], auto_increment: bool = True):
        self.name = name
        self._schema = schema
        self._records: list[dict[str, Any]] = []
        self._auto_increment = auto_increment
        self._next_id = 1

    def _get_next_id(self) -> int:
        if not self._records:
            return 1
        max_id = 0
        for record in self._records:
            record_id = record.get("id", 0)
            if isinstance(record_id, int) and record_id > max_id:
                max_id = record_id
        return max_id + 1

    def _validate_record(self, record: dict[str, Any]) -> None:
        for field, field_type in self._schema.items():
            if field not in record:
                raise ValidationError(
                    f"Отсутствует обязательное поле '{field}' в таблице '{self.name}'"
                )
            if not isinstance(record[field], field_type):
                raise ValidationError(
                    f"Поле '{field}' должно быть типа {field_type.__name__}, получен {type(record[field]).__name__}"
                )
        for field in record:
            if field not in self._schema:
                raise ValidationError(
                    f"Неизвестное поле '{field}' в таблице '{self.name}'"
                )

    def create(self, record: dict[str, Any]) -> dict[str, Any]:
        record_copy = deepcopy(record)
        if self._auto_increment and "id" not in record_copy:
            record_copy["id"] = self._get_next_id()
        elif "id" in record_copy:
            if any(r["id"] == record_copy["id"] for r in self._records):
                raise DuplicateIDError(
                    f"Запись с id={record_copy['id']} уже существует в таблице '{self.name}'"
                )
        self._validate_record(record_copy)
        self._records.append(record_copy)
        return deepcopy(record_copy)

    def find(self, record_id: Any) -> Optional[dict[str, Any]]:
        for record in self._records:
            if record["id"] == record_id:
                return deepcopy(record)
        return None

    def select(
        self,
        filters: Optional[dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        reverse: bool = False,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        result = deepcopy(self._records)
        if filters:
            for field in filters:
                if field not in self._schema:
                    raise InvalidFieldError(
                        f"Поле '{field}' не существует в таблице '{self.name}'"
                    )
            filtered_result = []
            for record in result:
                match = True
                for field, value in filters.items():
                    if field not in record or record[field] != value:
                        match = False
                        break
                if match:
                    filtered_result.append(record)
            result = filtered_result
        if sort_by:
            if sort_by not in self._schema:
                raise InvalidFieldError(
                    f"Поле '{sort_by}' не существует в таблице '{self.name}'"
                )
            try:
                result.sort(key=lambda x: x[sort_by], reverse=reverse)
            except TypeError as e:
                raise InvalidSortError(
                    f"Невозможно отсортировать по полю '{sort_by}': {e}"
                )
        if limit is not None and limit > 0:
            result = result[offset : offset + limit]
        elif offset > 0:
            result = result[offset:]
        return result

    def update(self, record_id: Any, updates: dict[str, Any]) -> dict[str, Any]:
        record_index = None
        for i, record in enumerate(self._records):
            if record["id"] == record_id:
                record_index = i
                break
        if record_index is None:
            raise RecordNotFoundError(
                f"Запись с id={record_id} не найдена в таблице '{self.name}'"
            )
        updated_record = deepcopy(self._records[record_index])
        updated_record.update(updates)
        if "id" in updates and updates["id"] != record_id:
            if any(
                r["id"] == updated_record["id"]
                for r in self._records
                if r["id"] != record_id
            ):
                raise DuplicateIDError(
                    f"Запись с id={updated_record['id']} уже существует в таблице '{self.name}'"
                )
        self._validate_record(updated_record)
        self._records[record_index] = updated_record
        return deepcopy(updated_record)

    def delete(self, record_id: Any) -> dict[str, Any]:
        record_index = None
        for i, record in enumerate(self._records):
            if record["id"] == record_id:
                record_index = i
                break
        if record_index is None:
            raise RecordNotFoundError(
                f"Запись с id={record_id} не найдена в таблице '{self.name}'"
            )
        deleted_record = deepcopy(self._records[record_index])
        del self._records[record_index]
        return deleted_record

    def delete_by_filter(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        records_to_delete = self.select(filters)
        deleted_records = []
        for record in records_to_delete:
            deleted = self.delete(record["id"])
            deleted_records.append(deleted)
        return deleted_records

    def clear(self) -> int:
        deleted_count = len(self._records)
        self._records = []
        return deleted_count

    def get_all(self) -> list[dict[str, Any]]:
        return deepcopy(self._records)

    @property
    def record_count(self) -> int:
        return len(self._records)

    @property
    def schema(self) -> dict[str, type]:
        return self._schema.copy()
