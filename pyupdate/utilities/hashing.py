"""
Hasher module for PyUpdate.

This module is a modified version of https://github.com/Trogiken/random-projects/blob/master/python/tools/DataIntegrityChecker/SCRIPT.py
"""

import hashlib
import os
import sqlite3
import sys
import time
from multiprocessing import Pool
from typing import Tuple


class Hasher:
    def __init__(self, project_name):
        self.project_name = project_name
    
    def get_relative_path(self, file_path: str) -> str:
        """Get the relative path of a file path."""
        proj_index = file_path.find(self.project_name)
        if proj_index != -1:
            relative_file_path = file_path[proj_index:]
        else:
            raise ValueError(f"Project name '{self.project_name}' not found in file path '{file_path}'")
        return relative_file_path

    def create_hash(self, file_path: str) -> Tuple[str, str]:
        """Create hash from file bytes using the chunk method, return hash as a string if found."""
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

            relative_file_path = self.get_relative_path(file_path)
            file_hash = hasher.hexdigest()
            
            return relative_file_path, file_hash
        except BaseException as error:
            return relative_file_path, '?'

    def create_hash_db(self, hash_dir_path: str, db_save_path: str, exclude_paths=[]) -> int:
        """Create a hash database from a directory path and save it to a file path. Return the file path and number of files hashed."""
        if os.path.exists(db_save_path):
            os.remove(db_save_path)

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
            for root, _, files in os.walk(hash_dir_path):
                if root in exclude_paths:
                    continue

                file_paths = [os.path.join(root, file) for file in files]
                if exclude_paths:
                    for path in exclude_paths:
                        if path in file_paths:
                            file_paths.remove(path)
                
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

        connection = sqlite3.connect(db_save_path)
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM hashes')
        num_files = cursor.fetchone()[0]
        connection.close()

        return db_save_path, num_files

    @staticmethod
    def compare_databases(db1_path: str, db2_path: str) -> dict:
        """Compare two hash databases and return a summary of the differences."""
        connection1 = sqlite3.connect(db1_path)
        cursor1 = connection1.cursor()

        connection2 = sqlite3.connect(db2_path)
        cursor2 = connection2.cursor()

        cursor1.execute('SELECT file_path, calculated_hash FROM hashes')
        db1_files = {row[0]: row[1] for row in cursor1.fetchall()}

        cursor2.execute('SELECT file_path, calculated_hash FROM hashes')
        db2_files = {row[0]: row[1] for row in cursor2.fetchall()}

        common_files = set(db1_files.keys()) & set(db2_files.keys())
        unique_files_db1 = set(db1_files.keys()) - set(db2_files.keys())
        unique_files_db2 = set(db2_files.keys()) - set(db1_files.keys())

        ok_files = [(file_path, db1_files[file_path]) for file_path in common_files if db1_files[file_path] == db2_files[file_path]]
        bad_files = [(file_path, db1_files[file_path], db2_files[file_path]) for file_path in common_files if db1_files[file_path] != db2_files[file_path]]
        unknown = [file_path for file_path in common_files if db1_files[file_path] == '?' or db2_files[file_path] == '?']

        sys.stdout.flush()
        connection1.close()
        connection2.close()

        summary = {
            'db1_path': db1_path,
            'db2_path': db2_path,

            'number_common_files': len(common_files),
            'number_unique_files_db1': len(unique_files_db1),
            'number_unique_files_db2': len(unique_files_db2),
            'number_ok_files': len(ok_files),
            'number_bad_files': len(bad_files),
            'number_unknown_files': len(unknown),
            'common_files': common_files,
            'unique_files_db1': unique_files_db1,
            'unique_files_db2': unique_files_db2,
            'ok_files': ok_files,
            'bad_files': bad_files,
            'unknown': unknown,
        }

        return summary