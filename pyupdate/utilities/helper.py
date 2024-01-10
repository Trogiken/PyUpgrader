import yaml
import os


class Config:
    def __init__(self):
        self._config_path = os.path.join(os.path.dirname(__file__), 'default.yml')
        self._comments_path = os.path.join(os.path.dirname(__file__), 'comments.yml')

    def load_comments(self):
        with open(self._comments_path, 'r') as comments_file:
            return yaml.safe_load(comments_file)


    def load_config(self):
        with open(self._config_path, 'r') as config_file:
            return yaml.safe_load(config_file)


    def display_info(self):
        comments = self.load_comments()
        config = self.load_config()

        header = "Config Information"
        print(f"""\n\t{header}\n\t{'-' * len(header)}\n\tAttributes marked as Dynamic can be changed by the user""")

        for key, value in config.items():
            print(f"{key}: {value}")
            if key in comments:
                print(f"  Comments: {comments[key]}")
            print()
