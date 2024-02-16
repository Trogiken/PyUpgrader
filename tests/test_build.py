import unittest
import os
import shutil
import logging
from .helper import create_dir_structure
from pyupgrader.utilities.build import Builder, PathError

LOGGER = logging.getLogger(__name__)

class BuilderTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_project")
        create_dir_structure(self.test_dir)

        # Define a valid project path that exists
        self.project_path = self.test_dir
        self.exclude_paths = ["/path/to/exclude1", "/path/to/exclude2"]

        # Initialize the builder with real data
        self.builder = Builder(self.project_path, exclude_paths=self.exclude_paths)

    def tearDown(self):
        # Clean up any created files or folders
        shutil.rmtree(self.test_dir)

    def test_build(self):
        self.builder.build()

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
        # Test when project_path is not set
        self.builder.project_path = None
        with self.assertRaises(PathError):
            self.builder.build()

        # Test when exclude_paths is not set
        self.builder.project_path = "/path/to/project"
        self.builder.exclude_paths = None
        with self.assertRaises(PathError):
            self.builder.build()

        # Test when project_path does not exist
        self.builder.project_path = "/path/to/nonexistent"
        with self.assertRaises(PathError):
            self.builder.build()

        # Test when project_path is in exclude_paths
        self.builder.project_path = "/path/to/project"
        self.builder.exclude_paths = ["/path/to/project"]
        with self.assertRaises(PathError):
            self.builder.build()

if __name__ == "__main__":
    unittest.main()
