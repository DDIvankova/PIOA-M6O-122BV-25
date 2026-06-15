import unittest
from unittest.mock import patch
from io import StringIO
import sys
import os
from itertools import chain, repeat

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db.tui import LibraryUI
from src.db.backend.errors import (
    RecordNotFoundError,
    DuplicateIDError,
    InvalidFieldError,
)


class MockDatabase:
    def __init__(self):
        self._id_counter = 1000
        self.tables = {
            "books": [
                {
                    "id": 1,
                    "title": "Мастер и Маргарита",
                    "author": "Булгаков",
                    "year": 1967,
                    "genre": "Роман",
                    "is_available": True,
                },
                {
                    "id": 2,
                    "title": "1984",
                    "author": "Оруэлл",
                    "year": 1949,
                    "genre": "Антиутопия",
                    "is_available": False,
                },
            ],
            "readers": [
                {
                    "id": 1,
                    "first_name": "Иван",
                    "last_name": "Петров",
                    "email": "ivan@test.com",
                    "phone": "+7-123",
                },
            ],
            "loans": [
                {
                    "id": 1,
                    "book_id": 2,
                    "reader_id": 1,
                    "loan_date": "2024-06-10",
                    "return_date": None,
                },
            ],
        }

    def create_table(self, name, schema):
        if name not in self.tables:
            self.tables[name] = []

    def insert_record(self, table_name, record):
        if "id" in record and any(
            r["id"] == record["id"] for r in self.tables[table_name]
        ):
            raise DuplicateIDError(f"ID {record['id']} уже существует")
        new_id = self._id_counter
        self._id_counter += 1
        new_record = {"id": new_id}
        new_record.update(record)
        self.tables[table_name].append(new_record)
        return new_record

    def select_records(self, table_name, filters=None, sort_by=None, reverse=False):
        data = self.tables.get(table_name, [])
        if filters:
            filtered_data = []
            for record in data:
                match = True
                for key, value in filters.items():
                    if key == "is_available" and isinstance(value, str):
                        record_value = str(record.get(key)).lower()
                        if value.lower() not in record_value:
                            match = False
                            break
                    elif record.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_data.append(record)
            data = filtered_data
        if sort_by:
            if not data:
                return data
            if sort_by not in data[0]:
                raise InvalidFieldError(f"Поле '{sort_by}' не существует")
            data = sorted(data, key=lambda x: x.get(sort_by), reverse=reverse)
        return data

    def update_record(self, table_name, record_id, updates):
        for record in self.tables[table_name]:
            if record["id"] == record_id:
                record.update(updates)
                return record
        raise RecordNotFoundError(f"Запись с ID {record_id} не найдена")

    def delete_record(self, table_name, record_id):
        for i, record in enumerate(self.tables[table_name]):
            if record["id"] == record_id:
                return self.tables[table_name].pop(i)
        raise RecordNotFoundError(f"Запись с ID {record_id} не найдена")

    def get_table_names(self):
        return list(self.tables.keys())


class TestLibraryUIFull(unittest.TestCase):
    @patch("src.db.tui.LibraryUI._select_database_type")
    def setUp(self, mock_select_db):
        mock_select_db.return_value = MockDatabase()
        self.ui = LibraryUI()

    def test_print_header(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.ui._print_header("Тест")
            output = mock_stdout.getvalue()
            self.assertIn("Тест", output)

    @patch("builtins.input", side_effect=["abc", "42"])
    def test_read_int_retry(self, mock_input):
        result = self.ui._read_int("Число: ")
        self.assertEqual(result, 42)

    @patch("builtins.input", side_effect=["да", "нет", "maybe", "yes"])
    def test_read_bool(self, mock_input):
        self.assertTrue(self.ui._read_bool("Вопрос: "))
        self.assertFalse(self.ui._read_bool("Вопрос: "))
        self.assertTrue(self.ui._read_bool("Вопрос: "))

    @patch(
        "builtins.input",
        side_effect=["Test Book", "Test Author", "2025", "Sci-Fi", "да"],
    )
    def test_add_book_success(self, mock_input):
        initial_count = len(self.ui.db.tables["books"])
        with patch("sys.stdout", new_callable=StringIO):
            self.ui._add_book()
        self.assertEqual(len(self.ui.db.tables["books"]), initial_count + 1)

    @patch(
        "builtins.input",
        side_effect=["Test Reader", "Testov", "test@mail.ru", "+7-999"],
    )
    def test_add_reader_success(self, mock_input):
        initial_count = len(self.ui.db.tables["readers"])
        with patch("sys.stdout", new_callable=StringIO):
            self.ui._add_reader()
        self.assertEqual(len(self.ui.db.tables["readers"]), initial_count + 1)

    @patch("builtins.input", side_effect=["Мастер и Маргарита", "", "", "", "", "", ""])
    def test_view_books_filter_by_id(self, mock_input):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.ui._view_books()
        self.assertIn("Мастер и Маргарита", mock_stdout.getvalue())

    @patch("builtins.input", side_effect=["", "", "", "", "недоступна", "", ""])
    def test_view_books_filter_by_availability(self, mock_input):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.ui._view_books()
        output = mock_stdout.getvalue()
        self.assertIn("1984", output)
        self.assertNotIn("Мастер и Маргарита", output)

    @patch(
        "builtins.input", side_effect=["1", "Новое название", "", "", ""] + [""] * 20
    )
    def test_update_book_success(self, mock_input):
        books = self.ui.db.select_records("books")
        book = next((b for b in books if b["id"] == 1), None)
        self.assertIsNotNone(book)
        original_title = book["title"]
        with patch("sys.stdout", new_callable=StringIO):
            self.ui._update_book()
        updated_books = self.ui.db.select_records("books")
        updated_book = next((b for b in updated_books if b["id"] == 1), None)
        self.assertNotEqual(original_title, updated_book["title"])
        self.assertEqual(updated_book["title"], "Новое название")

    @patch("builtins.input", side_effect=["999"])
    def test_update_book_not_found(self, mock_input):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.ui._update_book()
            self.assertIn("Книга с ID 999 не найдена", mock_stdout.getvalue())

    @patch("builtins.input", side_effect=["1", "да"])
    def test_delete_book_success(self, mock_input):
        initial_books_count = len(self.ui.db.tables["books"])
        with patch("sys.stdout", new_callable=StringIO):
            self.ui._delete_book()
        self.assertEqual(len(self.ui.db.tables["books"]), initial_books_count - 1)

    @patch("builtins.input", side_effect=["1", "нет"])
    def test_delete_book_cancelled(self, mock_input):
        initial_books_count = len(self.ui.db.tables["books"])
        with patch("sys.stdout", new_callable=StringIO):
            self.ui._delete_book()
        self.assertEqual(len(self.ui.db.tables["books"]), initial_books_count)

    @patch("builtins.input", side_effect=[""] * 25)
    def test_view_books_no_filters(self, mock_input):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.ui._view_books()
            output = mock_stdout.getvalue()
            self.assertIn("Мастер и Маргарита", output)
            self.assertIn("1984", output)

    @patch("builtins.input", side_effect=["", "", "", "", "", "title", "уб"])
    def test_view_books_with_sorting(self, mock_input):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.ui._view_books()
            self.assertIsNotNone(mock_stdout.getvalue())

    @patch("builtins.input")
    def test_update_book_no_changes(self, mock_input):
        mock_input.side_effect = chain(["1"], repeat(""))
        with patch.object(self.ui.db, "update_record") as mock_update:
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                self.ui._update_book()
                mock_update.assert_not_called()
                self.assertIn("Нет изменений", mock_stdout.getvalue())

    @patch("builtins.input", return_value="123")
    def test_read_optional_int_valid(self, mock_input):
        self.assertEqual(self.ui._read_optional_int(""), 123)

    @patch("builtins.input", return_value="")
    def test_read_optional_int_empty(self, mock_input):
        self.assertIsNone(self.ui._read_optional_int(""))

    @patch("builtins.input", return_value="abc")
    def test_read_optional_int_invalid(self, mock_input):
        with patch("sys.stdout", new_callable=StringIO):
            self.assertIsNone(self.ui._read_optional_int(""))

    @patch("builtins.input", return_value="test")
    def test_read_optional_str(self, mock_input):
        self.assertEqual(self.ui._read_optional_str(""), "test")

    @patch("builtins.input", return_value="")
    def test_read_optional_str_empty(self, mock_input):
        self.assertIsNone(self.ui._read_optional_str(""))

    @patch("builtins.input", side_effect=["title", "уб"])
    def test_read_sort_options_desc(self, mock_input):
        field, reverse = self.ui._read_sort_options()
        self.assertEqual(field, "title")
        self.assertTrue(reverse)

    @patch("builtins.input", side_effect=[""])
    def test_read_sort_options_none(self, mock_input):
        field, reverse = self.ui._read_sort_options()
        self.assertIsNone(field)
        self.assertFalse(reverse)

    @patch("builtins.input", side_effect=["Иван", "", "", "", ""])
    def test_view_readers(self, mock_input):
        with patch("sys.stdout", new_callable=StringIO) as out:
            self.ui._view_readers()
            self.assertIn("Иван", out.getvalue())

    @patch("builtins.input", side_effect=["", ""])
    def test_view_loans(self, mock_input):
        with patch("sys.stdout", new_callable=StringIO) as out:
            self.ui._view_loans()
            self.assertIn("Выдачи книг", out.getvalue())

    @patch(
        "builtins.input",
        side_effect=["1", "Петр", "Сидоров", "new@test.com", "+799999999"],
    )
    def test_update_reader(self, mock_input):
        self.ui._update_reader()
        reader = self.ui.db.select_records("readers", {"id": 1})[0]
        self.assertEqual(reader["first_name"], "Петр")

    @patch("builtins.input", return_value="999")
    def test_update_reader_not_found(self, mock_input):
        with patch("sys.stdout", new_callable=StringIO) as out:
            self.ui._update_reader()
            self.assertIn("не найден", out.getvalue())

    @patch("builtins.input", side_effect=["1", "да"])
    def test_delete_reader_success(self, mock_input):
        count = len(self.ui.db.tables["readers"])
        with patch("sys.stdout", new_callable=StringIO):
            self.ui._delete_reader()
        self.assertEqual(len(self.ui.db.tables["readers"]), count - 1)

    @patch("builtins.input", side_effect=["1", "нет"])
    def test_delete_reader_cancel(self, mock_input):
        count = len(self.ui.db.tables["readers"])
        with patch("sys.stdout", new_callable=StringIO):
            self.ui._delete_reader()
        self.assertEqual(len(self.ui.db.tables["readers"]), count)

    @patch("builtins.input", side_effect=["1", "1", ""])
    def test_add_loan_success(self, mock_input):
        self.ui.db.tables["books"][0]["is_available"] = True
        initial = len(self.ui.db.tables["loans"])
        with patch("sys.stdout", new_callable=StringIO):
            self.ui._add_loan()
        self.assertEqual(len(self.ui.db.tables["loans"]), initial + 1)

    @patch("builtins.input", side_effect=["999", "1", ""])
    def test_add_loan_book_not_found(self, mock_input):
        with patch("sys.stdout", new_callable=StringIO) as out:
            self.ui._add_loan()
            self.assertIn("не найдена", out.getvalue())

    @patch("builtins.input", side_effect=["2", "1", ""])
    def test_add_loan_book_unavailable(self, mock_input):
        with patch("sys.stdout", new_callable=StringIO) as out:
            self.ui._add_loan()
            self.assertIn("уже выдана", out.getvalue())

    @patch("builtins.input", side_effect=["1", "999", ""])
    def test_add_loan_reader_not_found(self, mock_input):
        with patch("sys.stdout", new_callable=StringIO) as out:
            self.ui._add_loan()
            self.assertIn("не найден", out.getvalue())

    @patch("builtins.input", side_effect=["1", ""])
    def test_return_book_already_returned(self, mock_input):
        self.ui.db.tables["loans"][0]["return_date"] = "2025-01-01"
        with patch("sys.stdout", new_callable=StringIO) as out:
            self.ui._return_book()
            self.assertIn("уже возвращена", out.getvalue())

    @patch("builtins.input", side_effect=["1", ""])
    def test_add_record_menu(self, mock_input):
        with patch.object(self.ui, "_add_book") as mock_method:
            self.ui._add_record_menu()
            mock_method.assert_called_once()

    @patch("builtins.input", side_effect=["2", ""])
    def test_view_record_menu(self, mock_input):
        with patch.object(self.ui, "_view_readers") as mock_method:
            self.ui._view_records_menu()
            mock_method.assert_called_once()

    @patch("builtins.input", side_effect=["2", ""])
    def test_update_record_menu(self, mock_input):
        with patch.object(self.ui, "_update_reader") as mock_method:
            self.ui._update_record_menu()
            mock_method.assert_called_once()

    @patch("builtins.input", side_effect=["2", ""])
    def test_delete_record_menu(self, mock_input):
        with patch.object(self.ui, "_delete_reader") as mock_method:
            self.ui._delete_record_menu()
            mock_method.assert_called_once()

    @patch("builtins.input", side_effect=["0"])
    def test_run_exit(self, mock_input):
        with patch("sys.stdout", new_callable=StringIO):
            self.ui.run()

    @patch("builtins.input", side_effect=["999", "", "0"])
    def test_run_invalid_command(self, mock_input):
        with patch("sys.stdout", new_callable=StringIO) as out:
            self.ui.run()
            self.assertIn("Неизвестная команда", out.getvalue())


if __name__ == "__main__":
    unittest.main()
