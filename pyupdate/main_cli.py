import argparse
import os
import sys
from pyupdate import builder


def cli():
    parser = argparse.ArgumentParser(description='Description of program.')
    parser.add_argument('-f', '--folder', help="Path to project folder", required=True)
    args = parser.parse_args()
    
    if not os.path.exists(args.folder):
        print(f'Folder "{args.folder}" does not exist')
        sys.exit(1)
    
    builder.build(args.folder)