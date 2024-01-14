import os
import requests
import tempfile
import shutil
import pickle
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
    check_update() -> dict
        Compare cloud and local version and return a dict with the results
    db_sum() -> DBSummary
        Return a DBSummary object using the cloud and local hash databases
    
    # TODO Add new methods
    """
    def __init__(self, url: str, project_path: str):
        self._url = url.rstrip('/')  # Remove trailing slash
        self._project_path = project_path
        self._pyupdate_path = os.path.join(self._project_path, '.pyupdate')
        self._config_path = os.path.join(self._pyupdate_path, 'config.yaml')
        self._local_hash_db_path = None  # Set in _validate_attributes

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
        self._local_hash_db_path = None  # Set in _validate_attributes
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
        self._local_hash_db_path = os.path.join(self._pyupdate_path, config_data['hash_db'])
        self._web_man = helper.Web(self._url)

        if not os.path.exists(self._local_hash_db_path):
            raise FileNotFoundError(self._local_hash_db_path)

    def check_update(self) -> dict:
        """Compare cloud and local version and return a dict with the results"""
        web_config = self._web_man.get_config()
        local_config = self._config_man.load_yaml(self._config_path)

        web_version = Version(web_config['version'])
        local_version = Version(local_config['version'])

        if web_version > local_version:
            has_update, description = True, web_config['description']
        else:
            has_update, description = False, local_config['description']
        
        return {'has_update': has_update, 'description': description, 'web_version': str(web_version), 'local_version': str(local_version)}
    
    def db_sum(self) -> hashing.DBSummary:
        """Return a DBSummary object using the cloud and local hash databases"""
        tmp_path = ""
        try:
            tmp_path = tempfile.mkdtemp()
            cloud_hash_db_path = self._web_man.download_hash_db(os.path.join(tmp_path, 'cloud_hashes.db'))

            return hashing.compare_databases(self._local_hash_db_path, cloud_hash_db_path)
        except Exception as error:
            raise error
        finally:
            if os.path.exists(tmp_path):
                shutil.rmtree(tmp_path)
    
    def download_files(self, save_path: str = "", required: bool = False) -> str:
        """Download all files to save_path, if save_path is empty, create a temp folder, return the save_path"""
        db_temp_path = ""
        cloud_db = None
        try:
            db_temp_path = tempfile.mkdtemp()
            if not save_path:
                save_path = tempfile.mkdtemp()

            cloud_hash_db_path = self._web_man.download_hash_db(os.path.join(db_temp_path, 'cloud_hashes.db'))
            cloud_db = hashing.HashDB(cloud_hash_db_path)
            compare_db = self.db_sum()

            base_url = self._url.split(".pyupdate")[0]
            # Download all files in db and copy structure
            for file in cloud_db.get_file_paths():
                if required:
                    print('required')
                    if file not in compare_db.bad_files:
                        print('skipping' + file)
                        continue
                    if file not in compare_db.unique_files_cloud_db:
                        print('skipping' + file)
                        continue

                download_url = base_url + file

                # Create save path
                relative_path = os.path.dirname(file)
                save_folder = os.path.join(save_path, relative_path)
                os.makedirs(save_folder, exist_ok=True)
                save_file = os.path.join(save_folder, os.path.basename(file))

                self._web_man.download(download_url, save_file)
            
            return save_path

        except Exception as error:
            raise error
        finally:
            if cloud_db is not None:
                cloud_db.close()
            if os.path.exists(db_temp_path):
                shutil.rmtree(db_temp_path)
