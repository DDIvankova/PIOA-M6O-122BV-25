from datetime import date
from typing import Optional, Any
from .backend.memory import db, ValidationError, TableNotFoundError, RecordNotFoundError


BOOKS_SCHEMA = {
    'id': int,
    'title': str,
    'author': str,
    'year': int,
    'genre': str,
    'is_available': bool
}

READERS_SCHEMA = {
    'id': int,
    'first_name': str,
    'last_name': str,
    'email': str,
    'phone': str
}

LOANS_SCHEMA = {
    'id': int,
    'book_id': int,
    'reader_id': int,
    'loan_date': str,
    'return_date': Optional[str]
}


def init_database() -> None:
    try:
        db.create_table('books', BOOKS_SCHEMA)
        db.create_table('readers', READERS_SCHEMA)
        db.create_table('loans', LOANS_SCHEMA)
        
        db.create_record('books', {
            'title': 'Мастер и Маргарита',
            'author': 'Михаил Булгаков',
            'year': 1967,
            'genre': 'Роман',
            'is_available': True
        })
        db.create_record('books', {
            'title': 'Преступление и наказание',
            'author': 'Фёдор Достоевский',
            'year': 1866,
            'genre': 'Роман',
            'is_available': True
        })
        db.create_record('books', {
            'title': '1984',
            'author': 'Джордж Оруэлл',
            'year': 1949,
            'genre': 'Антиутопия',
            'is_available': False
        })
        
        db.create_record('readers', {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'email': 'ivan@example.com',
            'phone': '+7-123-456-78-90'
        })
        db.create_record('readers', {
            'first_name': 'Мария',
            'last_name': 'Сидорова',
            'email': 'maria@example.com',
            'phone': '+7-098-765-43-21'
        })
        
    except ValidationError:
        pass


def _print_header(text: str) -> None:
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50)


def _print_separator() -> None:
    print("-" * 50)


def _print_record(record: dict[str, Any]) -> None:
    for key, value in record.items():
        if key == 'id':
            print(f"  #{value}")
        else:
            print(f"  {key}: {value}")
    _print_separator()


def _print_records(records: list[dict[str, Any]], title: str = "Записи") -> None:
    _print_header(title)
    if not records:
        print("  Записи не найдены.")
    else:
        for record in records:
            _print_record(record)
    input("\nНажмите Enter для продолжения...")


def _read_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Ошибка: введите целое число.")


def _read_optional_int(prompt: str) -> Optional[int]:
    value = input(prompt).strip()
    if value == "":
        return None
    try:
        return int(value)
    except ValueError:
        print("Ошибка: введите целое число или оставьте поле пустым.")
        return None


def _read_bool(prompt: str) -> bool:
    while True:
        value = input(prompt).strip().lower()
        if value in ('да', 'yes', 'true', '1', '+'):
            return True
        if value in ('нет', 'no', 'false', '0', '-'):
            return False
        print("Ошибка: введите 'да' или 'нет'")


def _read_optional_str(prompt: str) -> Optional[str]:
    value = input(prompt).strip()
    return value if value else None


def _add_record_menu() -> None:
    _print_header("Добавление записи")
    
    print("Выберите таблицу:")
    print("1. Книги")
    print("2. Читатели")
    print("3. Выдачи")
    
    choice = input("Ваш выбор: ").strip()
    
    try:
        if choice == "1":
            _add_book()
        elif choice == "2":
            _add_reader()
        elif choice == "3":
            _add_loan()
        else:
            print("Неверный выбор.")
    except ValidationError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    
    input("\nНажмите Enter для продолжения...")


def _add_book() -> None:
    print("\n--- Добавление книги ---")
    
    record = {
        'title': input("Название: ").strip(),
        'author': input("Автор: ").strip(),
        'year': _read_int("Год издания: "),
        'genre': input("Жанр: ").strip(),
        'is_available': _read_bool("Доступна для выдачи (да/нет): ")
    }
    
    result = db.create_record('books', record)
    print(f"\nКнига успешно добавлена (ID: {result['id']})")


def _add_reader() -> None:
    print("\n--- Добавление читателя ---")
    
    record = {
        'first_name': input("Имя: ").strip(),
        'last_name': input("Фамилия: ").strip(),
        'email': input("Email: ").strip(),
        'phone': input("Телефон: ").strip()
    }
    
    result = db.create_record('readers', record)
    print(f"\nЧитатель успешно добавлен (ID: {result['id']})")


def _add_loan() -> None:
    print("\n--- Добавление выдачи ---")
    
    record = {
        'book_id': _read_int("ID книги: "),
        'reader_id': _read_int("ID читателя: "),
        'loan_date': input("Дата выдачи (ГГГГ-ММ-ДД): ").strip(),
        'return_date': None
    }
    
    result = db.create_record('loans', record)
    print(f"\nВыдача успешно добавлена (ID: {result['id']})")
    
    book = db.find_by_id('books', record['book_id'])
    if book:
        db.update_record('books', record['book_id'], {'is_available': False})


def _view_records_menu() -> None:
    _print_header("Просмотр записей")
    
    print("Выберите таблицу:")
    print("1. Книги")
    print("2. Читатели")
    print("3. Выдачи")
    print("4. Все таблицы")
    
    choice = input("Ваш выбор: ").strip()
    
    try:
        if choice == "1":
            _view_books()
        elif choice == "2":
            _view_readers()
        elif choice == "3":
            _view_loans()
        elif choice == "4":
            _view_all_tables()
        else:
            print("Неверный выбор.")
            input("\nНажмите Enter для продолжения...")
    except Exception as e:
        print(f"Ошибка: {e}")
        input("\nНажмите Enter для продолжения...")


def _view_books() -> None:
    print("\n--- Фильтрация книг ---")
    print("Оставьте поле пустым, чтобы пропустить фильтр")
    
    filters = {}
    
    title = _read_optional_str("Название: ")
    if title:
        filters['title'] = title
    
    author = _read_optional_str("Автор: ")
    if author:
        filters['author'] = author
    
    year = _read_optional_int("Год издания: ")
    if year is not None:
        filters['year'] = year
    
    genre = _read_optional_str("Жанр: ")
    if genre:
        filters['genre'] = genre
    
    available = _read_optional_str("Доступность (доступна/недоступна): ")
    if available:
        filters['is_available'] = available.lower() in ('доступна', 'да', 'true', 'yes', '1','+')
    
    records = db.select_records('books', filters if filters else None)
    _print_records(records, "Книги")


def _view_readers() -> None:
    print("\n--- Фильтрация читателей ---")
    print("Оставьте поле пустым, чтобы пропустить фильтр")
    
    filters = {}
    
    first_name = _read_optional_str("Имя: ")
    if first_name:
        filters['first_name'] = first_name
    
    last_name = _read_optional_str("Фамилия: ")
    if last_name:
        filters['last_name'] = last_name
    
    email = _read_optional_str("Email: ")
    if email:
        filters['email'] = email
    
    records = db.select_records('readers', filters if filters else None)
    _print_records(records, "Читатели")


def _view_loans() -> None:
    print("\n--- Фильтрация выдач ---")
    print("Оставьте поле пустым, чтобы пропустить фильтр")
    
    filters = {}
    
    book_id = _read_optional_int("ID книги: ")
    if book_id is not None:
        filters['book_id'] = book_id
    
    reader_id = _read_optional_int("ID читателя: ")
    if reader_id is not None:
        filters['reader_id'] = reader_id
    
    records = db.select_records('loans', filters if filters else None)
    
    enriched_records = []
    for loan in records:
        enriched = loan.copy()
        book = db.find_by_id('books', loan['book_id'])
        reader = db.find_by_id('readers', loan['reader_id'])
        if book:
            enriched['book_title'] = book['title']
        if reader:
            enriched['reader_name'] = f"{reader['first_name']} {reader['last_name']}"
        enriched_records.append(enriched)
    
    _print_records(enriched_records, "Выдачи книг")


def _view_all_tables() -> None:
    _print_header("Информация о таблицах")
    
    for table_name in db.get_table_names():
        info = db.get_table_info(table_name)
        print(f"\n{table_name.upper()}:")
        print(f"  Записей: {info['record_count']}")
        print("  Схема:")
        for field, field_type in info['schema'].items():
            print(f"    {field}: {field_type.__name__}")
    
    input("\nНажмите Enter для продолжения...")


def _update_record_menu() -> None:
    _print_header("Обновление записи")
    
    print("Выберите таблицу:")
    print("1. Книги")
    print("2. Читатели")
    print("3. Выдачи")
    
    choice = input("Ваш выбор: ").strip()
    
    table_map = {
        "1": "books",
        "2": "readers",
        "3": "loans"
    }
    
    if choice not in table_map:
        print("Неверный выбор.")
        input("\nНажмите Enter для продолжения...")
        return
    
    table_name = table_map[choice]
    
    try:
        record_id = _read_int("ID записи для обновления: ")
        
        current = db.find_by_id(table_name, record_id)
        if not current:
            print(f"Запись с ID {record_id} не найдена")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("\nТекущие значения (оставьте поле пустым, чтобы не менять):")
        
        updates = {}
        for key, value in current.items():
            if key != 'id':
                new_value = input(f"{key} (было: {value}): ").strip()
                if new_value:
                    if isinstance(value, bool):
                        updates[key] = new_value.lower() in ('да', 'yes', 'true', '1')
                    elif isinstance(value, int):
                        try:
                            updates[key] = int(new_value)
                        except ValueError:
                            print(f"Значение для {key} должно быть числом, пропускаем")
                    else:
                        updates[key] = new_value
        
        if updates:
            result = db.update_record(table_name, record_id, updates)
            print(f"\nЗапись успешно обновлена (ID: {result['id']})")
            
            if table_name == 'books' and 'is_available' in updates:
                active_loans = db.select_records('loans', {'book_id': record_id, 'return_date': None})
                if active_loans and updates['is_available']:
                    print("Внимание: на эту книгу есть активные выдачи!")
        else:
            print("Нет изменений")
            
    except (RecordNotFoundError, ValidationError) as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    
    input("\nНажмите Enter для продолжения...")


def _delete_record_menu() -> None:
    _print_header("Удаление записи")
    
    print("Выберите таблицу:")
    print("1. Книги")
    print("2. Читатели")
    print("3. Выдачи")
    
    choice = input("Ваш выбор: ").strip()
    
    table_map = {
        "1": "books",
        "2": "readers",
        "3": "loans"
    }
    
    if choice not in table_map:
        print("Неверный выбор.")
        input("\nНажмите Enter для продолжения...")
        return
    
    table_name = table_map[choice]
    
    try:
        record_id = _read_int("ID записи для удаления: ")
        
        record = db.find_by_id(table_name, record_id)
        if not record:
            print(f"Запись с ID {record_id} не найдена")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("\nЗапись будет удалена:")
        _print_record(record)
        
        confirm = input("Подтвердите удаление (да/нет): ").strip().lower()
        if confirm in ('да', 'yes', 'true', '1'):
            deleted = db.delete_record(table_name, record_id)
            print(f"Запись ID {deleted['id']} успешно удалена")
            
            if table_name == 'books':
                related_loans = db.delete_records_by_filter('loans', {'book_id': record_id})
                if related_loans:
                    print(f"Удалено связанных выдач: {len(related_loans)}")
            
            if table_name == 'readers':
                related_loans = db.delete_records_by_filter('loans', {'reader_id': record_id})
                if related_loans:
                    print(f"Удалено связанных выдач: {len(related_loans)}")
        else:
            print("Удаление отменено")
            
    except (RecordNotFoundError, ValidationError) as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    
    input("\nНажмите Enter для продолжения...")


def _return_book_menu() -> None:
    _print_header("Возврат книги")
    
    try:
        loan_id = _read_int("ID выдачи: ")
        
        loan = db.find_by_id('loans', loan_id)
        if not loan:
            print(f"Выдача с ID {loan_id} не найдена")
            input("\nНажмите Enter для продолжения...")
            return
        
        if loan['return_date']:
            print(f"Книга уже возвращена {loan['return_date']}")
            input("\nНажмите Enter для продолжения...")
            return
        
        from datetime import date
        return_date = str(date.today())
        
        db.update_record('loans', loan_id, {'return_date': return_date})
        db.update_record('books', loan['book_id'], {'is_available': True})
        
        print(f"Книга успешно возвращена (дата: {return_date})")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    
    input("\nНажмите Enter для продолжения...")


def _print_main_menu() -> None:
    print("\n" + "=" * 50)
    print("  БИБЛИОТЕЧНАЯ СИСТЕМА (In-Memory Database)")
    print("=" * 50)
    print("1. Добавить запись")
    print("2. Просмотр записей")
    print("3. Обновить запись")
    print("4. Удалить запись")
    print("5. Вернуть книгу")
    print("0. Выход")
    print("=" * 50)


def run() -> None:
    init_database()
    
    print("\nДобро пожаловать в библиотечную систему!")
    
    while True:
        _print_main_menu()
        choice = input("Выберите действие: ").strip()
        
        if choice == "1":
            _add_record_menu()
        elif choice == "2":
            _view_records_menu()
        elif choice == "3":
            _update_record_menu()
        elif choice == "4":
            _delete_record_menu()
        elif choice == "5":
            _return_book_menu()
        elif choice == "0":
            print("\nДо свидания!")
            break
        else:
            print("Неизвестная команда. Повторите ввод.")
            input("Нажмите Enter для продолжения...")


if __name__ == "__main__":
    run()