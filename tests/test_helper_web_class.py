import pytest
import requests
import logging
from pyupgrader.utilities.helper import Web
from unittest.mock import Mock, patch, mock_open
from tests.misc import mock_config_str, mock_config_dict

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def web():
    return Web("https://example.com")

def test_get_request(web):
    LOGGER.info("Testing test_get_request")
    url = "https://example.com/api"
    response_mock = Mock()
    response_mock.raise_for_status.return_value = None
    with patch("requests.get", return_value=response_mock) as mock_get:
        response = web.get_request(url)
        mock_get.assert_called_once_with(url)
        response_mock.raise_for_status.assert_called_once()
        assert response == response_mock

def test_get_request_connection_error(web):
    LOGGER.info("Testing test_get_request_connection_error")
    url = "https://example.com/api"
    with patch("requests.get", side_effect=requests.ConnectionError):
        with pytest.raises(requests.ConnectionError):
            web.get_request(url)

def test_get_config(web):
    LOGGER.info("Testing test_get_config")
    config_url = "https://example.com/config.yaml"
    response_mock = Mock()
    response_mock.text = mock_config_str
    with patch.object(web, "get_request", return_value=response_mock) as mock_get_request:
        config = web.get_config()
        mock_get_request.assert_called_once_with(config_url)
        assert config == mock_config_dict

def test_download(web):
    LOGGER.info("Testing test_download")
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

def test_download_hash_db(web):
    LOGGER.info("Testing test_download_hash_db")
    config = mock_config_dict
    save_path = "/path/to/save/hash.db"
    with patch.object(web, "get_config", return_value=config) as mock_get_config:
        with patch.object(web, "download") as mock_download:
            web.download_hash_db(save_path)
            mock_get_config.assert_called_once()
            mock_download.assert_called_once_with("https://example.com/hash.db", save_path)
