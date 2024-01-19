# PyUpgrader

Python library to keep projects updated on client machines

**Pip Install:** `pip install pyupgrader`

## Getting Started

Build your project using the PyUpgrader CLI and upload it. Use the _-h_ flag to see a list of options.

`pyupgrader -p absolute/path/to/project -no_hidden`

Importing PyUpgrader and initialize the UpdateManager object.

``` python
import pyupgrader
import os
import sys

man = pyupgrader.UpdateManager(r'https://raw.githubusercontent.com/{Owner}/{Repo}/{Branch}/path/to/.pyupgrader', r'absolute/path/to/project')


if __name__ == '__main__':
    if man.check_update().get('has_update'):
        lock_path = man.update()
        input("Press enter to update...")
    
    if os.path.exists(lock_path):
        os.remove(lock_path)
        
    sys.exit()
```

Replace the temporary values `{}` with your information.
