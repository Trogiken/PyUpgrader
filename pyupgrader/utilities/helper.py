"""
This module contains utility functions and classes for PyUpgrader.

Functions:
- normalize_paths(paths: Union[str, List[str]]) -> List[str]

Classes:
- Config: Helper class for managing configuration files.
"""

from typing import List, Tuple
import logging
import yaml

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def normalize_paths(paths: str | List[str]) -> str | List[str]:
    """
    Replace backslashes with forward slashes and remove trailing slashes
    in a path or a list of paths.

    Args:
    - paths (str | List[str]): The path or list of paths to normalize.

    Returns:
    - str | List[str]: The normalized path or list of paths.

    Raises:
    - TypeError: If the input is not a string or a list of strings.
    """
    if isinstance(paths, str):
        return paths.replace("\\", "/").rstrip("/")
    if isinstance(paths, list):
        return [path.replace("\\", "/").rstrip("/") for path in paths]

    raise TypeError("Input must be a string or a list of strings")


class Config:
    """
    Config helper class

    Attributes:
    - default_config_data: dict
        Default config data

    Methods:
    - load_yaml(path: str) -> dict
        Load a yaml file at path
    - loads_yaml(yaml_string: str) -> dict
        Load a yaml from a string
    - write_yaml(path: str, data: dict) -> None
        Dump data to yaml file at path
    """

    def __init__(self):
        self.default_config_data = {
            "version": "1.0.0",
            "description": "Built with PyUpgrader",
            "startup_path": "",
            "required_only": False,
            "cleanup": False,
            "hash_db": "hash.db",
        }

    def __str__(self) -> str:
        return "Config Helper"

    def __repr__(self) -> str:
        return "Config()"

    def load_yaml(self, path: str) -> dict:
        """
        Load a yaml file at path.

        Args:
        - path (str): The path to the yaml file.

        Returns:
        - dict: The data loaded from the yaml file.
        """
        LOGGER.debug("Loading yaml file at '%s'", path)
        with open(path, "r", encoding="utf-8") as config_file:
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
        - dict: The data loaded from the yaml string.
        """
        LOGGER.debug("Loading yaml from string")
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
        LOGGER.debug("Writing yaml file at '%s'", path)
        with open(path, "w", encoding="utf-") as config_file:
            yaml.safe_dump(data, config_file)

    def _valid_config(self, config: dict) -> Tuple[bool, str]:
        """
        Validate the config.

        Args:
        - config (dict): The config to validate.

        Returns:
        - tuple (Tuple[bool, str]):
            Boolean indicating if the config is valid.
            String describing the error if it is not valid.
        """
        LOGGER.debug("Validating config")
        error = ""
        is_valid = True

        if "version" not in config:
            error = 'Missing "version" attribute'
            is_valid = False
        elif "description" not in config:
            error = 'Missing "description" attribute'
            is_valid = False
        elif "hash_db" not in config:
            error = 'Missing "hash_db" attribute'
            is_valid = False
        elif "startup_path" not in config:
            error = 'Missing "startup_path" attribute'
            is_valid = False
        elif "required_only" not in config:
            error = 'Missing "required_only" attribute'
            is_valid = False
        elif "cleanup" not in config:
            error = 'Missing "cleanup" attribute'
            is_valid = False

        if not is_valid:
            LOGGER.warning("Invalid config: '%s'", error)
        else:
            LOGGER.debug("Config is valid")

        return is_valid, error
