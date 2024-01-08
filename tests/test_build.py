import unittest
import os
import shutil
import yaml
import pyupdate

class TestBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = pyupdate.build.Builder()
        self.builder.folder_path = 'test_project'
        self.builder.exclude_paths = ['test_project/exclude']

    def tearDown(self):
        if os.path.exists('test_project'):
            shutil.rmtree('test_project')

    def test_build_success(self):
        self.builder.build()
        self.assertTrue(os.path.exists('test_project/.pyupdate'))
        self.assertTrue(os.path.exists('test_project/.pyupdate/config.yaml'))
        self.assertTrue(os.path.exists('test_project/.pyupdate/hashes.db'))

    def test_build_folder_path_not_set(self):
        self.builder.folder_path = None
        with self.assertRaises(pyupdate.BuildError):
            self.builder.build()

    def test_build_exclude_paths_not_set(self):
        self.builder.exclude_paths = None
        with self.assertRaises(pyupdate.build.BuildError):
            self.builder.build()

    def test_build_folder_not_exist(self):
        self.builder.folder_path = 'nonexistent_folder'
        with self.assertRaises(FileNotFoundError):
            self.builder.build()

    def test_build_exclude_folder_path(self):
        self.builder.exclude_paths = ['test_project']
        with self.assertRaises(pyupdate.build.PathError):
            self.builder.build()

    def test_build_folder_already_exists(self):
        os.mkdir('test_project/.pyupdate')
        with self.assertRaises(pyupdate.build.FolderCreationError):
            self.builder.build()

    def test_build_config_file_creation_error(self):
        self.builder.default_config_data = "invalid_yaml"
        with self.assertRaises(pyupdate.build.ConfigError):
            self.builder.build()

    def test_build_hash_db_creation_error(self):
        with self.assertRaises(pyupdate.build.HashDBError):
            self.builder.build()

    def test_validate_paths(self):
        self.builder.folder_path = 'test_project/'
        self.builder.exclude_paths = ['test_project/exclude/']
        self.builder._validate_paths()
        self.assertEqual(self.builder.folder_path, 'test_project')
        self.assertEqual(self.builder.exclude_paths, ['test_project/exclude'])

    def test_create_pyupdate_folder(self):
        self.builder._create_pyupdate_folder()
        self.assertTrue(os.path.exists('test_project/.pyupdate'))

    def test_create_config_file(self):
        self.builder._create_config_file()
        self.assertTrue(os.path.exists('test_project/.pyupdate/config.yaml'))
        with open('test_project/.pyupdate/config.yaml', 'r') as f:
            config_data = yaml.safe_load(f)
        self.assertEqual(config_data['version'], '0.0.0')
        self.assertEqual(config_data['description'], 'Description of the project')
        self.assertEqual(config_data['hash_db_name'], 'hashes.db')

    def test_create_hash_db(self):
        self.builder._create_hash_db()
        self.assertTrue(os.path.exists('test_project/.pyupdate/hashes.db'))

if __name__ == '__main__':
    unittest.main()
