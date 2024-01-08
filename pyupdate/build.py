"""Builds a project into a pyupdate project"""

import os
import yaml
import shutil
import pyupdate.hashing as hashing


class BuildError(Exception):
    """Raised when there is an error building a project"""
    pass


class FolderCreationError(Exception):
    """Raised when there is an error creating a folder"""
    pass


class ConfigError(Exception):
    """Raised when there is an error with the config file"""
    pass


class HashDBError(Exception):
    """Raised when there is an error with the hash database"""
    pass


class PathError(Exception):
    """Raised when there is an error with a path"""
    pass


class Builder:
    """Builds a project into a pyupdate project"""
    def __init__(self):
        self.folder_path = None
        self.exclude_paths = None

        self._pyudpdate_folder = None
        self._config_path = None
        self._hash_db_path = None

        self.default_config_data = """\
# Config file for pyupdate, attributes marked with a * are changable by the user

# The version of the project, uses the packing.version module *
version: 0.0.0

# Description of the current version of the project *
description: "Description of the project"

# Name of the hash database file
hash_db_name: hashes.db
"""

    def build(self):
        """Builds a project into a pyupdate project"""
        self._validate_paths()

        print('Building project...')

        try:
            self._create_pyupdate_folder()
        except Exception as error:
            raise FolderCreationError(f'Failed to create .pyupdate folder | {error}')
        
        try:
            self._create_config_file()
        except Exception as error:
            raise ConfigError(f'Failed to create config file | {error}')
        
        try:
            self._create_hash_db()
        except Exception as error:
            raise HashDBError(f'Failed to create hash database | {error}')

        print('Done!')
        print(f'Project built at "{self._pyudpdate_folder}"')
    
    def _validate_paths(self):
        """Validates and set paths"""
        if self.folder_path is None:
            raise BuildError('Folder path not set')
        if self.exclude_paths is None:
            raise BuildError('Exclude paths not set')

        if not os.path.exists(self.folder_path):
            raise FileNotFoundError(f'Folder "{self.folder_path}" does not exist')
        if self.folder_path in self.exclude_paths:
            raise PathError(f'Folder path cannot be excluded')
        
        # Remove trailing slashes
        if self.folder_path.endswith('/'):
            self.folder_path = self.folder_path[:-1]
        if self.folder_path.endswith('\\'):
            self.folder_path = self.folder_path[:-1]
        for i, path in enumerate(self.exclude_paths):
            if path.endswith('/'):
                self.exclude_paths[i] = path[:-1]
            if path.endswith('\\'):
                self.exclude_paths[i] = path[:-1]
        
        self._pyudpdate_folder = os.path.join(self.folder_path, '.pyupdate')
        self._config_path = os.path.join(self._pyudpdate_folder, 'config.yaml')
        self._hash_db_path = os.path.join(self._pyudpdate_folder, 'hashes.db')
    
    def _create_pyupdate_folder(self):
        """Creates the .pyupdate folder"""
        if os.path.exists(self._pyudpdate_folder):
            print(f'Folder "{self._pyudpdate_folder}" already exists')
            print('Deleting folder')
            shutil.rmtree(self._pyudpdate_folder)

        print(f'Creating folder at "{self._pyudpdate_folder}"')
        os.mkdir(self._pyudpdate_folder)
    
    def _create_config_file(self):
        """Creates the config file"""
        print(f'Creating config file at "{self._config_path}"')
        with open(self._config_path, 'w') as f:
            f.write(self.default_config_data)
        
        # Validate yaml file by loading it
        with open(self._config_path, 'r') as f:
            data = yaml.safe_load(f)

            if 'version' not in data:
                raise ConfigError('Missing "version" attribute')
            if 'description' not in data:
                raise ConfigError('Missing "description" attribute')
            if 'hash_db_name' not in data:
                raise ConfigError('Missing "hash_db_name" attribute')
    
    def _create_hash_db(self):
        """Creates the hash database"""
        print(f'Creating hash database at "{self._hash_db_path}"')
        excluded_paths = [".pyupdate"] + self.exclude_paths
        hashing.create_hash_db(self.folder_path, self._hash_db_path, excluded_paths)
