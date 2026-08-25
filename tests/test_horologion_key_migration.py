"""
tests/test_horologion_key_migration.py

Test suite to verify that all 48 flat Horologion keys were migrated to hierarchical namespaces
in Stamford text_horologion.json and that TextDB transparently redirects legacy aliases.
"""

import json
from pathlib import Path
import pytest
from engine.text_db import TextDB, humanize_key, LEGACY_KEY_ALIASES

MIGRATION_PAIRS = {
    # Vespers (horologion.vespers.*)
    "horologion.psalm_33": "horologion.vespers.psalm_33",
    "horologion.it_is_a_good_thing": "horologion.vespers.it_is_a_good_thing",

    # Matins (horologion.matins.*)
    "horologion.hexapsalmos": "horologion.matins.hexapsalmos",
    "horologion.six_psalms": "horologion.matins.six_psalms",
    "horologion.god_is_the_lord_verses": "horologion.matins.god_is_the_lord_verses",
    "horologion.polyeleos": "horologion.matins.polyeleos",
    "horologion.praises_psalms": "horologion.matins.praises_psalms",
    "horologion.doxology_great": "horologion.matins.great_doxology",
    "horologion.doxology_small_read": "horologion.matins.small_doxology_read",
    "horologion.invitatory_3x": "horologion.matins.invitatory_3x",
    "horologion.o_lord_open_lips": "horologion.matins.open_lips",
    "horologion.glory_to_god_highest": "horologion.matins.glory_to_god_highest",
    "horologion.glory_to_holy": "horologion.matins.glory_to_holy",
    "horologion.blessing_vigil": "horologion.matins.blessing_vigil",
    "horologion.vigil_bridge_blessing": "horologion.matins.vigil_bridge_blessing",

    # Compline (horologion.compline.*)
    "horologion.prayer_compline_spotless": "horologion.compline.prayer_spotless",
    "horologion.prayer_compline_grant_us": "horologion.compline.prayer_grant_us",
    "horologion.prayer_manasses": "horologion.compline.prayer_manasseh",
    "horologion.troparia_compline_day_passed": "horologion.compline.troparia_day_passed",
    "horologion.dismissal_great_compline_standard": "horologion.compline.dismissal_great_standard",
    "horologion.litany_final_compline": "horologion.compline.final_litany",
    "horologion.psalm_4": "horologion.compline.psalm_4",
    "horologion.psalm_6": "horologion.compline.psalm_6",
    "horologion.psalm_12": "horologion.compline.psalm_12",
    "horologion.psalm_24": "horologion.compline.psalm_24",
    "horologion.psalm_30": "horologion.compline.psalm_30",
    "horologion.psalm_90": "horologion.compline.psalm_90",

    # Hours (horologion.hours.*)
    "horologion.prayer_hour_1_christ_true_light": "horologion.hours.hour_1.prayer_christ_true_light",
    "horologion.prayer_the_first_hour": "horologion.hours.hour_1.ordinary_prayer",
    "horologion.verses_hour_1_order_my_steps": "horologion.hours.hour_1.verses_order_steps",
    "horologion.prayer_the_third_hour": "horologion.hours.hour_3.ordinary_prayer",
    "horologion.verses_hour_3_blessed_is_the_lord": "horologion.hours.hour_3.verses_blessed_is_lord",
    "horologion.prayer_hour_3_mardari": "horologion.hours.hour_3.prayer_mardari",
    "horologion.prayer_hour_6_god_and_lord_of_hosts": "horologion.hours.hour_6.prayer_lord_of_hosts",
    "horologion.prayer_the_sixth_hour": "horologion.hours.hour_6.ordinary_prayer",
    "horologion.verses_hour_6_compassions_quickly": "horologion.hours.hour_6.verses_compassions_quickly",
    "horologion.prayer_hour_9_master_lord": "horologion.hours.hour_9.prayer_master_lord",
    "horologion.prayer_the_ninth_hour": "horologion.hours.hour_9.ordinary_prayer",
    "horologion.verses_hour_9_forsake_not": "horologion.hours.hour_9.verses_forsake_not",
    "horologion.prayer_hours_thou_who": "horologion.hours.prayer_thou_who_at_all_times",

    # Common Ordinaries (horologion.common.*)
    "horologion.creed": "horologion.common.creed",
    "horologion.axion_estin": "horologion.common.axion_estin",
    "horologion.blessed_be_name_3x": "horologion.common.blessed_be_name_3x",
    "horologion.lord_have_mercy_3x": "horologion.common.lord_have_mercy_3x",
    "horologion.lord_have_mercy_12": "horologion.common.lord_have_mercy_12",
    "horologion.lord_have_mercy_40": "horologion.common.lord_have_mercy_40",
    "horologion.remit_pardon": "horologion.common.remit_pardon",
    "horologion.blessing_common": "horologion.common.blessing",
}


@pytest.fixture(scope="module")
def stamford_horologion_data():
    root = Path(__file__).resolve().parent.parent
    path = root / "Data" / "Service Books" / "Recensions" / "Stamford Divine Office" / "JSON" / "assets" / "text_horologion.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def text_db():
    return TextDB()


def test_all_old_keys_absent(stamford_horologion_data):
    """Verify that none of the original flat keys exist directly in the JSON file."""
    for old_key in MIGRATION_PAIRS:
        assert old_key not in stamford_horologion_data, f"Old flat key '{old_key}' still present in text_horologion.json"


def test_all_new_keys_present(stamford_horologion_data):
    """Verify that all new hierarchical keys exist directly in the JSON file."""
    for old_key, new_key in MIGRATION_PAIRS.items():
        assert new_key in stamford_horologion_data, f"New hierarchical key '{new_key}' missing from text_horologion.json"


def test_key_content_identity(text_db):
    """Verify that retrieving an old key returns identical text to the new hierarchical key."""
    for old_key, new_key in MIGRATION_PAIRS.items():
        old_item = text_db.get_text(old_key)
        new_item = text_db.get_text(new_key)
        assert old_item is not None, f"Failed to retrieve old key '{old_key}'"
        assert new_item is not None, f"Failed to retrieve new key '{new_key}'"
        assert not new_item.get("is_missing", False), f"New key '{new_key}' resolved to missing stub"
        assert old_item["content"] == new_item["content"], f"Content mismatch between '{old_key}' and '{new_key}'"


def test_humanize_keys():
    """Verify humanize_key produces clean titles for new hierarchical keys."""
    assert humanize_key("horologion.vespers.psalm_33") == "Psalm 33"
    assert humanize_key("horologion.matins.great_doxology") == "Great Doxology"
    assert humanize_key("horologion.hours.hour_3.ordinary_prayer") == "Ordinary Prayer"
    assert humanize_key("horologion.common.creed") == "Creed"
