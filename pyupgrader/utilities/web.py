"""
This module provides the WebHandler class for handling web requests in PyUpgrader.

Classes:
- WebHandler: Handles web related requests
"""

import logging
import requests
from pyupgrader.utilities import helper

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


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

    def get_request(self, url: str, timeout: int = 5, **kwargs) -> requests.Response:
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

    def get_config(self) -> dict:
        """
        Get the config file from the URL.

        Returns:
        - dict: The parsed config file as a dictionary
        """
        LOGGER.debug("Getting config from '%s'", self._config_url)
        response = self.get_request(self._config_url)
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
        response = self.get_request(url_path, stream=True)

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
