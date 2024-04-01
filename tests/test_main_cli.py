import unittest
from unittest.mock import patch
from pyupgrader.main_cli import cli

class CLITestCase(unittest.TestCase):
    @patch('pyupgrader.main_cli.util.Builder')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('logging.basicConfig')
    def test_cli(self, mock_logging, mock_parse_args, mock_builder):
        # Set up mock objects
        mock_args = mock_parse_args.return_value
        mock_args.project = '/path/to/project'
        mock_args.no_env = True
        mock_args.no_hidden = False
        mock_args.patterns = ['pattern1', 'pattern2']
        mock_args.exclude = ['/path/to/exclude1', '/path/to/exclude2']
        mock_args.log = 'DEBUG'

        # Call the cli function
        cli()

        # Assert that the Builder is initialized with the correct arguments
        mock_builder.assert_called_once_with(
            project_path='/path/to/project',
            exclude_envs=True,
            exclude_hidden=False,
            exclude_patterns=['pattern1', 'pattern2'],
            exclude_paths=['/path/to/exclude1', '/path/to/exclude2']
        )

        # Assert that the build method is called
        mock_builder.return_value.build.assert_called_once()

        # Assert that the logging is configured correctly
        mock_logging.assert_called_once_with(
            format='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )

if __name__ == '__main__':
    unittest.main()