"""
Модуль реализации in-memory базы данных.
"""

from typing import Any, Optional
from .table import Table
from .errors import TableNotFoundError, TableExistsError, ValidationError


class InMemoryDatabase:
    """
    In-memory база данных с поддержкой множества таблиц.
    """
    
    def __init__(self):
        """Инициализация пустой базы данных."""
        self._tables: dict[str, Table] = {}
    
    def create_table(
        self,
        name: str,
        schema: dict[str, type],
        auto_increment: bool = True
    ) -> Table:
        """
        Создание новой таблицы.
        
        Args:
            name: Имя таблицы
            schema: Схема таблицы
            auto_increment: Использовать автоинкремент для ID
            
        Returns:
            Созданная таблица
        """
        if name in self._tables:
            raise TableExistsError(f"Таблица '{name}' уже существует")
        
        table = Table(name, schema, auto_increment)
        self._tables[name] = table
        return table
    
    def drop_table(self, name: str) -> None:
        """
        Удаление таблицы.
        
        Args:
            name: Имя таблицы
        """
        if name not in self._tables:
            raise TableNotFoundError(f"Таблица '{name}' не существует")
        
        del self._tables[name]
    
    def get_table(self, name: str) -> Table:
        """
        Получение таблицы по имени.
        
        Args:
            name: Имя таблицы
            
        Returns:
            Таблица
        """
        if name not in self._tables:
            raise TableNotFoundError(f"Таблица '{name}' не существует")
        
        return self._tables[name]
    
    def table_exists(self, name: str) -> bool:
        """Проверка существования таблицы."""
        return name in self._tables
    
    def get_table_names(self) -> list[str]:
        """Получение списка имен таблиц."""
        return list(self._tables.keys())
    
    def get_all_tables_info(self) -> dict[str, dict]:
        """Получение информации о всех таблицах."""
        return {
            name: {
                'schema': table.schema,
                'record_count': table.record_count  # Убедитесь, что это поле есть
            }
            for name, table in self._tables.items()
        }