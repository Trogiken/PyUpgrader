# PyUpdate

Python library to keep projects updated on clients machines

**Pip Install:** `pip install git+https://github.com/Trogiken/PyUpdate`

## Getting Started

Build your project using the PyUpdate CLI and upload it. Use the _-h_ flag to see a list of options.

`pyupdate -p absolute/path/to/project -no_hidden`

Importing PyUpdate and initialize the UpdateManager object.

``` python
import pyupdate
import os
import sys

man = pyupdate.UpdateManager(r'https://raw.githubusercontent.com/{Owner}/{Repo}/{Branch}/path/to/.pyupdate', r'absolute/path/to/project')


if __name__ == '__main__':
    if man.check_update().get('has_update'):
        lock_path = man.update()
        input("Press enter to update...")
    
    if os.path.exists(lock_path):
        os.remove(lock_path)
        
    sys.exit()
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
