import os
import json
import pyupdate.hashing as hashing


def build(folder_path):
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f'Folder "{folder_path}" does not exist')
    else:
        print(f'Building project from "{folder_path}"')
    
    pyudpdate_folder = os.path.join(folder_path, '.pyupdate')
    config_path = os.path.join(pyudpdate_folder, 'config.json')
    hash_db_path = os.path.join(pyudpdate_folder, 'hashes.db')
    
    if not os.path.exists(pyudpdate_folder):
        os.mkdir(pyudpdate_folder)

    print(f'Creating config file at "{config_path}"')
    json_data = {
        'version': "0.0.0",
        'description': "Descript of version",
        'hash_db_name': os.path.basename(hash_db_path),
    }
    with open(config_path, 'w') as f:
        json.dump(json_data, f, indent=4)

    print(f'Creating hash database at "{hash_db_path}"')
    hashing.create_hash_db(folder_path, hash_db_path)

    print('Done!')
    print(f'Project built at "{folder_path}"')
