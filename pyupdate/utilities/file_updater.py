"""This module is a utility for updating files."""

import argparse
import os
import pickle
from time import sleep


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Update Utility')

    parser.add_argument('-p', '--path', help='Path to downloaded files', required=True)
    parser.add_argument('-a', '--action', help='Path to the action file', required=True)
    parser.add_argument('-l', '--lock', help='Path to the lock file', required=True)
    args = parser.parse_args()

    # Wait for the lock file to be removed
    while os.path.exists(args.lock):
        sleep(.5)
    sleep(1)

    with open(args.action, 'rb') as f:
        update_details = pickle.load(f)

    # DEBUG
    with open(os.path.join(os.path.dirname(__file__), 'test.txt'), 'w') as f:
        f.write(str(update_details))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        with open(os.path.join(os.path.dirname(__file__), 'update_crash.txt'), 'w') as f:
            f.write(str(e))
        raise e
