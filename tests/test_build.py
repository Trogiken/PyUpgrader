import unittest
from unittest.mock import patch
from .. import pyupdate
from ..pyupdate.build import PathError


class BuildTestCase(unittest.TestCase):
    def setUp(self):
        self.build = pyupdate.Builder('/path/to/project')

    def test_build_existing_folder(self):
        with patch('os.path.exists', return_value=True):
            with patch('Build._create_pyupdate_folder') as mock_create_folder:
                with patch('Build._create_config_file') as mock_create_config:
                    with patch('Build._create_hash_db') as mock_create_hash_db:
                        self.build.build()
                        mock_create_folder.assert_called_once()
                        mock_create_config.assert_called_once()
                        mock_create_hash_db.assert_called_once()

    def test_build_non_existing_folder(self):
        with patch('os.path.exists', return_value=False):
            with self.assertRaises(FileNotFoundError):
                self.build.build()

    def test_build_excluded_folder(self):
        self.build.exclude_paths.append('/path/to/project')
        with self.assertRaises(PathError):
            self.build.build()

if __name__ == '__main__':
    unittest.main()
