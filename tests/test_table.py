import unittest
from src.db.backend.table import Table
from src.db.backend.errors import (
    ValidationError, DuplicateIDError, RecordNotFoundError,
    InvalidFieldError, InvalidSortError  # Добавьте эту строку, если её нет
)
class TestTable(unittest.TestCase):
    """Тесты для класса Table."""
    
    def setUp(self):
        self.schema = {
            'id': int,
            'name': str,
            'age': int,
            'email': str
        }
        self.table = Table('test_table', self.schema)
    
    def test_table_creation(self):
        """Тест создания таблицы."""
        self.assertEqual(self.table.name, 'test_table')
        self.assertEqual(self.table.record_count, 0)
    
    def test_create_record(self):
        """Тест создания записи."""
        record = self.table.create({'name': 'John Doe', 'age': 25, 'email': 'john@example.com'})
        
        self.assertEqual(record['id'], 1)
        self.assertEqual(record['name'], 'John Doe')
        self.assertEqual(self.table.record_count, 1)
    
    def test_create_record_with_custom_id(self):
        """Тест создания записи с пользовательским ID."""
        # Создаем запись с ID=100
        record = self.table.create({'id': 100, 'name': 'Jane Doe', 'age': 30, 'email': 'jane@example.com'})
        self.assertEqual(record['id'], 100)
        self.assertEqual(self.table.record_count, 1)
        
        # Следующая запись БЕЗ указания ID должна получить ID = 101
        record2 = self.table.create({'name': 'Bob', 'age': 20, 'email': 'bob@example.com'})
        self.assertEqual(record2['id'], 101, f"Ожидалось 101, получено {record2['id']}")
        self.assertEqual(self.table.record_count, 2)
        
        # Еще одна запись должна получить ID = 102
        record3 = self.table.create({'name': 'Alice', 'age': 25, 'email': 'alice@example.com'})
        self.assertEqual(record3['id'], 102)
        self.assertEqual(self.table.record_count, 3)
    
    def test_create_duplicate_id(self):
        """Тест создания записи с дублирующимся ID."""
        self.table.create({'id': 1, 'name': 'John', 'age': 25, 'email': 'john@example.com'})
        
        with self.assertRaises(DuplicateIDError):
            self.table.create({'id': 1, 'name': 'Jane', 'age': 30, 'email': 'jane@example.com'})
    
    def test_find_record(self):
        """Тест поиска записи."""
        record = self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        
        found = self.table.find(record['id'])
        self.assertIsNotNone(found)
        self.assertEqual(found['name'], 'John')
        
        not_found = self.table.find(999)
        self.assertIsNone(not_found)
    
    def test_select_all(self):
        """Тест выборки всех записей."""
        for i in range(3):
            self.table.create({'name': f'User{i}', 'age': 20 + i, 'email': f'user{i}@example.com'})
        
        all_records = self.table.select()
        self.assertEqual(len(all_records), 3)
    
    def test_select_with_filters(self):
        """Тест выборки с фильтрацией."""
        self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        self.table.create({'name': 'Jane', 'age': 30, 'email': 'jane@example.com'})
        self.table.create({'name': 'John', 'age': 35, 'email': 'john2@example.com'})
        
        filtered = self.table.select({'name': 'John'})
        self.assertEqual(len(filtered), 2)
        
        filtered = self.table.select({'age': 30})
        self.assertEqual(len(filtered), 1)
    
    def test_select_with_sorting(self):
        """Тест выборки с сортировкой."""
        self.table.create({'name': 'Charlie', 'age': 30, 'email': 'charlie@example.com'})
        self.table.create({'name': 'Alice', 'age': 25, 'email': 'alice@example.com'})
        self.table.create({'name': 'Bob', 'age': 35, 'email': 'bob@example.com'})
        
        sorted_records = self.table.select(sort_by='name')
        names = [r['name'] for r in sorted_records]
        self.assertEqual(names, ['Alice', 'Bob', 'Charlie'])
        
        sorted_records = self.table.select(sort_by='name', reverse=True)
        names = [r['name'] for r in sorted_records]
        self.assertEqual(names, ['Charlie', 'Bob', 'Alice'])
    
    def test_update_record(self):
        """Тест обновления записи."""
        record = self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        
        updated = self.table.update(record['id'], {'name': 'John Updated', 'age': 26})
        
        self.assertEqual(updated['name'], 'John Updated')
        self.assertEqual(updated['age'], 26)
    
    def test_update_nonexistent_record(self):
        """Тест обновления несуществующей записи."""
        with self.assertRaises(RecordNotFoundError):
            self.table.update(999, {'name': 'New Name'})
    
    def test_delete_record(self):
        """Тест удаления записи."""
        record = self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        self.assertEqual(self.table.record_count, 1)
        
        deleted = self.table.delete(record['id'])
        self.assertEqual(deleted['id'], record['id'])
        self.assertEqual(self.table.record_count, 0)
        
        # Проверка, что запись действительно удалена
        found = self.table.find(record['id'])
        self.assertIsNone(found)
    
    def test_delete_nonexistent_record(self):
        """Тест удаления несуществующей записи."""
        with self.assertRaises(RecordNotFoundError):
            self.table.delete(999)
    
    def test_clear_table(self):
        """Тест очистки таблицы."""
        for i in range(5):
            self.table.create({'name': f'User{i}', 'age': 20, 'email': f'user{i}@example.com'})
        
        deleted_count = self.table.clear()
        self.assertEqual(deleted_count, 5)
        self.assertEqual(self.table.record_count, 0)
    # Добавьте эти методы в класс TestTable в файле tests/test_table.py

    def test_select_with_limit_and_offset(self):
        """Тест пагинации (limit и offset)"""
        # Создаем 10 записей
        for i in range(10):
            self.table.create({
                'name': f'User{i}', 
                'age': 20 + i, 
                'email': f'user{i}@example.com'
            })
        
        # Тест limit
        limited = self.table.select(limit=5)
        self.assertEqual(len(limited), 5)
        
        # Тест offset
        offset = self.table.select(offset=5)
        self.assertEqual(len(offset), 5)
        
        # Тест limit + offset
        paginated = self.table.select(limit=3, offset=2)
        self.assertEqual(len(paginated), 3)
        
        # Проверка правильности данных
        self.assertEqual(paginated[0]['name'], 'User2')
        self.assertEqual(paginated[1]['name'], 'User3')
        self.assertEqual(paginated[2]['name'], 'User4')


    def test_select_with_filters_and_sorting(self):
        """Тест комбинации фильтров и сортировки"""
        # Создаем тестовые данные
        self.table.create({'name': 'Alice', 'age': 30, 'email': 'alice@example.com'})
        self.table.create({'name': 'Bob', 'age': 25, 'email': 'bob@example.com'})
        self.table.create({'name': 'Alice', 'age': 20, 'email': 'alice2@example.com'})
        self.table.create({'name': 'Charlie', 'age': 35, 'email': 'charlie@example.com'})
        
        # Фильтр по имени + сортировка по возрасту
        result = self.table.select(
            filters={'name': 'Alice'},
            sort_by='age'
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['age'], 20)
        self.assertEqual(result[1]['age'], 30)


    def test_select_invalid_sort_field_raises_error(self):
        """Тест: сортировка по несуществующему полю вызывает ошибку"""
        self.table.create({'name': 'Test', 'age': 25, 'email': 'test@example.com'})
        
        with self.assertRaises(InvalidFieldError):
            self.table.select(sort_by='nonexistent_field')


    def test_update_with_id_change(self):
        """Тест обновления ID записи"""
        record = self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        
        # Меняем ID
        updated = self.table.update(record['id'], {'id': 999})
        
        self.assertEqual(updated['id'], 999)
        
        # Проверяем, что старая запись недоступна по старому ID
        old_found = self.table.find(record['id'])
        self.assertIsNone(old_found)
        
        # Проверяем, что новая доступна по новому ID
        new_found = self.table.find(999)
        self.assertIsNotNone(new_found)


    def test_update_id_to_duplicate_raises_error(self):
        """Тест: обновление ID на уже существующий вызывает ошибку"""
        record1 = self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        record2 = self.table.create({'name': 'Jane', 'age': 30, 'email': 'jane@example.com'})
        
        with self.assertRaises(DuplicateIDError):
            self.table.update(record2['id'], {'id': record1['id']})


    def test_delete_by_filter(self):
        """Тест удаления по фильтру"""
        self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        self.table.create({'name': 'John', 'age': 30, 'email': 'john2@example.com'})
        self.table.create({'name': 'Jane', 'age': 25, 'email': 'jane@example.com'})
        
        deleted = self.table.delete_by_filter({'name': 'John'})
        
        self.assertEqual(len(deleted), 2)
        self.assertEqual(self.table.record_count, 1)
        
        # Проверяем, что Jane осталась
        remaining = self.table.get_all()
        self.assertEqual(remaining[0]['name'], 'Jane')


    def test_delete_by_empty_filter(self):
        """Тест удаления с пустым фильтром (удаляет все)"""
        self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        self.table.create({'name': 'Jane', 'age': 30, 'email': 'jane@example.com'})
        
        deleted = self.table.delete_by_filter({})
        
        self.assertEqual(len(deleted), 2)
        self.assertEqual(self.table.record_count, 0)


    def test_clear_empty_table(self):
        """Тест очистки пустой таблицы"""
        self.assertEqual(self.table.record_count, 0)
        deleted_count = self.table.clear()
        self.assertEqual(deleted_count, 0)

    def test_select_with_limit_zero(self):
        """Покрытие строки 46 - select с limit=0"""
        self.table.create({'name': 'Test', 'age': 25, 'email': 'test@example.com'})
        result = self.table.select(limit=0)
        self.assertEqual(len(result), 1)
    
    def test_select_with_negative_limit(self):
        """Покрытие строки 50 - select с отрицательным limit"""
        self.table.create({'name': 'Test', 'age': 25, 'email': 'test@example.com'})
        result = self.table.select(limit=-5)
        self.assertEqual(len(result), 0)
    
    def test_select_with_only_offset(self):
        """Покрытие строки 58 - select с offset без limit"""
        for i in range(5):
            self.table.create({'name': f'User{i}', 'age': 20 + i, 'email': f'user{i}@example.com'})
        
        result = self.table.select(offset=2)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['name'], 'User2')
    
    def test_select_with_sorting_invalid_field(self):
        """Покрытие строк 124-125 - сортировка по несуществующему полю"""
        self.table.create({'name': 'Test', 'age': 25, 'email': 'test@example.com'})
        
        with self.assertRaises(InvalidFieldError):
            self.table.select(sort_by='field_that_does_not_exist')
if __name__ == '__main__':
    unittest.main()