# PyUpdate

Python library to keep projects updated on clients machines

**Pip Install Globally:** `pip install git+https://github.com/Trogiken/PyUpdate`

## Getting Started

Build your project using the PyUpdate CLI and upload it.

`pyupdate -f absolute/path/to/project`

Importing PyUpdate and initialize the UpdateManager object.

``` python
import pyupdate

update_man = pyupdate.UpdateManager(r"https://raw.githubusercontent.com/{Owner}/{Repo}/{Branch}/{path/to/.pyupdate}", r"{absolute/path/to/project}")

if __name__ == '__main__':
    update = update_man.check_update()

    if update.get("has_update")
        print(f"New Version Available")
        print(f"{update.get('web_version')} <- {update.get('local_version')}")
        print(update.get("description"))
```

Replace the temporary values `{}` with your information.

## Help/Information

PyUpdate has built in help classes that contain information about attributes and functions

### Example

``` python
from pyupdate.utilities import helper

config_help = helper.Config()
config_help.display_info()
```

This example of the Config helper class will show information about config attributes.
