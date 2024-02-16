import unittest
import os
import hashlib
import shutil
import sqlite3
from .helper import create_dir_structure
from pyupgrader.utilities.hashing import Hasher, HashDB

class HashDBTestCase(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "test_hashes.db")
        self.hash_db = HashDB(self.db_path)

    def tearDown(self):
        self.hash_db.close()
        os.remove(self.db_path)

    def test_get_file_paths(self):
        # Insert test data into the database
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE hashes (file_path TEXT, calculated_hash TEXT)")
        cursor.execute("INSERT INTO hashes VALUES (?, ?)", ("file1.txt", "hash1"))
        cursor.execute("INSERT INTO hashes VALUES (?, ?)", ("file2.txt", "hash2"))
        connection.commit()
        connection.close()

        # Test the get_file_paths method
        expected_file_paths = ["file1.txt", "file2.txt"]
        file_paths = list(self.hash_db.get_file_paths())
        self.assertEqual(file_paths, expected_file_paths)

    def test_get_file_hash(self):
        # Insert test data into the database
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE hashes (file_path TEXT, calculated_hash TEXT)")
        cursor.execute("INSERT INTO hashes VALUES (?, ?)", ("file1.txt", "hash1"))
        cursor.execute("INSERT INTO hashes VALUES (?, ?)", ("file2.txt", "hash2"))
        connection.commit()
        connection.close()

        # Test the get_file_hash method
        expected_hash = "hash1"
        file_hash = self.hash_db.get_file_hash("file1.txt")
        self.assertEqual(file_hash, expected_hash)

class HasherTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_project")
        self.save_dir = os.path.join(os.path.dirname(__file__), "save_project")
        create_dir_structure(self.test_dir)
        os.mkdir(self.save_dir)

        self.hasher = Hasher("test_project")
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.save_dir)

    def test_create_hash(self):
        file_path = os.path.join(self.test_dir, "file1.txt")  # created by create_dir_structure
        # hash file
        with open(file_path, "rb") as file:
            file_content = file.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
        
        expected_relative_file_path = "file1.txt"
        expected_file_hash = file_hash

        relative_file_path, file_hash = self.hasher.create_hash(file_path)

        self.assertEqual(relative_file_path, expected_relative_file_path)
        self.assertEqual(file_hash, expected_file_hash)

    def test_create_hash_db(self):
        hash_dir_path = self.test_dir
        db_save_path = os.path.join(self.save_dir, "hashes.db")
        exclude_paths = ["/path/to/exclude1", "/path/to/exclude2"]
        exclude_patterns = [".*/.txt"]
        expected_db_save_path = db_save_path

        returned_db_save_path = self.hasher.create_hash_db(
            hash_dir_path, db_save_path, exclude_paths, exclude_patterns
        )

        self.assertEqual(returned_db_save_path, expected_db_save_path)
        self.assertTrue(os.path.exists(db_save_path))

        # validate db

        # hash file
        file_path = os.path.join(self.test_dir, "file1.txt")  # created by create_dir_structure
        with open(file_path, "rb") as file:
            file_content = file.read()
            file_hash = hashlib.sha256(file_content).hexdigest()

        connection = sqlite3.connect(db_save_path)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM hashes")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 3)
        # file1.txt
        self.assertEqual(rows[0][0], "file1.txt")
        # hash file
        self.assertEqual(rows[0][1], file_hash)
        connection.close()

if __name__ == "__main__":
    unittest.main()
