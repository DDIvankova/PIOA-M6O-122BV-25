import unittest
from unittest.mock import patch
import sys
import os
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import TableNotFoundError, TableExistsError, RecordNotFoundError

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()

    def test_create_table(self):
        schema = {"id": int, "name": str}
        self.db.create_table("users", schema)
        self.assertIn("users", self.db.get_table_names())

    def test_create_duplicate_table(self):
        schema = {"id": int, "name": str}
        self.db.create_table("users", schema)
        with self.assertRaises(TableExistsError):
            self.db.create_table("users", schema)

    def test_insert_record(self):
        schema = {"id": int, "name": str, "age": int}
        self.db.create_table("users", schema)
        record = self.db.insert_record("users", {"name": "John", "age": 30})
        self.assertEqual(record["id"], 1)

    def test_select_with_filters(self):
        schema = {"id": int, "name": str, "age": int}
        self.db.create_table("users", schema)
        self.db.insert_record("users", {"name": "John", "age": 30})
        self.db.insert_record("users", {"name": "Jane", "age": 25})
        records = self.db.select_records("users", {"name": "John"})
        self.assertEqual(len(records), 1)

    def test_select_all_records(self):
        schema = {"id": int, "name": str, "age": int}
        self.db.create_table("users", schema)
        self.db.insert_record("users", {"name": "John", "age": 30})
        self.db.insert_record("users", {"name": "Jane", "age": 25})
        records = self.db.select_records("users")
        self.assertEqual(len(records), 2)

    def test_select_with_sort(self):
        schema = {"id": int, "name": str, "age": int}
        self.db.create_table("users", schema)
        self.db.insert_record("users", {"name": "Charlie", "age": 30})
        self.db.insert_record("users", {"name": "Alice", "age": 25})
        self.db.insert_record("users", {"name": "Bob", "age": 35})
        
        records = self.db.select_records("users", sort_by="name")
        names = [r["name"] for r in records]
        self.assertEqual(names, ["Alice", "Bob", "Charlie"])

    def test_update_record(self):
        schema = {"id": int, "name": str, "age": int}
        self.db.create_table("users", schema)
        record = self.db.insert_record("users", {"name": "John", "age": 30})
        updated = self.db.update_record("users", record["id"], {"age": 31})
        self.assertEqual(updated["age"], 31)

    def test_update_nonexistent_record(self):
        schema = {"id": int, "name": str}
        self.db.create_table("users", schema)
        with self.assertRaises(RecordNotFoundError):
            self.db.update_record("users", 999, {"name": "Test"})

    def test_delete_record(self):
        schema = {"id": int, "name": str, "age": int}
        self.db.create_table("users", schema)
        record = self.db.insert_record("users", {"name": "John", "age": 30})
        self.assertEqual(len(self.db.select_records("users")), 1)
        self.db.delete_record("users", record["id"])
        self.assertEqual(len(self.db.select_records("users")), 0)

    def test_delete_nonexistent_record(self):
        schema = {"id": int, "name": str}
        self.db.create_table("users", schema)
        with self.assertRaises(RecordNotFoundError):
            self.db.delete_record("users", 999)

    def test_select_from_nonexistent_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent")

    def test_table_exists(self):
        self.assertFalse(self.db.table_exists("users"))
        schema = {"id": int, "name": str}
        self.db.create_table("users", schema)
        self.assertTrue(self.db.table_exists("users"))


class TestMainCoverage(unittest.TestCase):
    @patch('src.db.__main__.run')
    def test_main_calls_run(self, mock_run):
        from src.db.__main__ import main
        main()
        mock_run.assert_called_once()

    @patch('src.db.__main__.run')
    def test_main_calls_run_only_once(self, mock_run):
        from src.db.__main__ import main
        main()
        self.assertEqual(mock_run.call_count, 1)

    def test_module_has_main_function(self):
        import src.db.__main__ as main_module
        self.assertTrue(hasattr(main_module, 'main'))
        self.assertTrue(callable(main_module.main))

    def test_module_has_run_import(self):
        import src.db.__main__ as main_module
        self.assertTrue(hasattr(main_module, 'run'))

    @patch('src.db.__main__.run')
    def test_main_executes_without_errors(self, mock_run):
        from src.db.__main__ import main
        try:
            main()
        except Exception as e:
            self.fail(f"main() вызвал исключение: {e}")

    def test_import_main_module(self):
        import src.db.__main__
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()