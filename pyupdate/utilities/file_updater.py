"""This module is a utility for updating files."""

import argparse
import os
import pickle
import shutil
import subprocess
import sys
from time import sleep
from pyupdate.utilities import hashing


def main():
    # Create the argument parser
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

    # DEBUG
    with open(os.path.join(os.path.dirname(__file__), 'test.txt'), 'w') as f:
        f.write(str(update_details))
    
    # Update the files
    for file in update_files:
        source = os.path.join(args.path, file)
        destination = os.path.join(project_path, file)
        if os.path.exists(destination):
            os.remove(destination)
        os.rename(source, destination)
    
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
        with open(os.path.join(os.path.dirname(__file__), 'update_crash.txt'), 'w') as f:
            f.write(str(e))
        raise e
