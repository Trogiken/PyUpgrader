"""This module provides the UpdateManager class for managing updates for a program."""

import os
import requests
import tempfile
import shutil
import pickle
import subprocess
import sys
from packaging.version import Version
from pyupgrader.utilities import helper, hashing


class DBSumError(Exception):
    """This exception is raised when there is an error in comparing values from the databases."""
    pass


class GetFilesError(Exception):
    """This exception is raised when there is an error in retrieving file paths from the cloud."""
    pass


class DownloadFilesError(Exception):
    """This exception is raised when there is an error in downloading files from the cloud."""
    pass


class NoUpdateError(Exception):
    """This exception is raised when there is no files downloaded during an update."""
    pass


class UpdateManager:
    """
    Class for managing updates for a program.

    Attributes:
    - url: str
        URL to the .pyupgrader folder
    - project_path: str
        Path to the project folder (Not the .pyupgrader folder)
    
    Methods:
    - check_update() -> dict
        Compare cloud and local version and return a dict with the results
    - db_sum() -> DBSummary
        Return a DBSummary object using the cloud and local hash databases
    - get_files(updated_only: bool = False) -> list
        Retrieves a list of files from the cloud database.
    - download_files(save_path: str = "", required: bool = False) -> str
        Download files to save_path, if save_path is empty, create a temp folder, return the save_path
    - update(file_dir: str = "") -> str
        Start the application update process.
    """

    def __init__(self, url: str, project_path: str):
        """
        Initialize the UpdateManager class.

        Args:
        - url: str
            URL to the .pyupgrader folder
        - project_path: str
            Path to the project folder (Not the .pyupgrader folder)
        """
        self._url = url.rstrip('/')
        self._project_path = project_path.rstrip('/')
        self._pyupgrader_path = os.path.join(self._project_path, '.pyupgrader')
        self._config_path = os.path.join(self._pyupgrader_path, 'config.yaml')
        self._local_hash_db_path = None  # Set in _validate_attributes

        self._config_man = helper.Config()
        self._web_man = None  # Set in _validate_attributes

        self._validate_attributes()

    @property
    def url(self) -> str:
        """
        Get the URL to the .pyupgrader folder.

        Returns:
        - str: The URL to the .pyupgrader folder.
        """
        return self._url

    @url.setter
    def url(self, value: str) -> None:
        """
        Set the URL to the .pyupgrader folder.

        Args:
        - value: str
            The URL to the .pyupgrader folder.
        """
        self._url = value.rstrip('/')  # Remove trailing slash
        self._web_man = helper.Web(self._url)
        self._validate_attributes()

    @property
    def project_path(self) -> str:
        """
        Get the path to the project folder (Not the .pyupgrader folder).

        Returns:
        - str: The path to the project folder.
        """
        return self._project_path

    @project_path.setter
    def project_path(self, value) -> None:
        """
        Set the path to the project folder (Not the .pyupgrader folder).

        Args:
        - value: str
            The path to the project folder.
        """
        self._project_path = value
        self._pyupgrader_path = os.path.join(self._project_path, '.pyupgrader')
        self._config_path = os.path.join(self._pyupgrader_path, 'config.yaml')
        self._local_hash_db_path = None  # Set in _validate_attributes
        self._validate_attributes()
    
    def _validate_attributes(self) -> None:
        """
        Validate and set attributes of the class.
        """
        if not os.path.exists(self._project_path):
            raise FileNotFoundError(self._project_path)
        try:
            requests.get(self._url)
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError(self._url)
        if not os.path.exists(self._pyupgrader_path):
            raise FileNotFoundError(self._pyupgrader_path)
        if not os.path.exists(self._config_path):
            raise FileNotFoundError(self._config_path)
        
        config_data = self._config_man.load_yaml(self._config_path)
        self._local_hash_db_path = os.path.join(self._pyupgrader_path, config_data['hash_db'])
        self._web_man = helper.Web(self._url)

        if not os.path.exists(self._local_hash_db_path):
            raise FileNotFoundError(self._local_hash_db_path)

    def check_update(self) -> dict:
        """
        Compare cloud and local version and return a dict with the results.

        Returns:
        - dict: A dictionary with the following keys:
            - has_update (bool): True if there is an update available, False otherwise.
            - description (str): The description of the update.
            - web_version (str): The version number from the cloud.
            - local_version (str): The version number from the local configuration.
        """
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
        """
        Return a DBSummary object using the cloud and local hash databases.

        Returns:
        - hashing.DBSummary: A DBSummary object.
        """
        tmp_path = ""
        try:
            tmp_path = tempfile.mkdtemp()
            cloud_hash_db_path = self._web_man.download_hash_db(os.path.join(tmp_path, 'cloud_hashes.db'))

            return hashing.compare_databases(self._local_hash_db_path, cloud_hash_db_path)
        except Exception as error:
            raise DBSumError(error)
        finally:
            if os.path.exists(tmp_path):
                shutil.rmtree(tmp_path)
    
    def get_files(self, updated_only: bool = False) -> list:
        """
        Retrieves a list of files from the cloud database.
        Note that this function does not return files that have been deleted from the cloud.

        Args:
        - updated_only (bool, optional): If True, only returns files that have been updated. 
            Defaults to False.

        Returns:
        - list: A list of file paths.

        Raises:
        - Exception: If an error occurs during the retrieval process.
        """
        db_temp_path = ""
        cloud_db = None
        try:
            db_temp_path = tempfile.mkdtemp()

            cloud_hash_db_path = self._web_man.download_hash_db(os.path.join(db_temp_path, 'cloud_hashes.db'))
            cloud_db = hashing.HashDB(cloud_hash_db_path)
            compare_db = self.db_sum()

            files = None

            if updated_only:
                bad_files = [path for path, _, _ in compare_db.bad_files]
                files = compare_db.unique_files_cloud_db + bad_files
            else:
                files = [path for path in cloud_db.get_file_paths()]

            return files
        except Exception as error:
            raise GetFilesError(error)
        finally:
            if cloud_db is not None:
                cloud_db.close()
            if db_temp_path:
                shutil.rmtree(db_temp_path)
    
    def download_files(self, save_path: str = "", required: bool = False) -> str:
        """
        Download cloud files and return the path where the files are saved.

        Args:
        - save_path: str, optional
            The path to save the downloaded files. If not provided, a temporary folder will be created.
        - required: bool, optional
            If True, only download files that have changed or have been added.

        Returns:
        - str: The path where the files are saved.

        Raises:
        - Exception: If an error occurs during the download process.
        """
        try:
            if not save_path:
                save_path = tempfile.mkdtemp()
            
            files_to_download = None
            
            if required:
                files_to_download = self.get_files(updated_only=True)
            else:
                files_to_download = self.get_files()

            # Download all files in db and copy structure
            base_url = self._url.split(".pyupgrader")[0]
            for file_path in files_to_download:
                download_url = base_url + '/' + file_path

                # Create save path
                relative_path = os.path.dirname(file_path)
                save_folder = os.path.join(save_path, relative_path)
                os.makedirs(save_folder, exist_ok=True)
                save_file = os.path.join(save_folder, os.path.basename(file_path))

                self._web_man.download(download_url, save_file)
            
            return save_path
        except Exception as error:
            raise DownloadFilesError(error)
    
    def update(self, file_dir: str = "") -> str:
            """
            Start the application update process.
            A lock file will be created in the .pyupgrader folder.
            This file is used by file_updater.py to determine when to start updating.
            Remove the lock file to start the update process,
            main application should call sys.exit() immediately after removing the lock file.

            Args:
            - file_dir (str, optional):
                The directory where temporary files will be stored. If not provided, a temporary directory will be created.

            Returns:
            - str: The path to the lock file.

            Raises:
            - NoUpdateError: If there are no files to update. Set required_only to False in the cloud config to update anyway.
            """
            # init values
            cloud_config = self._web_man.get_config()
            db_summary = self.db_sum()
            download_files = False
            if not file_dir:
                file_dir = tempfile.mkdtemp()
                download_files = True

            # Create temp folder in file_dir for holding update settings
            tmp_setting_dir = tempfile.mkdtemp(dir=file_dir)
            cloud_config_path = os.path.join(tmp_setting_dir, 'config.yaml')
            cloud_hash_db_path = os.path.join(tmp_setting_dir, 'hashes.db')

            # Populate settings folder
            self._web_man.download_hash_db(cloud_hash_db_path)
            self._config_man.write_yaml(cloud_config_path, cloud_config)

            update_details = {
                'update': [],
                'delete': [file_path for file_path in db_summary.unique_files_local_db],
                'project_path': self._project_path,
                'startup_path': os.path.join(self._project_path, cloud_config['startup_path']),
                'cloud_config_path': cloud_config_path,
                'cloud_hash_db_path': cloud_hash_db_path,
            }

            # Set the 'update' value and download files as needed
            if not cloud_config['required_only']:
                if download_files:
                    self.download_files(file_dir, required=False)
                update_details['update'] = self.get_files(updated_only=False)
            else:
                if download_files:
                    self.download_files(file_dir, required=True)
                update_details['update'] = [file_path for file_path in db_summary.unique_files_cloud_db] + [file_path for file_path, _, _ in db_summary.bad_files]
            
            if cloud_config['required_only'] and not update_details['update'] and not update_details['delete']:
                shutil.rmtree(file_dir)
                raise NoUpdateError('No files to update. | If you wish to update anyway, set required_only to False in the cloud config.')

            # save actions to pickle file
            action_pkl = os.path.join(tmp_setting_dir, 'actions.pkl')
            with open(action_pkl, 'wb') as file:
                pickle.dump(update_details, file)
            
            # create lock file
            lock_file = os.path.join(self._pyupgrader_path, 'lock')
            with open(lock_file, 'w') as file:
                file.write('')
            
            # start file_updater.py using subprocessing
            command = [sys.executable, os.path.join(os.path.dirname(__file__), 'utilities', 'file_updater.py'), '-p', file_dir, '-a', action_pkl, '-l', lock_file]
            if cloud_config['cleanup']:
                command.append('-c')
            subprocess.Popen(command)

            return lock_file
