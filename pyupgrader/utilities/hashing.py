"""
Hasher module for PyUpgrader.

This module provides classes and functions for hashing files, creating hash databases, 
and comparing hash databases.

Classes:
- DBSummary: Dataclass for database summary.
- HashDB: A class that provides methods to interact with a hash database.
- Hasher: A class that provides methods for hashing files and creating hash databases.

Functions:
- compare_databases(db1: str, db2: str) -> DBSummary

Exceptions:
- HashingError: Exception raised for errors in the hashing process.
"""

import hashlib
import os
import sqlite3
import time
import re
import logging
import multiprocessing as multiprc
from typing import List, Tuple, Generator
from dataclasses import dataclass
from pyupgrader.utilities import helper

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class HashingError(Exception):
    """Exception raised for errors in the hashing process."""


@dataclass
class DBSummary:
    """
    Dataclass for database summary

    Attributes
    ----------
    unique_files_local_db: list
        List of files unique to the local database
    unique_files_cloud_db: list
        List of files unique to the cloud database
    ok_files: list
        List of in-common files that have the same hash
    bad_files: list
        List of in-common files that have different hashes
    """

    unique_files_local_db: list
    unique_files_cloud_db: list
    ok_files: list
    bad_files: list

    def __str__(self) -> str:
        return (
            f"Unique files in local database: {len(self.unique_files_local_db)}\n"
            f"Unique files in cloud database: {len(self.unique_files_cloud_db)}\n"
            f"Files with matching hashes: {len(self.ok_files)}\n"
            f"Files with different hashes: {len(self.bad_files)}"
        )

    def __repr__(self) -> str:
        return (
            f"DBSummary(unique_files_local_db={self.unique_files_local_db}, "
            f"unique_files_cloud_db={self.unique_files_cloud_db}, "
            f"ok_files={self.ok_files}, "
            f"bad_files={self.bad_files})"
        )


def compare_databases(db1_path: str, db2_path: str) -> DBSummary:
    """
    Compare two hash databases and return a summary of the differences.

    Args:
    - db1_path (str): The file path of the first hash database.
    - db2_path (str): The file path of the second hash database.

    Returns:
    - DBSummary: An object containing the summary of the differences between the two databases.
    """
    LOGGER.info("Comparing hash databases")
    LOGGER.debug("DB 1 Path: '%s'", db1_path)
    LOGGER.debug("DB 2 Path: '%s'", db2_path)

    connection1 = sqlite3.connect(db1_path)
    cursor1 = connection1.cursor()

    connection2 = sqlite3.connect(db2_path)
    cursor2 = connection2.cursor()

    cursor1.execute("SELECT file_path, calculated_hash FROM hashes")
    local_db_files = {row[0]: row[1] for row in cursor1.fetchall()}

    cursor2.execute("SELECT file_path, calculated_hash FROM hashes")
    cloud_db_files = {row[0]: row[1] for row in cursor2.fetchall()}

    common_files = set(local_db_files.keys()) & set(cloud_db_files.keys())
    unique_files_local_db = list(set(local_db_files.keys()) - set(cloud_db_files.keys()))
    unique_files_cloud_db = list(set(cloud_db_files.keys()) - set(local_db_files.keys()))

    ok_files = [
        (file_path, local_db_files[file_path])
        for file_path in common_files
        if local_db_files[file_path] == cloud_db_files[file_path]
    ]

    bad_files = [
        (file_path, local_db_files[file_path], cloud_db_files[file_path])
        for file_path in common_files
        if local_db_files[file_path] != cloud_db_files[file_path]
    ]

    connection1.close()
    connection2.close()

    return DBSummary(
        unique_files_local_db=unique_files_local_db,
        unique_files_cloud_db=unique_files_cloud_db,
        ok_files=ok_files,
        bad_files=bad_files,
    )


class HashDB:
    """
    A class that provides methods to interact with a hash database.

    Attributes:
    - db_path (str): The path to the hash database.

    Methods:
    - get_file_paths() -> str: Generator that yields file paths from the database.
    - get_file_hash(file_path: str) -> str: Returns the hash of a file in the database.
    - open() -> None: Opens the database connection.
    - close() -> None: Closes the database connection.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.open()

    def __str__(self) -> str:
        return f"HashDB object for '{self.db_path}'"

    def __repr__(self) -> str:
        return f"HashDB(db_path={self.db_path})"

    def get_file_paths(self) -> Generator[str, None, None]:
        """
        Generator that yields file paths from the database.

        Yields:
        - str: The file path.

        Raises:
        - Exception: If there is an error retrieving file paths from the database.
        """
        LOGGER.debug("Retrieving file paths from '%s'", self.db_path)
        self.cursor.execute("SELECT file_path FROM hashes")
        try:
            for row in self.cursor.fetchall():
                yield row[0]
        except Exception as e:
            LOGGER.exception("Error retrieving file paths from '%s'", self.db_path)
            raise e

    def get_file_hash(self, file_path: str) -> str:
        """
        Returns the hash of a file in the database.

        Args:
        - file_path (str): The path of the file.

        Returns:
        - str: The hash of the file.

        Raises:
        - Exception: If there is an error retrieving the hash.
        """
        LOGGER.debug("Retrieving hash for '%s'", file_path)
        self.cursor.execute("SELECT calculated_hash FROM hashes WHERE file_path = ?", (file_path,))
        try:
            return self.cursor.fetchone()[0]
        except Exception as e:
            LOGGER.exception("Error retrieving hash for '%s'", file_path)
            raise e

    def open(self) -> None:
        """
        Opens the database connection.

        Raises:
        - Exception: If there is an error opening the database connection.
        """
        LOGGER.debug("Opening database connection to '%s'", self.db_path)
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            LOGGER.debug("Database connection opened")
        except Exception as e:
            LOGGER.exception("Error opening database connection")
            raise e

    def close(self) -> None:
        """
        Closes the database connection.

        Raises:
        - Exception: If there is an error closing the database connection.
        """
        LOGGER.debug("Closing database connection to '%s'", self.db_path)
        try:
            self.connection.close()
            self.connection = None
            self.cursor = None
            LOGGER.debug("Database connection closed")
        except Exception as e:
            LOGGER.exception("Error closing database connection")
            raise e


class Hasher:
    """
    A class that provides methods for hashing files and creating hash databases.

    Methods:
    - create_hash(self, file_path: str) -> (str, str):
        Creates a hash from file bytes using the chunk method.
    - create_hash_db(self, hash_dir_path: str, db_save_path: str,
                    exclude_paths=None, exclude_patterns=None
                    ) -> str:
        Creates a hash database from a directory path and saves it to a file path.
        Returns the file path.
    """

    def __init__(self):
        self._path_basename = None

    def __str__(self) -> str:
        return "Hasher object"

    def __repr__(self) -> str:
        return "Hasher()"

    def _create_hashes_table(self, cursor: sqlite3.Cursor) -> None:
        """
        Create the 'hashes' table in the database if it does not exist.

        Args:
        - cursor (sqlite3.Cursor): The database cursor.

        Raises:
        - Exception: If there is an error creating the table.
        """
        LOGGER.debug("Starting to create 'hashes' table if it does not exist")
        try:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS hashes "
                "(file_path TEXT PRIMARY KEY, calculated_hash TEXT)"
            )
            LOGGER.debug("'hashes' table created successfully")
        except Exception as e:
            LOGGER.exception("Error creating 'hashes' table")
            raise e

    def _process_batch_data(self, cursor: sqlite3.Cursor, batch_data: List[tuple]) -> None:
        """
        Insert batch data into the 'hashes' table.

        Args:
        - cursor (sqlite3.Cursor):
            The database cursor.
        - batch_data (List[tuple]):
            A list of tuples containing the relative file path and hash as a string.

        Raises:
        - Exception: If there is an error inserting the batch data.
        """
        LOGGER.debug("Processing batch data")
        try:
            cursor.executemany(
                "INSERT OR REPLACE INTO hashes (file_path, calculated_hash) VALUES (?, ?)",
                batch_data,
            )
            LOGGER.debug("Batch data inserted successfully.")
        except Exception as e:
            LOGGER.exception("Error inserting batch data")
            raise e

    def _create_path_and_hash(self, file_path: str) -> Tuple[str, str]:
        """
        Create a relative file path and hash for a file.

        Args:
        - file_path (str): The path of the file.

        Returns:
        - Tuple[str, str]: A tuple containing the relative file path and hash as a string.
        """
        relative_file_path = helper.normalize_paths(
            file_path.split(self._path_basename)[-1]
        ).lstrip(
            "/"
        )  # Remove leading slash and convert to relative path
        LOGGER.debug("Relative file path: %s", relative_file_path)

        return relative_file_path, self.create_hash(file_path)

    def _pool_hashes(self, file_paths: List[str]) -> List[tuple]:
        """
        Create a pool of processes to create hashes from a list of file paths.

        Args:
        - file_paths (List[str]):
            A list of file paths to create hashes for.

        Returns:
        - List[tuple]: A list of tuples containing the relative file path and hash as a string.

        Raises:
        - Exception: If there is an error mapping hashes creation.
        """
        LOGGER.debug("Mapping hashes for %d files", len(file_paths) if file_paths else 0)
        try:
            with multiprc.Pool() as pool:
                return pool.map(self._create_path_and_hash, file_paths)
        except Exception as e:
            LOGGER.exception("Error mapping hashes creation")
            raise e

    def _exclude_files_by_path(
        self, file_paths: List[str], exclude_file_paths: List[str]
    ) -> List[str]:
        """
        Exclude specified file paths from the list.

        Args:
        - file_paths (List[str]):
            A list of file paths to filter.
        - exclude_file_paths (List[str]):
            A list of file paths to exclude.

        Returns:
        - List[str]: A list of file paths that do not match any of the exclude file paths.

        Raises:
        - Exception: If there is an error excluding files by path.
        """
        LOGGER.debug(
            "Excluding %d files by path", len(exclude_file_paths) if exclude_file_paths else 0
        )
        try:
            return [path for path in file_paths if path not in exclude_file_paths]
        except Exception as e:
            LOGGER.exception("Error excluding files by path")
            raise e

    def _exclude_files_by_pattern(
        self, file_paths: List[str], exclude_patterns: List[str]
    ) -> List[str]:
        """
        Exclude specified file paths from the list.

        Args:
        - file_paths (List[str]):
            A list of file paths to filter.
        - exclude_patterns (List[str]):
            A list of patterns to exclude.

        Returns:
        - List[str]: A list of file paths that do not match any of the exclude patterns.

        Raises:
        - Exception: If there is an error excluding files by pattern.
        """
        LOGGER.debug(
            "Excluding %d files by pattern", len(exclude_patterns) if exclude_patterns else 0
        )
        try:
            return [
                path
                for path in file_paths
                if not any(re.search(pattern, path) for pattern in exclude_patterns)
            ]
        except Exception as e:
            LOGGER.exception("Error excluding files by pattern")
            raise e

    def _should_exclude_directory(self, exclude_dir_paths: List[str], root: str) -> bool:
        """
        Check if the directory should be excluded
        based on the list of exclude directory paths.

        Args:
        - exclude_dir_paths (List[str]):
            A list of directory paths to exclude.
        - root (str):
            The root directory path.

        Returns:
        - bool: True if the directory should be excluded, otherwise False.

        Raises:
        - Exception: If there is an error checking if the directory should be excluded.
        """
        LOGGER.debug("Checking if '%s' should be excluded", root)
        try:
            return any(
                exclude_dir_path in helper.normalize_paths(root)
                for exclude_dir_path in exclude_dir_paths
            )
        except Exception as e:
            LOGGER.exception("Error checking if directory should be excluded")
            raise e

    def _should_exclude_directory_by_pattern(self, exclude_patterns: List[str], root: str) -> bool:
        """Check if the directory should be excluded based on the list of exclude patterns."""
        LOGGER.debug("Check if '%s' should be excluded by pattern", root)
        try:
            return any(
                re.search(pattern, helper.normalize_paths(root)) for pattern in exclude_patterns
            )
        except Exception as e:
            LOGGER.exception("Error checking if directory should be excluded by pattern")
            raise e

    def _recursive_hash(
        self,
        cursor: sqlite3.Cursor,
        hash_dir_path: str,
        exclude_dir_paths: List[str],
        exclude_file_paths: List[str],
        exclude_patterns: List[str],
    ) -> None:
        """
        Recursively create hashes for files in a directory,
        then insert them into the database.

        Args:
        - cursor (sqlite3.Cursor):
            The database cursor.
        - hash_dir_path (str):
            The path of the directory to create the hash database from.
        - exclude_dir_paths (List[str]):
            A list of directory paths to exclude.
        - exclude_file_paths (List[str]):
            A list of file paths to exclude.
        - exclude_patterns (List[str]):
            A list of patterns to exclude.
        """
        # Batch size for parameterized queries
        max_time_per_batch = 3  # seconds
        batch_data = []

        start_time = time.time()  # Start timer
        for root, dirs, files in os.walk(hash_dir_path):
            # Skip excluded directories
            if self._should_exclude_directory(
                exclude_dir_paths, root
            ) or self._should_exclude_directory_by_pattern(exclude_patterns, root):
                LOGGER.debug("Skipping %s", root)
                dirs[:] = []  # Skip subdirectories
                continue

            # Get full file paths and filter out excluded files
            file_paths = helper.normalize_paths([os.path.join(root, file) for file in files])
            file_paths = self._exclude_files_by_path(file_paths, exclude_file_paths)
            file_paths = self._exclude_files_by_pattern(file_paths, exclude_patterns)

            results = self._pool_hashes(file_paths)
            batch_data.extend(results)

            elapsed_time = time.time() - start_time

            # If the max time per batch has been reached and there are files to be inserted
            if elapsed_time >= max_time_per_batch and batch_data:
                self._process_batch_data(cursor, batch_data)
                batch_data = []
                start_time = time.time()

        if batch_data:  # If there are any remaining files to be inserted
            self._process_batch_data(cursor, batch_data)

    def create_hash(self, file_path: str) -> str:
        """
        Create a hash from file bytes using the chunk method.

        Args:
        - file_path (str): The path of the file to be hashed.

        Returns:
        - str: The hash as a string.

        Raises:
        - HashingError: If there is an error hashing the file.
        """
        LOGGER.debug("Creating hash for '%s'", file_path)
        try:
            chunk_size = 4096
            file_size = os.path.getsize(file_path)

            if file_size > 1_000_000_000:  # If file size around 1 Gb or larger
                chunk_size = 8192

            LOGGER.debug("Chunk size: %d", chunk_size)
            LOGGER.debug("File size: %d", file_size)

            hasher = hashlib.sha256()

            with open(file_path, "rb") as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    hasher.update(chunk)

            file_hash = hasher.hexdigest()
            LOGGER.debug("Hash created for '%s'", file_path)

            return file_hash
        except Exception as error:
            LOGGER.exception("Error hashing '%s'", file_path)
            raise HashingError(f"Error hashing file '{file_path}'") from error

    def create_hash_db(
        self, hash_dir_path: str, db_save_path: str, exclude_paths=None, exclude_patterns=None
    ) -> str:
        """
        Create a hash database from a directory path,
        then save it to a file path. Return the save file path.

        Args:
        - hash_dir_path (str):
            The path of the directory to create the hash database from.
        - db_save_path (str):
            The path to save the hash database file.
        - exclude_paths (List[str]): optional
            A list of paths to exclude from the hash database creation. Default is an empty list.
            Defaults to None.
        - exclude_patterns (List[str]): optional
            A list of patterns to exclude from the hash database creation. Default is an empty list.
            Defaults to None.

        Returns:
        - str: The file path of the saved hash database.

        Raises:
        - Exception: If there is an error creating the hash database.
        """
        LOGGER.info("Creating hash database from directory: %s", hash_dir_path)

        if exclude_paths is None:
            exclude_paths = []

        if exclude_patterns is None:
            exclude_patterns = []

        LOGGER.debug("Excluding paths: %s", exclude_paths)
        LOGGER.debug("Excluding patterns: %s", exclude_patterns)

        if not os.path.exists(hash_dir_path):
            LOGGER.error("Directory '%s' does not exist", hash_dir_path)
            raise Exception(f"Directory '{hash_dir_path}' does not exist")

        # Set basename for relative file paths
        self._path_basename = os.path.basename(hash_dir_path)
        LOGGER.debug("Project name: %s", self._path_basename)

        if os.path.exists(db_save_path):
            try:
                os.remove(db_save_path)
                LOGGER.debug("Removed existing file '%s'", db_save_path)
            except Exception as error:
                LOGGER.exception("Error removing existing file '%s'", db_save_path)
                raise Exception(f"Error removing existing file '{db_save_path}'") from error

        # separate files and directories from exclude_paths
        exclude_paths = helper.normalize_paths(exclude_paths)
        exclude_file_paths = [path for path in exclude_paths if os.path.isfile(path)]
        exclude_dir_paths = [path for path in exclude_paths if os.path.isdir(path)]

        # Configure database
        hash_db = HashDB(db_save_path)
        connection = hash_db.connection
        cursor = hash_db.cursor

        self._create_hashes_table(cursor)
        self._recursive_hash(
            cursor, hash_dir_path, exclude_dir_paths, exclude_file_paths, exclude_patterns
        )

        connection.commit()
        hash_db.close()
        LOGGER.info("Hash database created at '%s'", db_save_path)

        return db_save_path
