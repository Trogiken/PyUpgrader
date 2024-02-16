import unittest
import os
import shutil
from .helper import create_dir_structure
from pyupgrader.utilities.build import Builder, PathError, FolderCreationError, ConfigError, HashDBError

class BuilderTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_project")
        create_dir_structure(self.test_dir)

        # Define a valid project path that exists
        self.project_path = self.test_dir
        self.exclude_paths = ["/path/to/exclude1", "/path/to/exclude2"]

    def tearDown(self):
        # Clean up any created files or folders
        shutil.rmtree(self.test_dir)

    def test_build(self):
        builder = Builder(self.project_path)
        builder.build()

        # Assert that the .pyupgrader folder is created
        pyupgrader_folder = os.path.join(self.project_path, ".pyupgrader")
        self.assertTrue(os.path.exists(pyupgrader_folder))

        # Assert that the config file is created
        config_path = os.path.join(pyupgrader_folder, "config.yaml")
        self.assertTrue(os.path.exists(config_path))

        # Assert that the hash database is created
        hash_db_path = os.path.join(pyupgrader_folder, "hashes.db")
        self.assertTrue(os.path.exists(hash_db_path))

    def test_build_with_invalid_paths(self):
        builder = Builder(self.project_path)

        # Test when project_path is not set
        builder.project_path = None
        with self.assertRaises(PathError):
            builder.build()

        # Test when project_path does not exist
        builder.project_path = "/path/to/nonexistent"
        with self.assertRaises(PathError):
            builder.build()

        # Test when project_path is in exclude_paths
        builder.project_path = self.project_path
        builder.exclude_paths = [self.project_path]
        with self.assertRaises(PathError):
            builder.build()

    def test_build_with_invalid_config(self):
        builder = Builder(self.project_path, exclude_paths=self.exclude_paths)

        # Test when config file creation fails
        def mock_create_config_file():
            raise ConfigError("Mock error while creating config file")

        builder._create_config_file = mock_create_config_file
        with self.assertRaises(ConfigError):
            builder.build()

    def test_build_with_invalid_folder_creation(self):
        builder = Builder(self.project_path, exclude_paths=self.exclude_paths)

        # Test when creating .pyupgrader folder fails
        def mock_create_pyupgrader_folder():
            raise FolderCreationError("Mock error while creating .pyupgrader folder")

        builder._create_pyupgrader_folder = mock_create_pyupgrader_folder
        with self.assertRaises(FolderCreationError):
            builder.build()

    def test_build_with_invalid_hash_db_creation(self):
        builder = Builder(self.project_path, exclude_paths=self.exclude_paths)

        # Test when creating hash database fails
        def mock_create_hash_db():
            raise HashDBError("Mock error while creating hash database")

        builder._create_hash_db = mock_create_hash_db
        with self.assertRaises(HashDBError):
            builder.build()

    def test_build_with_exclusion_settings(self):
        # Test with exclude_envs and exclude_hidden set to True
        builder_with_exclusions = Builder(
            self.project_path, exclude_envs=True, exclude_hidden=True, exclude_paths=self.exclude_paths
        )
        builder_with_exclusions.build()

        # Assert that the .pyupgrader folder is created
        pyupgrader_folder = os.path.join(self.project_path, ".pyupgrader")
        self.assertTrue(os.path.exists(pyupgrader_folder))

        # Assert that the config file is created
        config_path = os.path.join(pyupgrader_folder, "config.yaml")
        self.assertTrue(os.path.exists(config_path))

        # Assert that the hash database is created
        hash_db_path = os.path.join(pyupgrader_folder, "hashes.db")
        self.assertTrue(os.path.exists(hash_db_path))

    # Additional tests as per the suggestions:
    def test_build_with_custom_exclusions(self):
        # Test with custom exclude_patterns and exclude_paths
        custom_exclusions = [r"/path/to/exclude3", r"/path/to/exclude4"]
        builder_with_custom_exclusions = Builder(
            self.project_path, exclude_patterns=[".*/.txt"], exclude_paths=custom_exclusions
        )
        builder_with_custom_exclusions.build()

        # Assert that the .pyupgrader folder is created
        pyupgrader_folder = os.path.join(self.project_path, ".pyupgrader")
        self.assertTrue(os.path.exists(pyupgrader_folder))

        # Assert that the config file is created
        config_path = os.path.join(pyupgrader_folder, "config.yaml")
        self.assertTrue(os.path.exists(config_path))

        # Assert that the hash database is created
        hash_db_path = os.path.join(pyupgrader_folder, "hashes.db")
        self.assertTrue(os.path.exists(hash_db_path))

    def test_build_with_invalid_input_types(self):
        # Test with invalid input types
        with self.assertRaises(TypeError):
            Builder(123, exclude_paths=["/path/to/exclude"])

    def test_build_with_empty_directory(self):
        # Test with empty directories
        empty_dir = os.path.join(self.test_dir, "empty_dir")
        os.makedirs(empty_dir)
        builder_empty_dir = Builder(empty_dir, exclude_paths=self.exclude_paths)
        builder_empty_dir.build()

        # Assert that the .pyupgrader folder is created
        pyupgrader_folder = os.path.join(empty_dir, ".pyupgrader")
        self.assertTrue(os.path.exists(pyupgrader_folder))

        # Assert that the config file is created
        config_path = os.path.join(pyupgrader_folder, "config.yaml")
        self.assertTrue(os.path.exists(config_path))

        # Assert that the hash database is created
        hash_db_path = os.path.join(pyupgrader_folder, "hashes.db")
        self.assertTrue(os.path.exists(hash_db_path))


if __name__ == "__main__":
    unittest.main()
