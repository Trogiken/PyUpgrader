import sqlite3
import tempfile
import unittest
import logging
import shutil
import os
from pyupgrader.utilities.hashing import compare_databases

LOGGER = logging.getLogger(__name__)


class TestCompareDatabase(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment by creating temporary directories and files.
        """
        self.temp_dir_path = tempfile.mkdtemp()
        LOGGER.debug("Created temporary directory")
        self.local_db_path = os.path.join(self.temp_dir_path, "db1.db")
        self.cloud_db_path = os.path.join(self.temp_dir_path, "db2.db")
        
        with open(self.local_db_path, "w") as file:
            file.write("")
        LOGGER.debug(f"Created temporary file: {self.local_db_path}")
        with open(self.cloud_db_path, "w") as file:
            file.write("")
        LOGGER.debug(f"Created temporary file: {self.cloud_db_path}")
    
    def tearDown(self):
        """
        Clean up method that is called after each test case.
        Removes the temporary directory created for the test.
        """
        shutil.rmtree(self.temp_dir_path)
        LOGGER.debug(f"Removed temporary directory: {self.temp_dir_path}")
    
    def test_compare_databases(self):
        """
        Test case for comparing two databases and checking the summary of differences.

        This test case performs the following steps:
        1. Connects to the local database and creates a table called 'hashes'.
        2. Inserts sample data into the 'hashes' table in the local database.
        3. Connects to the cloud database and creates a table called 'hashes'.
        4. Inserts sample data into the 'hashes' table in the cloud database.
        5. Calls the 'compare_databases' function to compare the two databases.
        6. Asserts the expected results based on the comparison summary.
        7. Closes the database connections.

        The expected results are as follows:
        - 'unique_files_local_db' should be ['file2.txt']
        - 'unique_files_cloud_db' should be ['file3.txt']
        - 'ok_files' should be [('file1.txt', 'hash1')]
        - 'bad_files' should be [('file4.txt', 'hash4', 'hash10')]
        """
        connection1 = sqlite3.connect(self.local_db_path)
        cursor1 = connection1.cursor()
        cursor1.execute("CREATE TABLE hashes (file_path TEXT, calculated_hash TEXT)")
        cursor1.execute("INSERT INTO hashes VALUES ('file1.txt', 'hash1')")
        cursor1.execute("INSERT INTO hashes VALUES ('file2.txt', 'hash2')")
        cursor1.execute("INSERT INTO hashes VALUES ('file4.txt', 'hash4')")
        connection1.commit()

        connection2 = sqlite3.connect(self.cloud_db_path)
        cursor2 = connection2.cursor()
        cursor2.execute("CREATE TABLE hashes (file_path TEXT, calculated_hash TEXT)")
        cursor2.execute("INSERT INTO hashes VALUES ('file1.txt', 'hash1')")
        cursor2.execute("INSERT INTO hashes VALUES ('file3.txt', 'hash3')")
        cursor2.execute("INSERT INTO hashes VALUES ('file4.txt', 'hash10')")
        connection2.commit()

        summary = compare_databases(self.local_db_path, self.cloud_db_path)

        # Assert the expected results
        assert summary.unique_files_local_db == ['file2.txt']
        assert summary.unique_files_cloud_db == ['file3.txt']
        assert summary.ok_files == [('file1.txt', 'hash1')]
        assert summary.bad_files == [('file4.txt', 'hash4', 'hash10')]

        connection1.close()
        connection2.close()


if __name__ == "__main__":
    unittest.main()
