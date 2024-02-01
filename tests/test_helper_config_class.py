import unittest
import logging
import tempfile
import shutil
import os
import yaml
from pyupgrader.utilities.helper import Config

LOGGER = logging.getLogger(__name__)


class TestConfig(unittest.TestCase):
    
    def setUp(self):
        """
        Set up the test environment by creating a temporary directory and a temporary file.
        """
        # Create a temporary directory
        self.temp_dir_path = tempfile.mkdtemp()
        LOGGER.debug(f"Created temporary directory: {self.temp_dir_path}")

        self.config = Config()

        # Create yaml file
        self.yaml_file_path = os.path.join(self.temp_dir_path, "config.yaml")
        with open(self.yaml_file_path, "w") as file:
            yaml.dump(self.config.default_config_data, file)
    
    def tearDown(self):
        """
        Clean up method that is called after each test case.
        Removes the temporary directory and logs the removal.
        """
        shutil.rmtree(self.temp_dir_path)
        LOGGER.debug(f"Removed temporary directory: {self.temp_dir_path}")

    def test_load_yaml(self):
        """
        Test the load_yaml method of the Config class.
        """
        data = self.config.load_yaml(self.yaml_file_path)
        LOGGER.debug(f"data: {data}")
        self.assertEqual(data, self.config.default_config_data)

    def test_loads_yaml(self):
        """
        Test case for loading YAML configuration.
        """
        data = self.config.loads_yaml(str(self.config.default_config_data))
        self.assertEqual(data, self.config.default_config_data)

    def test_write_yaml(self):
        """
        Test the write_yaml method of the Config class.
        """
        temp_file_path = os.path.join(self.temp_dir_path, "temp.yaml")
        self.config.write_yaml(temp_file_path, self.config.default_config_data)
        with open(temp_file_path, "r") as file:
            written_data = yaml.safe_load(file)
        self.assertEqual(written_data, self.config.default_config_data)

    def test_valid_config(self):
        """
        Test case to verify the validity of the configuration.
        """
        is_valid, error = self.config._valid_config(self.config.default_config_data)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_invalid_config(self):
        invalid_config = {
            "version": "1.0",
            "description": "My config",
            "hash_db": "hash.db",
            "startup_path": "/path/to/startup",
            "required_only": True
        }

        is_valid, error = self.config._valid_config(invalid_config)
        self.assertFalse(is_valid)
        self.assertEqual(error, 'Missing "cleanup" attribute')

if __name__ == "__main__":
    unittest.main()
