"""Builds a project into a pyupdate project"""

import os
import shutil
from pyupdate.utilities import helper, hashing


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
    """
    Builds a project into a pyupdate project

    Attributes:
    project_path: str
        Path to the project folder
    exclude_envs: bool
        Whether to exclude common virtual environment folders
    exclude_hidden: bool
        Whether to exclude hidden files and folders
    exclude_paths: list
        List of absolute paths to exclude from the hash database
    
    Methods:
    build() -> None
        Builds the project
    """
    def __init__(self, project_path: str, exclude_envs: bool = False, exclude_hidden: bool = False, exclude_paths: list = []):
        self.project_path = project_path
        self.exclude_envs = exclude_envs
        self.exclude_paths = exclude_paths
        self.exclude_hidden = exclude_hidden

        self.env_names = [
            '.venv',
            'venv',
            'env',
            '.env',
            '.virtualenv',
            'virtualenv',
            'conda',
            '.conda',
            'condaenv',
            '.condaenv',
            'pipenv',
            '.pipenv',
            'poetry',
            '.poetry',
            'pyenv',
            '.pyenv'
        ]

        self._pyudpdate_folder = None
        self._config_path = None
        self._hash_db_path = None

    def build(self):
        """Builds a project into a pyupdate project"""
        self._validate_paths()

        print('Building project...\n')

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

        print('\nDone!')
        print(f'Project built at "{self._pyudpdate_folder}"')
    
    def _validate_paths(self):
        """Validates and set paths"""
        if self.project_path is None:
            raise BuildError('Folder path not set')
        if self.exclude_paths is None:
            raise BuildError('Exclude paths not set')

        if not os.path.exists(self.project_path):
            raise FileNotFoundError(f'Folder "{self.project_path}" does not exist')
        if self.project_path in self.exclude_paths:
            raise PathError(f'Folder path cannot be excluded')
        
        # Remove trailing slashes
        if self.project_path.endswith('/'):
            self.project_path = self.project_path.rstrip('/')
        if self.project_path.endswith('\\'):
            self.project_path = self.project_path.rstrip('\\')
        for i, path in enumerate(self.exclude_paths):
            if path.endswith('/'):
                self.exclude_paths[i] = path.rstrip('/')
            if path.endswith('\\'):
                self.exclude_paths[i] = path.rstrip('\\')
        
        self._pyudpdate_folder = os.path.join(self.project_path, '.pyupdate')
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
        config = helper.Config()

        default_data = config.load_yaml(config.default_config_path)
        default_data['hash_db'] = os.path.basename(self._hash_db_path)
        config.write_yaml(self._config_path, default_data)
        
        try:
            config.load_yaml(self._config_path)
        except ValueError as error:
            raise ConfigError(f'Failed to validate config file | {error}')
    
    def _create_hash_db(self):
        """Creates the hash database"""
        print(f'Creating hash database at "{self._hash_db_path}"')
        hasher = hashing.Hasher(project_name=os.path.basename(self.project_path))

        excluded_paths = [self._pyudpdate_folder]
        if self.exclude_paths:
            excluded_paths += self.exclude_paths
        if self.exclude_envs:
            excluded_paths += [os.path.join(self.project_path, path) for path in self.env_names]
        if self.exclude_hidden:
            hasher.create_hash_db(self.project_path, self._hash_db_path, excluded_paths, [r'.*/\..*'])
        else:
            hasher.create_hash_db(self.project_path, self._hash_db_path, excluded_paths)
