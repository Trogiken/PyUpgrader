import tempfile
import os
import logging
import unittest
import shutil
import sqlite3
from pyupgrader.utilities import hashing

LOGGER = logging.getLogger(__name__)


class Hasher(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.temp_dir_path = tempfile.mkdtemp()
        LOGGER.debug("Created temporary directory")

        # Create a hasher
        self.hasher = hashing.Hasher(os.path.basename(self.temp_dir_path))

        # Create a temporary file
        self.temp_file_path = os.path.join(self.temp_dir_path, "file.txt")
        with open(self.temp_file_path, "w") as file:
            file.write("hello world")
        
        LOGGER.debug("Creating temporary directory structure")
        # create temporary hashing directory structure
        self.hashing_dir_path = os.path.join(self.temp_dir_path, "hashing")
        self.dir1_path = os.path.join(self.hashing_dir_path, "dir1")
        self.dir2_path = os.path.join(self.hashing_dir_path, "dir2")
        os.makedirs(self.dir1_path)
        os.makedirs(self.dir2_path)
        with open(os.path.join(self.hashing_dir_path, "file1.txt"), "w") as file:
            file.write("hello world1")
        with open(os.path.join(self.hashing_dir_path, "file2.log"), "w") as file:
            file.write("hello world2")
        with open(os.path.join(self.dir1_path, "file3.txt"), "w") as file:
            file.write("hello world3")
        with open(os.path.join(self.dir1_path, "file4.txt"), "w") as file:
            file.write("hello world4")
        with open(os.path.join(self.dir2_path, "file5.txt"), "w") as file:
            file.write("hello world5")
        with open(os.path.join(self.dir2_path, "file6.txt"), "w") as file:
            file.write("hello world6")
        LOGGER.debug("Created temporary directory structure")

    def tearDown(self):
        shutil.rmtree(self.temp_dir_path)
        LOGGER.debug(f"Removed temporary directory: {self.temp_dir_path}")

    def test_create_hash(self):
        LOGGER.info("Testing test_create_hash")
        expected_relative_file_path = "file.txt"
        expected_file_hash = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

        relative_file_path, file_hash = self.hasher.create_hash(self.temp_file_path)

        LOGGER.debug(f"relative_file_path: {relative_file_path}")
        LOGGER.debug(f"file_hash: {file_hash}")
        assert relative_file_path == expected_relative_file_path
        assert file_hash == expected_file_hash

    def test_create_hash_db(self):
        LOGGER.info("Testing test_create_hash_db")
        db_save_path = os.path.join(self.temp_dir_path, "hash.db")
        exclude_paths = [self.dir1_path, os.path.join(self.hashing_dir_path, "file1.txt")]
        exclude_patterns = [r".*\.log$"]
        expected_db_save_path = os.path.join(self.temp_dir_path, "hash.db")

        db_save_path = self.hasher.create_hash_db(self.hashing_dir_path, db_save_path, exclude_paths, exclude_patterns)

        LOGGER.debug(f"db_save_path: {db_save_path}")
        assert db_save_path == expected_db_save_path

        # Verify the database
        connection = sqlite3.connect(db_save_path)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM hashes")
        rows = cursor.fetchall()
        LOGGER.debug(f"rows: {rows}")
        assert len(rows) == 2
        assert rows[0][0] == "hashing/dir2/file5.txt"
        assert rows[0][1] == "3445b50a09c46b3dee912cd1b8dc9eaa4e756a82b417d97615b92d5cce04d1dd"
        assert rows[1][0] == "hashing/dir2/file6.txt"
        assert rows[1][1] == "a51c576ed146f5517946f646f8e42d304e08ef2d0b104f442e1d90be8dc34b54"
        connection.close()
