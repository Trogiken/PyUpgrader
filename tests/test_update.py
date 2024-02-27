import unittest
from os import path
from tempfile import mkdtemp
from unittest.mock import patch, MagicMock
from pyupgrader.utilities.hashing import DBSummary
from pyupgrader.update import UpdateManager, URLNotValidError, GetFilesError

class UpdateManagerTestCase(unittest.TestCase):
    @patch('os.path.exists')
    @patch('requests.get')
    @patch('pyupgrader.update.helper.Web')
    @patch('pyupgrader.update.helper.Config')
    def test_init(self, mock_config, mock_web, mock_requests_get, mock_os_path_exists):
        # Set up mock objects
        mock_os_path_exists.return_value = True
        mock_requests_get.return_value = MagicMock()
        mock_config.return_value.load_yaml.return_value = {"hash_db": "hashes.db"}
        
        # Create an instance of UpdateManager
        update_manager = UpdateManager("http://example.com", path.join("path", "to", "project"))
        
        # Assert that the attributes are set correctly
        self.assertEqual(update_manager.url, "http://example.com")
        self.assertEqual(update_manager.project_path, path.join("path", "to", "project"))
        self.assertEqual(update_manager.config_path, path.join("path", "to", "project", ".pyupgrader", "config.yaml"))
        self.assertEqual(update_manager.hash_db_path, path.join("path", "to", "project", ".pyupgrader", "hashes.db"))
        
        # Assert that the mock objects are called with the correct arguments
        mock_requests_get.assert_called_with("http://example.com", timeout=5)
        mock_web.assert_called_with("http://example.com")
        mock_config.assert_called_with()
        mock_config.return_value.load_yaml.assert_called_with(path.join("path", "to", "project", ".pyupgrader", "config.yaml"))
        
    @patch('os.path.exists')
    @patch('requests.get')
    @patch('pyupgrader.update.helper.Web')
    @patch('pyupgrader.update.helper.Config')
    def test_init_invalid_path(self, mock_config, mock_web, mock_requests_get, mock_os_path_exists):
        # Set up mock objects
        mock_os_path_exists.return_value = False
        mock_requests_get.return_value = MagicMock()
        mock_config.return_value.load_yaml.return_value = {"hash_db": "hashes.db"}
        
        # Assert that FileNotFoundError is raised when the project path does not exist
        with self.assertRaises(FileNotFoundError):
            UpdateManager("http://example.com", "/path/to/nonexistent")
        
    @patch('os.path.exists')
    @patch('requests.get')
    @patch('pyupgrader.update.helper.Config')
    def test_init_invalid_url(self, mock_config, mock_requests_get, mock_os_path_exists):
        # Set up mock objects
        mock_os_path_exists.return_value = True
        mock_requests_get.side_effect = Exception()
        mock_config.return_value.load_yaml.return_value = {"hash_db": "hashes.db"}
        
        # Assert that URLNotValidError is raised when the URL is not valid
        with self.assertRaises(URLNotValidError):
            UpdateManager("http://example.com", "/path/to/project")
    
    @patch('os.path.exists')
    @patch('requests.get')
    @patch('pyupgrader.update.helper.Web')
    @patch('pyupgrader.update.helper.Config')
    def test_check_update(self, mock_config, mock_web, mock_requests_get, mock_os_path_exists):
        # Set up mock objects
        mock_os_path_exists.return_value = True
        mock_requests_get.return_value = MagicMock()
        mock_config.return_value.load_yaml.return_value = {"hash_db": "hashes.db"}

        # Create an instance of UpdateManager
        update_manager = UpdateManager("http://example.com", "/path/to/project")
        
        # Mock the return values
        update_manager._web_man.get_config.return_value = {"version": "1.0.0", "description": "New version available"}
        update_manager._config_man.load_yaml.return_value = {"version": "0.9.0", "description": "Current version"}
        
        # Call the check_update method
        result = update_manager.check_update()
        
        # Assert that the result is as expected
        self.assertEqual(result, {
            "has_update": True,
            "description": "New version available",
            "web_version": "1.0.0",
            "local_version": "0.9.0"
        })
        
    @patch('tempfile.mkdtemp')
    @patch('os.path.exists')
    @patch('shutil.rmtree')
    @patch('pyupgrader.update.helper.Web')
    @patch('pyupgrader.update.helper.Config')
    @patch('pyupgrader.utilities.hashing.compare_databases')
    def test_db_sum(self, mock_compare_databases, mock_web, mock_mkdtemp, mock_os_path_exists, mock_config, mock_shutil_rmtree):
        # Set up mock objects
        mock_os_path_exists.return_value = True
        mock_config.return_value.load_yaml.return_value = {"hash_db": "hashes.db"}

        # Create an instance of UpdateManager
        update_manager = UpdateManager("http://example.com", "/path/to/project")
        
        db_sum = DBSummary(
            unique_files_cloud_db=list(),
            unique_files_local_db=list(),
            ok_files=list(),
            bad_files=list(),
        )

        # Mock the return values
        mock_compare_databases.return_value = db_sum
        
        # Call the db_sum method
        result = update_manager.db_sum()
        
        # Assert that the result is as expected
        self.assertEqual(result, db_sum)
        
        # Assert that the mock objects are called with the correct arguments
        mock_mkdtemp.assert_called()
        mock_compare_databases.assert_called()
        mock_shutil_rmtree.assert_called()

    @patch('tempfile.mkdtemp')
    @patch('os.path.exists')
    @patch('shutil.rmtree')
    @patch('pyupgrader.update.helper.Config')
    @patch('pyupgrader.utilities.hashing.HashDB')
    @patch('pyupgrader.utilities.helper.Web')
    def test_get_files(self, mock_web_man, mock_os_path_exists, mock_hashdb, mock_config, mock_rmtree, mock_mkdtemp):
        # Mock return values and methods
        mock_os_path_exists.return_value = True
        mock_config.return_value.load_yaml.return_value = {"hash_db": "hashes.db"}
        mock_web_man.download_hash_db.return_value = '/mock/cloud_hashes.db'
        mock_hashdb_instance = MagicMock()
        mock_hashdb.return_value = mock_hashdb_instance
        mock_hashdb_instance.get_file_paths.return_value = ['file1.py', 'file2.py']
        db_sum_mock = MagicMock()
        db_sum_mock.bad_files = []
        db_sum_mock.unique_files_cloud_db = ['file1.py', 'file2.py']
        UpdateManager.db_sum = MagicMock(return_value=db_sum_mock)

        # Create an instance of UpdateManager
        update_manager = UpdateManager("http://example.com", "/path/to/project")

        # Test case 1: get_files with updated_only=False
        result = update_manager.get_files(updated_only=False)
        self.assertEqual(result, ['file1.py', 'file2.py'])
        mock_web_man.download_hash_db.assert_called_once()
        mock_hashdb.assert_called_once_with('/mock/cloud_hashes.db')
        mock_hashdb_instance.get_file_paths.assert_called_once()
        UpdateManager.db_sum.assert_called_once()

        # Test case 2: get_files with updated_only=True
        mock_hashdb_instance.reset_mock()  # Reset call counts
        db_sum_mock.unique_files_cloud_db = ['file1.py', 'file2.py']
        db_sum_mock.bad_files = ['file2.py']
        result = update_manager.get_files(updated_only=True)
        self.assertEqual(result, ['file1.py'])  # 'file2.py' is in bad_files list
        mock_web_man.download_hash_db.assert_called_once()
        mock_hashdb.assert_called_once_with('/mock/cloud_hashes.db')
        mock_hashdb_instance.get_file_paths.assert_not_called()  # Shouldn't call get_file_paths in updated_only mode
        UpdateManager.db_sum.assert_called_once()

        # Test case 3: Exception handling
        mock_hashdb_instance.reset_mock()  # Reset call counts
        mock_hashdb_instance.get_file_paths.side_effect = Exception('Some error')
        with self.assertRaises(GetFilesError):
            update_manager.get_files()
        mock_web_man.download_hash_db.assert_called_once()
        mock_hashdb.assert_called_once_with('/mock/cloud_hashes.db')
        mock_hashdb_instance.get_file_paths.assert_called_once()
        UpdateManager.db_sum.assert_not_called()  # Shouldn't call db_sum if an exception occurs

        # Test case 4: Cleanup
        mock_hashdb_instance.reset_mock()  # Reset call counts
        mock_rmtree.side_effect = OSError('Some error')
        with self.assertRaises(GetFilesError):
            update_manager.get_files()
        mock_web_man.download_hash_db.assert_called_once()
        mock_hashdb.assert_called_once_with('/mock/cloud_hashes.db')
        mock_hashdb_instance.get_file_paths.assert_called_once()
        mock_rmtree.assert_called_once_with('/mock/temp_path')  # Verify rmtree called with correct path

if __name__ == '__main__':
    unittest.main()
