import os
import unittest
import responses
import pyupgrader.utilities.web as web

class WebTestCase(unittest.TestCase):
    def setUp(self):
        self.web = web.WebHandler("https://example.com")

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

        res = web.get_request(url)

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
