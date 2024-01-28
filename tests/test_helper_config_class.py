import unittest
from unittest.mock import patch
from pyupgrader.utilities.helper import Config

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.config = Config()

    def test_load_yaml_from_package(self):
        package_name = "my_package"
        file_path = "config.yaml"
        expected_data = {"key": "value"}

        with patch("pkg_resources.resource_string") as mock_resource_string:
            mock_resource_string.return_value = b"key: value"
            data = self.config.load_yaml_from_package(package_name, file_path)
            self.assertEqual(data, expected_data)

    def test_load_yaml(self):
        path = "/path/to/config.yaml"
        expected_data = {"key": "value"}

        with patch("builtins.open") as mock_open:
            mock_file = mock_open.return_value.__enter__.return_value
            mock_file.read.return_value = "key: value"
            data = self.config.load_yaml(path)
            self.assertEqual(data, expected_data)

    def test_loads_yaml(self):
        yaml_string = "key: value"
        expected_data = {"key": "value"}

        data = self.config.loads_yaml(yaml_string)
        self.assertEqual(data, expected_data)

    def test_write_yaml(self):
        path = "/path/to/config.yaml"
        data = {"key": "value"}

        with patch("builtins.open") as mock_open:
            mock_file = mock_open.return_value.__enter__.return_value
            self.config.write_yaml(path, data)
            mock_file.write.assert_called_once_with("key: value")

    def test_valid_config(self):
        config = {
            "version": "1.0",
            "description": "My config",
            "hash_db": "hash.db",
            "startup_path": "/path/to/startup",
            "required_only": True,
            "cleanup": False
        }

        is_valid, error = self.config._valid_config(config)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_invalid_config(self):
        config = {
            "version": "1.0",
            "description": "My config",
            "hash_db": "hash.db",
            "startup_path": "/path/to/startup",
            "required_only": True
        }

        is_valid, error = self.config._valid_config(config)
        self.assertFalse(is_valid)
        self.assertEqual(error, 'Missing "cleanup" attribute')

if __name__ == "__main__":
    unittest.main()
