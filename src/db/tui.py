from typing import Any, Optional
from datetime import date
from .backend.memory import InMemoryDatabase
from .backend.table import Table
from .backend.errors import (
    ValidationError, RecordNotFoundError, DuplicateIDError,
    InvalidFieldError, InvalidSortError
)


class LibraryUI:
    
    def __init__(self):
        self.db = InMemoryDatabase()
        self._init_database()
    
    def _init_database(self) -> None:
        books_schema = {
            'id': int,
            'title': str,
            'author': str,
            'year': int,
            'genre': str,
            'is_available': bool
        }
        
        readers_schema = {
            'id': int,
            'first_name': str,
            'last_name': str,
            'email': str,
            'phone': str
        }
        
        loans_schema = {
            'id': int,
            'book_id': int,
            'reader_id': int,
            'loan_date': str,
            'return_date': Optional[str]
        }
        
        self.books = self.db.create_table('books', books_schema)
        self.readers = self.db.create_table('readers', readers_schema)
        self.loans = self.db.create_table('loans', loans_schema)
        
        self._add_test_data()
    
    def _add_test_data(self) -> None:
        try:
            self.books.create({
                'title': 'Мастер и Маргарита',
                'author': 'Михаил Булгаков',
                'year': 1967,
                'genre': 'Роман',
                'is_available': True
            })
            self.books.create({
                'title': 'Преступление и наказание',
                'author': 'Фёдор Достоевский',
                'year': 1866,
                'genre': 'Роман',
                'is_available': True
            })
            self.books.create({
                'title': '1984',
                'author': 'Джордж Оруэлл',
                'year': 1949,
                'genre': 'Антиутопия',
                'is_available': False
            })
            self.books.create({
                'title': 'Война и мир',
                'author': 'Лев Толстой',
                'year': 1869,
                'genre': 'Роман-эпопея',
                'is_available': True
            })
            
            self.readers.create({
                'first_name': 'Иван',
                'last_name': 'Петров',
                'email': 'ivan@example.com',
                'phone': '+7-123-456-78-90'
            })
            self.readers.create({
                'first_name': 'Мария',
                'last_name': 'Сидорова',
                'email': 'maria@example.com',
                'phone': '+7-098-765-43-21'
            })
            
        except (ValidationError, DuplicateIDError):
            pass
    
    def _print_header(self, text: str) -> None:
        print("\n" + "=" * 50)
        print(f"  {text}")
        print("=" * 50)
    
    def _print_separator(self) -> None:
        print("-" * 50)
    
    def _print_record(self, record: dict[str, Any]) -> None:
        for key, value in record.items():
            if key == 'id':
                print(f"  #{value}")
            else:
                if isinstance(value, bool):
                    value = "Да" if value else "Нет"
                print(f"  {key}: {value}")
        self._print_separator()
    
    def _print_records(
        self,
        records: list[dict[str, Any]],
        title: str = "Записи"
    ) -> None:
        self._print_header(title)
        if not records:
            print("  Записи не найдены.")
        else:
            for record in records:
                self._print_record(record)
    
    def _read_int(self, prompt: str) -> int:
        while True:
            try:
                return int(input(prompt).strip())
            except ValueError:
                print("Ошибка: введите целое число.")
    
    def _read_optional_int(self, prompt: str) -> Optional[int]:
        value = input(prompt).strip()
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")
            return None
    
    def _read_bool(self, prompt: str) -> bool:
        while True:
            value = input(prompt).strip().lower()
            if value in ('да', 'yes', 'true', '1', '+'):
                return True
            if value in ('нет', 'no', 'false', '0', '-'):
                return False
            print("Ошибка: введите 'да' или 'нет'")
    
    def _read_optional_str(self, prompt: str) -> Optional[str]:
        value = input(prompt).strip()
        return value if value else None
    
    def _read_sort_options(self) -> tuple[Optional[str], bool]:
        sort_by = self._read_optional_str("Сортировать по полю (Enter - без сортировки): ")
        if not sort_by:
            return None, False
        
        order = self._read_optional_str("Порядок (возр/уб): ")
        reverse = order and order.lower() in ('уб', 'убыв', 'desc', 'убывание')
        return sort_by, reverse
    
    def _add_book(self) -> None:
        print("\n--- Добавление книги ---")
        
        record = {
            'title': input("Название: ").strip(),
            'author': input("Автор: ").strip(),
            'year': self._read_int("Год издания: "),
            'genre': input("Жанр: ").strip(),
            'is_available': self._read_bool("Доступна для выдачи (да/нет): ")
        }
        
        result = self.books.create(record)
        print(f"\nКнига успешно добавлена (ID: {result['id']})")
    
    def _add_reader(self) -> None:
        print("\n--- Добавление читателя ---")
        
        record = {
            'first_name': input("Имя: ").strip(),
            'last_name': input("Фамилия: ").strip(),
            'email': input("Email: ").strip(),
            'phone': input("Телефон: ").strip()
        }
        
        result = self.readers.create(record)
        print(f"\nЧитатель успешно добавлен (ID: {result['id']})")
    
    def _add_loan(self) -> None:
        print("\n--- Добавление выдачи ---")
        
        book_id = self._read_int("ID книги: ")
        reader_id = self._read_int("ID читателя: ")
        
        record = {
            'book_id': book_id,
            'reader_id': reader_id,
            'loan_date': str(date.today()),
            'return_date': None
        }
        
        result = self.loans.create(record)
        print(f"\nВыдача успешно добавлена (ID: {result['id']})")
        
        try:
            self.books.update(book_id, {'is_available': False})
        except RecordNotFoundError:
            print(f"Внимание: книга с ID {book_id} не найдена")
    
    def _view_books(self) -> None:
        print("\n--- Фильтрация книг ---")
        print("Оставьте поле пустым, чтобы пропустить фильтр")
        
        filters = {}
        
        title = self._read_optional_str("Название: ")
        if title:
            filters['title'] = title
        
        author = self._read_optional_str("Автор: ")
        if author:
            filters['author'] = author
        
        year = self._read_optional_int("Год издания: ")
        if year is not None:
            filters['year'] = year
        
        genre = self._read_optional_str("Жанр: ")
        if genre:
            filters['genre'] = genre
        
        available = self._read_optional_str("Доступность (доступна/недоступна): ")
        if available:
            filters['is_available'] = available.lower() in ('доступна', 'да', 'true', 'yes', '1')
        
        sort_by, reverse = self._read_sort_options()
        
        try:
            records = self.books.select(
                filters if filters else None,
                sort_by=sort_by,
                reverse=reverse
            )
            self._print_records(records, "Книги")
        except (InvalidFieldError, InvalidSortError) as e:
            print(f"Ошибка: {e}")
    
    def _view_readers(self) -> None:
        print("\n--- Фильтрация читателей ---")
        print("Оставьте поле пустым, чтобы пропустить фильтр")
        
        filters = {}
        
        first_name = self._read_optional_str("Имя: ")
        if first_name:
            filters['first_name'] = first_name
        
        last_name = self._read_optional_str("Фамилия: ")
        if last_name:
            filters['last_name'] = last_name
        
        email = self._read_optional_str("Email: ")
        if email:
            filters['email'] = email
        
        sort_by, reverse = self._read_sort_options()
        
        try:
            records = self.readers.select(
                filters if filters else None,
                sort_by=sort_by,
                reverse=reverse
            )
            self._print_records(records, "Читатели")
        except (InvalidFieldError, InvalidSortError) as e:
            print(f"Ошибка: {e}")
    
    def _view_loans(self) -> None:
        print("\n--- Фильтрация выдач ---")
        print("Оставьте поле пустым, чтобы пропустить фильтр")
        
        filters = {}
        
        book_id = self._read_optional_int("ID книги: ")
        if book_id is not None:
            filters['book_id'] = book_id
        
        reader_id = self._read_optional_int("ID читателя: ")
        if reader_id is not None:
            filters['reader_id'] = reader_id
        
        records = self.loans.select(filters if filters else None)
        
        enriched_records = []
        for loan in records:
            enriched = loan.copy()
            book = self.books.find(loan['book_id'])
            reader = self.readers.find(loan['reader_id'])
            if book:
                enriched['book_title'] = book['title']
            if reader:
                enriched['reader_name'] = f"{reader['first_name']} {reader['last_name']}"
            enriched_records.append(enriched)
        
        self._print_records(enriched_records, "Выдачи книг")
    
    def _update_book(self) -> None:
        record_id = self._read_int("ID книги: ")
        
        book = self.books.find(record_id)
        if not book:
            print(f"Книга с ID {record_id} не найдена")
            return
        
        print("\nТекущие значения (оставьте поле пустым, чтобы не менять):")
        
        updates = {}
        for key, value in book.items():
            if key != 'id':
                prompt = f"{key} (было: {value}): "
                new_value = input(prompt).strip()
                if new_value:
                    if isinstance(value, bool):
                        updates[key] = new_value.lower() in ('да', 'yes', 'true', '1')
                    elif isinstance(value, int):
                        updates[key] = int(new_value)
                    else:
                        updates[key] = new_value
        
        if updates:
            result = self.books.update(record_id, updates)
            print(f"\nКнига успешно обновлена (ID: {result['id']})")
        else:
            print("Нет изменений")
    
    def _update_reader(self) -> None:
        record_id = self._read_int("ID читателя: ")
        
        reader = self.readers.find(record_id)
        if not reader:
            print(f"Читатель с ID {record_id} не найден")
            return
        
        print("\nТекущие значения (оставьте поле пустым, чтобы не менять):")
        
        updates = {}
        for key, value in reader.items():
            if key != 'id':
                new_value = input(f"{key} (было: {value}): ").strip()
                if new_value:
                    updates[key] = new_value
        
        if updates:
            result = self.readers.update(record_id, updates)
            print(f"\nЧитатель успешно обновлен (ID: {result['id']})")
        else:
            print("Нет изменений")
    
    def _delete_book(self) -> None:
        record_id = self._read_int("ID книги: ")
        
        book = self.books.find(record_id)
        if not book:
            print(f"Книга с ID {record_id} не найдена")
            return
        
        print("\nКнига будет удалена:")
        self._print_record(book)
        
        confirm = input("Подтвердите удаление (да/нет): ").strip().lower()
        if confirm in ('да', 'yes', 'true', '1'):
            deleted = self.books.delete(record_id)
            print(f"Книга ID {deleted['id']} успешно удалена")
            
            related_loans = self.loans.delete_by_filter({'book_id': record_id})
            if related_loans:
                print(f"Удалено связанных выдач: {len(related_loans)}")
        else:
            print("Удаление отменено")
    
    def _delete_reader(self) -> None:
        record_id = self._read_int("ID читателя: ")
        
        reader = self.readers.find(record_id)
        if not reader:
            print(f"Читатель с ID {record_id} не найден")
            return
        
        print("\nЧитатель будет удален:")
        self._print_record(reader)
        
        confirm = input("Подтвердите удаление (да/нет): ").strip().lower()
        if confirm in ('да', 'yes', 'true', '1'):
            deleted = self.readers.delete(record_id)
            print(f"Читатель ID {deleted['id']} успешно удален")
            
            related_loans = self.loans.delete_by_filter({'reader_id': record_id})
            if related_loans:
                print(f"Удалено связанных выдач: {len(related_loans)}")
        else:
            print("Удаление отменено")
    
    def _return_book(self) -> None:
        self._print_header("Возврат книги")
        
        try:
            loan_id = self._read_int("ID выдачи: ")
            
            loan = self.loans.find(loan_id)
            if not loan:
                print(f"Выдача с ID {loan_id} не найдена")
                input("\nНажмите Enter для продолжения...")
                return
            
            if loan['return_date']:
                print(f"Книга уже возвращена {loan['return_date']}")
                input("\nНажмите Enter для продолжения...")
                return
            
            return_date = str(date.today())
            
            self.loans.update(loan_id, {'return_date': return_date})
            self.books.update(loan['book_id'], {'is_available': True})
            
            print(f"Книга успешно возвращена (дата: {return_date})")
            
        except (RecordNotFoundError, ValidationError) as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def _print_main_menu(self) -> None:
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
    
    def _add_record_menu(self) -> None:
        self._print_header("Добавление записи")
        
        print("Выберите таблицу:")
        print("1. Книги")
        print("2. Читатели")
        print("3. Выдачи")
        
        choice = input("Ваш выбор: ").strip()
        
        try:
            if choice == "1":
                self._add_book()
            elif choice == "2":
                self._add_reader()
            elif choice == "3":
                self._add_loan()
            else:
                print("Неверный выбор.")
        except (ValidationError, DuplicateIDError) as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def _view_records_menu(self) -> None:
        self._print_header("Просмотр записей")
        
        print("Выберите таблицу:")
        print("1. Книги")
        print("2. Читатели")
        print("3. Выдачи")
        print("4. Все таблицы")
        
        choice = input("Ваш выбор: ").strip()
        
        try:
            if choice == "1":
                self._view_books()
            elif choice == "2":
                self._view_readers()
            elif choice == "3":
                self._view_loans()
            elif choice == "4":
                info = self.db.get_all_tables_info()
                self._print_header("Информация о таблицах")
                for name, data in info.items():
                    print(f"\n{name.upper()}:")
                    print(f"  Записей: {data['record_count']}")
            else:
                print("Неверный выбор.")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def _update_record_menu(self) -> None:
        self._print_header("Обновление записи")
        
        print("Выберите таблицу:")
        print("1. Книги")
        print("2. Читатели")
        
        choice = input("Ваш выбор: ").strip()
        
        try:
            if choice == "1":
                self._update_book()
            elif choice == "2":
                self._update_reader()
            else:
                print("Неверный выбор.")
        except (RecordNotFoundError, ValidationError, DuplicateIDError) as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def _delete_record_menu(self) -> None:
        self._print_header("Удаление записи")
        
        print("Выберите таблицу:")
        print("1. Книги")
        print("2. Читатели")
        
        choice = input("Ваш выбор: ").strip()
        
        try:
            if choice == "1":
                self._delete_book()
            elif choice == "2":
                self._delete_reader()
            else:
                print("Неверный выбор.")
        except (RecordNotFoundError, ValidationError) as e:
            print(f"Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def run(self) -> None:
        print("\nДобро пожаловать в библиотечную систему!")
        
        while True:
            self._print_main_menu()
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                self._add_record_menu()
            elif choice == "2":
                self._view_records_menu()
            elif choice == "3":
                self._update_record_menu()
            elif choice == "4":
                self._delete_record_menu()
            elif choice == "5":
                self._return_book()
            elif choice == "0":
                print("\nДо свидания!")
                break
            else:
                print("Неизвестная команда. Повторите ввод.")
                input("Нажмите Enter для продолжения...")


def run() -> None:
    ui = LibraryUI()
    ui.run()