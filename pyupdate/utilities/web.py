import requests
from pyupdate.utilities import helper


class GetRequestError(Exception):
    """Raised when there is an error sending a get request"""
    pass


class GitManager:
    """Class for managing web requests"""
    def __init__(self, url: str, branch: str):
        self._url = url
        self._branch = branch
        self._config_url = self._url + '/config.yaml'
        self._config_man = helper.Config()
    
    def get_request(self, url: str, params={}) -> requests.Response:
        """Get a request from the url"""
        if not params:
            params = {'ref': self._branch}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
        except Exception as e:
            raise GetRequestError(f'Url: "{url}" Parms: "{params}" | {e}')
    
    def get_config(self) -> dict:
        """Get the config file from the url"""
        response = self.get_request(self._config_url)
        return self._config_man.load_config(response.text)
