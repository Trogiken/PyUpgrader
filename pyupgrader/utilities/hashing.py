"""
Hasher module for PyUpgrader.

This module provides classes and functions for hashing files, creating hash databases, 
and comparing hash databases.

Modified version of:
https://github.com/Trogiken/random-projects/blob/master/python/tools/DataIntegrityChecker/SCRIPT.py

Classes:
- DBSummary: Dataclass for database summary.
- HashDB: A class that provides methods to interact with a hash database.
- Hasher: A class that provides methods for hashing files and creating hash databases.

Functions:
- compare_databases(local_db_path: str, cloud_db_path: str) -> DBSummary

Exceptions:
- HashingError: Exception raised for errors in the hashing process.
"""

import hashlib
import os
import sqlite3
import time
import re
from typing import List
from multiprocessing import Pool
from dataclasses import dataclass
from pyupgrader.utilities import helper


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


def compare_databases(local_db_path: str, cloud_db_path: str) -> DBSummary:
    """
    Compare two hash databases and return a summary of the differences.

    - local_db_path (str): The file path of the local hash database.
    - cloud_db_path (str): The file path of the cloud hash database.

    Returns:
        DBSummary: An object containing the summary of the differences between the two databases.
    """
    connection1 = sqlite3.connect(local_db_path)
    cursor1 = connection1.cursor()

    connection2 = sqlite3.connect(cloud_db_path)
    cursor2 = connection2.cursor()

    cursor1.execute('SELECT file_path, calculated_hash FROM hashes')
    local_db_files = {row[0]: row[1] for row in cursor1.fetchall()}

    cursor2.execute('SELECT file_path, calculated_hash FROM hashes')
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
        bad_files=bad_files
    )


class HashDB:
    """
    A class that provides methods to interact with a hash database.

    Attributes:
        db_path (str): The path to the hash database.

    Methods:
        get_file_paths() -> str: Generator that yields file paths from the database.
        get_file_hash(file_path: str) -> str: Returns the hash of a file in the database.
        open() -> None: Opens the database connection.
        close() -> None: Closes the database connection.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.open()

    def get_file_paths(self) -> str:
        """
        Generator that yields file paths from the database.
        """
        self.cursor.execute('SELECT file_path FROM hashes')
        for row in self.cursor.fetchall():
            yield row[0]

    def get_file_hash(self, file_path: str) -> str:
        """
        Returns the hash of a file in the database.

        Args:
        - file_path (str): The path of the file.

        Returns:
        - str: The hash of the file.
        """
        self.cursor.execute('SELECT calculated_hash FROM hashes WHERE file_path = ?', (file_path,))
        return self.cursor.fetchone()[0]

    def open(self) -> None:
        """
        Opens the database connection.
        """
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def close(self) -> None:
        """
        Closes the database connection.
        """
        self.connection.close()
        self.connection = None
        self.cursor = None


class Hasher:
    """
    A class that provides methods for hashing files and creating hash databases.

    Attributes:
    - project_name: str
        The name of the project directory (Not the full path)

    Methods:
    - create_hash(self, file_path: str) -> (str, str):
        Creates a hash from file bytes using the chunk method.
        Returns the relative file path and hash as a string.
    - create_hash_db(self, hash_dir_path: str, db_save_path: str,
                    exclude_paths=[], exclude_patterns=[]
                    ) -> str:
        Creates a hash database from a directory path and saves it to a file path.
        Returns the file path.
    """

    def __init__(self, project_name: str):
        self.project_name = project_name

    def _create_hashes_table(self, cursor: sqlite3.Cursor) -> None:
        """
        Create the 'hashes' table in the database if it does not exist.

        Args:
        - cursor: sqlite3.Cursor
            The database cursor.
        """
        cursor.execute('CREATE TABLE IF NOT EXISTS hashes '
                       '(file_path TEXT PRIMARY KEY, calculated_hash TEXT)')

    def _process_batch_data(self, cursor: sqlite3.Cursor, batch_data: List[tuple]) -> None:
        """
        Insert batch data into the 'hashes' table.

        Args:
        - cursor: sqlite3.Cursor
            The database cursor.
        - batch_data: List[tuple]
            A list of tuples containing the relative file path and hash as a string.
        """
        cursor.executemany('INSERT OR REPLACE INTO hashes '
                           '(file_path, calculated_hash) VALUES (?, ?)', batch_data
                        )

    def _map_hashes_creation(self, pool: Pool, file_paths: List[str]) -> List[tuple]:
        """
        Use multiprocessing to create hashes for a list of file paths.

        Args:
        - pool: Pool
            The multiprocessing pool.
        - file_paths: List[str]
            A list of file paths to create hashes for.
        
        Returns:
        - List[tuple]: A list of tuples containing the relative file path and hash as a string.
        """
        return pool.map(self.create_hash, file_paths)

    def _exclude_files_by_path(self,
                               file_paths: List[str],
                               exclude_file_paths: List[str]
                               ) -> List[str]:
        """
        Exclude specified file paths from the list.

        Args:
        - file_paths: List[str]
            A list of file paths to filter.
        - exclude_file_paths: List[str]
            A list of file paths to exclude.

        Returns:
        - List[str]: A list of file paths that do not match any of the exclude file paths.
        """
        return [
            path
            for path in file_paths
            if path not in exclude_file_paths
        ]

    def _exclude_files_by_pattern(self,
                                  file_paths: List[str],
                                  exclude_patterns: List[str]
                                  ) -> List[str]:
        """
        Exclude specified file paths from the list.

        Args:
        - file_paths: List[str]
            A list of file paths to filter.
        - exclude_patterns: List[str]
            A list of patterns to exclude.

        Returns:
        - List[str]: A list of file paths that do not match any of the exclude patterns.
        """
        return [
            path
            for path in file_paths
            if not any(re.search(pattern, path)
                       for pattern in exclude_patterns)
        ]

    def _should_exclude_directory(self,
                                  exclude_dir_paths: List[str],
                                  root: str
                                  ) -> bool:
        """
        Check if the directory should be excluded
        based on the list of exclude directory paths.

        Args:
        - exclude_dir_paths: List[str]
            A list of directory paths to exclude.
        - root: str
            The root directory path.

        Returns:
        - bool: True if the directory should be excluded, otherwise False.
        """
        return any(
            exclude_dir_path in helper.normalize_paths(root)
            for exclude_dir_path in exclude_dir_paths
        )

    def _should_exclude_directory_by_pattern(self,
                                             exclude_patterns: List[str],
                                             root: str
                                             ) -> bool:
        """Check if the directory should be excluded based on the list of exclude patterns."""
        return any(
            re.search(pattern, helper.normalize_paths(root))
            for pattern in exclude_patterns
        )

    def create_hash(self, file_path: str) -> (str, str):
        """
        Create a hash from file bytes using the chunk method, 
        return the relative file path and hash as a string.

        Args:
        - file_path: str
            The path of the file to be hashed.

        Returns:
        - Tuple[str, str]: The relative file path and hash as a string.
        
        Raises:
        - HashingError: If there is an error hashing the file.
        """
        try:
            chunk_size = 4096
            file_size = os.path.getsize(file_path)

            if file_size > 1_000_000_000:  # If file size around 1 Gb or larger
                chunk_size = 8192

            hasher = hashlib.sha256()

            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    hasher.update(chunk)

            relative_file_path = (
                helper.normalize_paths(file_path.split(self.project_name)[-1])
                .lstrip("/")
            )
            file_hash = hasher.hexdigest()

            return relative_file_path, file_hash
        except Exception as error:
            raise HashingError(f"Error hashing file '{file_path}'") from error

    def create_hash_db(self,
                       hash_dir_path: str,
                       db_save_path: str,
                       exclude_paths=None,
                       exclude_patterns=None) -> str:
        """
        Create a hash database from a directory path,
        then save it to a file path. Return the save file path.

        Args:
        - hash_dir_path: str
            The path of the directory to create the hash database from.
        - db_save_path: str
            The path to save the hash database file.
        - exclude_paths: List[str], optional
            A list of paths to exclude from the hash database creation. Default is an empty list.
        - exclude_patterns: List[str], optional
            A list of patterns to exclude from the hash database creation. Default is an empty list.

        Returns:
        - str: The file path of the saved hash database.
        """
        if exclude_paths is None:
            exclude_paths = []

        if exclude_patterns is None:
            exclude_patterns = []

        if os.path.exists(db_save_path):
            os.remove(db_save_path)

        # separate files and directories from exclude_paths
        exclude_paths = helper.normalize_paths(exclude_paths)
        exclude_file_paths = [path for path in exclude_paths if os.path.isfile(path)]
        exclude_dir_paths = [path for path in exclude_paths if os.path.isdir(path)]

        # Configure database
        connection = sqlite3.connect(db_save_path)
        cursor = connection.cursor()
        self._create_hashes_table(cursor)

        # Batch size for parameterized queries
        max_time_per_batch = 3  # seconds
        batch_data = []

        # Create a pool, default number of processes is the number of cores on the machine
        with Pool() as pool:
            start_time = time.time()  # Start timer
            for root, dirs, files in os.walk(hash_dir_path):
                # Skip excluded directories
                if self._should_exclude_directory(exclude_dir_paths, root):
                    dirs[:] = []  # Skip subdirectories
                    continue
                if self._should_exclude_directory_by_pattern(exclude_patterns, root):
                    dirs[:] = []  # Skip subdirectories
                    continue

                # Get full file paths and filter out excluded files
                file_paths = helper.normalize_paths([os.path.join(root, file) for file in files])
                file_paths = self._exclude_files_by_path(file_paths, exclude_file_paths)
                file_paths = self._exclude_files_by_pattern(file_paths, exclude_patterns)

                results = self._map_hashes_creation(pool, file_paths)
                batch_data.extend(results)

                elapsed_time = time.time() - start_time

                # If the max time per batch has been reached and there are files to be inserted
                if elapsed_time >= max_time_per_batch and batch_data:
                    self._process_batch_data(cursor, batch_data)
                    batch_data = []
                    start_time = time.time()

            if batch_data:  # If there are any remaining files to be inserted
                self._process_batch_data(cursor, batch_data)

        connection.commit()
        connection.close()

        return db_save_path
