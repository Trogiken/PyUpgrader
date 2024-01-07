import argparse
import os
import sys
from pyupdate.build import Builder


def cli():
    parser = argparse.ArgumentParser(description='PyUpdate CLI')
    parser.add_argument('-f', '--folder', help="Path to project folder", required=True)
    args = parser.parse_args()
    
    if not os.path.exists(args.folder):
        print(f'Folder "{args.folder}" does not exist')
        sys.exit(1)
    
    builder = Builder(args.folder)
    builder.build()
