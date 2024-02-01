import sqlite3
import pytest
import logging
from pyupgrader.utilities.hashing import HashDB

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def hash_db(tmp_path):
    """
    Create a temporary database for hashing.

    Args:
        tmp_path (str): The path to the temporary directory.

    Returns:
        HashDB: The created HashDB object.
    """
    LOGGER.debug("Creating a temporary database")
    db_path = tmp_path / "test.db"
    hash_db = HashDB(str(db_path))
    return hash_db

def test_get_file_paths(hash_db):
    """
    Test the get_file_paths method of the HashDB class.

    This function adds some file paths to the database and then retrieves them using the get_file_paths method.
    It asserts that the retrieved file paths match the expected file paths.

    Args:
        hash_db (HashDB): An instance of the HashDB class.
    """
    # Add some file paths to the database
    hash_db.cursor.execute("CREATE TABLE hashes (file_path TEXT)")
    hash_db.cursor.execute("INSERT INTO hashes (file_path) VALUES ('path/to/file1')")
    hash_db.cursor.execute("INSERT INTO hashes (file_path) VALUES ('path/to/file2')")
    hash_db.cursor.execute("INSERT INTO hashes (file_path) VALUES ('path/to/file3')")

    # Test the get_file_paths method
    file_paths = list(hash_db.get_file_paths())
    assert file_paths == ['path/to/file1', 'path/to/file2', 'path/to/file3']

def test_get_file_hash(hash_db):
    """
    Test the get_file_hash method of the HashDB class.

    This function tests the functionality of the get_file_hash method by adding a file hash to the database,
    and then retrieving the hash using the get_file_hash method. It asserts that the retrieved hash matches
    the expected hash value.

    Args:
        hash_db (HashDB): An instance of the HashDB class.
    """
    # Add a file hash to the database
    hash_db.cursor.execute("CREATE TABLE hashes (file_path TEXT, calculated_hash TEXT)")
    hash_db.cursor.execute("INSERT INTO hashes (file_path, calculated_hash) VALUES ('path/to/file', 'hash123')")

    # Test the get_file_hash method
    file_hash = hash_db.get_file_hash('path/to/file')
    assert file_hash == 'hash123'

def test_open_close(hash_db):
    """
    Test the open and close functionality of the hash_db object.

    This function verifies that the hash_db object correctly opens a connection
    and cursor, and then closes them when requested.
    """
    assert hash_db.connection is not None
    assert hash_db.cursor is not None

    hash_db.close()
    assert hash_db.connection is None
    assert hash_db.cursor is None