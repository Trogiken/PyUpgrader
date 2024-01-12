import os
import requests
import tempfile
import shutil
from packaging.version import Version
from pyupdate.utilities import helper, hashing


class UpdateManager:
    """
    Class for managing updates for a program.

    Attributes:
    url: str
        URL to the .pyupdate folder
    project_path: str
        Path to the project folder (Not the .pyupdate folder)
    
    Methods:
    check_update() -> (bool, str)
        Check if there is an update available.
        Return (bool, Description)
    """
    def __init__(self, url: str, project_path: str):
        self._url = url.rstrip('/')  # Remove trailing slash
        self._project_path = project_path
        self._pyupdate_path = os.path.join(self._project_path, '.pyupdate')
        self._config_path = os.path.join(self._pyupdate_path, 'config.yaml')
        self._hash_db_path = None  # Set in _validate_attributes

        self._config_man = helper.Config()
        self._web_man = None  # Set in _validate_attributes

        self._validate_attributes()

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str) -> None:
        self._url = value.rstrip('/')  # Remove trailing slash
        self._web_man = helper.Web(self._url)
        self._validate_attributes()

    @property
    def project_path(self) -> str:
        return self._project_path

    @project_path.setter
    def project_path(self, value) -> None:
        self._project_path = value
        self._pyupdate_path = os.path.join(self._project_path, '.pyupdate')
        self._config_path = os.path.join(self._pyupdate_path, 'config.yml')
        self._hash_db_path = None  # Set in _validate_attributes
        self._validate_attributes()
    
    def _validate_attributes(self) -> None:
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
        self._web_man = helper.Web(self._url)

        if not os.path.exists(self._hash_db_path):
            raise FileNotFoundError(self._hash_db_path)

    def check_update(self) -> (bool, str):
        """
        Compare cloud and local version
        Return (bool, Description)
        """
        web_config = self._web_man.get_config()
        local_config = self._config_man.load_yaml(self._config_path)

        web_version = Version(web_config['version'])
        local_version = Version(local_config['version'])

        if web_version > local_version:
            return (True, web_config['description'])
        else:
            return (False, local_config['description'])
    
    def test_update(self) -> None:
        """Test the update process"""
        #tmp = tempfile.mkdtemp()
        hasher = hashing.Hasher(self._project_path)

        #cloud_hash_db = self._web_man.download_hash_db(os.path.join(tmp, 'cloud_hashes.db'))
        local_hash_db = hasher.create_hash_db(self._project_path, os.path.join("C:/Users/Owner/Desktop", 'local_hashes.db'))

        #shutil.rmtree(tmp)
        #summary = hasher.compare_hash_dbs(local_hash_db, cloud_hash_db)
        #print(summary)
