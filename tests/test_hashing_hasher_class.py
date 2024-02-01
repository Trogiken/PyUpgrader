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
        """
        Set up the test environment by creating a temporary directory, a hasher object,
        and a temporary file with some content. Also, create a temporary directory structure
        with multiple files for testing purposes.
        """
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
        """
        Clean up method that is called after each test case.
        Removes the temporary directory and logs the removal.
        """
        shutil.rmtree(self.temp_dir_path)
        LOGGER.debug(f"Removed temporary directory: {self.temp_dir_path}")

    def test_create_hash(self):
        """
        Test case for the create_hash method.

        This method tests the functionality of the create_hash method in the Hasher class.
        It verifies that the method correctly creates a hash for a given file path and returns
        the relative file path and the file hash.
        """
        expected_relative_file_path = "file.txt"
        expected_file_hash = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

        relative_file_path, file_hash = self.hasher.create_hash(self.temp_file_path)

        LOGGER.debug(f"relative_file_path: {relative_file_path}")
        LOGGER.debug(f"file_hash: {file_hash}")
        assert relative_file_path == expected_relative_file_path
        assert file_hash == expected_file_hash

    def test_create_hash_db(self):
        """
        Test case for the create_hash_db method.

        This test case verifies the following:
        - The create_hash_db method correctly creates a hash database file.
        - The database schema is verified to have a 'hashes' table.
        - The database contents are verified by querying specific file paths and their corresponding hashes.
        """
        db_save_path = os.path.join(self.temp_dir_path, "hash.db")
        exclude_paths = [self.dir1_path, os.path.join(self.hashing_dir_path, "file1.txt")]
        exclude_patterns = [r".*\.log$"]
        expected_db_save_path = os.path.join(self.temp_dir_path, "hash.db")

        db_save_path = self.hasher.create_hash_db(self.hashing_dir_path, db_save_path, exclude_paths, exclude_patterns)

        LOGGER.debug(f"db_save_path: {db_save_path}")
        assert db_save_path == expected_db_save_path

        LOGGER.info("Verifying the database schema")
        connection = sqlite3.connect(db_save_path)
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hashes'")
        rows = cursor.fetchall()
        LOGGER.debug(f"rows: {rows}")
        assert len(rows) == 1
        assert rows[0][0] == "hashes"

        LOGGER.info("Verifying the database contents")
        cursor.execute("SELECT * FROM hashes")
        rows = cursor.fetchall()
        LOGGER.debug(f"All Rows: {rows}")
        # get file5 from the database using sql
        cursor.execute("SELECT * FROM hashes WHERE file_path='hashing/dir2/file5.txt'")
        rows = cursor.fetchall()
        LOGGER.debug(f"file 5: {rows}")
        assert len(rows) == 1
        assert rows[0][0] == "hashing/dir2/file5.txt"
        assert rows[0][1] == "3445b50a09c46b3dee912cd1b8dc9eaa4e756a82b417d97615b92d5cce04d1dd"
        # get file6 from the database using sql
        cursor.execute("SELECT * FROM hashes WHERE file_path='hashing/dir2/file6.txt'")
        rows = cursor.fetchall()
        LOGGER.debug(f"file 6: {rows}")
        assert len(rows) == 1
        assert rows[0][0] == "hashing/dir2/file6.txt"
        assert rows[0][1] == "a51c576ed146f5517946f646f8e42d304e08ef2d0b104f442e1d90be8dc34b54"

        connection.close()


if __name__ == "__main__":
    unittest.main()
