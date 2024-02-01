import os
import logging
from pyupgrader.utilities import build

LOGGER = logging.getLogger(__name__)


def test_build_success(tmpdir):
    """
    Test the success of the build process.

    This function creates a temporary project directory, sets up the necessary paths,
    and performs the build using the `build.Builder` class. It then asserts the existence
    of certain files in the project directory.
    """
    project_path = str(tmpdir.mkdir("project"))
    exclude_paths = [os.path.join(project_path, "exclude")]
    builder = build.Builder(project_path, exclude_paths=exclude_paths)

    builder.build()

    assert os.path.exists(os.path.join(project_path, ".pyupgrader"))
    assert os.path.exists(os.path.join(project_path, ".pyupgrader", "config.yaml"))
    assert os.path.exists(os.path.join(project_path, ".pyupgrader", "hashes.db"))

def test_build_folder_already_exists(tmpdir):
    """
    Test case to verify the behavior when the .pyupgrader folder already exists.
    """
    project_path = str(tmpdir.mkdir("project"))
    exclude_paths = [os.path.join(project_path, "exclude")]
    builder = build.Builder(project_path, exclude_paths=exclude_paths)

    # Create .pyupgrader folder manually
    os.mkdir(os.path.join(project_path, ".pyupgrader"))

    builder.build()

    assert os.path.exists(os.path.join(project_path, ".pyupgrader"))
    assert os.path.exists(os.path.join(project_path, ".pyupgrader", "config.yaml"))
    assert os.path.exists(os.path.join(project_path, ".pyupgrader", "hashes.db"))

def test_build_folder_path_not_set():
    """
    Test case for when the build folder path is not set.
    """
    builder = build.Builder(None)

    try:
        builder.build()
        assert False, "Expected BuildError to be raised"
    except build.BuildError:
        assert True

def test_build_folder_not_exist(tmpdir):
    """
    Test case for building a folder that does not exist.

    This test verifies that the build process raises a FileNotFoundError
    when attempting to build a project from a non-existent folder.

    Raises:
        AssertionError: If the FileNotFoundError is not raised during the build process.
    """
    project_path = str(tmpdir.join("nonexistent"))
    exclude_paths = [os.path.join(project_path, "exclude")]
    builder = build.Builder(project_path, exclude_paths=exclude_paths)

    try:
        builder.build()
        assert False, "Expected FileNotFoundError to be raised"
    except FileNotFoundError:
        assert True

def test_build_exclude_folder_path(tmpdir):
    """
    Test case to verify the behavior of excluding a folder path during the build process.

    Raises:
        build.PathError: If the build process does not raise a PathError.
    """
    project_path = str(tmpdir.mkdir("project"))
    exclude_paths = [project_path]
    builder = build.Builder(project_path, exclude_paths=exclude_paths)

    try:
        builder.build()
        assert False, "Expected PathError to be raised"
    except build.PathError:
        assert True
