"""Builds a project into a pyupdate project"""

import os
import yaml
import shutil
import pyupdate.hashing as hashing


class BuildError(Exception):
    """Raised when there is an error building a project"""
    pass


class ConfigError(Exception):
    """Raised when there is an error with the config file"""
    pass


class HashDBError(Exception):
    """Raised when there is an error with the hash database"""
    pass


class Builder:
    """Builds a project into a pyupdate project"""
    def __init__(self, folder_path, exclude_paths=[]):
        self.folder_path = folder_path
        self.exclude_paths = exclude_paths
        self.pyudpdate_folder = os.path.join(folder_path, '.pyupdate')
        self.config_path = os.path.join(self.pyudpdate_folder, 'config.yaml')
        self.hash_db_path = os.path.join(self.pyudpdate_folder, 'hashes.db')

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
        if not os.path.exists(self.folder_path):
            raise FileNotFoundError(f'Folder "{self.folder_path}" does not exist')
        else:
            print(f'Building project from "{self.folder_path}"')
        
        try:
            self._create_pyupdate_folder()
        except Exception as error:
            raise BuildError(f'Failed to create .pyupdate folder | {error}')
        
        try:
            self._create_config_file()
        except Exception as error:
            raise ConfigError(f'Failed to create config file | {error}')
        
        try:
            self._create_hash_db()
        except Exception as error:
            raise HashDBError(f'Failed to create hash database | {error}')

        print('Done!')
        print(f'Project built at "{self.pyudpdate_folder}"')
    
    def _create_pyupdate_folder(self):
        """Creates the .pyupdate folder"""
        if os.path.exists(self.pyudpdate_folder):
            print(f'Folder "{self.pyudpdate_folder}" already exists')
            print('Deleting folder')
            shutil.rmtree(self.pyudpdate_folder)

        print(f'Creating folder at "{self.pyudpdate_folder}"')
        os.mkdir(self.pyudpdate_folder)
    
    def _create_config_file(self):
        """Creates the config file"""
        print(f'Creating config file at "{self.config_path}"')
        with open(self.config_path, 'w') as f:
            f.write(self.default_config_data)
        
        # Validate config file
        print(yaml.safe_load(self.config_path))
    
    def _create_hash_db(self):
        """Creates the hash database"""
        print(f'Creating hash database at "{self.hash_db_path}"')
        exclude_paths = [".pyupdate"] + self.exclude_paths
        hashing.create_hash_db(self.folder_path, self.hash_db_path, exclude_paths)
