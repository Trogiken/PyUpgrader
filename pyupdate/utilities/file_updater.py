"""This module is a utility for updating files."""

import argparse


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Update Utility')

    parser.add_argument('p', 'path', help='Path to the input file', required=True)
    args = parser.parse_args()

    print(args.path)


if __name__ == '__main__':
    main()
