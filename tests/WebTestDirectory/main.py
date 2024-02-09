import pyupgrader
from pyupgrader.utilities.helper import Config
import os

# DEBUG: Change branch to master when merging into master
pyupgrader_url = r"https://raw.githubusercontent.com/Trogiken/PyUpgrader/master/tests/WebTestDirectory/.pyupgrader"  # Replace with your info inside the {}
local_project_path = os.path.dirname(__file__)  # Assuming the entry point module is in the upper most directory

update_manager = pyupgrader.UpdateManager(pyupgrader_url, local_project_path)
config = Config()

# TODO Add file checks


def main():
    local_config = config.load_yaml(update_manager.config_path)
    version = local_config.get('version')
    description = local_config.get('description')
    print(f"Hello! from version '{version}'\nDescription: {description}")


if __name__ == '__main__':
    update_check = update_manager.check_update()
    has_update = update_check.get('has_update')
    if has_update:
        local_version = update_check.get('local_version')
        web_version = update_check.get('web_version')

        print(f"{local_version} -> {web_version}")
        actions_file = update_manager.prepare_update()
    else:
        print("** Up to date **")

    if has_update and os.path.exists(actions_file):
        input("Press Enter to update...")
        update_manager.update(actions_file)

    main()
