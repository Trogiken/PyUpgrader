import unittest
import os
import shutil
import argparse
import pickle
import sys
import unittest.mock as mock
from pyupgrader.utilities.file_updater import main, LoadActionError, MergeError, DeleteError, ConfigOverwriteError, DBOverwriteError, GatherDetailsError, UpdateError

class FileUpdaterTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_project")
        os.makedirs(os.path.join(self.test_dir, ".pyupgrader"), exist_ok=True)

        # Create a temporary startup path
        self.startup_path = os.path.join(self.test_dir, "startup.py")
        with open(self.startup_path, "w") as startup_file:
            startup_file.write("# Startup file")

        # Create a temporary downloads directory
        self.downloads_dir = os.path.join(os.path.dirname(__file__), "downloads")
        os.makedirs(self.downloads_dir, exist_ok=True)
        
        config_name = "config.yaml"
        hash_db_name = "hashes.db"
        # create files
        files = ["file1.txt",
                 "file2.txt",
                 "file3.txt",
                 "file4.txt",
        ]
        for file in files:
            file_path = os.path.join(self.test_dir, file)
            with open(file_path, "w") as f:
                f.write(f"This is {file}")
            file_path = os.path.join(self.downloads_dir, file)
            with open(file_path, "w") as f:
                f.write(f"This is {file}")
        
        # create temporary cloud config and hash db
        special_files = [config_name, hash_db_name]
        for file in special_files:
            file_path = os.path.join(self.downloads_dir, file)
            with open(file_path, "w") as f:
                f.write(f"This is {file}")
            file_path = os.path.join(self.test_dir, ".pyupgrader", file)
            with open(file_path, "w") as f:
                f.write(f"This is {file}")

        # Create a temporary action file
        self.action_file_path = os.path.join(self.downloads_dir, "action.pkl")
        action_data = {
            "update": ["file1.txt", "file2.txt"],
            "delete": ["file3.txt", "file4.txt"],
            "project_path": self.test_dir,
            "downloads_directory": self.downloads_dir,
            "startup_path": self.startup_path,
            "cloud_config_path": os.path.join(self.downloads_dir, config_name),
            "cloud_hash_db_path": os.path.join(self.downloads_dir, hash_db_name),
            "cleanup": True
        }
        with open(self.action_file_path, "wb") as action_file:
            pickle.dump(action_data, action_file)

    def tearDown(self):
        # # Clean up any created folders
        shutil.rmtree(self.test_dir)
        if os.path.exists(self.downloads_dir):  # cleanup flag
            shutil.rmtree(self.downloads_dir)

    def test_main(self):
        # Call the main function
        with mock.patch.object(sys, "executable", "python"):
            with mock.patch.object(os, "execv"):
                with mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(action=self.action_file_path)):
                    main()

        # Assert that the files are updated
        updated_files = ["file1.txt", "file2.txt"]
        for file in updated_files:
            destination = os.path.join(self.test_dir, file)
            self.assertTrue(os.path.exists(destination))

        # Assert that the files are deleted
        deleted_files = ["file3.txt", "file4.txt"]
        for file in deleted_files:
            destination = os.path.join(self.test_dir, file)
            self.assertFalse(os.path.exists(destination))

        # Assert that the config file is replaced
        config_destination = os.path.join(self.test_dir, ".pyupgrader", "config.yaml")
        self.assertTrue(os.path.exists(config_destination))

        # Assert that the hash db is replaced
        hash_db_destination = os.path.join(self.test_dir, ".pyupgrader", "hashes.db")
        self.assertTrue(os.path.exists(hash_db_destination))

        # Assert that the downloads directory is cleaned up
        self.assertFalse(os.path.exists(self.downloads_dir))

        # Can't test to see if the application is restarted

if __name__ == "__main__":
    unittest.main()
