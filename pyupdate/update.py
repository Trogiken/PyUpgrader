import os
import requests
import tempfile

# TODO When class is initialized create program file folder


class UpdateManager:
    def __init__(self, url, project_path):
        if not os.path.exists(project_path):
            raise FileNotFoundError(project_path)
        try:
            requests.get(url)
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError(url)
        
        self.url = url
        self.project_path = project_path
