import os
import requests
import tempfile
from packaging.version import Version
from pyupdate.utilities import helper, GitManager


class UpdateManager:
    """Class for managing updates for a program."""
    def __init__(self, url: str, project_path: str):
        self._url = url.rstrip('/')  # Remove trailing slash
        self._project_path = project_path
        self._pyupdate_path = os.path.join(self._project_path, '.pyupdate')
        self._config_path = os.path.join(self._pyupdate_path, 'config.yaml')
        self._hash_db_path = None  # Set in _validate_attributes

        self._config_man = helper.Config()
        self._git_man = None  # Set in _validate_attributes

        self._validate_attributes()

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value: str):
        self._url = value.rstrip('/')  # Remove trailing slash
        self._git_man = GitManager(self._url)
        self._validate_attributes()

    @property
    def project_path(self):
        return self._project_path

    @project_path.setter
    def project_path(self, value):
        self._project_path = value
        self._pyupdate_path = os.path.join(self._project_path, '.pyupdate')
        self._config_path = os.path.join(self._pyupdate_path, 'config.yml')
        self._hash_db_path = None  # Set in _validate_attributes
        self._validate_attributes()
    
    def _validate_attributes(self):
        """Validate and set attributes of the class"""
        if not os.path.exists(self._project_path):
            raise FileNotFoundError(self._project_path)
        try:
            requests.get(self._url)
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError(self._url)
        if not os.path.exists(self._pyupdate_path):
            raise FileNotFoundError(self._pyupdate_path)
        if not os.path.exists(self._config_path):
            raise FileNotFoundError(self._config_path)
        
        config_data = self._config_man.load_yaml(self._config_path)
        self._hash_db_path = os.path.join(self._pyupdate_path, config_data['hash_db'])
        self._git_man = GitManager(self._url)

        if not os.path.exists(self._hash_db_path):
            raise FileNotFoundError(self._hash_db_path)

    def _create_program_folder(self):
        # do not use context manager
        # will have to manually delete folder
        pass

    def check_update(self) -> (bool, str):
        """
        Compare cloud and local version
        Return (bool, Description)
        """
        git_config = self._git_man.get_config()
        local_config = self._config_man.load_yaml(self._config_path)

        git_version = Version(git_config['version'])
        local_version = Version(local_config['version'])

        if git_version > local_version:
            return (True, git_config['description'])
        else:
            return (False, local_config['description'])

