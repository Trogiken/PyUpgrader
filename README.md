# PyUpdate

Python library to keep projects updated on clients machines

**Pip Install:** `pip install git+https://github.com/Trogiken/PyUpdate`

## Getting Started

Importing pyupdate and initialize the UpdateManager object.

``` python
import pyupdate

update_man = pyupdate.UpdateManager(r""https://raw.githubusercontent.com/{Owner}/{Repo}/{Branch}/Report-Analyzer/version.txt{path/to/.pyupdate}", r"path/to/project/folder")
```

Replace the temporary url names `{}` with your repositories information.

## Help/Information

PyUpdate has built in help classes that contain information about attributes and functions

### Example

``` python
from pyupdate.utilities import helper

config_help = helper.Config()
config_help.display_info()
```

This example of the Config helper class will show information about config attributes.
