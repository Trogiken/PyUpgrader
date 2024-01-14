import pyupdate
from pyupdate.utilities import hashing, helper
import tempfile
import os


update_man = pyupdate.UpdateManager(r"https://raw.githubusercontent.com/Trogiken/PyUpdate/downloading-cloud-files/Testing/.pyupdate", r"C:\Users\Owner\VScode\PyUpdate\Testing")


if __name__ == '__main__':
    update_check = update_man.check_update()
    # if update_check.get('has_update'):
    #     print("Update found!")
    #     print(f"{update_check.get('web_version')} <- {update_check.get('local_version')}")
    #     print(update_check.get('description'))
    #     print(f"\nUpdated files at: {update_man.download_all()}")
    web_manager = helper.Web(r"https://raw.githubusercontent.com/Trogiken/PyUpdate/downloading-cloud-files/Testing/.pyupdate")
    print(web_manager.get_config())
    cloud_db = web_manager.download_hash_db(os.path.join(tempfile.mkdtemp(), 'cloud_hashes.db'))
    hash_manager = hashing.HashDB()
    for path in hash_manager.get_file_paths(cloud_db):
        print(path)
        print(hash_manager.get_file_hash(path))
    
    sum = update_man.db_sum()
    print(f"Good Files: {sum.ok_files}")
    print(f"Bad Files: {sum.bad_files}")
    print(f"Unique Files Local DB: {sum.unique_files_local_db}")
    print(f"Unique Files Cloud DB: {sum.unique_files_cloud_db}")

    input("Press enter to exit...")
