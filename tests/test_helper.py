import unittest
import os
import yaml
import requests
import responses
from pyupgrader.utilities.helper import normalize_paths, Config, Web

class NormalizePathsTestCase(unittest.TestCase):
    def test_normalize_single_path(self):
        # Test with a single path
        path = "C:\\Users\\noah\\Documents\\file.txt\\"
        expected_normalized_path = "C:/Users/noah/Documents/file.txt"

        normalized_path = normalize_paths(path)

        self.assertEqual(normalized_path, expected_normalized_path)

    def test_normalize_multiple_paths(self):
        # Test with a list of paths
        paths = [
            "C:\\Users\\noah\\Documents\\file1.txt",
            "C:\\Users\\noah\\Downloads\\file2.txt",
            "C:\\Program Files\\file3.txt\\"
        ]
        expected_normalized_paths = [
            "C:/Users/noah/Documents/file1.txt",
            "C:/Users/noah/Downloads/file2.txt",
            "C:/Program Files/file3.txt"
        ]

        normalized_paths = normalize_paths(paths)

        self.assertEqual(normalized_paths, expected_normalized_paths)

    def test_normalize_invalid_input(self):
        # Test with invalid input (integer)
        path = 123

        with self.assertRaises(TypeError):
            normalize_paths(path)

class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.valid_config_path = os.path.join(os.path.dirname(__file__), "valid_config.yaml")
        self.invalid_config_path = os.path.join(os.path.dirname(__file__), "invalid_config.yaml")

        # Create a test config file
        with open(self.valid_config_path, "w", encoding="utf-8") as config_file:
            config_file.write(
                "version: 1.0.0\n"
                "description: Built with PyUpgrader\n"
                "startup_path: \"\"\n"
                "required_only: false\n"
                "cleanup: false\n"
                "hash_db: hash.db\n"
            )

        # Create an invalid test config file
        with open(self.invalid_config_path, "w", encoding="utf-8") as config_file:
            config_file.write(
                "version: 1.0.0\n"
                "description: Built with PyUpgrader\n"
                "startup_path: \"\"\n"
                "required_only: false\n"
                # Missing "cleanup" attribute
                "hash_db: hash.db\n"
            )
        
        self.valid_config_data = {
            "version": "1.0.0",
            "description": "Built with PyUpgrader",
            "startup_path": "",
            "required_only": False,
            "cleanup": False,
            "hash_db": "hash.db",
        }
        
    def tearDown(self):
        os.remove(self.valid_config_path)
        os.remove(self.invalid_config_path)

    def test_load_yaml_valid_config(self):
        # Test loading a valid yaml file
        config = Config()
        path = self.valid_config_path
        expected_data = self.valid_config_data

        data = config.load_yaml(path)

        self.assertEqual(data, expected_data)

    def test_load_yaml_invalid_config(self):
        # Test loading an invalid yaml file
        config = Config()
        path = self.invalid_config_path

        with self.assertRaises(ValueError):
            config.load_yaml(path)

    def test_loads_yaml_valid_config(self):
        # Test loading a valid yaml string
        config = Config()
        yaml_string = """
        version: 1.0.0
        description: Built with PyUpgrader
        startup_path: ""
        required_only: false
        cleanup: false
        hash_db: hash.db
        """
        expected_data = self.valid_config_data

        data = config.loads_yaml(yaml_string)

        self.assertEqual(data, expected_data)

    def test_loads_yaml_invalid_config(self):
        # Test loading an invalid yaml string
        config = Config()
        yaml_string = """
        version: 1.0.0
        description: Built with PyUpgrader
        startup_path: ""
        required_only: false
        """
        
        with self.assertRaises(ValueError):
            config.loads_yaml(yaml_string)

    def test_write_yaml(self):
        # Test writing data to a yaml file
        config = Config()
        path = os.path.join(os.path.dirname(__file__), "output.yaml")
        data = self.valid_config_data

        config.write_yaml(path, data)

        # Verify that the file was written correctly
        with open(path, "r", encoding="utf-8") as output_file:
            written_data = yaml.safe_load(output_file)
            self.assertEqual(written_data, data)
        
        os.remove(path)

    def test_valid_config(self):
        # Test validating a valid config
        config = Config()
        valid_config = self.valid_config_data

        is_valid, error = config._valid_config(valid_config)

        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_invalid_config(self):
        # Test validating an invalid config
        config = Config()
        invalid_config = {
            "version": "1.0.0",
            "description": "Built with PyUpgrader",
            "startup_path": "",
            # Missing "required_only" attribute
            "cleanup": False,
            "hash_db": "hash.db",
        }

        is_valid, error = config._valid_config(invalid_config)

        self.assertFalse(is_valid)
        self.assertEqual(error, 'Missing "required_only" attribute')
    
    def test_default_config_data(self):
        # Test the default config data
        config = Config()
        expected_default_config_data = self.valid_config_data

        self.assertEqual(config.default_config_data, expected_default_config_data)

class WebTestCase(unittest.TestCase):
    def setUp(self):
        self.web = Web("https://example.com")

        self.config_data = {
            "version": "1.0.0",
            "description": "Built with PyUpgrader",
            "startup_path": "",
            "required_only": False,
            "cleanup": False,
            "hash_db": "hash.db",
        }

    @responses.activate
    def test_get_request_success(self):
        # Test successful GET request
        url = "https://example.com"
        responses.add(responses.GET, url, json={'key': 'value'}, status=200)

        res = self.web.get_request(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {'key': 'value'})

    @responses.activate
    def test_get_request_failure(self):
        # Test failed GET request
        url = "https://example.com/nonexistent"
        responses.add(responses.GET, url, status=404)

        with self.assertRaises(Exception):
            self.web.get_request(url)

    @responses.activate
    def test_get_config(self):
        # Test getting the config file
        expected_config = self.config_data

        responses.add(responses.GET, "https://example.com/config.yaml", json=expected_config, status=200)

        config = self.web.get_config()

        self.assertEqual(config, expected_config)

    @responses.activate
    def test_download(self):
        # Test downloading a file
        url_path = "https://example.com/file.txt"
        save_path = os.path.join(os.path.dirname(__file__), "file.txt")
        expected_save_path = save_path

        file_content = "Mocked file content"
        responses.add(responses.GET, url_path, body=file_content, status=200)

        returned_save_path = self.web.download(url_path, save_path)

        self.assertEqual(returned_save_path, expected_save_path)
        self.assertTrue(os.path.exists(save_path))
        with open(save_path, "r", encoding="utf-8") as file:
            self.assertEqual(file.read(), file_content)
        
        os.remove(save_path)

    @responses.activate
    def test_download_hash_db(self):
        # Test downloading the hash database
        save_path = os.path.join(os.path.dirname(__file__), "hash.db")
        expected_save_path = save_path

        responses.add(responses.GET, "https://example.com/config.yaml", json=self.config_data, status=200)
        responses.add(responses.GET, "https://example.com/hash.db", body="Mocked hash.db content", status=200)
        returned_save_path = self.web.download_hash_db(save_path)

        self.assertEqual(returned_save_path, expected_save_path)
        self.assertTrue(os.path.exists(save_path))

        os.remove(save_path)

if __name__ == "__main__":
    unittest.main()
