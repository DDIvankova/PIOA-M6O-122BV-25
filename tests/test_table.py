import unittest
from src.db.backend.table import Table
from src.db.backend.errors import (
    ValidationError, DuplicateIDError, RecordNotFoundError,
    InvalidFieldError, InvalidSortError
)


class TestTable(unittest.TestCase):
    def setUp(self):
        self.schema = {'id': int, 'name': str, 'age': int, 'email': str}
        self.table = Table('test_table', self.schema)

    def test_create_record(self):
        record = self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        self.assertEqual(record['id'], 1)
        self.assertEqual(self.table.record_count, 1)

    def test_create_record_with_custom_id(self):
        record = self.table.create({'id': 100, 'name': 'Jane', 'age': 30, 'email': 'jane@test.com'})
        self.assertEqual(record['id'], 100)
        
        record2 = self.table.create({'name': 'Bob', 'age': 20, 'email': 'bob@test.com'})
        self.assertEqual(record2['id'], 101)

    def test_create_duplicate_id(self):
        self.table.create({'id': 1, 'name': 'John', 'age': 25, 'email': 'john@test.com'})
        with self.assertRaises(DuplicateIDError):
            self.table.create({'id': 1, 'name': 'Jane', 'age': 30, 'email': 'jane@test.com'})

    def test_create_missing_field(self):
        with self.assertRaises(ValidationError):
            self.table.create({'name': 'John', 'age': 25})

    def test_create_extra_field(self):
        with self.assertRaises(ValidationError):
            self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com', 'extra': 'value'})

    def test_find_record(self):
        record = self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        found = self.table.find(record['id'])
        self.assertIsNotNone(found)
        self.assertEqual(found['name'], 'John')

    def test_find_not_found(self):
        result = self.table.find(999)
        self.assertIsNone(result)

    def test_select_all(self):
        self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        self.table.create({'name': 'Jane', 'age': 30, 'email': 'jane@test.com'})
        records = self.table.select()
        self.assertEqual(len(records), 2)

    def test_select_with_filters(self):
        self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        self.table.create({'name': 'Jane', 'age': 30, 'email': 'jane@test.com'})
        self.table.create({'name': 'John', 'age': 35, 'email': 'john2@test.com'})
        
        records = self.table.select({'name': 'John'})
        self.assertEqual(len(records), 2)
        
        records = self.table.select({'age': 30})
        self.assertEqual(len(records), 1)

    def test_select_with_limit(self):
        for i in range(10):
            self.table.create({'name': f'User{i}', 'age': i, 'email': f'user{i}@test.com'})
        
        result = self.table.select(limit=5)
        self.assertEqual(len(result), 5)

    def test_select_with_offset(self):
        for i in range(10):
            self.table.create({'name': f'User{i}', 'age': i, 'email': f'user{i}@test.com'})
        
        result = self.table.select(offset=5)
        self.assertEqual(len(result), 5)

    def test_select_with_limit_and_offset(self):
        for i in range(10):
            self.table.create({'name': f'User{i}', 'age': i, 'email': f'user{i}@test.com'})
        
        result = self.table.select(limit=3, offset=2)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['name'], 'User2')

    def test_select_with_sorting(self):
        self.table.create({'name': 'Charlie', 'age': 30, 'email': 'c@test.com'})
        self.table.create({'name': 'Alice', 'age': 25, 'email': 'a@test.com'})
        self.table.create({'name': 'Bob', 'age': 35, 'email': 'b@test.com'})
        
        result = self.table.select(sort_by='name')
        names = [r['name'] for r in result]
        self.assertEqual(names, ['Alice', 'Bob', 'Charlie'])

    def test_select_with_sort_descending(self):
        self.table.create({'name': 'Charlie', 'age': 30, 'email': 'c@test.com'})
        self.table.create({'name': 'Alice', 'age': 25, 'email': 'a@test.com'})
        self.table.create({'name': 'Bob', 'age': 35, 'email': 'b@test.com'})
        
        result = self.table.select(sort_by='name', reverse=True)
        names = [r['name'] for r in result]
        self.assertEqual(names, ['Charlie', 'Bob', 'Alice'])

    def test_select_with_invalid_filter_field(self):
        self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        
        with self.assertRaises(InvalidFieldError):
            self.table.select(filters={'invalid': 'value'})

    def test_select_with_invalid_sort_field(self):
        self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        
        with self.assertRaises(InvalidFieldError):
            self.table.select(sort_by='invalid')

    def test_update_record(self):
        record = self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        updated = self.table.update(record['id'], {'name': 'John Updated', 'age': 26})
        
        self.assertEqual(updated['name'], 'John Updated')
        self.assertEqual(updated['age'], 26)

    def test_update_with_id_change(self):
        record = self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        updated = self.table.update(record['id'], {'id': 999})
        
        self.assertEqual(updated['id'], 999)
        self.assertIsNone(self.table.find(record['id']))
        self.assertIsNotNone(self.table.find(999))

    def test_update_id_to_duplicate(self):
        record1 = self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        record2 = self.table.create({'name': 'Jane', 'age': 30, 'email': 'jane@test.com'})
        
        with self.assertRaises(DuplicateIDError):
            self.table.update(record2['id'], {'id': record1['id']})

    def test_update_nonexistent_record(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.update(999, {'name': 'New Name'})

    def test_delete_record(self):
        record = self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        self.assertEqual(self.table.record_count, 1)
        
        deleted = self.table.delete(record['id'])
        self.assertEqual(deleted['id'], record['id'])
        self.assertEqual(self.table.record_count, 0)
        self.assertIsNone(self.table.find(record['id']))

    def test_delete_nonexistent_record(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.delete(999)

    def test_delete_by_filter(self):
        self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        self.table.create({'name': 'John', 'age': 30, 'email': 'john2@test.com'})
        self.table.create({'name': 'Jane', 'age': 25, 'email': 'jane@test.com'})
        
        deleted = self.table.delete_by_filter({'name': 'John'})
        
        self.assertEqual(len(deleted), 2)
        self.assertEqual(self.table.record_count, 1)
        self.assertEqual(self.table.get_all()[0]['name'], 'Jane')

    def test_delete_by_empty_filter(self):
        self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        self.table.create({'name': 'Jane', 'age': 30, 'email': 'jane@test.com'})
        
        deleted = self.table.delete_by_filter({})
        
        self.assertEqual(len(deleted), 2)
        self.assertEqual(self.table.record_count, 0)

    def test_clear_table(self):
        self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        self.table.create({'name': 'Jane', 'age': 30, 'email': 'jane@test.com'})
        
        deleted = self.table.clear()
        self.assertEqual(deleted, 2)
        self.assertEqual(self.table.record_count, 0)

    def test_clear_empty_table(self):
        self.assertEqual(self.table.record_count, 0)
        deleted = self.table.clear()
        self.assertEqual(deleted, 0)

    def test_get_all_returns_copy(self):
        record = self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        
        records = self.table.get_all()
        records[0]['name'] = 'Changed'
        
        original = self.table.find(record['id'])
        self.assertEqual(original['name'], 'John')

    def test_record_count_property(self):
        self.assertEqual(self.table.record_count, 0)
        self.table.create({'name': 'John', 'age': 25, 'email': 'john@test.com'})
        self.assertEqual(self.table.record_count, 1)

    def test_schema_property(self):
        schema = self.table.schema
        self.assertEqual(schema['id'], int)
        self.assertEqual(schema['name'], str)
        
        # Изменение копии не влияет на оригинал
        schema['new'] = float
        self.assertNotIn('new', self.table.schema)


if __name__ == '__main__':
    unittest.main()