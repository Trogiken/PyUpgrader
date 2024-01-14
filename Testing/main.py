import pyupdate


update_man = pyupdate.UpdateManager(r"https://raw.githubusercontent.com/Trogiken/PyUpdate/downloading-cloud-files/Testing/.pyupdate", r"C:\Users\Owner\VScode\PyUpdate\Testing")


if __name__ == '__main__':
    update_check = update_man.check_update()
    if update_check.get('has_update'):
        print("Update found!")
        print(f"{update_check.get('cloud_version')} <- {update_check.get('local_version')}")
        print(update_check.get('description'))
    else:
        print("No Updates")
