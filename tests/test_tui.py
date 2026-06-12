import unittest
from unittest.mock import patch
from io import StringIO
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db.tui import LibraryUI


class TestTUISimple(unittest.TestCase):
    def setUp(self):
        with patch('builtins.input', return_value='1'):
            self.ui = LibraryUI()

    def test_print_header(self):
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._print_header("Тест")
            self.assertIn("Тест", mock.getvalue())

    def test_print_separator(self):
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._print_separator()
            self.assertIn("-" * 50, mock.getvalue())

    def test_print_record(self):
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._print_record({'id': 1, 'name': 'Test'})
            self.assertIn("#1", mock.getvalue())

    def test_read_int(self):
        with patch('builtins.input', return_value='42'):
            result = self.ui._read_int("Число: ")
            self.assertEqual(result, 42)

    def test_read_optional_int(self):
        with patch('builtins.input', return_value='42'):
            result = self.ui._read_optional_int("Число: ")
            self.assertEqual(result, 42)

    def test_read_optional_int_empty(self):
        with patch('builtins.input', return_value=''):
            result = self.ui._read_optional_int("Число: ")
            self.assertIsNone(result)

    def test_read_bool_true(self):
        with patch('builtins.input', return_value='да'):
            result = self.ui._read_bool("Да/нет: ")
            self.assertTrue(result)

    def test_read_bool_false(self):
        with patch('builtins.input', return_value='нет'):
            result = self.ui._read_bool("Да/нет: ")
            self.assertFalse(result)

    def test_read_optional_str(self):
        with patch('builtins.input', return_value='hello'):
            result = self.ui._read_optional_str("Строка: ")
            self.assertEqual(result, 'hello')

    def test_read_optional_str_empty(self):
        with patch('builtins.input', return_value=''):
            result = self.ui._read_optional_str("Строка: ")
            self.assertIsNone(result)

    @patch('builtins.input')
    def test_add_book(self, mock_input):
        mock_input.side_effect = ['1', 'Тест книга', 'Тест автор', '2024', 'Тест жанр', 'да', '']
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._add_record_menu()

    @patch('builtins.input')
    def test_add_reader(self, mock_input):
        mock_input.side_effect = ['2', 'Иван', 'Петров', 'ivan@test.com', '+7-123-456-78-90', '']
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._add_record_menu()

    @patch('builtins.input')
    def test_view_books(self, mock_input):
        mock_input.side_effect = ['2', '1', '', '', '', '', '', '', '']
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._view_records_menu()

    @patch('builtins.input')
    def test_view_all_tables(self, mock_input):
        mock_input.side_effect = ['2', '4', '', '', '', '', '', '', '', '']
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._view_records_menu()

if __name__ == '__main__':
    unittest.main()