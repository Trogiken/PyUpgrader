import argparse
import os
import sys
import pyupdate.utilities as util
from pyupdate.utilities.build import BuildError


def cli():
    parser = argparse.ArgumentParser(description='PyUpdate CLI')
    parser.add_argument('-f', '--folder', help="Path to project folder", required=True)
    parser.add_argument('-e', '--exclude', help="Exclude files and directories", nargs='+', default=[])
    args = parser.parse_args()
    
    if not os.path.exists(args.folder):
        print(f'Folder "{args.folder}" does not exist')
        sys.exit(1)
    
    try:
        builder = util.Builder()
        builder.folder_path = args.folder
        builder.exclude_paths = args.exclude
        builder.build()
    except Exception as error:
        raise BuildError(error)
