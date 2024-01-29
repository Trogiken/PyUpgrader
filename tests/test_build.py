import os
import logging
from pyupgrader.utilities import build

LOGGER = logging.getLogger(__name__)


def test_build_success(tmpdir):
    LOGGER.info("Testing test_build_success")
    project_path = str(tmpdir.mkdir("project"))
    exclude_paths = [os.path.join(project_path, "exclude")]
    builder = build.Builder(project_path, exclude_paths=exclude_paths)

    builder.build()

    assert os.path.exists(os.path.join(project_path, ".pyupgrader"))
    assert os.path.exists(os.path.join(project_path, ".pyupgrader", "config.yaml"))
    assert os.path.exists(os.path.join(project_path, ".pyupgrader", "hashes.db"))

def test_build_folder_already_exists(tmpdir):
    LOGGER.info("Testing test_build_folder_already_exists")
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
    LOGGER.info("Testing test_build_folder_path_not_set")
    builder = build.Builder(None)

    try:
        builder.build()
        assert False, "Expected BuildError to be raised"
    except build.BuildError:
        assert True

def test_build_folder_not_exist(tmpdir):
    LOGGER.info("Testing test_build_folder_not_exist")
    project_path = str(tmpdir.join("nonexistent"))
    exclude_paths = [os.path.join(project_path, "exclude")]
    builder = build.Builder(project_path, exclude_paths=exclude_paths)

    try:
        builder.build()
        assert False, "Expected FileNotFoundError to be raised"
    except FileNotFoundError:
        assert True

def test_build_exclude_folder_path(tmpdir):
    LOGGER.info("Testing test_build_exclude_folder_path")
    project_path = str(tmpdir.mkdir("project"))
    exclude_paths = [project_path]
    builder = build.Builder(project_path, exclude_paths=exclude_paths)

    try:
        builder.build()
        assert False, "Expected PathError to be raised"
    except build.PathError:
        assert True
