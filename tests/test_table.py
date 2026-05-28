import unittest
from src.db.backend.table import Table
from src.db.backend.errors import (
    ValidationError, DuplicateIDError, RecordNotFoundError,
    InvalidFieldError, InvalidSortError
)


class TestTable(unittest.TestCase):
    
    def setUp(self):
        self.schema = {
            'id': int,
            'name': str,
            'age': int,
            'email': str
        }
        self.table = Table('test_table', self.schema)
    
    def test_table_creation(self):
        self.assertEqual(self.table.name, 'test_table')
        self.assertEqual(self.table.record_count, 0)
    
    def test_create_record(self):
        record = self.table.create({'name': 'John Doe', 'age': 25, 'email': 'john@example.com'})
        
        self.assertEqual(record['id'], 1)
        self.assertEqual(record['name'], 'John Doe')
        self.assertEqual(self.table.record_count, 1)
    
    def test_create_record_with_custom_id(self):
        record = self.table.create({'id': 100, 'name': 'Jane Doe', 'age': 30, 'email': 'jane@example.com'})
        self.assertEqual(record['id'], 100)
        self.assertEqual(self.table.record_count, 1)
        
        record2 = self.table.create({'name': 'Bob', 'age': 20, 'email': 'bob@example.com'})
        self.assertEqual(record2['id'], 101, f"Ожидалось 101, получено {record2['id']}")
        self.assertEqual(self.table.record_count, 2)
        
        record3 = self.table.create({'name': 'Alice', 'age': 25, 'email': 'alice@example.com'})
        self.assertEqual(record3['id'], 102)
        self.assertEqual(self.table.record_count, 3)
    
    def test_create_duplicate_id(self):
        self.table.create({'id': 1, 'name': 'John', 'age': 25, 'email': 'john@example.com'})
        
        with self.assertRaises(DuplicateIDError):
            self.table.create({'id': 1, 'name': 'Jane', 'age': 30, 'email': 'jane@example.com'})
    
    def test_find_record(self):
        record = self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        
        found = self.table.find(record['id'])
        self.assertIsNotNone(found)
        self.assertEqual(found['name'], 'John')
        
        not_found = self.table.find(999)
        self.assertIsNone(not_found)
    
    def test_select_all(self):
        for i in range(3):
            self.table.create({'name': f'User{i}', 'age': 20 + i, 'email': f'user{i}@example.com'})
        
        all_records = self.table.select()
        self.assertEqual(len(all_records), 3)
    
    def test_select_with_filters(self):
        self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        self.table.create({'name': 'Jane', 'age': 30, 'email': 'jane@example.com'})
        self.table.create({'name': 'John', 'age': 35, 'email': 'john2@example.com'})
        
        filtered = self.table.select({'name': 'John'})
        self.assertEqual(len(filtered), 2)
        
        filtered = self.table.select({'age': 30})
        self.assertEqual(len(filtered), 1)
    
    def test_select_with_sorting(self):
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
        record = self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        
        updated = self.table.update(record['id'], {'name': 'John Updated', 'age': 26})
        
        self.assertEqual(updated['name'], 'John Updated')
        self.assertEqual(updated['age'], 26)
    
    def test_update_nonexistent_record(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.update(999, {'name': 'New Name'})
    
    def test_delete_record(self):
        record = self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        self.assertEqual(self.table.record_count, 1)
        
        deleted = self.table.delete(record['id'])
        self.assertEqual(deleted['id'], record['id'])
        self.assertEqual(self.table.record_count, 0)
        
        found = self.table.find(record['id'])
        self.assertIsNone(found)
    
    def test_delete_nonexistent_record(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.delete(999)
    
    def test_clear_table(self):
        for i in range(5):
            self.table.create({'name': f'User{i}', 'age': 20, 'email': f'user{i}@example.com'})
        
        deleted_count = self.table.clear()
        self.assertEqual(deleted_count, 5)
        self.assertEqual(self.table.record_count, 0)
    
    def test_select_with_limit_and_offset(self):
        for i in range(10):
            self.table.create({
                'name': f'User{i}', 
                'age': 20 + i, 
                'email': f'user{i}@example.com'
            })
        
        limited = self.table.select(limit=5)
        self.assertEqual(len(limited), 5)
        
        offset = self.table.select(offset=5)
        self.assertEqual(len(offset), 5)
        
        paginated = self.table.select(limit=3, offset=2)
        self.assertEqual(len(paginated), 3)
        
        self.assertEqual(paginated[0]['name'], 'User2')
        self.assertEqual(paginated[1]['name'], 'User3')
        self.assertEqual(paginated[2]['name'], 'User4')
    
    def test_select_with_filters_and_sorting(self):
        self.table.create({'name': 'Alice', 'age': 30, 'email': 'alice@example.com'})
        self.table.create({'name': 'Bob', 'age': 25, 'email': 'bob@example.com'})
        self.table.create({'name': 'Alice', 'age': 20, 'email': 'alice2@example.com'})
        self.table.create({'name': 'Charlie', 'age': 35, 'email': 'charlie@example.com'})
        
        result = self.table.select(
            filters={'name': 'Alice'},
            sort_by='age'
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['age'], 20)
        self.assertEqual(result[1]['age'], 30)
    
    def test_select_invalid_sort_field_raises_error(self):
        self.table.create({'name': 'Test', 'age': 25, 'email': 'test@example.com'})
        
        with self.assertRaises(InvalidFieldError):
            self.table.select(sort_by='nonexistent_field')
    
    def test_update_with_id_change(self):
        record = self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        
        updated = self.table.update(record['id'], {'id': 999})
        
        self.assertEqual(updated['id'], 999)
        
        old_found = self.table.find(record['id'])
        self.assertIsNone(old_found)
        
        new_found = self.table.find(999)
        self.assertIsNotNone(new_found)
    
    def test_update_id_to_duplicate_raises_error(self):
        record1 = self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        record2 = self.table.create({'name': 'Jane', 'age': 30, 'email': 'jane@example.com'})
        
        with self.assertRaises(DuplicateIDError):
            self.table.update(record2['id'], {'id': record1['id']})
    
    def test_delete_by_filter(self):
        self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        self.table.create({'name': 'John', 'age': 30, 'email': 'john2@example.com'})
        self.table.create({'name': 'Jane', 'age': 25, 'email': 'jane@example.com'})
        
        deleted = self.table.delete_by_filter({'name': 'John'})
        
        self.assertEqual(len(deleted), 2)
        self.assertEqual(self.table.record_count, 1)
        
        remaining = self.table.get_all()
        self.assertEqual(remaining[0]['name'], 'Jane')
    
    def test_delete_by_empty_filter(self):
        self.table.create({'name': 'John', 'age': 25, 'email': 'john@example.com'})
        self.table.create({'name': 'Jane', 'age': 30, 'email': 'jane@example.com'})
        
        deleted = self.table.delete_by_filter({})
        
        self.assertEqual(len(deleted), 2)
        self.assertEqual(self.table.record_count, 0)
    
    def test_clear_empty_table(self):
        self.assertEqual(self.table.record_count, 0)
        deleted_count = self.table.clear()
        self.assertEqual(deleted_count, 0)
    
    def test_select_with_limit_zero(self):
        self.table.create({'name': 'Test', 'age': 25, 'email': 'test@example.com'})
        result = self.table.select(limit=0)
        self.assertEqual(len(result), 1)
    
    def test_select_with_negative_limit(self):
        self.table.create({'name': 'Test', 'age': 25, 'email': 'test@example.com'})
        result = self.table.select(limit=-5)
        self.assertEqual(len(result), 0)
    
    def test_select_with_only_offset(self):
        for i in range(5):
            self.table.create({'name': f'User{i}', 'age': 20 + i, 'email': f'user{i}@example.com'})
        
        result = self.table.select(offset=2)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['name'], 'User2')
    
    def test_select_with_sorting_invalid_field(self):
        self.table.create({'name': 'Test', 'age': 25, 'email': 'test@example.com'})
        
        with self.assertRaises(InvalidFieldError):
            self.table.select(sort_by='field_that_does_not_exist')


if __name__ == '__main__':
    unittest.main()