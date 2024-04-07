"""
This module provides the WebHandler class for handling web requests in PyUpgrader.

Functions:
- get_request(url: str, timeout: int = 5, **kwargs) -> requests.Response
    Get a request from the specified URL

Classes:
- DownloadThread: Class for downloading files asynchronously
- WebHandler: Handles web related requests
"""

import logging
import threading
import requests
from pyupgrader.utilities import helper

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


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

    Methods:
    - get_request(url: str) -> requests.Response
        Get a request from the url
    - get_config() -> dict
        Get the config file from the url
    - download(url_path: str, save_path: str) -> str
        Download a file from the url_path and save it to save_path
    - download_hash_db(save_path: str) -> str
        Download the hash database and save it to save_path
    """

    def __init__(self, url: str):
        self._url = url
        self._config_url = self._url + "/config.yaml"
        self._config_man = helper.Config()

    def __str__(self) -> str:
        return f"Web Handler for {self._url}"

    def __repr__(self) -> str:
        return f"WebHandler(url={self._url})"

    @property
    def url(self) -> str:
        """
        URL to the .pyupgrader folder.
        """
        return self._url

    def get_config(self) -> dict:
        """
        Get the config file from the URL.

        Returns:
        - dict: The parsed config file as a dictionary
        """
        LOGGER.debug("Getting config from '%s'", self._config_url)
        response = get_request(self._config_url)
        return self._config_man.loads_yaml(response.text)

    def download(self, url_path: str, save_path: str) -> str:
        """
        Download a file from the specified URL path and save it to the specified save path.

        Args:
        - url_path (str): URL path of the file to download
        - save_path (str): Path to save the downloaded file

        Returns:
        - str: The save path of the downloaded file
        """
        LOGGER.debug("Downloading '%s' to '%s'", url_path, save_path)
        response = get_request(url_path, stream=True)

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return save_path

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

        return self.download(self._url + "/" + db_name, save_path)
