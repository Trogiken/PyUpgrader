"""PyUpgrader CLI"""

import argparse
import os
import sys
import pyupgrader.utilities as util
from pyupgrader.utilities.build import BuildError


def cli():
    """PyUpgrader CLI

    This function is the entry point for the PyUpgrader command-line interface (CLI).
    It parses the command-line arguments, validates the project folder path,
    and builds the project using the specified options.

    Args:
        -p, --project: Absolute path to project folder
        -no_env: Exclude environment directories
        -no_hidden: Exclude hidden files and directories
        -patterns: Exclude files and directories using regex patterns
        -e, --exclude: Absolute paths for excluded files and directories

    Raises:
        BuildError: If an error occurs during the build process.
    """
    parser = argparse.ArgumentParser(description='PyUpgrader CLI')
    parser.add_argument('-p', '--project',
                        help="Absolute path to project folder",
                        required=True)
    parser.add_argument('-no_env',
                        help="Exclude environment directories",
                        action='store_true')
    parser.add_argument('-no_hidden',
                        help="Exclude hidden files and directories",
                        action='store_true')
    parser.add_argument('-patterns',
                        help="Exclude files and directories using regex patterns",
                        nargs='+',
                        default=[])
    parser.add_argument('-e', '--exclude',
                        help="Absolute paths for excluded files and directories",
                        nargs='+',
                        default=[])
    args = parser.parse_args()

    if not os.path.exists(args.project):
        print(f'Folder "{args.project}" does not exist')
        sys.exit(1)

    try:
        builder = util.Builder(project_path=args.project,
                               exclude_envs=args.no_env,
                               exclude_hidden=args.no_hidden,
                               exclude_patterns=args.patterns,
                               exclude_paths=args.exclude)
        builder.build()
    except Exception as error:
        raise BuildError from error
