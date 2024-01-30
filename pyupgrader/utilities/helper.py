"""
This module contains utility functions and classes for PyUpgrader.

Functions:
- normalize_paths(paths: Union[str, List[str]]) -> List[str]

Classes:
- Config: Helper class for managing configuration files.
- Web: Class for managing web requests.
"""

from typing import List, Union
import yaml
import requests

def normalize_paths(paths: Union[str, List[str]]) -> Union[str, List[str]]:
    """
    Replace backslashes with forward slashes and remove trailing slashes 
    in a path or a list of paths.

    Args:
        paths (Union[str, List[str]]): A path or a list of paths.

    Returns:
        Union[str, List[str]]: The normalized path or list of paths.
        
    Raises:
        TypeError: If the input is not a string or a list of strings.
    """
    if isinstance(paths, str):
        return paths.replace('\\', '/').rstrip('/')
    if isinstance(paths, list):
        return [path.replace('\\', '/').rstrip('/') for path in paths]

    raise TypeError("Input must be a string or a list of strings")


class Config:
    """
    Config helper class

    Attributes:
    default_config_data: dict
        Default config data

    Methods:
    load_yaml(path: str) -> dict
        Load a yaml file at path
    loads_yaml(yaml_string: str) -> dict
        Load a yaml from a string
    write_yaml(path: str, data: dict) -> None
        Dump data to yaml file at path
    """
    def __init__(self):
        self.default_config_data = {
            'version': '1.0.0',
            'description': 'Built with PyUpgrader',
            'startup_path': '',
            'required_only': False,
            'cleanup': False,
            'hash_db': 'hash.db',
        }

    def load_yaml(self, path: str) -> dict:
        """
        Load a yaml file at path.

        Args:
        - path (str): The path to the yaml file.

        Returns:
        dict: The data loaded from the yaml file.
        """
        with open(path, 'r', encoding="utf-8") as config_file:
            data = yaml.safe_load(config_file)
            is_valid, error = self._valid_config(data)
            if not is_valid:
                raise ValueError(error)
            return data

    def loads_yaml(self, yaml_string: str) -> dict:
        """
        Load a yaml from a string.

        Args:
        - yaml_string (str): The yaml string to load.

        Returns:
        dict: The data loaded from the yaml string.
        """
        data = yaml.safe_load(yaml_string)
        is_valid, error = self._valid_config(data)
        if not is_valid:
            raise ValueError(error)
        return data

    def write_yaml(self, path: str, data: dict) -> None:
        """
        Dump data to yaml file at path.

        Args:
        - path (str): The path to the yaml file.
        - data (dict): The data to dump to the yaml file.
        """
        with open(path, 'w', encoding="utf-") as config_file:
            yaml.safe_dump(data, config_file)

    def _valid_config(self, config: dict) -> (bool, str):
        """
        Validate the config.

        Args:
        - config (dict): The config to validate.

        Returns:
        tuple: A tuple containing a boolean indicating if the config is valid 
        and a string describing the error if it is not valid.
        """
        error = ""
        is_valid = True

        if 'version' not in config:
            error = 'Missing "version" attribute'
            is_valid = False
        elif 'description' not in config:
            error = 'Missing "description" attribute'
            is_valid = False
        elif 'hash_db' not in config:
            error = 'Missing "hash_db" attribute'
            is_valid = False
        elif 'startup_path' not in config:
            error = 'Missing "startup_path" attribute'
            is_valid = False
        elif 'required_only' not in config:
            error = 'Missing "required_only" attribute'
            is_valid = False
        elif 'cleanup' not in config:
            error = 'Missing "cleanup" attribute'
            is_valid = False

        return is_valid, error


class Web:
    """
    Class for managing web requests
    
    Attributes:
    url: str
        URL to the .pyupgrader folder
    
    Methods:
    get_request(url: str) -> requests.Response
        Get a request from the url
    get_config() -> dict
        Get the config file from the url
    download(url_path: str, save_path) -> str
        Download a file from the url_path and save it to save_path
    download_hash_db(save_path: str) -> str
        Download the hash database and save it to save_path
    """
    def __init__(self, url: str):
        self._url = url
        self._config_url = self._url + '/config.yaml'
        self._config_man = Config()

    def get_request(self, url: str, timeout: int = 5) -> requests.Response:
        """
        Get a request from the specified URL.
        
        Parameters:
        - url (str): URL to send the request to
        
        Returns:
        - requests.Response: The response object from the request
        """
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
        except Exception as e:
            raise requests.ConnectionError(f'Url: "{url}" | {e}')

        return response

    def get_config(self) -> dict:
        """
        Get the config file from the URL.
        
        Returns:
        - dict: The parsed config file as a dictionary
        """
        response = self.get_request(self._config_url)
        return self._config_man.loads_yaml(response.text)

    def download(self, url_path: str, save_path: str) -> str:
        """
        Download a file from the specified URL path and save it to the specified save path.
        
        Args:
        - url_path (str): URL path of the file to download
        - save_path: Path to save the downloaded file
        
        Returns:
        - str: The save path of the downloaded file
        """
        response = self.get_request(url_path)

        with open(save_path, 'wb') as f:
            f.write(response.content)

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
        return self.download(self._url + '/' + config['hash_db'], save_path)
