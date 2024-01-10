import os
import requests
import tempfile
from pyupdate.utilities import helper, GitManager


class UpdateManager:
    """Class for managing updates for a program."""
    def __init__(self, url: str, branch: str, project_path: str):
        self.url = url
        self.branch = branch
        self.project_path = project_path
        self._pyupdate_path = os.path.join(self._project_path, '.pyupdate')
        self._config_path = os.path.join(self._pyupdate_path, 'config.yml')
        self._hash_db_path = None  # Set in _validate_attributes

        self._validate_attributes()

        self._config_man = helper.Config()
        self._git_man = GitManager(self.url, self.branch)
    
    def _validate_attributes(self):
        """Validate and set attributes of the class"""
        if not os.path.exists(self.project_path):
            raise FileNotFoundError(self.project_path)
        try:
            requests.get(self.url)
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError(self.url)
        if not os.path.exists(self._pyupdate_path):
            raise FileNotFoundError(self._pyupdate_path)
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(self.config_path)
        
        config_data = self._config_man.load_config(self.config_path)
        self._hash_db_path = os.path.join(self._pyupdate_path, config_data['hash_db'])

        if not os.path.exists(self.hash_db_path):
            raise FileNotFoundError(self.hash_db_path)

    def _create_program_folder(self):
        # do not use context manager
        # will have to manually delete folder
        pass

    def TEST_print_config(self):
        """Prints the config file"""
        return self._git_man.get_config()
