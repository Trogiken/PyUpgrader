"""
This module provides the WebHandler class for handling web requests in PyUpgrader.

Functions:
- get_request(url: str, timeout: int = 5, **kwargs) -> requests.Response
    Get a request from the specified URL

Classes:
- DownloadThread: Class for downloading files asynchronously
- WebHandler: Handles web related requests

Exceptions:
- DBSumError: Raised when there is an error in comparing values from the databases
- GetFilesError: Raised when there is an error in retrieving file paths from the cloud
- DownloadFilesError: Raised when there is an error in downloading files from the cloud
"""

import os
import shutil
import tempfile
import logging
import threading
import queue
import requests
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor
from pyupgrader.utilities import helper, hashing

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class DBSumError(Exception):
    """This exception is raised when there is an error in comparing values from the databases."""


class GetFilesError(Exception):
    """This exception is raised when there is an error in retrieving file paths from the cloud."""


class DownloadFilesError(Exception):
    """This exception is raised when there is an error in downloading files from the cloud."""


def get_request(url: str, timeout: int = 5, **kwargs) -> requests.Response:
    """
    Get a request from the specified URL.

    Parameters:
    - url (str): URL to send the request to
    - timeout (int): The timeout for the request
    - **kwargs: Additional keyword arguments to pass to requests.get

    Returns:
    - requests.Response: The response object from the request

    Raises:
    - requests.ConnectionError: If the request fails
    """
    try:
        response = requests.get(url, timeout=timeout, **kwargs)
        response.raise_for_status()
    except Exception as e:
        LOGGER.exception("Failed to get request from '%s'", url)
        raise e

    return response


class DownloadThread(threading.Thread):
    """
    Class for downloading files asynchronously
    Use DownloadThread.start() to being the download

    Attributes:
    - url: str
        URL to the .pyupgrader folder
    - save_path: str
        Path to save the downloaded file
    - timeout: int
        Timeout for the request
    - chunk_size: int
        Size of the chunks to download

    Methods:
    - run() -> str
        Download a file from the specified URL path and save it to the specified save path
    """

    def __init__(self, url: str, save_path: str, timeout: int = 5, chunk_size: int = 8192):
        super().__init__()
        self._url = url
        self._save_path = save_path
        self._timeout = timeout
        self._chunk_size = chunk_size

        self.total_size: int = 0
        self.bytes_downloaded: int = 0
        self.percentage: float = 0

    def __str__(self) -> str:
        return f"Download Thread for {self._url}"

    def __repr__(self) -> str:
        return f"DownloadThread(url={self._url})"

    def run(self) -> str:
        """
        Download a file from the specified URL path and save it to the specified save path.

        Returns:
        - str: The save path of the downloaded file
        """
        LOGGER.debug("Downloading '%s' to '%s'", self._url, self._save_path)
        response = requests.get(self._url, timeout=5, stream=True)
        self.total_size = int(response.headers.get("content-length", 0))

        with open(self._save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=self._chunk_size):
                if chunk:
                    f.write(chunk)

        return self._save_path


# TODO: make a method that compiles the download percents and returns it
class WebHandler:
    """
    Class for handling web requests

    Attributes:
    - url: str
        URL to the .pyupgrader folder
    - local_db_path: str
        Path to the local hash database
    - _max_threads: int
        Maximum number of threads to use for downloading files

    Methods:
    - download(downloads: List[Tuple[str, str]] | Tuple) -> queue.Queue
        Download files from the specified URLs and save them to the specified paths
    - get_config() -> dict
        Get the config file data from the URL
    - download_hash_db(save_path: str) -> str
        Download the hash database and save it to the specified save path
    - get_db_sum() -> hashing.DBSummary
        Return a DBSummary object using the cloud and local hash databases
    - get_files(updated_only: bool = False) -> list
        Retrieves a list of files from the cloud database
    - download_cloud_files(save_path: str = "", updated_only: bool = False) -> str
        Download cloud files and return the path where the files are saved
    """

    def __init__(self, url: str, project_path: str, max_threads: int = 5):
        config_man = helper.Config()
        self.url = url
        self.project_path = project_path
        self.pyupgrader_path = os.path.join(self.project_path, ".pyupgrader")
        self.config_path = os.path.join(self.pyupgrader_path, "config.yaml")
        self.local_db_path = os.path.join(
            self.pyupgrader_path, config_man.load_yaml(self.config_path)["hash_db"]
        )
        self._max_threads = max_threads
        self._config_url = self.url + "/config.yaml"
        self._config_man = helper.Config()

        self.task_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=self._max_threads)

    def __str__(self) -> str:
        return f"Web Handler for {self.url}"

    def __repr__(self) -> str:
        return f"WebHandler(url={self.url})"

    def _start_downloads(self):
        """
        Start downloading files from the task queue.
        """
        while not self.task_queue.empty():
            # Limit the number of threads to avoid exceeding the maximum
            num_threads = min(self._max_threads, self.task_queue.qsize())
            # Submit download tasks to the executor
            for _ in range(num_threads):
                url, save_path = self.task_queue.get()
                download_thread = DownloadThread(url, save_path)
                self.executor.submit(download_thread.start)

    def download(self, downloads: List[Tuple[str, str]] | Tuple) -> queue.Queue:
        """
        Download files from the specified URLs and save them to the specified paths.

        Args:
        - downloads (List[Tuple[str, str]] | Tuple):
            List of tuples containing the URL and the save path,
            Or a single tuple containing the URL and the save path.
        """
        if isinstance(downloads, tuple):
            self.task_queue.put(downloads)
        elif isinstance(downloads, list):
            for download in downloads:
                self.task_queue.put(download)
        else:
            raise TypeError(f"Task must be a tuple or list, not {type(downloads)}")

        self._start_downloads()

        return self.task_queue

    def get_config(self) -> dict:
        """
        Get the config file from the URL.

        Returns:
        - dict: The parsed config file as a dictionary
        """
        LOGGER.debug("Getting config from '%s'", self._config_url)
        response = get_request(self._config_url)
        return self._config_man.loads_yaml(response.text)

    def download_hash_db(self, save_path: str) -> str:
        """
        Download the hash database and save it to the specified save path.

        Args:
        - save_path (str): Path to save the hash database file

        Returns:
        - str: The save path of the downloaded hash database file
        """
        config = self.get_config()
        db_name = config["hash_db"]
        LOGGER.debug("DB Name: '%s'", db_name)

        return self.download((self.url + "/" + db_name, save_path))

    def get_db_sum(self) -> hashing.DBSummary:
        """
        Return a DBSummary object using the cloud and local hash databases.

        Args:
        - local_db_path (str): The path to the local hash database.

        Returns:
        - hashing.DBSummary: A DBSummary object.
        """
        LOGGER.info("Creating DBSummary")
        try:
            db_tmp_path = ""
            try:
                db_tmp_path = tempfile.mkdtemp()
                cloud_hash_db_path = self.download_hash_db(
                    os.path.join(db_tmp_path, "cloud_hashes.db")
                )

                LOGGER.debug("DB Temp Dir Path: '%s'", self.local_db_path)
                LOGGER.debug("Cloud Hash DB Path: '%s'", cloud_hash_db_path)

                db_summary = hashing.compare_databases(self.local_db_path, cloud_hash_db_path)
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
            raise DBSumError("Error occurred while creating DBSummary") from e

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
                cloud_hash_db_path = self.download_hash_db(
                    os.path.join(db_tmp_path, "cloud_hashes.db")
                )

                LOGGER.debug("DB Temp Dir Path: '%s'", db_tmp_path)
                LOGGER.debug("Cloud Hash DB Path: '%s'", cloud_hash_db_path)

                if not os.path.exists(cloud_hash_db_path):
                    raise FileNotFoundError(cloud_hash_db_path)

                cloud_db = hashing.HashDB(cloud_hash_db_path)
                LOGGER.debug("Cloud DB Manager: '%s'", cloud_db)

                compare_db = self.get_db_sum()

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
            raise GetFilesError("Error occurred while retrieving files from cloud database") from e

    def download_cloud_files(self, save_path: str = "", updated_only: bool = False) -> str:
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

            base_url = self.url.split(".pyupgrader")[0]
            LOGGER.debug("Base Url: '%s'", base_url)

            # Download files while maintaining directory structure
            downloads = []
            for file_path in files_to_download:
                download_url = base_url + "/" + file_path
                LOGGER.debug("Download Url: '%s'", download_url)

                # Create save path
                relative_path = os.path.dirname(file_path)
                save_folder = os.path.join(save_path, relative_path)
                os.makedirs(save_folder, exist_ok=True)
                save_file = os.path.join(save_folder, os.path.basename(file_path))

                downloads.append((download_url, save_file))

            self.download(downloads)

            LOGGER.info("Files downloaded to %s", save_path)

            return save_path
        except Exception as e:
            LOGGER.exception("Error occurred while downloading files from cloud")
            raise DownloadFilesError("Error occurred while downloading files from cloud") from e
