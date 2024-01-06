import argparse
import os
import re
import sys


def cli():
    parser = argparse.ArgumentParser(description='Description of program.')
    parser.add_argument('--test', action='store_true', help='Test')
    args = parser.parse_args()

    if args.test:
        print("Test")


def main():
    print("Main Function")
