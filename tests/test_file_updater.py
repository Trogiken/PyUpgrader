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
    
    # TODO Test for the following errors

    # def test_load_action_file_error(self):
    #     # Test if LoadActionError is raised when loading action file fails
    #     with mock.patch("builtins.open", side_effect=Exception("Failed to load file")):
    #         with self.assertRaises(LoadActionError):
    #             main()

    # def test_merge_files_error(self):
    #     # Test if MergeError is raised when merging files fails
    #     with mock.patch("shutil.copy", side_effect=Exception("Failed to copy file")):
    #         with self.assertRaises(MergeError):
    #             main()

    # def test_delete_files_error(self):
    #     # Test if DeleteError is raised when deleting files fails
    #     with mock.patch("os.remove", side_effect=Exception("Failed to delete file")):
    #         with self.assertRaises(DeleteError):
    #             main()

    # def test_overwrite_config_error(self):
    #     # Test if ConfigOverwriteError is raised when overwriting config fails
    #     with mock.patch("shutil.copy", side_effect=Exception("Failed to overwrite config")):
    #         with self.assertRaises(ConfigOverwriteError):
    #             main()

    # def test_overwrite_hash_db_error(self):
    #     # Test if DBOverwriteError is raised when overwriting hash database fails
    #     with mock.patch("shutil.copy", side_effect=Exception("Failed to overwrite hash database")):
    #         with self.assertRaises(DBOverwriteError):
    #             main()

    # def test_gather_details_error(self):
    #     # Test if GatherDetailsError is raised when gathering update details fails
    #     with mock.patch("pyupgrader.utilities.file_updater.load_action_file", side_effect=Exception("Failed to gather update details")):
    #         with self.assertRaises(GatherDetailsError):
    #             main()

    # def test_update_error(self):
    #     # Test if UpdateError is raised when update process fails
    #     with mock.patch("pyupgrader.utilities.file_updater.merge_files", side_effect=Exception("Update process failed")):
    #         with self.assertRaises(UpdateError):
    #             main()

if __name__ == "__main__":
    unittest.main()