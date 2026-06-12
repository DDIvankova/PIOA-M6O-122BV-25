class DatabaseError(Exception):
    pass


class TableNotFoundError(DatabaseError):
    pass


class TableExistsError(DatabaseError):
    pass


class RecordNotFoundError(DatabaseError):
    pass


class DuplicateIDError(DatabaseError):
    pass


class ValidationError(DatabaseError):
    pass


class InvalidFieldError(DatabaseError):
    pass


class InvalidSortError(DatabaseError):
    pass


class InvalidStorageDataError(DatabaseError):
    pass


class StorageError(DatabaseError):
    pass
