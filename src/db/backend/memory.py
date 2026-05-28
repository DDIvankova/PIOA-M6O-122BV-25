from typing import Any, Optional
from copy import deepcopy


class DatabaseError(Exception):
    pass


class TableExistsError(DatabaseError):
    pass


class TableNotFoundError(DatabaseError):
    pass


class RecordNotFoundError(DatabaseError):
    pass


class ValidationError(DatabaseError):
    pass


class InMemoryDatabase:
    def __init__(self):
        self._tables: dict[str, list[dict[str, Any]]] = {}
        self._table_schemas: dict[str, dict[str, type]] = {}
        self._next_ids: dict[str, int] = {}
    
    def create_table(
        self, 
        table_name: str, 
        schema: dict[str, type],
        auto_increment: bool = True
    ) -> None:
        if table_name in self._tables:
            raise TableExistsError(f"Таблица '{table_name}' уже существует")
        
        if 'id' not in schema:
            raise ValidationError("Схема таблицы должна содержать поле 'id'")
        
        if schema['id'] not in (int, str):
            raise ValidationError("Поле 'id' должно быть типа int или str")
        
        self._tables[table_name] = []
        self._table_schemas[table_name] = schema
        self._next_ids[table_name] = 1 if auto_increment else 0
    
    def drop_table(self, table_name: str) -> None:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        
        del self._tables[table_name]
        del self._table_schemas[table_name]
        if table_name in self._next_ids:
            del self._next_ids[table_name]
    
    def _validate_record(self, table_name: str, record: dict[str, Any]) -> None:
        schema = self._table_schemas[table_name]
        
        for field, field_type in schema.items():
            if field not in record:
                raise ValidationError(f"Отсутствует обязательное поле '{field}'")
            if not isinstance(record[field], field_type):
                raise ValidationError(
                    f"Поле '{field}' должно быть типа {field_type.__name__}, "
                    f"получен {type(record[field]).__name__}"
                )
        
        for field in record:
            if field not in schema:
                raise ValidationError(f"Неизвестное поле '{field}'")
    
    def _get_next_id(self, table_name: str) -> int:
        current_id = self._next_ids.get(table_name, 1)
        self._next_ids[table_name] = current_id + 1
        return current_id
    
    def create_record(
        self, 
        table_name: str, 
        record: dict[str, Any],
        auto_id: bool = True
    ) -> dict[str, Any]:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        
        record_copy = deepcopy(record)
        
        if auto_id and 'id' not in record_copy:
            record_copy['id'] = self._get_next_id(table_name)
        
        self._validate_record(table_name, record_copy)
        
        existing_ids = [r['id'] for r in self._tables[table_name]]
        if record_copy['id'] in existing_ids:
            raise ValidationError(f"Запись с id={record_copy['id']} уже существует")
        
        self._tables[table_name].append(record_copy)
        return record_copy
    
    def select_records(
        self, 
        table_name: str, 
        filters: Optional[dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        
        result = self._tables[table_name].copy()
        
        if filters:
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
        
        result = result[offset:offset + limit] if limit else result[offset:]
        return deepcopy(result)
    
    def find_by_id(
        self, 
        table_name: str, 
        record_id: Any
    ) -> Optional[dict[str, Any]]:
        results = self.select_records(table_name, {'id': record_id})
        return results[0] if results else None
    
    def update_record(
        self, 
        table_name: str, 
        record_id: Any, 
        updates: dict[str, Any]
    ) -> dict[str, Any]:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        
        record_index = None
        for i, record in enumerate(self._tables[table_name]):
            if record['id'] == record_id:
                record_index = i
                break
        
        if record_index is None:
            raise RecordNotFoundError(
                f"Запись с id={record_id} в таблице '{table_name}' не найдена"
            )
        
        updated_record = deepcopy(self._tables[table_name][record_index])
        updated_record.update(updates)
        
        original_record = self._tables[table_name][record_index]
        self._tables[table_name][record_index] = updated_record
        
        try:
            self._validate_record(table_name, updated_record)
            if updates.get('id') and updates['id'] != record_id:
                existing_ids = [
                    r['id'] for j, r in enumerate(self._tables[table_name]) 
                    if j != record_index
                ]
                if updated_record['id'] in existing_ids:
                    raise ValidationError(
                        f"Запись с id={updated_record['id']} уже существует"
                    )
        except (ValidationError, DatabaseError):
            self._tables[table_name][record_index] = original_record
            raise
        
        return deepcopy(updated_record)
    
    def delete_record(
        self, 
        table_name: str, 
        record_id: Any
    ) -> dict[str, Any]:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        
        record_index = None
        for i, record in enumerate(self._tables[table_name]):
            if record['id'] == record_id:
                record_index = i
                break
        
        if record_index is None:
            raise RecordNotFoundError(
                f"Запись с id={record_id} в таблице '{table_name}' не найдена"
            )
        
        deleted_record = deepcopy(self._tables[table_name][record_index])
        del self._tables[table_name][record_index]
        
        return deleted_record
    
    def delete_records_by_filter(
        self, 
        table_name: str, 
        filters: dict[str, Any]
    ) -> list[dict[str, Any]]:
        records_to_delete = self.select_records(table_name, filters)
        deleted_records = []
        
        for record in records_to_delete:
            deleted = self.delete_record(table_name, record['id'])
            deleted_records.append(deleted)
        
        return deleted_records
    
    def get_table_names(self) -> list[str]:
        return list(self._tables.keys())
    
    def get_table_info(self, table_name: str) -> dict[str, Any]:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        
        return {
            'name': table_name,
            'schema': self._table_schemas[table_name],
            'record_count': len(self._tables[table_name])
        }
    
    def clear_table(self, table_name: str) -> int:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        
        deleted_count = len(self._tables[table_name])
        self._tables[table_name] = []
        
        return deleted_count


db = InMemoryDatabase()