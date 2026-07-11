import os
import sys
import re
import json
from pathlib import Path
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Complete New Testament Verse Maps
MATTHEW_VERSES = {
    1: 25, 2: 23, 3: 17, 4: 25, 5: 48, 6: 34, 7: 29, 8: 34, 9: 38, 10: 42,
    11: 30, 12: 50, 13: 58, 14: 36, 15: 39, 16: 28, 17: 27, 18: 35, 19: 30, 20: 34,
    21: 46, 22: 46, 23: 39, 24: 51, 25: 46, 26: 75, 27: 66, 28: 20
}
MARK_VERSES = {
    1: 45, 2: 27, 3: 35, 4: 41, 5: 43, 6: 56, 7: 37, 8: 38, 9: 50, 10: 52,
    11: 33, 12: 44, 13: 37, 14: 72, 15: 47, 16: 20
}
LUKE_VERSES = {
    1: 80, 2: 52, 3: 38, 4: 44, 5: 39, 6: 49, 7: 50, 8: 56, 9: 62, 10: 42,
    11: 54, 12: 59, 13: 35, 14: 35, 15: 32, 16: 31, 17: 37, 18: 43, 19: 48, 20: 47,
    21: 38, 22: 71, 23: 56, 24: 53
}
JOHN_VERSES = {
    1: 51, 2: 25, 3: 36, 4: 54, 5: 47, 6: 71, 7: 53, 8: 59, 9: 41, 10: 42,
    11: 57, 12: 50, 13: 38, 14: 31, 15: 27, 16: 33, 17: 26, 18: 40, 19: 42, 20: 31,
    21: 25
}
ACTS_VERSES = {
    1: 26, 2: 47, 3: 26, 4: 37, 5: 42, 6: 15, 7: 60, 8: 40, 9: 43, 10: 48,
    11: 30, 12: 25, 13: 52, 14: 28, 15: 41, 16: 40, 17: 34, 18: 28, 19: 41, 20: 38,
    21: 40, 22: 30, 23: 35, 24: 27, 25: 27, 26: 32, 27: 44, 28: 31
}
ROMANS_VERSES = {
    1: 32, 2: 29, 3: 31, 4: 25, 5: 21, 6: 23, 7: 25, 8: 39, 9: 33, 10: 21,
    11: 36, 12: 21, 13: 14, 14: 23, 15: 33, 16: 27
}
CORINTHIANS_1_VERSES = {
    1: 31, 2: 16, 3: 23, 4: 21, 5: 13, 6: 20, 7: 40, 8: 13, 9: 27, 10: 33,
    11: 34, 12: 31, 13: 13, 14: 40, 15: 58, 16: 24
}
CORINTHIANS_2_VERSES = {
    1: 24, 2: 17, 3: 18, 4: 18, 5: 21, 6: 18, 7: 16, 8: 24, 9: 15, 10: 18,
    11: 33, 12: 21, 13: 14
}
GALATIANS_VERSES = {
    1: 24, 2: 21, 3: 29, 4: 31, 5: 26, 6: 18
}
EPHESIANS_VERSES = {
    1: 23, 2: 22, 3: 21, 4: 32, 5: 33, 6: 24
}
PHILIPPIANS_VERSES = {
    1: 30, 2: 30, 3: 21, 4: 23
}
COLOSSIANS_VERSES = {
    1: 29, 2: 23, 3: 25, 4: 18
}
THESSALONIANS_1_VERSES = {
    1: 10, 2: 20, 3: 13, 4: 18, 5: 28
}
THESSALONIANS_2_VERSES = {
    1: 12, 2: 17, 3: 18
}
TIMOTHY_1_VERSES = {
    1: 20, 2: 15, 3: 16, 4: 16, 5: 25, 6: 21
}
TIMOTHY_2_VERSES = {
    1: 18, 2: 26, 3: 17, 4: 22
}
TITUS_VERSES = {
    1: 16, 2: 15, 3: 15
}
PHILEMON_VERSES = {
    1: 25
}
HEBREWS_VERSES = {
    1: 14, 2: 18, 3: 19, 4: 16, 5: 14, 6: 20, 7: 28, 8: 13, 9: 28, 10: 39,
    11: 40, 12: 29, 13: 25
}
JAMES_VERSES = {
    1: 27, 2: 26, 3: 18, 4: 17, 5: 20
}
PETER_1_VERSES = {
    1: 25, 2: 25, 3: 22, 4: 19, 5: 14
}
PETER_2_VERSES = {
    1: 21, 2: 22, 3: 18
}
JOHN_1_VERSES = {
    1: 10, 2: 29, 3: 24, 4: 21, 5: 21
}
JOHN_2_VERSES = {
    1: 13
}
JOHN_3_VERSES = {
    1: 14
}
JUDE_VERSES = {
    1: 25
}
REVELATION_VERSES = {
    1: 20, 2: 29, 3: 22, 4: 11, 5: 14, 6: 17, 7: 17, 8: 13, 9: 21, 10: 11,
    11: 19, 12: 17, 13: 18, 14: 20, 15: 8, 16: 21, 17: 18, 18: 24, 19: 21, 20: 15,
    21: 27, 22: 21
}

# Standard biblical book chapter limits for syntax and bounds verification
BIBLE_METADATA = {
    # Gospels & Acts
    "Matthew": MATTHEW_VERSES, "Mt": MATTHEW_VERSES, "Matt": MATTHEW_VERSES,
    "Mark": MARK_VERSES, "Mk": MARK_VERSES,
    "Luke": LUKE_VERSES, "Lk": LUKE_VERSES,
    "John": JOHN_VERSES, "Jn": JOHN_VERSES,
    "Acts": ACTS_VERSES,
    
    # Epistles
    "Romans": ROMANS_VERSES, "Rom": ROMANS_VERSES,
    "1 Corinthians": CORINTHIANS_1_VERSES, "1 Cor": CORINTHIANS_1_VERSES,
    "2 Corinthians": CORINTHIANS_2_VERSES, "2 Cor": CORINTHIANS_2_VERSES,
    "Galatians": GALATIANS_VERSES, "Gal": GALATIANS_VERSES,
    "Ephesians": EPHESIANS_VERSES, "Eph": EPHESIANS_VERSES,
    "Philippians": PHILIPPIANS_VERSES, "Phil": PHILIPPIANS_VERSES,
    "Colossians": COLOSSIANS_VERSES, "Col": COLOSSIANS_VERSES,
    "1 Thessalonians": THESSALONIANS_1_VERSES, "1 Thess": THESSALONIANS_1_VERSES,
    "2 Thessalonians": THESSALONIANS_2_VERSES, "2 Thess": THESSALONIANS_2_VERSES,
    "1 Timothy": TIMOTHY_1_VERSES, "1 Tim": TIMOTHY_1_VERSES,
    "2 Timothy": TIMOTHY_2_VERSES, "2 Tim": TIMOTHY_2_VERSES,
    "Titus": TITUS_VERSES,
    "Philemon": PHILEMON_VERSES,
    "Hebrews": HEBREWS_VERSES, "Heb": HEBREWS_VERSES,
    "James": JAMES_VERSES, "Jas": JAMES_VERSES,
    "1 Peter": PETER_1_VERSES, "1 Pet": PETER_1_VERSES,
    "2 Peter": PETER_2_VERSES, "2 Pet": PETER_2_VERSES,
    "1 John": JOHN_1_VERSES, "1 Jn": JOHN_1_VERSES,
    "2 John": JOHN_2_VERSES, "2 Jn": JOHN_2_VERSES,
    "3 John": JOHN_3_VERSES, "3 Jn": JOHN_3_VERSES,
    "Jude": JUDE_VERSES,
    "Revelation": REVELATION_VERSES, "Rev": REVELATION_VERSES,
    
    # Common Old Testament Readings (Paremias)
    "Genesis": 50, "Gen": 50,
    "Exodus": 40, "Ex": 40,
    "Proverbs": 31, "Prov": 31,
    "Isaiah": 66, "Is": 66, "Isa": 66,
    "Job": 42,
    "Joel": 3,
    "Daniel": 12, "Dan": 12,
    "Ezekiel": 48, "Ezek": 48,
    "Psalm": 150, "Psalms": 150
}

# Regex to match scriptural citations (e.g. "1 Cor 6:12-20" or "Galatians 5:22-6:2" or "Lk 15:11-32")
CITATION_REGEX = re.compile(
    r"\b(?P<book>[1-3]?\s*[A-Za-z]+)\s+(?P<chap>\d+)\s*:\s*(?P<start_v>\d+)"
    r"(?:\s*-\s*(?:(?P<end_c>\d+)\s*:\s*)?(?P<end_v>\d+))?\b"
)

def parse_and_validate_citation(citation_str, file_context):
    errors = []
    match = CITATION_REGEX.search(citation_str)
    if not match:
        return errors
        
    book = match.group("book").strip()
    # Normalize spacing in book names like "1Cor" -> "1 Cor"
    normalized_book = re.sub(r"^(\d)([A-Za-z])", r"\1 \2", book)
    
    # Check if the book name is recognized in our metadata
    if normalized_book not in BIBLE_METADATA:
        # Some strings might look like citations but aren't (e.g. digital hours or times like "2:30")
        # We ignore book names that don't match alphabet characters (e.g. "UTC 12:00")
        if book.isalpha() or (book.replace(" ", "").isalnum() and any(c.isdigit() for c in book)):
            errors.append(f"{file_context}: Unrecognized biblical book name '{book}' in citation '{citation_str}'")
        return errors
        
    meta = BIBLE_METADATA[normalized_book]
    if isinstance(meta, int):
        # Old Testament/chapter-only check
        max_chapters = meta
        chap = int(match.group("chap"))
        if not (1 <= chap <= max_chapters):
            errors.append(f"{file_context}: Chapter {chap} is out of bounds for {normalized_book} (Max: {max_chapters}) in '{citation_str}'")
        return errors
        
    # New Testament verse-level check
    max_chapters = len(meta)
    chap = int(match.group("chap"))
    if not (1 <= chap <= max_chapters):
        errors.append(f"{file_context}: Chapter {chap} is out of bounds for {normalized_book} (Max: {max_chapters}) in '{citation_str}'")
        return errors
        
    max_verses = meta[chap]
    start_v = int(match.group("start_v"))
    if not (1 <= start_v <= max_verses):
        errors.append(f"{file_context}: Start verse {start_v} is out of bounds for {normalized_book} {chap} (Max: {max_verses}) in '{citation_str}'")
        
    # Validate end chapter/verse span
    end_c_str = match.group("end_c")
    end_v_str = match.group("end_v")
    
    if end_c_str:
        end_c = int(end_c_str)
        if not (1 <= end_c <= max_chapters):
            errors.append(f"{file_context}: End chapter {end_c} is out of bounds for {normalized_book} (Max: {max_chapters}) in '{citation_str}'")
        elif end_c < chap:
            errors.append(f"{file_context}: End chapter {end_c} is smaller than start chapter {chap} in '{citation_str}'")
        elif end_v_str:
            end_v = int(end_v_str)
            max_end_verses = meta[end_c]
            if not (1 <= end_v <= max_end_verses):
                errors.append(f"{file_context}: End verse {end_v} is out of bounds for {normalized_book} {end_c} (Max: {max_end_verses}) in '{citation_str}'")
    elif end_v_str:
        end_v = int(end_v_str)
        if not (1 <= end_v <= max_verses):
            errors.append(f"{file_context}: End verse {end_v} is out of bounds for {normalized_book} {chap} (Max: {max_verses}) in '{citation_str}'")
        elif end_v < start_v:
            errors.append(f"{file_context}: End verse {end_v} is smaller than start verse {start_v} in '{citation_str}'")
            
    return errors

def scan_dict_for_citations(data, filepath, errors):
    if isinstance(data, str):
        # We check keys that represent bible citations (like 'text' or 'ref_key' values containing books)
        # Or look for matches of CITATION_REGEX
        if CITATION_REGEX.search(data):
            errs = parse_and_validate_citation(data, filepath)
            errors.extend(errs)
    elif isinstance(data, list):
        for item in data:
            scan_dict_for_citations(item, filepath, errors)
    elif isinstance(data, dict):
        for k, v in data.items():
            # If the key itself is a citation (unlikely but possible), check it
            scan_dict_for_citations(k, filepath, errors)
            scan_dict_for_citations(v, filepath, errors)

def test_scripture_citations_bounds():
    """
    Scans all JSON database files under json_db/ and checks for any
    Bible citation formatting issues or chapter/verse range violations.
    """
    json_db_path = PROJECT_ROOT / "json_db"
    json_files = list(json_db_path.glob("**/*.json"))
    
    errors = []
    for filepath in json_files:
        # Skip output files or almanacs since they are generated from these sources
        if "almanac" in str(filepath) or "st_sergius" in str(filepath) or "propers_comparisons" in str(filepath):
            continue
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            scan_dict_for_citations(data, filepath.name, errors)
        except Exception as e:
            errors.append(f"Failed to read/parse {filepath.name}: {str(e)}")
            
    assert not errors, f"Bible citation validation failed:\n" + "\n".join(errors)
