import pytest
import requests
import logging
from pyupgrader.utilities.helper import Web, Config
from unittest.mock import Mock, patch, mock_open

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def web():
    """
    This function creates a Web object with the specified URL.

    Returns:
        Web: The created Web object.
    """
    return Web("https://example.com")

@pytest.fixture
def config():
    """
    This function creates a Config object with the specified config data.

    Returns:
        Config: The created Config object.
    """
    return Config()

def test_get_request(web):
    """
    Test the get_request method of the web class.

    This function tests the behavior of the get_request method by mocking the requests.get function
    and asserting that the expected calls are made.

    Args:
        web: An instance of the web class.
    """
    url = "https://example.com/api"
    response_mock = Mock()
    response_mock.raise_for_status.return_value = None
    with patch("requests.get", return_value=response_mock) as mock_get:
        response = web.get_request(url)
        mock_get.assert_called_once_with(url, timeout=5)
        response_mock.raise_for_status.assert_called_once()
        assert response == response_mock

def test_get_request_connection_error(web):
    """
    Test case for handling connection error during get request.

    This test case verifies that the web.get_request() method correctly handles a connection error
    when making a GET request to a specified URL.

    Steps:
    1. Mock the requests.get() method to raise a requests.ConnectionError.
    2. Call the web.get_request() method with a sample URL.
    3. Verify that a requests.ConnectionError is raised.
    """
    url = "https://example.com/api"
    with patch("requests.get", side_effect=requests.ConnectionError):
        with pytest.raises(requests.ConnectionError):
            web.get_request(url)

def test_get_config(web, config):
    """
    Test the get_config method of the web class.
    """
    config_url = "https://example.com/config.yaml"
    response_mock = Mock()
    response_mock.text = str(config.default_config_data)
    with patch.object(web, "get_request", return_value=response_mock) as mock_get_request:
        config_data = web.get_config()
        mock_get_request.assert_called_once_with(config_url)
        assert config_data == config.default_config_data

def test_download(web):
    """
    Test the download method of the web class.

    This function tests the download method of the web class by mocking the get_request method and the built-in open function.
    It verifies that the get_request method is called with the correct URL path and that the content of the response is written to the file.

    Args:
        web: An instance of the web class.
    """
    url_path = "https://example.com/file.txt"
    save_path = "/path/to/save/file.txt"
    response_mock = Mock()
    response_mock.content = b"File content"
    with patch.object(web, "get_request", return_value=response_mock) as mock_get_request:
        with patch("builtins.open", mock_open()) as mock_file:
            file_mock = mock_file.return_value
            web.download(url_path, save_path)
            mock_get_request.assert_called_once_with(url_path)
            file_mock.write.assert_called_once_with(response_mock.content)

def test_download_hash_db(web, config):
    """
    Test case for the download_hash_db method of the web helper class.
    
    This test verifies that the download_hash_db method correctly calls the get_config and download methods of the web helper class with the expected arguments.
    """
    save_path = "/path/to/save/hash.db"
    with patch.object(web, "get_config", return_value=config.default_config_data) as mock_get_config:
        with patch.object(web, "download") as mock_download:
            web.download_hash_db(save_path)
            mock_get_config.assert_called_once()
            mock_download.assert_called_once_with("https://example.com/hash.db", save_path)
