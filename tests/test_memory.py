import unittest
from src.db.backend.memory import InMemoryDatabase
from src.db.backend.errors import TableExistsError, TableNotFoundError, ValidationError


class TestInMemoryDatabase(unittest.TestCase):
    
    def setUp(self):
        self.db = InMemoryDatabase()
        self.schema = {
            'id': int,
            'name': str,
            'age': int
        }
    
    def test_create_table(self):
        table = self.db.create_table('users', self.schema)
        
        self.assertIsNotNone(table)
        self.assertEqual(table.name, 'users')
        self.assertTrue(self.db.table_exists('users'))
        self.assertEqual(self.db.get_table_names(), ['users'])
    
    def test_create_duplicate_table(self):
        self.db.create_table('users', self.schema)
        
        with self.assertRaises(TableExistsError):
            self.db.create_table('users', self.schema)
    
    def test_get_table(self):
        created = self.db.create_table('users', self.schema)
        retrieved = self.db.get_table('users')
        
        self.assertEqual(created.name, retrieved.name)
    
    def test_get_nonexistent_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.get_table('nonexistent')
    
    def test_drop_table(self):
        self.db.create_table('users', self.schema)
        self.assertTrue(self.db.table_exists('users'))
        
        self.db.drop_table('users')
        self.assertFalse(self.db.table_exists('users'))
        self.assertEqual(self.db.get_table_names(), [])
    
    def test_drop_nonexistent_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.drop_table('nonexistent')
    
    def test_get_all_tables_info(self):
        self.db.create_table('users', self.schema)
        self.db.create_table('products', {'id': int, 'name': str, 'price': float})
        
        info = self.db.get_all_tables_info()
        
        self.assertEqual(set(info.keys()), {'users', 'products'})
        
        if 'record_count' in info['users']:
            self.assertEqual(info['users']['record_count'], 0)
        elif 'records_count' in info['users']:
            self.assertEqual(info['users']['records_count'], 0)
        else:
            self.assertIn('record_count', info['users'].keys())
        
        self.assertIn('name', info['users']['schema'])
    
    def test_table_operations_through_db(self):
        table = self.db.create_table('users', self.schema)
        
        record = table.create({'name': 'John', 'age': 25})
        self.assertEqual(record['id'], 1)
        
        found = table.find(1)
        self.assertEqual(found['name'], 'John')
        
        updated = table.update(1, {'age': 26})
        self.assertEqual(updated['age'], 26)
        
        deleted = table.delete(1)
        self.assertEqual(deleted['id'], 1)
        self.assertEqual(table.record_count, 0)
    
    def test_multiple_tables_independence(self):
        users = self.db.create_table('users', {'id': int, 'name': str})
        products = self.db.create_table('products', {'id': int, 'title': str})
        
        users.create({'name': 'John'})
        users.create({'name': 'Jane'})
        products.create({'title': 'Book'})
        
        self.assertEqual(users.record_count, 2)
        self.assertEqual(products.record_count, 1)
        
        self.assertEqual(users.find(1)['name'], 'John')
        self.assertEqual(products.find(1)['title'], 'Book')


if __name__ == '__main__':
    unittest.main()