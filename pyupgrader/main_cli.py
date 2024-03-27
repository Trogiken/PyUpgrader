"""This module contains the CLI for building the project."""

import argparse
import logging
import pyupgrader.utilities as util


class BuildError(Exception):
    """Raised when there is an error building a project"""


def cli():
    """
    This function is the entry point for the PyUpgrader command-line interface (CLI).
    It parses the command-line arguments, validates the project folder path,
    and builds the project using the specified options.

    Args:
        -p, --project: Absolute path to project folder
        -no_env: Exclude environment directories
        -no_hidden: Exclude hidden files and directories
        -patterns: Exclude files and directories using regex patterns
        -e, --exclude: Absolute paths for excluded files and directories
        -l, --log: Set the logging level

    Raises:
        BuildError: If an error occurs during the build process.
    """
    parser = argparse.ArgumentParser(description="PyUpgrader CLI Builder")
    parser.add_argument("-p", "--project", help="Absolute path to project folder", required=True)
    parser.add_argument("-no_env", help="Exclude environment directories", action="store_true")
    parser.add_argument(
        "-no_hidden", help="Exclude hidden files and directories", action="store_true"
    )
    parser.add_argument(
        "-patterns",
        help="Exclude files and directories using regex patterns",
        nargs="+",
        default=[],
    )
    parser.add_argument(
        "-e",
        "--exclude",
        help="Absolute paths for excluded files and directories",
        nargs="+",
        default=[],
    )
    parser.add_argument(
        "-l",
        "--log",
        help="Set the logging level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
    )
    args = parser.parse_args()

    log_format = "%(asctime)s | %(levelname)-8s | %(message)s"
    logging.basicConfig(format=log_format, datefmt="%H:%M:%S")

    # Set the log level of the 'hashing' logger
    if args.log == "DEBUG":
        logging.getLogger("pyupgrader.utilities.hashing").setLevel(logging.DEBUG)
    else:
        logging.getLogger("pyupgrader.utilities.hashing").setLevel(logging.ERROR)
    # Set the log level of the 'build' logger
    logging.getLogger("pyupgrader.utilities.build").setLevel(args.log)

    try:
        builder = util.Builder(
            project_path=args.project,
            exclude_envs=args.no_env,
            exclude_hidden=args.no_hidden,
            exclude_patterns=args.patterns,
            exclude_paths=args.exclude,
        )
        builder.build()
    except Exception as error:
        raise BuildError from error
