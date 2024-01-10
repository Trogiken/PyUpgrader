import requests
from pyupdate.utilities import helper


class GitManager:
    """Class for managing web requests"""
    def __init__(self, url: str):
        self._url = url
        self._config_man = helper.Config()
    
    def get_request(self, url: str) -> requests.Response:
        """Get a request from the url"""
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.HTTPError(e)
        except requests.exceptions.ConnectionError as e:
            raise requests.exceptions.ConnectionError(e)
        except requests.exceptions.Timeout as e:
            raise requests.exceptions.Timeout(e)
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(e)
        return response
    
    def get_config(self) -> dict:
        """Get the config file from the url"""
        response = self.get_request(self._url)
        # TODO load this with the config manager and return as dict
        raise NotImplementedError
