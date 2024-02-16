import unittest
from pyupgrader.utilities.helper import normalize_paths

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

if __name__ == "__main__":
    unittest.main()