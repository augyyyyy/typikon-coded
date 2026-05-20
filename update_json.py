import json
import os
import glob

json_dir = 'json_db'
files = glob.glob(os.path.join(json_dir, '*.json'))

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            continue
            
    updated = False
    
    if 'file_metadata' in data and 'authority' in data['file_metadata']:
        authority = data['file_metadata']['authority']
        if 'Dolnytsky Typikon' in authority:
            data['file_metadata']['authority'] = authority.replace('Dolnytsky Typikon', 'Lviv (Dolnytsky) Typikon (2010)')
            updated = True
            
    if '_meta' in data and 'authority' in data['_meta']:
        authority = data['_meta']['authority']
        if 'Dolnytsky Typikon' in authority:
            data['_meta']['authority'] = authority.replace('Dolnytsky Typikon', 'Lviv (Dolnytsky) Typikon (2010)')
            updated = True
            
    if updated:
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            print(f'Updated {fpath}')
