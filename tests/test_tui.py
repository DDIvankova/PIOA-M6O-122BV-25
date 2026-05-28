import unittest
from unittest.mock import patch
from io import StringIO
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db.tui import LibraryUI


class TestLibraryUI(unittest.TestCase):
    
    def setUp(self):
        self.ui = LibraryUI()
    
    def test_ui_initialization(self):
        self.assertIsNotNone(self.ui.db)
        self.assertIsNotNone(self.ui.books)
        self.assertIsNotNone(self.ui.readers)
        self.assertIsNotNone(self.ui.loans)
        
        books = self.ui.books.get_all()
        self.assertGreater(len(books), 0)
    
    def test_print_header(self):
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._print_header("Тестовый заголовок")
            output = mock.getvalue()
            self.assertIn("Тестовый заголовок", output)
            self.assertIn("=", output)
    
    def test_print_separator(self):
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._print_separator()
            output = mock.getvalue()
            self.assertIn("-" * 50, output)
    
    def test_print_record(self):
        record = {'id': 1, 'name': 'Test', 'age': 25, 'is_available': True}
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._print_record(record)
            output = mock.getvalue()
            self.assertIn("#1", output)
            self.assertIn("name: Test", output)
    
    def test_print_records_empty(self):
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._print_records([], "Пусто")
            output = mock.getvalue()
            self.assertIn("не найдены", output)
    
    def test_print_records_with_data(self):
        records = [{'id': 1, 'name': 'Test'}]
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._print_records(records, "Записи")
            output = mock.getvalue()
            self.assertIn("Test", output)
    
    def test_read_int_valid(self):
        with patch('builtins.input', return_value='123'):
            result = self.ui._read_int("Введите число: ")
            self.assertEqual(result, 123)
    
    def test_read_int_negative(self):
        with patch('builtins.input', return_value='-50'):
            result = self.ui._read_int("Введите число: ")
            self.assertEqual(result, -50)
    
    def test_read_int_zero(self):
        with patch('builtins.input', return_value='0'):
            result = self.ui._read_int("Введите число: ")
            self.assertEqual(result, 0)
    
    def test_read_int_invalid_then_valid(self):
        with patch('builtins.input', side_effect=['abc', '456']):
            with patch('sys.stdout', new_callable=StringIO):
                result = self.ui._read_int("Введите число: ")
                self.assertEqual(result, 456)
    
    def test_read_optional_int_valid(self):
        with patch('builtins.input', return_value='123'):
            result = self.ui._read_optional_int("Введите число: ")
            self.assertEqual(result, 123)
    
    def test_read_optional_int_empty(self):
        with patch('builtins.input', return_value=''):
            result = self.ui._read_optional_int("Введите число: ")
            self.assertIsNone(result)
    
    def test_read_optional_int_invalid(self):
        with patch('builtins.input', return_value='abc'):
            with patch('sys.stdout', new_callable=StringIO):
                result = self.ui._read_optional_int("Введите число: ")
                self.assertIsNone(result)
    
    def test_read_bool_true(self):
        for true_input in ['да', 'yes', 'true', '1', '+']:
            with patch('builtins.input', return_value=true_input):
                result = self.ui._read_bool("Введите да/нет: ")
                self.assertTrue(result)
    
    def test_read_bool_false(self):
        for false_input in ['нет', 'no', 'false', '0', '-']:
            with patch('builtins.input', return_value=false_input):
                result = self.ui._read_bool("Введите да/нет: ")
                self.assertFalse(result)
    
    def test_read_bool_invalid_retry(self):
        with patch('builtins.input', side_effect=['invalid', 'да']):
            with patch('sys.stdout', new_callable=StringIO):
                result = self.ui._read_bool("Введите да/нет: ")
                self.assertTrue(result)
    
    def test_read_optional_str_with_value(self):
        with patch('builtins.input', return_value='hello'):
            result = self.ui._read_optional_str("Введите строку: ")
            self.assertEqual(result, 'hello')
    
    def test_read_optional_str_empty(self):
        with patch('builtins.input', return_value=''):
            result = self.ui._read_optional_str("Введите строку: ")
            self.assertIsNone(result)
    
    def test_read_optional_str_with_spaces(self):
        with patch('builtins.input', return_value='  hello world  '):
            result = self.ui._read_optional_str("Введите строку: ")
            self.assertEqual(result, 'hello world')
    
    def test_read_sort_options_no_sort(self):
        with patch('builtins.input', side_effect=['', '']):
            sort_by, reverse = self.ui._read_sort_options()
            self.assertIsNone(sort_by)
            self.assertFalse(reverse)
    
    def test_read_sort_options_ascending(self):
        with patch('builtins.input', side_effect=['name', 'возр']):
            sort_by, reverse = self.ui._read_sort_options()
            self.assertEqual(sort_by, 'name')
            self.assertFalse(reverse)
    
    def test_read_sort_options_descending(self):
        with patch('builtins.input', side_effect=['age', 'уб']):
            sort_by, reverse = self.ui._read_sort_options()
            self.assertEqual(sort_by, 'age')
            self.assertTrue(reverse)
        
    @patch('builtins.input')
    def test_add_book(self, mock_input):
        mock_input.side_effect = ['1', 'Тест книга', 'Тест автор', '2024', 'Тест жанр', 'да', '']
        
        initial_count = self.ui.books.record_count
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._add_record_menu()
        
        self.assertEqual(self.ui.books.record_count, initial_count + 1)
    
    @patch('builtins.input')
    def test_add_book_invalid_year(self, mock_input):
        mock_input.side_effect = ['1', 'Книга', 'Автор', 'не число', '2024', 'Жанр', 'да', '']
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._add_record_menu()
            output = mock.getvalue()
            self.assertIn("целое число", output.lower())
    
    @patch('builtins.input')
    def test_update_book(self, mock_input):
        book = self.ui.books.create({
            'title': 'Книга для обновления',
            'author': 'Старый автор',
            'year': 2020,
            'genre': 'Тест',
            'is_available': True
        })
        
        mock_input.side_effect = ['1', str(book['id']), '', 'Новый автор', '', '', '', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._update_record_menu()
        
        updated_book = self.ui.books.find(book['id'])
        self.assertEqual(updated_book['author'], 'Новый автор')
    
    @patch('builtins.input')
    def test_update_book_no_changes(self, mock_input):
        book = self.ui.books.create({
            'title': 'Без изменений',
            'author': 'Автор',
            'year': 2024,
            'genre': 'Жанр',
            'is_available': True
        })
        
        mock_input.side_effect = ['1', str(book['id']), '', '', '', '', '', '']
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._update_record_menu()
            output = mock.getvalue()
            self.assertIn("Нет изменений", output)
    
    @patch('builtins.input')
    def test_delete_book(self, mock_input):
        book = self.ui.books.create({
            'title': 'Книга для удаления',
            'author': 'Автор',
            'year': 2024,
            'genre': 'Тест',
            'is_available': True
        })
        
        mock_input.side_effect = ['1', str(book['id']), 'да', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._delete_record_menu()
        
        self.assertIsNone(self.ui.books.find(book['id']))
    
    @patch('builtins.input')
    def test_delete_book_cancel(self, mock_input):
        book = self.ui.books.create({
            'title': 'Книга для отмены',
            'author': 'Автор',
            'year': 2024,
            'genre': 'Тест',
            'is_available': True
        })
        
        mock_input.side_effect = ['1', str(book['id']), 'нет', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._delete_record_menu()
        
        self.assertIsNotNone(self.ui.books.find(book['id']))
    
    @patch('builtins.input')
    def test_add_reader(self, mock_input):
        mock_input.side_effect = ['2', 'Тест Читатель', 'Тестов', 'test@example.com', '+7-999-999-99-99', '']
        
        initial_count = self.ui.readers.record_count
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._add_record_menu()
        
        self.assertEqual(self.ui.readers.record_count, initial_count + 1)
    
    @patch('builtins.input')
    def test_update_reader(self, mock_input):
        reader = self.ui.readers.create({
            'first_name': 'СтароеИмя',
            'last_name': 'СтараяФамилия',
            'email': 'old@example.com',
            'phone': '111'
        })
        
        mock_input.side_effect = ['2', str(reader['id']), 'НовоеИмя', 'НоваяФамилия', 'new@example.com', '222', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._update_record_menu()
        
        updated_reader = self.ui.readers.find(reader['id'])
        self.assertEqual(updated_reader['first_name'], 'НовоеИмя')
        self.assertEqual(updated_reader['email'], 'new@example.com')
    
    @patch('builtins.input')
    def test_delete_reader(self, mock_input):
        reader = self.ui.readers.create({
            'first_name': 'ДляУдаления',
            'last_name': 'Тестов',
            'email': 'delete@example.com',
            'phone': '999'
        })
        
        mock_input.side_effect = ['2', str(reader['id']), 'да', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._delete_record_menu()
        
        self.assertIsNone(self.ui.readers.find(reader['id']))

    @patch('builtins.input')
    def test_add_loan(self, mock_input):
        available_books = self.ui.books.select({'is_available': True})
        if available_books:
            book_id = available_books[0]['id']
            reader_id = self.ui.readers.get_all()[0]['id']
            
            mock_input.side_effect = ['3', str(book_id), str(reader_id), '']
            
            with patch('sys.stdout', new_callable=StringIO):
                initial_count = self.ui.loans.record_count
                self.ui._add_record_menu()
                
                self.assertEqual(self.ui.loans.record_count, initial_count + 1)

    @patch('builtins.input')
    def test_return_book_not_found(self, mock_input):
        mock_input.side_effect = ['99999', '']
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._return_book()
            output = mock.getvalue()
            self.assertIn("не найдена", output)
    
    @patch('builtins.input')
    def test_return_book_already_returned(self, mock_input):
        book = self.ui.books.create({
            'title': 'Test Book',
            'author': 'Author',
            'year': 2024,
            'genre': 'Test',
            'is_available': True
        })
        
        reader = self.ui.readers.create({
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '123'
        })
        
        loan = self.ui.loans.create({
            'book_id': book['id'],
            'reader_id': reader['id'],
            'loan_date': '2024-01-01',
            'return_date': '2024-01-15'
        })
        
        mock_input.side_effect = [str(loan['id']), '']
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._return_book()
            output = mock.getvalue()
            self.assertIn("уже возвращена", output)
    
    def test_read_optional_int_with_spaces(self):
        with patch('builtins.input', return_value='  123  '):
            result = self.ui._read_optional_int("Число: ")
            self.assertEqual(result, 123)

    @patch('builtins.input')
    def test_add_book_with_spaces_in_fields(self, mock_input):
        mock_input.side_effect = ['1', '  Книга с пробелами  ', '  Автор  ', '2024', '  Жанр  ', 'да', '', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._add_record_menu()

    @patch('builtins.input')
    def test_view_readers_with_last_name_filter(self, mock_input):
        mock_input.side_effect = ['2', '2', '', 'Петров', '', '', '', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._view_records_menu()
    
    @patch('builtins.input')
    def test_update_book_year_only(self, mock_input):
        book = self.ui.books.create({
            'title': 'Книга для обновления года',
            'author': 'Автор',
            'year': 2000,
            'genre': 'Жанр',
            'is_available': True
        })
        
        mock_input.side_effect = ['1', str(book['id']), '', '', '2024', '', '', '', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._update_record_menu()
        
        updated = self.ui.books.find(book['id'])
        if updated:
            self.assertEqual(updated['year'], 2024)
    
    @patch('builtins.input')
    def test_update_book_title_only(self, mock_input):
        book = self.ui.books.create({
            'title': 'Старое название',
            'author': 'Автор',
            'year': 2024,
            'genre': 'Жанр',
            'is_available': True
        })
        
        mock_input.side_effect = ['1', str(book['id']), 'Новое название', '', '', '', '', '', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._update_record_menu()
        
        updated = self.ui.books.find(book['id'])
        if updated:
            self.assertEqual(updated['title'], 'Новое название')
    
    @patch('builtins.input')
    def test_update_reader_email_only(self, mock_input):
        reader = self.ui.readers.create({
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'old@example.com',
            'phone': '123'
        })
        
        mock_input.side_effect = ['2', str(reader['id']), '', '', 'new@example.com', '', '', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._update_record_menu()
        
        updated = self.ui.readers.find(reader['id'])
        if updated:
            self.assertEqual(updated['email'], 'new@example.com')
    
    @patch('builtins.input')
    def test_delete_nonexistent_book(self, mock_input):
        mock_input.side_effect = ['1', '99999', '', '']
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._delete_record_menu()
            output = mock.getvalue()
            self.assertIn("не найдена", output)
    
    @patch('builtins.input')
    def test_delete_nonexistent_reader(self, mock_input):
        mock_input.side_effect = ['2', '99999', '', '']
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._delete_record_menu()
            output = mock.getvalue()
            self.assertIn("не найден", output)
    
    @patch('builtins.input')
    def test_return_book_success(self, mock_input):
        book = self.ui.books.create({
            'title': 'Возвращаемая книга',
            'author': 'Автор',
            'year': 2024,
            'genre': 'Жанр',
            'is_available': False
        })
        
        reader = self.ui.readers.create({
            'first_name': 'Читатель',
            'last_name': 'ДляВозврата',
            'email': 'return@test.com',
            'phone': '123'
        })
        
        loan = self.ui.loans.create({
            'book_id': book['id'],
            'reader_id': reader['id'],
            'loan_date': '2024-01-01',
            'return_date': None
        })
        
        mock_input.side_effect = [str(loan['id']), '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._return_book()
        
        updated_loan = self.ui.loans.find(loan['id'])
        if updated_loan:
            self.assertIsNotNone(updated_loan['return_date'])

    def test_print_record_with_negative_id(self):
        record = {'id': -1, 'name': 'Test', 'age': 25}
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._print_record(record)
            output = mock.getvalue()
            self.assertIn("#-1", output)
    
    def test_print_record_with_unicode(self):
        record = {'id': 1, 'name': 'Тест Юникод 🎉', 'age': 25}
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._print_record(record)
            output = mock.getvalue()
            self.assertIn("Тест Юникод", output)
    
    @patch('builtins.input')
    def test_view_books_with_sort_descending(self, mock_input):
        mock_input.side_effect = ['2', '1', '', '', '', '', '', 'year', 'уб', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._view_records_menu()
    
    @patch('builtins.input')
    def test_view_readers_with_sort_descending(self, mock_input):
        mock_input.side_effect = ['2', '2', '', '', '', 'last_name', 'уб', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._view_records_menu()
    
    @patch('builtins.input')
    def test_add_reader_empty_name(self, mock_input):
        mock_input.side_effect = ['2', '', 'Петров', 'test@mail.com', '123', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            initial_count = self.ui.readers.record_count
            self.ui._add_record_menu()
            self.assertEqual(self.ui.readers.record_count, initial_count + 1)
    
    @patch('builtins.input')
    def test_delete_reader_confirm_no(self, mock_input):
        reader = self.ui.readers.create({
            'first_name': 'Отмена',
            'last_name': 'Удаления',
            'email': 'cancel@test.com',
            'phone': '111'
        })
        
        mock_input.side_effect = ['2', str(reader['id']), 'нет', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._delete_record_menu()
        
        self.assertIsNotNone(self.ui.readers.find(reader['id']))
    
    @patch('builtins.input')
    def test_view_books_with_not_available_filter(self, mock_input):
        mock_input.side_effect = ['2', '1', '', '', '', '', 'недоступна', '', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._view_records_menu()

    def test_print_record_with_false_bool(self):
        record = {'id': 1, 'name': 'Test', 'is_available': False}
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._print_record(record)
            output = mock.getvalue()
            self.assertIn("Нет", output)
    
    @patch('builtins.input')
    def test_add_book_max_values(self, mock_input):
        mock_input.side_effect = ['1', 'X'*100, 'Y'*100, '9999', 'Z'*50, 'да', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            initial_count = self.ui.books.record_count
            self.ui._add_record_menu()
            self.assertEqual(self.ui.books.record_count, initial_count + 1)
    
    @patch('builtins.input')
    def test_update_book_all_fields(self, mock_input):
        book = self.ui.books.create({
            'title': 'Old Title',
            'author': 'Old Author',
            'year': 2000,
            'genre': 'Old Genre',
            'is_available': True
        })
        
        mock_input.side_effect = [
            '1', str(book['id']),
            'New Title',
            'New Author',
            '2024',
            'New Genre',
            'нет',
            ''
        ]
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._update_record_menu()
        
        updated = self.ui.books.find(book['id'])
        if updated:
            self.assertEqual(updated['title'], 'New Title')
            self.assertEqual(updated['author'], 'New Author')
            self.assertEqual(updated['year'], 2024)
            self.assertEqual(updated['genre'], 'New Genre')
            self.assertFalse(updated['is_available'])
    
    @patch('builtins.input')
    def test_update_reader_all_fields(self, mock_input):
        reader = self.ui.readers.create({
            'first_name': 'OldFirst',
            'last_name': 'OldLast',
            'email': 'old@test.com',
            'phone': '111'
        })
        
        mock_input.side_effect = [
            '2', str(reader['id']),
            'NewFirst',
            'NewLast',
            'new@test.com',
            '999',
            ''
        ]
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._update_record_menu()
        
        updated = self.ui.readers.find(reader['id'])
        if updated:
            self.assertEqual(updated['first_name'], 'NewFirst')
            self.assertEqual(updated['last_name'], 'NewLast')
            self.assertEqual(updated['email'], 'new@test.com')
            self.assertEqual(updated['phone'], '999')
    
    @patch('builtins.input')
    def test_add_loan_book_not_available(self, mock_input):
        unavailable_books = self.ui.books.select({'is_available': False})
        if unavailable_books:
            book_id = unavailable_books[0]['id']
            reader_id = self.ui.readers.get_all()[0]['id']
            
            mock_input.side_effect = ['3', str(book_id), str(reader_id), '']
            
            with patch('sys.stdout', new_callable=StringIO):
                self.ui._add_record_menu()
       
    def test_print_record_with_zero_id(self):
        record = {'id': 0, 'name': 'Zero ID', 'age': 25}
        
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._print_record(record)
            output = mock.getvalue()
            self.assertIn("#0", output)
    
    @patch('builtins.input')
    def test_add_reader_minimal_data(self, mock_input):
        mock_input.side_effect = ['2', 'Тест', '', '', '', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._add_record_menu()
    
    @patch('builtins.input')
    def test_return_book_successful(self, mock_input):
        book = self.ui.books.create({
            'title': 'Return Book',
            'author': 'Author',
            'year': 2024,
            'genre': 'Genre',
            'is_available': False
        })
        reader = self.ui.readers.create({
            'first_name': 'Returner',
            'last_name': 'Test',
            'email': 'return@test.com',
            'phone': '111'
        })
        loan = self.ui.loans.create({
            'book_id': book['id'],
            'reader_id': reader['id'],
            'loan_date': '2024-01-01',
            'return_date': None
        })
        
        mock_input.side_effect = [str(loan['id']), '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._return_book()
        
        updated_book = self.ui.books.find(book['id'])
        if updated_book:
            self.assertTrue(updated_book['is_available'])
    
    @patch('builtins.input')
    def test_delete_reader_final(self, mock_input):
        reader = self.ui.readers.create({
            'first_name': 'ToDelete',
            'last_name': 'Now',
            'email': 'delete@test.com',
            'phone': '999'
        })
        
        mock_input.side_effect = ['2', str(reader['id']), 'да', '']
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._delete_record_menu()
        
        self.assertIsNone(self.ui.readers.find(reader['id']))
    
    @patch('builtins.input')
    def test_update_reader_all_fields_full(self, mock_input):
        reader = self.ui.readers.create({
            'first_name': 'OldF',
            'last_name': 'OldL',
            'email': 'old@test.com',
            'phone': '111'
        })
        
        mock_input.side_effect = [
            '2', str(reader['id']),
            'NewF', 'NewL', 'new@test.com', '222', ''
        ]
        
        with patch('sys.stdout', new_callable=StringIO):
            self.ui._update_record_menu()
        
        updated = self.ui.readers.find(reader['id'])
        if updated:
            self.assertEqual(updated['first_name'], 'NewF')
            self.assertEqual(updated['email'], 'new@test.com')
    
    @patch('builtins.input')
    def test_add_loan_specific_filters(self, mock_input):
        available_books = self.ui.books.select({'is_available': True})
        if available_books:
            mock_input.side_effect = ['3', str(available_books[0]['id']), '1', '']
            
            with patch('sys.stdout', new_callable=StringIO):
                self.ui._add_record_menu()

    @patch('builtins.input')
    def test_main_run_exit(self, mock_input):
        mock_input.side_effect = ['0']

        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui.run()
            output = mock.getvalue()

            self.assertIn("До свидания", output)

    @patch('builtins.input')
    def test_main_run_invalid_choice(self, mock_input):
        mock_input.side_effect = ['999', '', '0']

        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui.run()
            output = mock.getvalue()

            self.assertIn("Неизвестная команда", output)

    @patch('builtins.input')
    def test_add_record_menu_invalid_choice(self, mock_input):
        mock_input.side_effect = ['999', '']

        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._add_record_menu()
            output = mock.getvalue()

            self.assertIn("Неверный выбор", output)

    @patch('builtins.input')
    def test_view_records_menu_invalid_choice(self, mock_input):
        mock_input.side_effect = ['999', '']

        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._view_records_menu()
            output = mock.getvalue()

            self.assertIn("Неверный выбор", output)

    @patch('builtins.input')
    def test_update_record_menu_invalid_choice(self, mock_input):
        mock_input.side_effect = ['999', '']

        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._update_record_menu()
            output = mock.getvalue()

            self.assertIn("Неверный выбор", output)

    @patch('builtins.input')
    def test_delete_record_menu_invalid_choice(self, mock_input):
        mock_input.side_effect = ['999', '']

        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._delete_record_menu()
            output = mock.getvalue()
            self.assertIn("Неверный выбор", output)

    @patch('builtins.input')
    def test_view_books_invalid_sort_field(self, mock_input):
        mock_input.side_effect = [
            '', '', '', '', '',
            'unknown_field',
            'возр'
        ]

        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._view_books()
            output = mock.getvalue()

            self.assertIn("Ошибка", output)

    @patch('builtins.input')
    def test_view_readers_invalid_sort_field(self, mock_input):
        mock_input.side_effect = [
            '', '', '',
            'bad_field',
            'уб'
        ]

        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._view_readers()
            output = mock.getvalue()

            self.assertIn("Ошибка", output)

    @patch('builtins.input')
    def test_update_nonexistent_book(self, mock_input):
        mock_input.side_effect = ['999999', '']

        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._update_book()
            output = mock.getvalue()

            self.assertIn("не найдена", output)

    @patch('builtins.input')
    def test_update_nonexistent_reader(self, mock_input):
        mock_input.side_effect = ['999999', '']

        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._update_reader()
            output = mock.getvalue()

            self.assertIn("не найден", output)

    def test_global_run_function(self):
        from src.db.tui import run

        with patch('src.db.tui.LibraryUI.run') as mock_run:
            run()
            mock_run.assert_called_once()

    def test_print_records_multiple(self):
        records = [
            {'id': 1, 'name': 'One'},
            {'id': 2, 'name': 'Two'}
        ]
        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._print_records(records, "Тест")
            output = mock.getvalue()
            self.assertIn("One", output)
            self.assertIn("Two", output)

    def test_print_record_bool_true_false(self):
        record = {
            'id': 1,
            'active': True,
            'blocked': False
        }

        with patch('sys.stdout', new_callable=StringIO) as mock:
            self.ui._print_record(record)

            output = mock.getvalue()

            self.assertIn("Да", output)
            self.assertIn("Нет", output)


if __name__ == '__main__':
    unittest.main()