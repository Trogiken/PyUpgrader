import logging
from pyupgrader.utilities.helper import normalize_paths

LOGGER = logging.getLogger(__name__)


def test_normalize_paths_single_path():
    """
    Test case for the normalize_paths function with a single path.
    """
    path = "C:\\Users\\Owner\\Documents\\file.txt"
    expected = "C:/Users/Owner/Documents/file.txt"
    assert normalize_paths(path) == expected

def test_normalize_paths_multiple_paths():
    """
    Test case for the normalize_paths function with multiple paths.
    """
    paths = [
        "C:\\Users\\Owner\\Documents\\file1.txt",
        "C:\\Users\\Owner\\Documents\\file2.txt",
        "C:\\Users\\Owner\\Documents\\file3.txt"
    ]
    expected = [
        "C:/Users/Owner/Documents/file1.txt",
        "C:/Users/Owner/Documents/file2.txt",
        "C:/Users/Owner/Documents/file3.txt"
    ]
    assert normalize_paths(paths) == expected

def test_normalize_paths_trailing_slash():
    """
    Test case for the normalize_paths function when the path has a trailing slash.
    """
    path = "C:\\Users\\Owner\\Documents\\folder\\"
    expected = "C:/Users/Owner/Documents/folder"
    assert normalize_paths(path) == expected

def test_normalize_paths_multiple_paths_trailing_slash():
    """
    Test case for normalizing multiple paths with trailing slashes.
    """
    paths = [
        "C:\\Users\\Owner\\Documents\\folder1\\",
        "C:\\Users\\Owner\\Documents\\folder2\\",
        "C:\\Users\\Owner\\Documents\\folder3\\"
    ]
    expected = [
        "C:/Users/Owner/Documents/folder1",
        "C:/Users/Owner/Documents/folder2",
        "C:/Users/Owner/Documents/folder3"
    ]
    assert normalize_paths(paths) == expected

def test_normalize_paths_invalid_input():
    """
    Test case for the `normalize_paths` function with invalid input.
    """
    invalid_input = 123
    try:
        normalize_paths(invalid_input)
        assert False, "Expected TypeError to be raised"
    except TypeError:
        assert True
