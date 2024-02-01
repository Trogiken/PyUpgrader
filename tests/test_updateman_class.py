import os
import unittest
import logging
import pytest
import pickle
import shutil
from unittest.mock import Mock
from pyupgrader.update import UpdateManager
from pyupgrader.utilities.hashing import DBSummary
from pyupgrader.utilities.helper import Config, normalize_paths
from pyupgrader.update import NoUpdateError

LOGGER = logging.getLogger(__name__)


class TestUpdateManager(unittest.TestCase):
    def setUp(self):
        self.url = r"https://raw.githubusercontent.com/Trogiken/PyUpgrader/master/tests/TestingDirectory/.pyupgrader"
        self.project_path = normalize_paths(os.path.join(os.path.dirname(__file__), "TestingDirectory"))
        self.update_manager = UpdateManager(self.url, self.project_path)
        self.config = Config()

    def test_check_update(self):
        """Test the check_update method of the UpdateManager class."""
        web_mock = Mock()
        config_mock = Mock()
        self.update_manager._web_man = web_mock
        self.update_manager._config_man = config_mock

        # Mock the get_config method to return a sample web config
        web_config = {
            'version': '1.0.0',
            'description': 'Sample update description'
        }
        web_mock.get_config.return_value = web_config

        # Mock the load_yaml method to return a sample local config
        local_config = {
            'version': '0.9.0',
            'description': 'Sample local description'
        }
        config_mock.load_yaml.return_value = local_config

        result = self.update_manager.check_update()

        assert result == {
            'has_update': True,
            'description': 'Sample update description',
            'web_version': '1.0.0',
            'local_version': '0.9.0'
        }

    def test_db_sum(self):
        """Test the db_sum method of the UpdateManager class."""
        result = self.update_manager.db_sum()
        LOGGER.debug(f"result: {result}")

        # check if result is a DBSummary object
        assert isinstance(result, DBSummary)

    def test_get_files(self):
        """Test the get_files method of the UpdateManager class."""
        hashing_mock = Mock()

        # Mock the get_files method to return a sample list of file paths
        files = ['ImADirectory/loader.py', 'ImADirectory/moreData.pkl', 'data.yml', 'start_me.py']
        hashing_mock.HashDB.return_value.get_file_paths.return_value = files

        result = self.update_manager.get_files()
        assert result == files

    def test_download_files(self):
        """Test the download_files method of the UpdateManager class."""
        temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        self.update_manager.download_files(temp_dir)

        # check that the correct files were downloaded
        assert os.path.exists(os.path.join(temp_dir, "ImADirectory", "loader.py"))
        assert os.path.exists(os.path.join(temp_dir, "ImADirectory", "moreData.pkl"))
        assert os.path.exists(os.path.join(temp_dir, "data.yml"))
        assert os.path.exists(os.path.join(temp_dir, "start_me.py"))

        shutil.rmtree(temp_dir)


    def test_prepare_update(self):
        """Test the prepare_update method of the UpdateManager class."""
        result = self.update_manager.prepare_update()
        with open(result, "rb") as f:
            data = pickle.load(f)
            LOGGER.debug(f"data: {data}")
        
        actual_data = {
            'update': data['update'],
            'project_path': data['project_path'],
            'startup_path': data['startup_path'],
            'cleanup': data['cleanup'],
        }

        expected_data = {
            'update': ['ImADirectory/loader.py', 'ImADirectory/moreData.pkl', 'data.yml', 'start_me.py'],
            'project_path': self.project_path,
            'startup_path': os.path.join(self.project_path, "start_me.py"),
            'cleanup': True,
        }

        assert actual_data == expected_data
