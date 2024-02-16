import os
import shutil


def create_dir_structure(path: str):
    """Create a directory structure with files"""
    if os.path.exists(path):
        shutil.rmtree(path)
    
    os.mkdir(path)

    # Create a file in the root directory
    with open(os.path.join(path, "file1.txt"), "w") as file:
        file.write("This is file1")
    
    # Create a dir1 in the root directory
    os.mkdir(os.path.join(path, "dir1"))

    # Create a file in the dir1
    with open(os.path.join(path, "dir1", "file2.txt"), "w") as file:
        file.write("This is file2")

    # Create a dir2 in dir1
    os.mkdir(os.path.join(path, "dir1", "dir2"))

    # Create a file in dir2
    with open(os.path.join(path, "dir1", "dir2", "file3.txt"), "w") as file:
        file.write("This is file3")
