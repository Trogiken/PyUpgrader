import os
import yaml
from typing import Tuple


class Config:
    def __init__(self):
        self.default_config_path = os.path.join(os.path.dirname(__file__), 'default.yml')
        self.comments_path = os.path.join(os.path.dirname(__file__), 'comments.yml')

    def load_comments(self) -> dict:
        """Load the comments from the comments.yml file"""
        with open(self.comments_path, 'r') as comments_file:
            data = yaml.safe_load(comments_file)
            is_valid, error = self._valid_config(data)
            if not is_valid:
                raise ValueError(error)
            return data

    def load_config(self, path: str) -> dict:
        """Load a config file at path"""
        with open(path, 'r') as config_file:
            data = yaml.safe_load(config_file)
            is_valid, error = self._valid_config(data)
            if not is_valid:
                raise ValueError(error)
            return data
    
    def write_config(self, path: str, data: dict) -> None:
        """Dump data to yaml file at path"""
        with open(path, 'w') as config_file:
            yaml.safe_dump(data, config_file)

    def display_info(self) -> None:
        """Display config values and comments"""
        comments = self.load_comments()
        config = self.load_config(self.default_config_path)

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
                print(f"{key}: {value}")
                print()
    
    def _valid_config(self, config: dict) -> tuple(bool, str):
        """Validate the config"""
        if 'version' not in config:
            return False, 'Missing "version" attribute'
        if 'description' not in config:
            return False, 'Missing "description" attribute'
        if 'hash_db' not in config:
            return False, 'Missing "hash_db" attribute'
        if 'update_path' not in config:
            return False, 'Missing "update_path" attribute'

        return True, ""
