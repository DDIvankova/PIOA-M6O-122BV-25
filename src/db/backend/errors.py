class DatabaseError(Exception):
    pass


class TableError(DatabaseError):
    pass


class TableNotFoundError(TableError):
    pass


class TableExistsError(TableError):
    pass


class RecordError(DatabaseError):
    pass


class RecordNotFoundError(RecordError):
    pass


class DuplicateIDError(RecordError):
    pass


class ValidationError(RecordError):
    pass


class InvalidAgeError(ValidationError):
    pass


class InvalidFieldError(ValidationError):
    pass


class InvalidSortError(ValidationError):
    pass