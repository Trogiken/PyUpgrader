import os
import unittest
from unittest.mock import Mock
from pyupgrader.update import UpdateManager
from pyupgrader.utilities.helper import Config


class TestUpdateManager(unittest.TestCase):
    def setUp(self):
        url = r"https://raw.githubusercontent.com/Trogiken/PyUpgrader/tests-for-update-module/tests/TestingDirectory/.pyupgrader"  # Replace with your info inside the {}

        project_path = os.path.join(os.path.dirname(__file__), "TestingDirectory")
        self.update_manager = UpdateManager(url, project_path)
        self.config = Config()
    
    def tearDown(self):
        pass

    def test_check_update(self):
        """Test the check_update method of the UpdateManager class."""
        # Mock the web manager and config manager
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

        # Call the check_update method
        result = self.update_manager.check_update()

        # Assert the expected result
        assert result == {
            'has_update': True,
            'description': 'Sample update description',
            'web_version': '1.0.0',
            'local_version': '0.9.0'
        }

        # Assert that the get_config and load_yaml methods were called
        web_mock.get_config.assert_called_once()
        config_mock.load_yaml.assert_called_once_with("/path/to/project/.pyupgrader/config.yaml")

    def test_db_sum(self):
        """Test the db_sum method of the UpdateManager class."""
        # Mock the web manager and hashing module
        web_mock = Mock()
        hashing_mock = Mock()
        self.update_manager._web_man = web_mock
        self.update_manager._hashing = hashing_mock

        # Mock the download_hash_db method to return a sample cloud hash db path
        cloud_hash_db_path = "/path/to/cloud_hashes.db"
        web_mock.download_hash_db.return_value = cloud_hash_db_path

        # Mock the compare_databases method to return a sample DBSummary object
        db_summary_mock = Mock()
        hashing_mock.compare_databases.return_value = db_summary_mock

        # Call the db_sum method
        result = self.update_manager.db_sum()

        # Assert the expected result
        assert result == db_summary_mock

        # Assert that the download_hash_db and compare_databases methods were called
        web_mock.download_hash_db.assert_called_once_with("/path/to/cloud_hashes.db")
        hashing_mock.compare_databases.assert_called_once_with("/path/to/project/.pyupgrader/hash.db", cloud_hash_db_path)

        def test_get_files(self):
            """Test the get_files method of the UpdateManager class."""
            # Mock the web manager and hashing module
            web_mock = Mock()
            hashing_mock = Mock()
            self.update_manager._web_man = web_mock
            self.update_manager._hashing = hashing_mock

            # Mock the download_hash_db method to return a sample cloud hash db path
            cloud_hash_db_path = "/path/to/cloud_hashes.db"
            web_mock.download_hash_db.return_value = cloud_hash_db_path

            # Mock the get_files method to return a sample list of file paths
            files = ["/path/to/file1.py", "/path/to/file2.py"]
            hashing_mock.HashDB.return_value.get_file_paths.return_value = files

            # Call the get_files method
            result = self.update_manager.get_files()

            # Assert the expected result
            assert result == files

            # Assert that the download_hash_db and get_file_paths methods were called
            web_mock.download_hash_db.assert_called_once_with("/path/to/cloud_hashes.db")
            hashing_mock.HashDB.return_value.get_file_paths.assert_called_once()

    def test_download_files(self):
        """Test the download_files method of the UpdateManager class."""
        # Mock the get_files method to return a sample list of file paths
        files = ["/path/to/file1.py", "/path/to/file2.py"]
        self.update_manager.get_files = Mock(return_value=files)

        # Mock the download method to do nothing
        self.update_manager._web_man.download = Mock()

        # Call the download_files method
        result = self.update_manager.download_files()

        # Assert the expected result
        assert result == "/path/to/project/.pyupgrader"

        # Assert that the get_files and download methods were called
        self.update_manager.get_files.assert_called_once()
        assert self.update_manager._web_man.download.call_count == 2

    def test_prepare_update(self):
        """
        Test the prepare_update method of the UpdateManager class.
        """
        # Mock the get_files method to return a sample list of file paths
        files = ["/path/to/file1.py", "/path/to/file2.py"]
        self.update_manager.get_files = Mock(return_value=files)

        # Mock the download_files method to do nothing
        self.update_manager.download_files = Mock()

        # Call the prepare_update method
        result = self.update_manager.prepare_update()

        # Assert the expected result
        assert result == "/path/to/project/.pyupgrader"

        # Assert that the get_files and download_files methods were called
        self.update_manager.get_files.assert_called_once()
        self.update_manager.download_files.assert_called_once()
