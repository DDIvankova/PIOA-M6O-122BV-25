from typing import Any, Optional, Callable
from copy import deepcopy


class DatabaseError(Exception):
    """Базовое исключение для ошибок базы данных."""
    pass


class TableExistsError(DatabaseError):
    """Исключение при попытке создать существующую таблицу."""
    pass


class TableNotFoundError(DatabaseError):
    """Исключение при обращении к несуществующей таблице."""
    pass


class RecordNotFoundError(DatabaseError):
    """Исключение при обращении к несуществующей записи."""
    pass


class ValidationError(DatabaseError):
    """Исключение при ошибках валидации данных."""
    pass


class InMemoryDatabase:
    """
    In-memory база данных с поддержкой множества таблиц.
    
    Каждая таблица представляет собой список записей (словарей).
    Записи обязательно содержат поле 'id' (уникальный идентификатор).
    """
    
    def __init__(self):
        """Инициализация пустой базы данных."""
        self._tables: dict[str, list[dict[str, Any]]] = {}
        self._table_schemas: dict[str, dict[str, type]] = {}
        self._next_ids: dict[str, int] = {}
    
    def create_table(
        self, 
        table_name: str, 
        schema: dict[str, type],
        auto_increment: bool = True
    ) -> None:
        """
        Создание новой таблицы.
        
        Args:
            table_name: Имя таблицы
            schema: Схема таблицы {имя_поля: тип}
            auto_increment: Использовать автоинкремент для id
            
        Raises:
            TableExistsError: Если таблица уже существует
            ValidationError: Если схема не содержит поля id
        """
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
        """
        Удаление таблицы.
        
        Args:
            table_name: Имя таблицы
            
        Raises:
            TableNotFoundError: Если таблица не существует
        """
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        
        del self._tables[table_name]
        del self._table_schemas[table_name]
        if table_name in self._next_ids:
            del self._next_ids[table_name]
    
    def _validate_record(self, table_name: str, record: dict[str, Any]) -> None:
        """
        Валидация записи соответствию схеме таблицы.
        
        Args:
            table_name: Имя таблицы
            record: Запись для валидации
            
        Raises:
            ValidationError: Если запись не соответствует схеме
        """
        schema = self._table_schemas[table_name]
        
        # Проверка наличия всех полей
        for field, field_type in schema.items():
            if field not in record:
                raise ValidationError(f"Отсутствует обязательное поле '{field}'")
            if not isinstance(record[field], field_type):
                raise ValidationError(
                    f"Поле '{field}' должно быть типа {field_type.__name__}, "
                    f"получен {type(record[field]).__name__}"
                )
        
        # Проверка отсутствия лишних полей
        for field in record:
            if field not in schema:
                raise ValidationError(f"Неизвестное поле '{field}'")
    
    def _get_next_id(self, table_name: str) -> int:
        """
        Получение следующего доступного ID для автоинкремента.
        
        Args:
            table_name: Имя таблицы
            
        Returns:
            Следующий ID
        """
        current_id = self._next_ids.get(table_name, 1)
        self._next_ids[table_name] = current_id + 1
        return current_id
    
    def create_record(
        self, 
        table_name: str, 
        record: dict[str, Any],
        auto_id: bool = True
    ) -> dict[str, Any]:
        """
        Добавление новой записи в таблицу.
        
        Args:
            table_name: Имя таблицы
            record: Запись для добавления
            auto_id: Автоматически генерировать ID
            
        Returns:
            Добавленная запись
            
        Raises:
            TableNotFoundError: Если таблица не существует
            ValidationError: Если запись невалидна
        """
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        
        record_copy = deepcopy(record)
        
        # Автоматическая генерация ID
        if auto_id and 'id' not in record_copy:
            record_copy['id'] = self._get_next_id(table_name)
        
        # Валидация
        self._validate_record(table_name, record_copy)
        
        # Проверка уникальности ID
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
        """
        Выборка записей с фильтрацией.
        
        Args:
            table_name: Имя таблицы
            filters: Словарь фильтров {поле: значение}
            limit: Максимальное количество записей
            offset: Смещение для пагинации
            
        Returns:
            Список записей, удовлетворяющих фильтрам
            
        Raises:
            TableNotFoundError: Если таблица не существует
        """
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        
        result = self._tables[table_name].copy()
        
        # Применение фильтров
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
        
        # Пагинация
        result = result[offset:offset + limit] if limit else result[offset:]
        
        return deepcopy(result)
    
    def find_by_id(
        self, 
        table_name: str, 
        record_id: Any
    ) -> Optional[dict[str, Any]]:
        """
        Поиск записи по ID.
        
        Args:
            table_name: Имя таблицы
            record_id: ID записи
            
        Returns:
            Найденная запись или None
        """
        results = self.select_records(table_name, {'id': record_id})
        return results[0] if results else None
    
    def update_record(
        self, 
        table_name: str, 
        record_id: Any, 
        updates: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Обновление записи по ID.
        
        Args:
            table_name: Имя таблицы
            record_id: ID обновляемой записи
            updates: Словарь обновлений {поле: новое_значение}
            
        Returns:
            Обновленная запись
            
        Raises:
            TableNotFoundError: Если таблица не существует
            RecordNotFoundError: Если запись не найдена
            ValidationError: Если обновление невалидно
        """
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        
        # Поиск записи
        record_index = None
        for i, record in enumerate(self._tables[table_name]):
            if record['id'] == record_id:
                record_index = i
                break
        
        if record_index is None:
            raise RecordNotFoundError(
                f"Запись с id={record_id} в таблице '{table_name}' не найдена"
            )
        
        # Создание обновленной записи
        updated_record = deepcopy(self._tables[table_name][record_index])
        updated_record.update(updates)
        
        # Валидация обновленной записи
        # Временно заменяем для валидации
        original_record = self._tables[table_name][record_index]
        self._tables[table_name][record_index] = updated_record
        
        try:
            self._validate_record(table_name, updated_record)
            # Проверка уникальности ID (если ID изменился)
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
            # Откат изменений в случае ошибки
            self._tables[table_name][record_index] = original_record
            raise
        
        return deepcopy(updated_record)
    
    def delete_record(
        self, 
        table_name: str, 
        record_id: Any
    ) -> dict[str, Any]:
        """
        Удаление записи по ID.
        
        Args:
            table_name: Имя таблицы
            record_id: ID удаляемой записи
            
        Returns:
            Удаленная запись
            
        Raises:
            TableNotFoundError: Если таблица не существует
            RecordNotFoundError: Если запись не найдена
        """
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
        """
        Удаление записей по фильтру.
        
        Args:
            table_name: Имя таблицы
            filters: Словарь фильтров
            
        Returns:
            Список удаленных записей
        """
        records_to_delete = self.select_records(table_name, filters)
        deleted_records = []
        
        for record in records_to_delete:
            deleted = self.delete_record(table_name, record['id'])
            deleted_records.append(deleted)
        
        return deleted_records
    
    def get_table_names(self) -> list[str]:
        """Возвращает список имен всех таблиц."""
        return list(self._tables.keys())
    
    def get_table_info(self, table_name: str) -> dict[str, Any]:
        """
        Возвращает информацию о таблице.
        
        Returns:
            Словарь с информацией о таблице (схема, количество записей)
        """
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        
        return {
            'name': table_name,
            'schema': self._table_schemas[table_name],
            'record_count': len(self._tables[table_name])
        }
    
    def clear_table(self, table_name: str) -> int:
        """
        Очистка таблицы (удаление всех записей).
        
        Returns:
            Количество удаленных записей
        """
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует")
        
        deleted_count = len(self._tables[table_name])
        self._tables[table_name] = []
        
        return deleted_count


# Создание глобального экземпляра БД
db = InMemoryDatabase()