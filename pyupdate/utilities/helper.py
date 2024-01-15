"""
This module contains utility functions and classes for PyUpdate.

Functions:
- normalize_paths(paths: Union[str, List[str]]) -> List[str]: Replace backslashes with forward slashes in a path or a list of paths.

Classes:
- Config: Helper class for managing configuration files.
- Web: Class for managing web requests.
"""

import os
import yaml
import requests
from typing import List, Union


def normalize_paths(paths: Union[str, List[str]]) -> List[str]:
    """
    Replace backslashes with forward slashes in a path or a list of paths.

    Args:
        paths (Union[str, List[str]]): A path or a list of paths.

    Returns:
        List[str]: A list of paths with backslashes replaced by forward slashes.

    Raises:
        TypeError: If the input is not a string or a list of strings.
    """
    if isinstance(paths, str):
        return paths.replace('\\', '/')
    elif isinstance(paths, list):
        return [path.replace('\\', '/') for path in paths]
    else:
        raise TypeError("Input must be a string or a list of strings")


class Config:
    """
    Config helper class

    Attributes:
    default_config_path: str
        Path to the default config file
    comments_path: str
        Path to the comments file

    Methods:
    load_comments() -> dict
        Load the comments from the comments.yml file
    load_yaml(path: str) -> dict
        Load a yaml file at path
    loads_yaml(yaml_string: str) -> dict
        Load a yaml from a string
    write_yaml(path: str, data: dict) -> None
        Dump data to yaml file at path
    display_info() -> None
        Display config values and comments
    """

    def __init__(self):
        """
        Initialize the Config object.

        Sets the default_config_path and comments_path attributes.
        """
        self.default_config_path = os.path.join(os.path.dirname(__file__), 'default.yml')
        self.comments_path = os.path.join(os.path.dirname(__file__), 'comments.yml')

    def load_comments(self) -> dict:
        """
        Load the comments from the comments.yml file.

        Returns:
        dict: The comments loaded from the file.
        """
        with open(self.comments_path, 'r') as comments_file:
            data = yaml.safe_load(comments_file)
            is_valid, error = self._valid_config(data)
            if not is_valid:
                raise ValueError(error)
            return data

    def load_yaml(self, path: str) -> dict:
        """
        Load a yaml file at path.

        Args:
        - path (str): The path to the yaml file.

        Returns:
        dict: The data loaded from the yaml file.
        """
        with open(path, 'r') as config_file:
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
        with open(path, 'w') as config_file:
            yaml.safe_dump(data, config_file)

    def display_info(self) -> None:
        """
        Display config values and comments.

        Prints the config values and their corresponding comments.
        """
        comments = self.load_comments()
        config = self.load_yaml(self.default_config_path)

        header = "Config Information"
        print(f"""\n\t{header}\n\t{'-' * len(header)}\n\tAttributes marked as Dynamic can be changed by the user\n""")

        misc_comments = {}

        # Display config values and comments
        for key, value in config.items():
            print(f"{key}: {value}")
            if key in comments:
                print(f"  Comments: {comments[key]}")
            else:
                misc_comments[key] = comments.get(key, "")
            print()

        # Display misc comments
        if misc_comments:
            print("Misc Comments:")
            for key, value in misc_comments.items():
                print(f"{key}: {value}\n")
    
    def _valid_config(self, config: dict) -> (bool, str):
        """
        Validate the config.

        Args:
        - config (dict): The config to validate.

        Returns:
        tuple: A tuple containing a boolean indicating if the config is valid and a string describing the error if it is not valid.
        """
        if 'version' not in config:
            return False, 'Missing "version" attribute'
        if 'description' not in config:
            return False, 'Missing "description" attribute'
        if 'hash_db' not in config:
            return False, 'Missing "hash_db" attribute'
        if 'update_path' not in config:
            return False, 'Missing "update_path" attribute'

        return True, ""


class Web:
    """
    Class for managing web requests
    
    Attributes:
    url: str
        URL to the .pyupdate folder
    
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
        """
        Initialize the Web class with the provided URL.
        
        Args:
        - url (str): URL to the .pyupdate folder
        """
        self._url = url
        self._config_url = self._url + '/config.yaml'
        self._config_man = Config()
    
    def get_request(self, url: str) -> requests.Response:
        """
        Get a request from the specified URL.
        
        Parameters:
        - url (str): URL to send the request to
        
        Returns:
        - requests.Response: The response object from the request
        """
        try:
            response = requests.get(url)
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
    
    def download(self, url_path: str, save_path) -> str:
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
