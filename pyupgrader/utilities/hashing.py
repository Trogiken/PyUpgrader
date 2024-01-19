"""
Hasher module for PyUpgrader.

This module provides classes and functions for hashing files, creating hash databases, and comparing hash databases.
Modified version of https://github.com/Trogiken/random-projects/blob/master/python/tools/DataIntegrityChecker/SCRIPT.py

Classes:
- DBSummary: Dataclass for database summary.
- HashDB: A class that provides methods to interact with a hash database.
- Hasher: A class that provides methods for hashing files and creating hash databases.

Functions:
- compare_databases(local_db_path: str, cloud_db_path: str) -> DBSummary: Compare two hash databases and return a summary of the differences.

Exceptions:
- HashingError: Exception raised for errors in the hashing process.
"""

import hashlib
import os
import sqlite3
import time
import re
from multiprocessing import Pool
from dataclasses import dataclass
from pyupgrader.utilities import helper


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


class HashingError(Exception):
    """Exception raised for errors in the hashing process."""
    pass


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
        """
        Initializes a new instance of the HashDB class.

        Args:
        - db_path (str): The path to the hash database.
        """
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


class Hasher:
    """
    A class that provides methods for hashing files and creating hash databases.

    Attributes:
    - project_name: str
        The name of the project directory (Not the full path)

    Methods:
    - create_hash(self, file_path: str) -> (str, str): Creates a hash from file bytes using the chunk method and returns the relative file path and hash as a string.
    - create_hash_db(self, hash_dir_path: str, db_save_path: str, exclude_paths=[], exclude_patterns=[]) -> str: Creates a hash database from a directory path and saves it to a file path. Returns the file path.
    """

    def __init__(self, project_name: str):
        """
        Initialize the Hasher class.

        Args:
        - project_name: str
            The name of the project directory (Not the full path)
        """
        self.project_name = project_name

    def create_hash(self, file_path: str) -> (str, str):
        """
        Create a hash from file bytes using the chunk method and return the relative file path and hash as a string.

        Args:
        - file_path: str
            The path of the file to be hashed.

        Returns:
        - Tuple[str, str]: The relative file path and hash as a string.
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

            relative_file_path = file_path.split(self.project_name)[-1].lstrip('/')
            file_hash = hasher.hexdigest()

            return relative_file_path, file_hash
        except Exception as error:
            raise HashingError(f"Error hashing file '{file_path}' | {error}")

    def create_hash_db(self, hash_dir_path: str, db_save_path: str, exclude_paths=[], exclude_patterns=[]) -> str:
        """
        Create a hash database from a directory path and save it to a file path. Return the save file path.

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
        if os.path.exists(db_save_path):
            os.remove(db_save_path)

        exclude_paths = helper.normalize_paths(exclude_paths)

        # separate files and directories from exclude_paths
        exclude_file_paths = [path for path in exclude_paths if os.path.isfile(path)]
        exclude_dir_paths = [path for path in exclude_paths if os.path.isdir(path)]

        connection = sqlite3.connect(db_save_path)
        cursor = connection.cursor()

        # Create table for hashes
        cursor.execute('''CREATE TABLE IF NOT EXISTS hashes (
                            file_path TEXT PRIMARY KEY,
                            calculated_hash TEXT
                        )''')

        # Batch size for parameterized queries
        max_time_per_batch = 3  # seconds
        batch_data = []

        # Create a pool, default number of processes is the number of cores on the machine
        with Pool() as pool:
            start_time = time.time()  # Start timer

            for root, dirs, files in os.walk(hash_dir_path):
                if exclude_dir_paths:
                    # If the root directory is in the exclude directories
                    if any(exclude_dir_path in helper.normalize_paths(root) for exclude_dir_path in exclude_dir_paths):
                        dirs[:] = []  # Skip subdirectories
                        continue

                if exclude_patterns:
                    # if any directory in the root matches a pattern, skip it
                    if any(re.search(pattern, helper.normalize_paths(root)) for pattern in exclude_patterns):
                        dirs[:] = []  # Skip subdirectories
                        continue

                file_paths = helper.normalize_paths([os.path.join(root, file) for file in files])  # Get full file paths

                if exclude_file_paths:
                    for path in exclude_file_paths:
                        if path in file_paths:
                            file_paths.remove(path)

                if exclude_patterns:
                    # if any file in the root matches a pattern, skip it
                    file_paths = [
                        path
                        for path in file_paths
                        if not any(re.search(pattern, path) for pattern in exclude_patterns)
                    ]

                results = pool.map(self.create_hash, file_paths)  # Use workers to create hashes
                batch_data.extend(results)

                elapsed_time = time.time() - start_time
                if elapsed_time >= max_time_per_batch and batch_data:  # If the max time per batch has been reached and there are files to be inserted
                    cursor.executemany('INSERT OR REPLACE INTO hashes (file_path, calculated_hash) VALUES (?, ?)', batch_data)
                    batch_data = []
                    start_time = time.time()

            if batch_data:  # If there are any remaining files to be inserted
                cursor.executemany('INSERT OR REPLACE INTO hashes (file_path, calculated_hash) VALUES (?, ?)', batch_data)

        connection.commit()
        connection.close()

        return db_save_path
