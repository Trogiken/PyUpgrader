mock_config_str = """\
version: 1.0
description: My config
hash_db: hash.db
startup_path: /path/to/startup
required_only: True
cleanup: False
"""

mock_config_dict = {
    "version": 1.0,
    "description": "My config",
    "hash_db": "hash.db",
    "startup_path": "/path/to/startup",
    "required_only": True,
    "cleanup": False
}