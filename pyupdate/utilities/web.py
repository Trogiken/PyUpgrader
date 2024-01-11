import requests
from pyupdate.utilities import helper


class GetRequestError(Exception):
    """Raised when there is an error sending a get request"""
    pass


class GitManager:
    """Class for managing web requests"""
    def __init__(self, url: str):
        self._url = url
        self._config_url = self._url + '/config.yaml'
        self._config_man = helper.Config()
    
    def get_request(self, url: str) -> requests.Response:
        """Get a request from the url"""
        try:
            response = requests.get(url)
            response.raise_for_status()
        except Exception as e:
            raise GetRequestError(f'Url: "{url}" | {e}')
        return response
    
    def get_config(self) -> dict:
        """Get the config file from the url"""
        response = self.get_request(self._config_url)
        return self._config_man.loads_yaml(response.text)
