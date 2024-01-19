"""This module is a utility for updating files."""

import argparse
import os
import pickle
import shutil
import subprocess
import sys
import datetime
from time import sleep
from pyupgrader.utilities import hashing


def main():
    parser = argparse.ArgumentParser(description='Update Utility')

    parser.add_argument('-p', '--path', help='Path to downloaded files', required=True)
    parser.add_argument('-a', '--action', help='Path to the action file', required=True)
    parser.add_argument('-l', '--lock', help='Path to the lock file', required=True)
    parser.add_argument('-c', '--clean', help='Clean the downloads path', action='store_true')
    args = parser.parse_args()

    # Wait for the lock file to be removed
    while os.path.exists(args.lock):
        sleep(.5)
    sleep(1)

    with open(args.action, 'rb') as f:
        update_details = pickle.load(f)

        update_files = update_details['update']
        del_files = update_details['delete']
        project_path = update_details['project_path']
        startup_path = update_details['startup_path']
        cloud_config_path = update_details['cloud_config_path']
        cloud_hash_db_path = update_details['cloud_hash_db_path']
    
    # Replace config and hash db
    if os.path.exists(cloud_config_path):
        source = cloud_config_path
        destination = os.path.join(project_path, '.pyupgrader', os.path.basename(cloud_config_path))
        os.remove(destination)
        shutil.copy(source, destination)
    else:
        raise FileNotFoundError(f"Cloud config not found at '{cloud_config_path}'")
    
    if os.path.exists(cloud_hash_db_path):
        source = cloud_hash_db_path
        destination = os.path.join(project_path, '.pyupgrader', os.path.basename(cloud_hash_db_path))
        os.remove(destination)
        shutil.copy(source, destination)
    else:
        raise FileNotFoundError(f"Cloud hash db not found at '{cloud_hash_db_path}'")
    
    # Update the files
    for file in update_files:
        source = os.path.join(args.path, file)
        destination = os.path.join(project_path, file)
        if os.path.exists(destination):
            os.remove(destination)
        shutil.copy(source, destination)
    
    for file in del_files:
        destination = os.path.join(project_path, file)
        if os.path.exists(destination):
            os.remove(destination)
    
    if args.clean:
        shutil.rmtree(args.path)

    subprocess.Popen([sys.executable, startup_path])

    sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        crash_file = f"update_crash_{timestamp}.txt"
        with open(os.path.join(os.path.dirname(__file__), crash_file), 'w') as f:
            f.write(str(e))
        raise e
