class DatabaseError(Exception):
    pass


class TableError(DatabaseError):
    pass


class TableNotFoundError(TableError):
    """Исключение при обращении к несуществующей таблице."""
    pass


class TableExistsError(TableError):
    """Исключение при попытке создать существующую таблицу."""
    pass


class RecordError(DatabaseError):
    """Базовое исключение для ошибок записей."""
    pass


class RecordNotFoundError(RecordError):
    """Исключение при обращении к несуществующей записи."""
    pass


class DuplicateIDError(RecordError):
    """Исключение при попытке создать запись с существующим ID."""
    pass


class ValidationError(RecordError):
    """Исключение при ошибках валидации данных."""
    pass


class InvalidAgeError(ValidationError):
    """Исключение при некорректном возрасте."""
    pass


class InvalidFieldError(ValidationError):
    """Исключение при некорректном имени поля."""
    pass


class InvalidSortError(ValidationError):
    """Исключение при некорректной сортировке."""
    pass