"""This module is a utility for the update process."""

import argparse
import os
import pickle
import shutil
import sys
import datetime
import logging
from time import sleep

dump_dir = os.path.join(os.path.dirname(__file__), "Update_Logs")
os.makedirs(dump_dir, exist_ok=True)

# Check if log file limit is exceeded
FILE_LIMIT = 10
log_files = os.listdir(dump_dir)
if len(log_files) >= FILE_LIMIT:
    log_files.sort()  # Sort by creation time
    # Remove oldest logs until the limit is satisfied
    for _ in range((len(log_files) - FILE_LIMIT) + 1):  # +1 to account for the latest log
        os.remove(os.path.join(dump_dir, log_files.pop(0)))  # Remove the oldest log

timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
log_filename = f"update_{timestamp}.log"
log_filepath = os.path.join(dump_dir, log_filename)

handler = logging.FileHandler(log_filepath)
formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
handler.setFormatter(formatter)

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(handler)
LOGGER.setLevel(logging.DEBUG)


class LoadActionError(Exception):
    """Error occured while loading action file."""


class MergeError(Exception):
    """Error occurred while merging files."""


class DeleteError(Exception):
    """Error occurred while deleting files."""


class ConfigOverwriteError(Exception):
    """Error occurred while overwritting the config."""


class DBOverwriteError(Exception):
    """Error occurred while overwritting the hash database."""


class GatherDetailsError(Exception):
    """Error occurred while gathering update details."""


class UpdateError(Exception):
    """Error occurred while updating"""


def load_action_file(action_file_path: str):
    """
    Load the action file containing the update details.

    Args:
        action_file_path (str): Path to the action file

    Returns:
        dict: Update details

    Raises:
        LoadActionError: Error occurred while loading action file
    """
    LOGGER.info("Loading action file at %s", action_file_path)
    try:
        with open(action_file_path, "rb") as action_file:
            update_details = pickle.load(action_file)
        LOGGER.info("Action file loaded successfully")
        return update_details
    except Exception as file_error:
        raise LoadActionError("Failed to load action file") from file_error


def merge_files(changed_files: list, project_path: str, downloads_dir: str):
    """
    Overwrite the files in the project directory.

    Args:
        changed_files (list): List of files to overwrite or add
        project_path (str): Path to the project directory
        downloads_dir (str): Path to the downloads directory

    Raises:
        MergeError: Error occurred while merging files
    """
    LOGGER.info("Merging %d files...", len(changed_files))
    try:
        for file in changed_files:
            source = os.path.join(downloads_dir, file)
            destination = os.path.join(project_path, file)
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            if os.path.exists(destination):
                os.remove(destination)
                LOGGER.debug("Removed existing file at %s", destination)
            shutil.copy(source, destination)
            LOGGER.debug("Copied file from %s to %s", source, destination)
    except Exception as update_error:
        raise MergeError("Error occurred while merging files") from update_error
    LOGGER.info("Merged %d files successfully", len(changed_files))


def delete_files(del_files: list, project_path: str):
    """
    Delete the files in the project directory.

    Args:
        del_files (list): List of files to delete
        project_path (str): Path to the project directory

    Raises:
        DeleteError: Error occurred while deleting files
    """
    LOGGER.info("Deleting %d files...", len(del_files))
    try:
        for file in del_files:
            destination = os.path.join(project_path, file)
            if os.path.exists(destination):
                os.remove(destination)
                LOGGER.debug("Removed %s", destination)

            # Delete directory if empty
            dir_path = os.path.dirname(destination)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                LOGGER.debug("Removed empty directory at %s", dir_path)
    except Exception as delete_error:
        raise DeleteError("Error occurred while deleting files") from delete_error
    LOGGER.info("Deleted %d files successfully", len(del_files))


def overwrite_config(cloud_config_path: str, project_path: str):
    """
    Update the cloud config in the project directory.

    Args:
        cloud_config_path (str): Path to the cloud config file
        project_path (str): Path to the project directory

    Raises:
        ConfigOverwriteError: Error occurred while overwriting config
    """
    LOGGER.info("Overwriting config...")
    try:
        if os.path.exists(cloud_config_path):
            source = cloud_config_path
            destination = os.path.join(
                project_path, ".pyupgrader", os.path.basename(cloud_config_path)
            )
            if not os.path.exists(destination):
                LOGGER.warning("Local config file not found")
            else:
                os.remove(destination)
            shutil.copy(source, destination)
            LOGGER.debug("Copied cloud config from %s to %s", source, destination)
        else:
            raise FileNotFoundError(f"Cloud config not found at '{cloud_config_path}'")
    except Exception as config_error:
        raise ConfigOverwriteError("Error occurred while overwriting config") from config_error
    LOGGER.info("Overwritten config successfully")


def overwrite_hash_db(cloud_hash_db_path: str, project_path: str):
    """
    Update the cloud hash database in the project directory.

    Args:
        cloud_hash_db_path (str): Path to the cloud hash database file
        project_path (str): Path to the project directory

    Raises:
        DBOverwriteError: Error occurred while overwriting hash database
    """
    LOGGER.info("Overwriting hash database...")
    try:
        if os.path.exists(cloud_hash_db_path):
            source = cloud_hash_db_path
            destination = os.path.join(
                project_path, ".pyupgrader", os.path.basename(cloud_hash_db_path)
            )
            if not os.path.exists(destination):
                LOGGER.warning("Local hash database not found")
            else:
                os.remove(destination)
            shutil.copy(source, destination)
            LOGGER.debug("Copied cloud hash db from %s to %s", source, destination)
        else:
            raise FileNotFoundError(f"Cloud hash db not found at '{cloud_hash_db_path}'")
    except Exception as db_error:
        raise DBOverwriteError("Error occurred while overwriting the hash database") from db_error
    LOGGER.info("Overwritten hash database successfully")


def main():
    """
    Main function for the file updater utility.

    Args:
        -a, --action: Path to the action file
    """
    LOGGER.info("Update Utility Started")

    parser = argparse.ArgumentParser(description="Update Utility")

    parser.add_argument("-a", "--action", help="Path to the action file", required=True)
    args = parser.parse_args()

    sleep(1)

    LOGGER.info("Gathering update details...")
    try:
        update_details = load_action_file(args.action)

        changed_files = update_details["update"]
        del_files = update_details["delete"]
        project_path = update_details["project_path"]
        downloads_dir = update_details["downloads_directory"]
        startup_path = update_details["startup_path"]
        cloud_config_path = update_details["cloud_config_path"]
        cloud_hash_db_path = update_details["cloud_hash_db_path"]
        cleanup = update_details["cleanup"]
        LOGGER.debug("Update Details: %s", update_details)
    except Exception as details_error:
        raise GatherDetailsError("Error occurred while gathering update details") from details_error
    LOGGER.info("Update details gathered successfully")

    # Call update functions
    merge_files(changed_files, project_path, downloads_dir)
    delete_files(del_files, project_path)
    overwrite_config(cloud_config_path, project_path)
    overwrite_hash_db(cloud_hash_db_path, project_path)

    if cleanup:
        shutil.rmtree(downloads_dir)
        LOGGER.info("Cleaned up downloads directory at %s", downloads_dir)
    else:
        LOGGER.info("Downloads directory left at %s", downloads_dir)

    LOGGER.info("Update completed successfully. Restarting application...")

    # Start the application
    os.execv(sys.executable, [sys.executable, startup_path])


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        LOGGER.exception("Update failed")
        raise UpdateError(f"Update failed. Crash file created at {log_filepath}") from e
