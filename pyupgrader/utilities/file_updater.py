"""This module is a utility for the update process."""

import argparse
import os
import pickle
import shutil
import sys
import datetime
import traceback
from time import sleep


def main():
    """
    Main function for the file updater utility.

    Args:
        -a, --action: Path to the action file
    """
    parser = argparse.ArgumentParser(description="Update Utility")

    parser.add_argument("-a", "--action", help="Path to the action file", required=True)
    args = parser.parse_args()

    sleep(1)

    with open(args.action, "rb") as action_file:
        update_details = pickle.load(action_file)

        update_files = update_details["update"]
        del_files = update_details["delete"]
        project_path = update_details["project_path"]
        downloads_dir = update_details["downloads_directory"]
        startup_path = update_details["startup_path"]
        cloud_config_path = update_details["cloud_config_path"]
        cloud_hash_db_path = update_details["cloud_hash_db_path"]
        cleanup = update_details["cleanup"]

    # Update the files
    for file in update_files:
        # Copy/Overwrite files
        source = os.path.join(downloads_dir, file)
        destination = os.path.join(project_path, file)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        if os.path.exists(destination):
            os.remove(destination)
        shutil.copy(source, destination)

    for file in del_files:
        # Delete files
        destination = os.path.join(project_path, file)
        if os.path.exists(destination):
            os.remove(destination)

        # Delete directory if empty
        dir_path = os.path.dirname(destination)
        if not os.listdir(dir_path):
            os.rmdir(dir_path)

    # Replace config and hash db
    if os.path.exists(cloud_config_path):
        source = cloud_config_path
        destination = os.path.join(project_path, ".pyupgrader", os.path.basename(cloud_config_path))
        os.remove(destination)
        shutil.copy(source, destination)
    else:
        raise FileNotFoundError(f"Cloud config not found at '{cloud_config_path}'")

    if os.path.exists(cloud_hash_db_path):
        source = cloud_hash_db_path
        destination = os.path.join(
            project_path, ".pyupgrader", os.path.basename(cloud_hash_db_path)
        )
        os.remove(destination)
        shutil.copy(source, destination)
    else:
        raise FileNotFoundError(f"Cloud hash db not found at '{cloud_hash_db_path}'")

    if cleanup:
        shutil.rmtree(downloads_dir)

    # Start the application
    os.execv(sys.executable, [sys.executable, startup_path])


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Create crash dump and raise exception
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
        dump_dir = os.path.join(os.path.dirname(__file__), "crash_dump")
        os.makedirs(dump_dir, exist_ok=True)
        crash_file = os.path.join(os.path.dirname(__file__), "crash_dump", f"{timestamp}.txt")
        with open(crash_file, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())

        raise Exception(f"Update failed. Crash file created at {crash_file}") from e
