from typing import Any, Optional
from .table import Table
from .errors import TableNotFoundError, TableExistsError, ValidationError


class InMemoryDatabase:
    
    def __init__(self):
        self._tables: dict[str, Table] = {}
    
    def create_table(
        self,
        name: str,
        schema: dict[str, type],
        auto_increment: bool = True
    ) -> Table:
        if name in self._tables:
            raise TableExistsError(f"Таблица '{name}' уже существует")
        
        table = Table(name, schema, auto_increment)
        self._tables[name] = table
        return table
    
    def drop_table(self, name: str) -> None:
        if name not in self._tables:
            raise TableNotFoundError(f"Таблица '{name}' не существует")
        
        del self._tables[name]
    
    def get_table(self, name: str) -> Table:
        if name not in self._tables:
            raise TableNotFoundError(f"Таблица '{name}' не существует")
        
        return self._tables[name]
    
    def table_exists(self, name: str) -> bool:
        return name in self._tables
    
    def get_table_names(self) -> list[str]:
        return list(self._tables.keys())
    
    def get_all_tables_info(self) -> dict[str, dict]:
        return {
            name: {
                'schema': table.schema,
                'record_count': table.record_count
            }
            for name, table in self._tables.items()
        }