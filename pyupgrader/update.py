"""
This module provides the UpdateManager class for managing updates for a program.

Classes:
- UpdateManager: Manages updates for a program

Exceptions:
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
from pyupgrader.utilities import helper, web

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


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
            self._web_man = web.WebHandler(self._url, self._project_path)
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
            self._web_man = web.WebHandler(self._url, self._project_path)

            LOGGER.debug("Local Hash DB Path: '%s'", self._local_hash_db_path)
            LOGGER.debug("Web Handler: '%s'", self._web_man)

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

    def prepare_update(self, file_dir: str) -> str:
        """
        Start the application update process.
        A 'actions' file will be created.
        This file is used by file_updater.py.

        Args:
        - file_dir (str):
            Directory that has contains the downloaded files

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
            db_summary = self._web_man.get_db_sum()

            LOGGER.debug("File Dir: '%s'", file_dir)

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

            # Set the 'update' value
            if not cloud_config["required_only"]:
                update_details["update"] = self._web_man.get_files(updated_only=False)
            else:
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
