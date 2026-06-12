import unittest
import tempfile
import shutil
import json
import os
from src.db.backend.file import FileDatabase
from src.db.backend.errors import TableNotFoundError, TableExistsError


class TestFileDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = FileDatabase(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_create_table(self):
        schema = {"id": int, "name": str, "age": int}
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
        self.assertEqual(record["name"], "John")

    def test_select_all_records(self):
        schema = {"id": int, "name": str, "age": int}
        self.db.create_table("users", schema)
        self.db.insert_record("users", {"name": "John", "age": 30})
        self.db.insert_record("users", {"name": "Jane", "age": 25})
        records = self.db.select_records("users")
        self.assertEqual(len(records), 2)

    def test_select_with_filters(self):
        schema = {"id": int, "name": str, "age": int}
        self.db.create_table("users", schema)
        self.db.insert_record("users", {"name": "John", "age": 30})
        self.db.insert_record("users", {"name": "Jane", "age": 25})
        records = self.db.select_records("users", {"name": "John"})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "John")

    def test_update_record(self):
        schema = {"id": int, "name": str, "age": int}
        self.db.create_table("users", schema)
        record = self.db.insert_record("users", {"name": "John", "age": 30})
        updated = self.db.update_record("users", record["id"], {"age": 31})
        self.assertEqual(updated["age"], 31)

    def test_delete_record(self):
        schema = {"id": int, "name": str, "age": int}
        self.db.create_table("users", schema)
        record = self.db.insert_record("users", {"name": "John", "age": 30})
        self.assertEqual(len(self.db.select_records("users")), 1)
        self.db.delete_record("users", record["id"])
        self.assertEqual(len(self.db.select_records("users")), 0)

    def test_data_persistence(self):
        schema = {"id": int, "name": str, "age": int}
        db1 = FileDatabase(self.temp_dir)
        db1.create_table("users", schema)
        db1.insert_record("users", {"name": "John", "age": 30})
        
        db2 = FileDatabase(self.temp_dir)
        records = db2.select_records("users")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "John")

    def test_select_from_nonexistent_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent")

    def test_drop_table(self):
        schema = {"id": int, "name": str}
        self.db.create_table("users", schema)
        self.assertIn("users", self.db.get_table_names())
        self.db.drop_table("users")
        self.assertNotIn("users", self.db.get_table_names())

    def test_insert_record_with_custom_id(self):
        schema = {"id": int, "name": str}
        self.db.create_table("users", schema)
        record = self.db.insert_record("users", {"id": 100, "name": "John"})
        self.assertEqual(record["id"], 100)

    def test_file_created_on_disk(self):
        schema = {"id": int, "name": str}
        self.db.create_table("users", schema)
        file_path = os.path.join(self.temp_dir, "users.json")
        self.assertTrue(os.path.exists(file_path))
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("schema", data)
        self.assertIn("records", data)


if __name__ == "__main__":
    unittest.main()