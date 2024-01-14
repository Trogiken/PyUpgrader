import argparse
import os
import sys
import pyupdate.utilities as util
from pyupdate.utilities.build import BuildError


def cli():
    """PyUpdate CLI"""
    parser = argparse.ArgumentParser(description='PyUpdate CLI')
    parser.add_argument('-p', '--project', help="Path to project folder", required=True)
    parser.add_argument('-no_env', help="Exclude Evironment Directories", action='store_true')
    parser.add_argument('-e', '--exclude', help="Exclude files and directories", nargs='+', default=[])
    args = parser.parse_args()
    
    if not os.path.exists(args.project):
        print(f'Folder "{args.project}" does not exist')
        sys.exit(1)
    
    # DEBUG
    print(args.no_env)
    
    try:
        builder = util.Builder(project_path=args.project, exclude_envs=args.no_env, exclude_paths=args.exclude)
        builder.build()
    except Exception as error:
        raise BuildError(error)
