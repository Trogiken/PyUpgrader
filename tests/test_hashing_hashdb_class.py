import sqlite3
import pytest
import logging
from pyupgrader.utilities.hashing import HashDB

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def hash_db(tmp_path):
    LOGGER.debug("Creating a temporary database")
    db_path = tmp_path / "test.db"
    hash_db = HashDB(str(db_path))
    return hash_db

def test_get_file_paths(hash_db):
    LOGGER.info("Testing test_get_file_paths")
    # Add some file paths to the database
    hash_db.cursor.execute("CREATE TABLE hashes (file_path TEXT)")
    hash_db.cursor.execute("INSERT INTO hashes (file_path) VALUES ('path/to/file1')")
    hash_db.cursor.execute("INSERT INTO hashes (file_path) VALUES ('path/to/file2')")
    hash_db.cursor.execute("INSERT INTO hashes (file_path) VALUES ('path/to/file3')")

    # Test the get_file_paths method
    file_paths = list(hash_db.get_file_paths())
    assert file_paths == ['path/to/file1', 'path/to/file2', 'path/to/file3']

def test_get_file_hash(hash_db):
    LOGGER.info("Testing test_get_file_hash")
    # Add a file hash to the database
    hash_db.cursor.execute("CREATE TABLE hashes (file_path TEXT, calculated_hash TEXT)")
    hash_db.cursor.execute("INSERT INTO hashes (file_path, calculated_hash) VALUES ('path/to/file', 'hash123')")

    # Test the get_file_hash method
    file_hash = hash_db.get_file_hash('path/to/file')
    assert file_hash == 'hash123'

def test_open_close(hash_db):
    LOGGER.info("Testing test_open_close")
    assert hash_db.connection is not None
    assert hash_db.cursor is not None

    hash_db.close()
    assert hash_db.connection is None
    assert hash_db.cursor is None