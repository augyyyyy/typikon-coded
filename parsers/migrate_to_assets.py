"""
Asset Migration Script - Bulk to Granular Assets
Converts json_db/stamford/*.json bulk files into individual assets/stamford/**/*.json files.
Uses short hash-based filenames to avoid Windows 260-character path limit.
"""

import json
import os
from pathlib import Path
import shutil
import hashlib

def short_hash(text, length=8):
    """Generate short hash for long filenames."""
    return hashlib.md5(text.encode()).hexdigest()[:length]

def migrate_bulk_to_assets():
    """
    Main migration function.
    Reads all bulk JSON files and extracts into individual assets.
    """
    
    base_dir = Path(__file__).parent.parent
    bulk_dir = base_dir / "json_db" / "stamford"
    assets_dir = base_dir / "assets" / "stamford"
    
    print("=" * 60)
    print("ASSET MIGRATION: Bulk -> Granular Assets")
    print("=" * 60)
    
    # Create backup
    backup_dir = base_dir / "json_db" / "stamford_backup"
    if not backup_dir.exists():
        print(f"\n[BACKUP] Creating backup: {backup_dir}")
        shutil.copytree(bulk_dir, backup_dir)
        print("[OK] Backup created")
    
    # Process each bulk file
    bulk_files = {
        "text_horologion.json": "horologion",
        "text_horologion_supplement.json": "horologion_supplement",
        "text_octoechos.json": "octoechos",
        "text_eothinon.json": "eothinon",
        "text_triodion.json": "triodion",
        "text_pentecostarion.json": "pentecostarion",
        "text_liturgikon.json": "liturgikon"
    }
    
    total_assets = 0
    id_map = {}  # Maps hash -> original ID
    
    for filename, book_name in bulk_files.items():
        bulk_path = bulk_dir / filename
        
        if not bulk_path.exists():
            print(f"\n[SKIP] {filename} (not found)")
            continue
        
        print(f"\n[BOOK] Processing {book_name}...")
        
        with open(bulk_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count, book_id_map = migrate_book(data, assets_dir, book_name)
        total_assets += count
        id_map.update(book_id_map)
        
        print(f"   [OK] Migrated {count} assets")
    
    # Write ID map for reference
    id_map_path = assets_dir / "_id_map.json"
    with open(id_map_path, 'w', encoding='utf-8') as f:
        json.dump(id_map, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 60}")
    print(f"[DONE] MIGRATION COMPLETE: {total_assets} total assets")
    print(f"{'=' * 60}")
    print(f"\nAssets location: {assets_dir}")
    print(f"Backup location: {backup_dir}")
    print(f"ID Map: {id_map_path}")

def migrate_book(data, assets_dir, book_name):
    """
    Migrates a single book's data to asset files.
    
    Args:
        data: Dictionary of key -> content
        assets_dir: Base assets directory
        book_name: Name of the book (e.g., 'octoechos')
    
    Returns:
        Tuple of (count, id_map)
    """
    count = 0
    id_map = {}
    
    for key, value in data.items():
        # Determine file path from key
        asset_path, file_id = determine_asset_path_safe(key, assets_dir, book_name)
        
        # Store ID mapping
        id_map[file_id] = key
        
        # Add original ID to asset data
        if isinstance(value, dict):
            value['_original_id'] = key
        
        # Create directory
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write asset
        with open(asset_path, 'w', encoding='utf-8') as f:
            json.dump(value, f, indent=2, ensure_ascii=False)
        
        count += 1
    
    return count, id_map

def determine_asset_path_safe(key, assets_dir, book_name):
    """
    Converts a dotted key into a file path with safe filename lengths.
    Returns tuple of (path, file_id).
    
    Strategy: Use directories for structure, short hash for filename.
    """
    
    parts = key.split('.')
    
    # Generate safe filename using hash
    file_id = short_hash(key)
    
    if book_name == "octoechos":
        # Key format: tone_N.service.hymn_name
        if len(parts) >= 2:
            tone = parts[0][:10]  # tone_1
            service = parts[1][:20] if len(parts) > 1 else "misc"
            return assets_dir / book_name / tone / service / f"{file_id}.json", file_id
        else:
            return assets_dir / book_name / f"{file_id}.json", file_id
    
    elif book_name in ["horologion", "horologion_supplement"]:
        # Key format: category.item
        if len(parts) >= 1:
            category = parts[0][:20]
            return assets_dir / "horologion" / category / f"{file_id}.json", file_id
        else:
            return assets_dir / "horologion" / f"{file_id}.json", file_id
    
    elif book_name == "eothinon":
        # Key format: eothinon_N.section
        if len(parts) >= 1:
            eothinon_num = parts[0][:15]
            return assets_dir / book_name / eothinon_num / f"{file_id}.json", file_id
        else:
            return assets_dir / book_name / f"{file_id}.json", file_id
    
    elif book_name in ["triodion", "pentecostarion"]:
        # Key format: sunday_name.service.hymn
        if len(parts) >= 1:
            day = parts[0][:30]
            return assets_dir / book_name / day / f"{file_id}.json", file_id
        else:
            return assets_dir / book_name / f"{file_id}.json", file_id
    
    else:
        # Generic
        return assets_dir / book_name / f"{file_id}.json", file_id

if __name__ == "__main__":
    migrate_bulk_to_assets()

    """
    Main migration function.
    Reads all bulk JSON files and extracts into individual assets.
    """
    
    base_dir = Path(__file__).parent.parent
    bulk_dir = base_dir / "json_db" / "stamford"
    assets_dir = base_dir / "assets" / "stamford"
    
    print("=" * 60)
    print("ASSET MIGRATION: Bulk -> Granular Assets")
    print("=" * 60)
    
    # Create backup
    backup_dir = base_dir / "json_db" / "stamford_backup"
    if not backup_dir.exists():
        print(f"\n[BACKUP] Creating backup: {backup_dir}")
        shutil.copytree(bulk_dir, backup_dir)
        print("[OK] Backup created")
    
    # Process each bulk file
    bulk_files = {
        "text_horologion.json": "horologion",
        "text_horologion_supplement.json": "horologion_supplement",
        "text_octoechos.json": "octoechos",
        "text_eothinon.json": "eothinon",
        "text_triodion.json": "triodion",
        "text_pentecostarion.json": "pentecostarion",
        "text_liturgikon.json": "liturgikon"
    }
    
    total_assets = 0
    
    for filename, book_name in bulk_files.items():
        bulk_path = bulk_dir / filename
        
        if not bulk_path.exists():
            print(f"\n[SKIP] {filename} (not found)")
            continue
        
        print(f"\n[BOOK] Processing {book_name}...")
        
        with open(bulk_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count = migrate_book(data, assets_dir, book_name)
        total_assets += count
        
        print(f"   [OK] Migrated {count} assets")
    
    print(f"\n{'=' * 60}")
    print(f"[DONE] MIGRATION COMPLETE: {total_assets} total assets")
    print(f"{'=' * 60}")
    print(f"\nAssets location: {assets_dir}")
    print(f"Backup location: {backup_dir}")

def migrate_book(data, assets_dir, book_name):
    """
    Migrates a single book's data to asset files.
    
    Args:
        data: Dictionary of key -> content
        assets_dir: Base assets directory
        book_name: Name of the book (e.g., 'octoechos')
    
    Returns:
        Number of assets created
    """
    count = 0
    
    for key, value in data.items():
        # Determine file path from key
        asset_path = determine_asset_path(key, assets_dir, book_name)
        
        # Create directory
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write asset
        with open(asset_path, 'w', encoding='utf-8') as f:
            json.dump(value, f, indent=2, ensure_ascii=False)
        
        count += 1
    
    return count

def determine_asset_path(key, assets_dir, book_name):
    """
    Converts a dotted key into a file path.
    
    Examples:
        tone_1.sat_vespers.stichera_lord_i_call → 
            assets/stamford/octoechos/tone_1/sat_vespers/stichera_lord_i_call.json
        
        horologion.vespers.psalm_103 →
            assets/stamford/horologion/vespers/psalm_103.json
    """
    
    parts = key.split('.')
    
    if book_name == "octoechos":
        # Key format: tone_N.service.hymn_name
        if len(parts) >= 3:
            tone = parts[0]          # tone_1
            service = parts[1]       # sat_vespers
            hymn = '.'.join(parts[2:])  # stichera_lord_i_call (or longer)
            return assets_dir / book_name / tone / service / f"{hymn}.json"
        elif len(parts) == 2:
            tone = parts[0]
            item = parts[1]
            return assets_dir / book_name / tone / f"{item}.json"
        else:
            return assets_dir / book_name / f"{key}.json"
    
    elif book_name == "horologion" or book_name == "horologion_supplement":
        # Key format: category.item or service.category.item
        if len(parts) >= 2:
            category = parts[0]
            item = '.'.join(parts[1:])
            return assets_dir / "horologion" / category / f"{item}.json"
        else:
            return assets_dir / "horologion" / f"{key}.json"
    
    elif book_name == "eothinon":
        # Key format: eothinon_N.section
        if len(parts) >= 2:
            eothinon_num = parts[0]  # eothinon_01
            section = '.'.join(parts[1:])
            return assets_dir / book_name / eothinon_num / f"{section}.json"
        else:
            return assets_dir / book_name / f"{key}.json"
    
    elif book_name in ["triodion", "pentecostarion"]:
        # Key format: sunday_name.service.hymn or day_name.item
        if len(parts) >= 2:
            day = parts[0]  # publican_pharisee
            item = '.'.join(parts[1:])
            return assets_dir / book_name / day / f"{item}.json"
        else:
            return assets_dir / book_name / f"{key}.json"
    
    else:
        # Generic: use parts as directory structure
        if len(parts) > 1:
            dirs = parts[:-1]
            filename = parts[-1]
            return assets_dir / book_name / '/'.join(dirs) / f"{filename}.json"
        else:
            return assets_dir / book_name / f"{key}.json"

if __name__ == "__main__":
    migrate_bulk_to_assets()
