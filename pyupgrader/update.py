"""
This module provides the UpdateManager class for managing updates for a program.

Classes:
- UpdateManager: Manages updates for a program

Exceptions:
- DBSumError: Raised when there is an error in comparing values from the databases.
- GetFilesError: Raised when there is an error in retrieving file paths from the cloud.
- DownloadFilesError: Raised when there is an error in downloading files from the cloud.
- NoUpdateError: Raised when there is no files downloaded during an update.
- URLNotValidError: Raised when the URL is not valid.
"""

import os
import tempfile
import shutil
import pickle
import sys
import logging
import requests
from packaging.version import Version
from pyupgrader.utilities import helper, hashing

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class DBSumError(Exception):
    """This exception is raised when there is an error in comparing values from the databases."""


class GetFilesError(Exception):
    """This exception is raised when there is an error in retrieving file paths from the cloud."""


class DownloadFilesError(Exception):
    """This exception is raised when there is an error in downloading files from the cloud."""


class NoUpdateError(Exception):
    """This exception is raised when there is no files downloaded during an update."""


class URLNotValidError(Exception):
    """This exception is raised when the URL is not valid."""


class UpdateManager:
    """
    Class for managing updates for a program.

    Attributes:
    - url: str
        URL to the .pyupgrader folder
    - project_path: str
        Path to the project folder (Not the .pyupgrader folder)
    - config_path: str
        Path to the local config file
    - hash_db_path: str
        Path to the local hash database

    Methods:
    - check_update() -> dict
        Compare cloud and local version and return a dict with the results
    - db_sum() -> DBSummary
        Return a DBSummary object using the cloud and local hash databases
    - get_files(updated_only: bool = False) -> list
        Retrieves a list of files from the cloud database.
    - download_files(save_path: str = "", required: bool = False) -> str
        Download files to save_path, if save_path is empty, create a temp folder.
        Return the save_path
    - prepare_update(file_dir: str = "") -> str
        A 'actions' file will be created.
        This file is used by file_updater.py.
    - update(actions_path: str) -> None
        Start the application update process. This function will replace the current process.
    """

    def __init__(self, url: str, project_path: str):
        LOGGER.info("Initializing UpdateManager")
        try:
            self._url = url
            self._project_path = project_path
            self._pyupgrader_path = os.path.join(self._project_path, ".pyupgrader")
            self._config_path = os.path.join(self._pyupgrader_path, "config.yaml")
            self._local_hash_db_path = None  # Set in _validate_attributes

            self._config_man = helper.Config()
            self._web_man = None  # Set in _validate_attributes

            self._validate_attributes()
        except Exception as e:
            LOGGER.exception("Error occurred during initialization")
            raise e

    def __str__(self) -> str:
        return f"UpdateManager for {self._project_path} using {self._url}"

    def __repr__(self) -> str:
        return f"UpdateManager(url={self.url}, project_path={self.project_path})"

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
        - value (str): The URL to the .pyupgrader folder.
        """
        LOGGER.debug("Setting URL to: '%s'", value)
        try:
            self._url = value
            self._web_man = helper.Web(self._url)
            self._validate_attributes()
        except Exception as e:
            LOGGER.exception("Error occurred while setting URL")
            raise e

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
        - value (str): The path to the project folder.
        """
        LOGGER.debug("Setting project path to: '%s'", value)
        try:
            self._project_path = value
            self._pyupgrader_path = os.path.join(self._project_path, ".pyupgrader")
            self._config_path = os.path.join(self._pyupgrader_path, "config.yaml")
            self._local_hash_db_path = None  # Set in _validate_attributes
            self._validate_attributes()
        except Exception as e:
            LOGGER.exception("Error occurred while setting project path")
            raise e

    @property
    def config_path(self) -> str:
        """
        Get the path to the config file.

        Returns:
        - str: The path to the config file.
        """
        return self._config_path

    @property
    def hash_db_path(self) -> str:
        """
        Get the path to the local hash database.

        Returns:
        - str: The path to the local hash database.
        """
        return self._local_hash_db_path

    def _validate_attributes(self) -> None:
        """
        Validate and set attributes of the class.

        Raises:
        - FileNotFoundError: If the path does not exist.
        - URLNotValidError: If the URL is not valid.
        """
        LOGGER.info("Validating attributes")
        try:
            LOGGER.debug("Project Path: '%s'", self._project_path)
            LOGGER.debug("URL: '%s'", self._url)
            LOGGER.debug("PyUpgrader Path: '%s'", self._pyupgrader_path)
            LOGGER.debug("Config Path: '%s'", self._config_path)

            if not os.path.exists(self._project_path):
                raise FileNotFoundError(self._project_path)
            try:
                requests.get(self._url, timeout=5)
            except Exception as error:
                raise URLNotValidError(self._url) from error
            if not os.path.exists(self._pyupgrader_path):
                raise FileNotFoundError(self._pyupgrader_path)
            if not os.path.exists(self._config_path):
                raise FileNotFoundError(self._config_path)

            config_data = self._config_man.load_yaml(self._config_path)
            self._local_hash_db_path = os.path.join(self._pyupgrader_path, config_data["hash_db"])
            self._web_man = helper.Web(self._url)

            LOGGER.debug("Local Hash DB Path: '%s'", self._local_hash_db_path)
            LOGGER.debug("Web Manager: '%s'", self._web_man)

            if not os.path.exists(self._local_hash_db_path):
                raise FileNotFoundError(self._local_hash_db_path)
        except Exception as e:
            LOGGER.exception("Error occurred during attribute validation")
            raise e

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
        LOGGER.info("Checking for updates")
        try:
            web_config = self._web_man.get_config()
            local_config = self._config_man.load_yaml(self._config_path)

            web_version = Version(web_config["version"])
            local_version = Version(local_config["version"])

            LOGGER.debug("Web Version: '%s'", web_version)
            LOGGER.debug("Local Version: '%s'", local_version)

            if web_version > local_version:
                has_update, description = True, web_config["description"]
            else:
                has_update, description = False, local_config["description"]

            LOGGER.debug("Update Available: '%s'", has_update)
            LOGGER.debug("Update Description: '%s'", description)

            return {
                "has_update": has_update,
                "description": description,
                "web_version": str(web_version),
                "local_version": str(local_version),
            }
        except Exception as e:
            LOGGER.exception("Error occurred while checking for updates")
            raise e

    def db_sum(self) -> hashing.DBSummary:
        """
        Return a DBSummary object using the cloud and local hash databases.

        Returns:
        - hashing.DBSummary: A DBSummary object.
        """
        LOGGER.info("Creating DBSummary")
        try:
            db_tmp_path = ""
            try:
                db_tmp_path = tempfile.mkdtemp()
                cloud_hash_db_path = self._web_man.download_hash_db(
                    os.path.join(db_tmp_path, "cloud_hashes.db")
                )

                LOGGER.debug("DB Temp Dir Path: '%s'", self._local_hash_db_path)
                LOGGER.debug("Cloud Hash DB Path: '%s'", cloud_hash_db_path)

                db_summary = hashing.compare_databases(self._local_hash_db_path, cloud_hash_db_path)
                LOGGER.debug("DBSummary: '%s'", db_summary)

                return db_summary
            finally:
                if os.path.exists(db_tmp_path):
                    shutil.rmtree(db_tmp_path)
                    LOGGER.debug("Deleted '%s'", db_tmp_path)
                else:
                    LOGGER.warning("Tried deleting '%s' but did not exist", db_tmp_path)
        except Exception as e:
            LOGGER.exception("Error occurred while creating DBSummary")
            raise e

    def get_files(self, updated_only: bool = False) -> list:
        """
        Retrieves a list of files from the cloud database.
        Note that this function does not return files that have been deleted from the cloud.

        Args:
        - updated_only (bool): optional
            If True, only returns files that have been updated.
            Defaults to False.

        Returns:
        - list: A list of file paths.

        Raises:
        - GetFilesError: If an error occurs during the download process.
        """
        LOGGER.info("Retrieving files from cloud database")
        try:
            db_tmp_path = ""
            cloud_db = None
            try:
                db_tmp_path = tempfile.mkdtemp()
                cloud_hash_db_path = self._web_man.download_hash_db(
                    os.path.join(db_tmp_path, "cloud_hashes.db")
                )

                LOGGER.debug("DB Temp Dir Path: '%s'", db_tmp_path)
                LOGGER.debug("Cloud Hash DB Path: '%s'", cloud_hash_db_path)

                if not os.path.exists(cloud_hash_db_path):
                    raise FileNotFoundError(cloud_hash_db_path)

                cloud_db = hashing.HashDB(cloud_hash_db_path)
                LOGGER.debug("Cloud DB Manager: '%s'", cloud_db)

                compare_db = self.db_sum()

                files = None

                if updated_only:
                    bad_files = [path for path, _, _ in compare_db.bad_files]
                    files = compare_db.unique_files_cloud_db + bad_files
                else:
                    files = list(cloud_db.get_file_paths())

                LOGGER.debug("Files Retrieved: '%s'", files)

                return files
            finally:
                if isinstance(cloud_db, type(hashing.HashDB)):
                    cloud_db.close()
                else:
                    LOGGER.warning("Cloud DB is not a HashDB object")
                if db_tmp_path:
                    shutil.rmtree(db_tmp_path)
                    LOGGER.debug("Deleted '%s'", db_tmp_path)
                else:
                    LOGGER.warning("Tried deleting '%s' but did not exist", db_tmp_path)
        except Exception as e:
            LOGGER.exception("Error occurred while retrieving files from cloud database")
            raise e

    def download_files(self, save_path: str = "", updated_only: bool = False) -> str:
        """
        Download cloud files and return the path where the files are saved.

        Args:
        - save_path (str): optional
            The path to save the downloaded files.
            If not provided, a temporary folder will be created.
        - updated_only (bool): optional
            If True, only download files that have changed or have been added.

        Returns:
        - str: The path where the files are saved.

        Raises:
        - Exception: If an error occurs during the download process.
        """
        LOGGER.info("Downloading files from cloud")
        try:
            if not save_path:
                save_path = tempfile.mkdtemp()

            LOGGER.debug("Save Path: '%s'", save_path)

            files_to_download = None

            if updated_only:
                files_to_download = self.get_files(updated_only=True)
            else:
                files_to_download = self.get_files()

            base_url = self._url.split(".pyupgrader")[0]
            LOGGER.debug("Base Url: '%s'", base_url)

            # Download files while maintaining directory structure
            for file_path in files_to_download:
                download_url = base_url + "/" + file_path
                LOGGER.debug("Download Url: '%s'", download_url)

                # Create save path
                relative_path = os.path.dirname(file_path)
                save_folder = os.path.join(save_path, relative_path)
                os.makedirs(save_folder, exist_ok=True)
                save_file = os.path.join(save_folder, os.path.basename(file_path))

                self._web_man.download(download_url, save_file)

            LOGGER.info("Files downloaded to %s", save_path)

            return save_path
        except Exception as e:
            LOGGER.exception("Error occurred while downloading files from cloud")
            raise e

    def prepare_update(self, file_dir: str = "") -> str:
        """
        Start the application update process.
        A 'actions' file will be created.
        This file is used by file_updater.py.

        Args:
        - file_dir (str): optional
            The directory where temporary files will be stored.
            If not provided, a temporary directory will be created.

        Returns:
        - str: The path to the actions file.

        Raises:
        - NoUpdateError: If there are no files to update.
            Set 'required_only' to False in the cloud config to update anyway.
        """
        LOGGER.info("Preparing update")
        try:
            # init values
            cloud_config = self._web_man.get_config()
            db_summary = self.db_sum()
            download_files = False
            if not file_dir:
                file_dir = tempfile.mkdtemp()
                download_files = True

            LOGGER.debug("File Dir: '%s'", file_dir)
            LOGGER.debug("Download Files: '%s'", download_files)

            # Create temp folder in file_dir for holding update settings
            tmp_setting_dir = tempfile.mkdtemp(dir=file_dir)

            LOGGER.debug("Settings Directory: '%s'", tmp_setting_dir)

            # Populate settings folder
            cloud_config_path = os.path.join(tmp_setting_dir, "config.yaml")
            cloud_hash_db_path = os.path.join(tmp_setting_dir, "hashes.db")
            self._web_man.download_hash_db(cloud_hash_db_path)
            self._config_man.write_yaml(cloud_config_path, cloud_config)

            LOGGER.debug("Cloud Config Path: '%s'", cloud_config_path)
            LOGGER.debug("Cloud Hash DB Path: '%s'", cloud_hash_db_path)

            update_details = {
                "update": None,
                "delete": list(db_summary.unique_files_local_db),
                "project_path": self._project_path,
                "downloads_directory": file_dir,
                "startup_path": os.path.join(self._project_path, cloud_config["startup_path"]),
                "cloud_config_path": cloud_config_path,
                "cloud_hash_db_path": cloud_hash_db_path,
                "cleanup": cloud_config["cleanup"],
            }

            # Set the 'update' value and download files as needed
            if not cloud_config["required_only"]:
                if download_files:
                    self.download_files(file_dir, updated_only=False)
                update_details["update"] = self.get_files(updated_only=False)
            else:
                if download_files:
                    self.download_files(file_dir, updated_only=True)
                bad_files_paths = [file_path for file_path, _, _ in db_summary.bad_files]
                update_details["update"] = list(db_summary.unique_files_cloud_db) + bad_files_paths

            LOGGER.debug("Update Details: '%s'", update_details)

            # Check if there are no files to update and required_only is True
            if all(
                [
                    cloud_config["required_only"],
                    not update_details["update"],
                    not update_details["delete"],
                ]
            ):
                shutil.rmtree(file_dir)
                LOGGER.debug("Deleted '%s'", file_dir)
                raise NoUpdateError(
                    "No files to update. Set 'required_only' to 'false' for forced update."
                )

            # save actions to pickle file
            action_pkl = os.path.join(tmp_setting_dir, "actions.pkl")

            LOGGER.debug("Action File Path: '%s'", action_pkl)

            with open(action_pkl, "wb") as file:
                pickle.dump(update_details, file)

            LOGGER.info("Update prepared at %s", file_dir)

            return action_pkl
        except Exception as e:
            LOGGER.exception("Error occurred while preparing update")
            raise e

    def update(self, actions_path: str) -> None:
        """
        Start the application update process. This function will replace the current process.

        Args:
        - actions_path (str): The path to the actions file.

        Raises:
        - FileNotFoundError: If the actions file does not exist.
        """
        LOGGER.info("Starting update process")
        try:
            if not os.path.exists(actions_path):
                raise FileNotFoundError(actions_path)

            LOGGER.debug("Actions Path: '%s'", actions_path)

            updater_path = os.path.join(os.path.dirname(__file__), "utilities", "file_updater.py")

            LOGGER.debug("Updater Path: '%s'", updater_path)

            args = ["-a", actions_path]

            LOGGER.debug("Args: '%s'", args)

            os.execv(sys.executable, [sys.executable, updater_path] + args)
        except Exception as e:
            LOGGER.exception("Error occurred during update process")
            raise e
