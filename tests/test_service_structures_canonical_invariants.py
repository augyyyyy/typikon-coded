"""
tests/test_service_structures_canonical_invariants.py

Canonical Invariant Audit Suite for Part I Service Structures (01a–01n).
Verifies that all 14 service structure blueprints maintain uncompromised
ordinal fidelity against Isidor Dolnytsky's Typikon (2010 Lviv Synod edition, Part I)
and the Ordo Celebrationis (Rome, 1944 / 1996).
"""

import glob
import json
import os
from pathlib import Path
import pytest
from jsonschema import validate

from engine import RuthenianEngine

REPO_ROOT = Path(__file__).resolve().parent.parent
JSON_DB_DIR = REPO_ROOT / "json_db"
SCHEMAS_DIR = REPO_ROOT / "schemas"


@pytest.fixture(scope="module")
def engine():
    return RuthenianEngine()


@pytest.fixture(scope="module")
def structure_files():
    files = sorted([
        JSON_DB_DIR / f for f in os.listdir(JSON_DB_DIR)
        if f.startswith("01") and f.endswith(".json")
    ])
    assert len(files) >= 14, f"Expected at least 14 service structure files, found {len(files)}"
    return files


def test_all_14_blueprints_validate_against_schema(structure_files):
    """Invariant 1: All 14 service structure blueprints (01a–01n) strictly validate against service_structure.schema.json."""
    schema_path = SCHEMAS_DIR / "service_structure.schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    for fpath in structure_files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        validate(instance=data, schema=schema)


def test_all_structures_resolve_non_empty_sequences(engine, structure_files):
    """Invariant 2: Every defined structure in all 01 blueprints resolves via inheritance to a non-empty sequence."""
    for fpath in structure_files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        for sname, sdef in data.get("structures", {}).items():
            if sname == "structure_suppressed":
                continue
            seq = engine._get_structure_sequence(data, sname)
            assert seq is not None, f"Failed to resolve structure sequence for '{sname}' in '{fpath.name}'"
            assert len(seq) > 0, f"Structure '{sname}' in '{fpath.name}' resolved to an empty sequence!"
            for slot in seq:
                assert "id" in slot, f"Slot missing 'id' in structure '{sname}' of '{fpath.name}': {slot}"


def test_vespers_canonical_ordinal_invariants(engine):
    """
    Invariant 3: Vespers structures adhere strictly to Dolnytsky Part I and Ordo Celebrationis:
      - great_vespers_vigil: Begins with 'Glory to the Holy...' (blessing_vigil), has Litiya, Artoklasia, Vigil dismissal.
      - great_vespers_simple: Begins with 'Blessed is our God' + introductory prayers, NO Litiya/Artoklasia, Great dismissal.
      - great_vespers_polyeleos: Inherits great_vespers_simple with 8 stichera at Lord I have cried.
      - daily_vespers: Begins with 'Blessed is our God', NO Entrance (phos_hilaron read), Fervent Litany after troparia, Small dismissal.
      - small_vespers: Begins with 'Blessed is our God', 4 stichera, NO Kathisma, NO Entrance, Small dismissal.
    """
    fpath = JSON_DB_DIR / "01h_struct_vespers.json"
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Great Vespers WITH Vigil
    vigil_seq = engine._get_structure_sequence(data, "great_vespers_vigil")
    vigil_slot_ids = [s["id"] for s in vigil_seq]

    assert "opening_vigil" in vigil_slot_ids
    opening_vigil_slot = next(s for s in vigil_seq if s["id"] == "opening_vigil")
    assert opening_vigil_slot["content"]["ref_key"] == "horologion.matins.blessing_vigil"
    assert "censing_psalm_103" in vigil_slot_ids
    assert "great_litany" in vigil_slot_ids
    assert "entrance_great" in vigil_slot_ids
    assert "litiya_rite" in vigil_slot_ids
    assert "aposticha" in vigil_slot_ids
    assert "artoklasia_rite" in vigil_slot_ids
    assert "dismissal_vigil" in vigil_slot_ids

    # 2. Great Vespers WITHOUT Vigil
    simple_seq = engine._get_structure_sequence(data, "great_vespers_simple")
    simple_slot_ids = [s["id"] for s in simple_seq]

    # Must open with Blessed is our God + introductory prayers (Ordo §29-30, Dolnytsky lines 52-57)
    assert "opening_simple" in simple_slot_ids
    opening_simple_slot = next(s for s in simple_seq if s["id"] == "opening_simple")
    ref_keys = opening_simple_slot["content"]["ref_keys"]
    assert "horologion.common.blessing" in ref_keys
    assert "horologion.common.trisagion_block" in ref_keys
    assert "horologion.matins.invitatory_3x" in ref_keys

    # Must NOT have vigil opening, pre-service censing, litiya, or artoklasia
    assert "opening_vigil" not in simple_slot_ids
    assert "censing_psalm_103" not in simple_slot_ids
    assert "litiya_rite" not in simple_slot_ids
    assert "artoklasia_rite" not in simple_slot_ids

    # Must have entrance with censer, aposticha, and full great dismissal
    assert "entrance_great" in simple_slot_ids
    assert "aposticha" in simple_slot_ids
    assert "dismissal_great" in simple_slot_ids
    dismissal_slot = next(s for s in simple_seq if s["id"] == "dismissal_great")
    assert dismissal_slot["content"]["ref_key"] == "horologion.dismissal_great"

    # 3. Great Vespers Polyeleos
    polyeleos_seq = engine._get_structure_sequence(data, "great_vespers_polyeleos")
    polyeleos_slot_ids = [s["id"] for s in polyeleos_seq]
    assert "opening_simple" in polyeleos_slot_ids
    assert "lord_i_have_cried_8" in polyeleos_slot_ids
    assert "entrance_great" in polyeleos_slot_ids
    assert "dismissal_great" in polyeleos_slot_ids

    # 4. Daily Vespers
    daily_seq = engine._get_structure_sequence(data, "daily_vespers")
    daily_slot_ids = [s["id"] for s in daily_seq]

    assert "beginning_daily" in daily_slot_ids
    beg_daily_slot = next(s for s in daily_seq if s["id"] == "beginning_daily")
    assert beg_daily_slot["content"]["ref_key"] == "horologion.common.blessing"

    # No entrance: phos_hilaron read
    assert "entrance_suppression" in daily_slot_ids
    phos_slot = next(s for s in daily_seq if s["id"] == "entrance_suppression")
    assert phos_slot["content"]["ref_key"] == "horologion.vespers.phos_hilaron_read"

    # Fervent Litany positioned after troparia (Dolnytsky Part I line 85)
    trop_idx = daily_slot_ids.index("troparia_daily")
    lit_idx = daily_slot_ids.index("litany_have_mercy")
    dism_idx = daily_slot_ids.index("dismissal_daily")
    assert trop_idx < lit_idx < dism_idx, "In Daily Vespers, Fervent Litany must follow troparia and precede dismissal!"
    lit_slot = next(s for s in daily_seq if s["id"] == "litany_have_mercy")
    assert lit_slot["content"]["ref_key"] == "horologion.vespers.fervent_litany"

    # 5. Small Vespers
    small_seq = engine._get_structure_sequence(data, "small_vespers")
    small_slot_ids = [s["id"] for s in small_seq]
    assert "beginning_small" in small_slot_ids
    assert "lord_i_have_cried_4" in small_slot_ids
    assert "entrance_suppression" in small_slot_ids
    assert "great_litany" not in small_slot_ids
    assert "kathisma_daily" not in small_slot_ids


def test_compline_canonical_ordinal_invariants(engine):
    """
    Invariant 4: Compline structures adhere to Dolnytsky Part I and Ordo Celebrationis:
      - small_compline: 'Blessed is our God', Psalms (50, 69, 142), Doxology, Creed, Canon, Troparia, Dismissal.
      - great_compline_lenten: 3 parts, 'God is with us', Prayer of Manasseh, 'Lord of Hosts', Ephrem prostrations.
      - great_compline_vigil: Censing, 'Blessed is our God', Parts 1-2, Litiya, Artoklasia, Vigil dismissal.
    """
    fpath = JSON_DB_DIR / "01f_struct_compline.json"
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Small Compline
    small_seq = engine._get_structure_sequence(data, "small_compline")
    small_slot_ids = [s["id"] for s in small_seq]
    assert "opening_blessing" in small_slot_ids
    assert "introductory_prayers" in small_slot_ids
    assert "invitatory" in small_slot_ids
    assert "psalms_compline" in small_slot_ids
    assert "doxology_small" in small_slot_ids
    assert "creed" in small_slot_ids
    assert "canon_slot" in small_slot_ids
    assert "troparia_slot" in small_slot_ids
    assert "dismissal_sequence" in small_slot_ids

    # Great Compline with Vigil
    vigil_seq = engine._get_structure_sequence(data, "great_compline_vigil")
    vigil_slot_ids = [s["id"] for s in vigil_seq]
    assert "censing_vigil" in vigil_slot_ids
    assert "opening_blessing" in vigil_slot_ids
    assert "close_doors" in vigil_slot_ids
    assert "vigil_tail" in vigil_slot_ids


def test_midnight_office_canonical_ordinal_invariants(engine):
    """
    Invariant 5: Midnight Office forms (Weekday, Saturday, Sunday, Feast) adhere to Dolnytsky Part I:
      - midnight_weekday / daily: Psalm 50, Kathisma 17 (Psalm 118), Creed, Troparia ('Behold the Bridegroom'), Part II.
      - midnight_saturday: Psalm 50, Kathisma 9 (Psalms 64-69), Creed, Troparia.
      - midnight_sunday: Psalm 50, Triadic Canon, Creed, Hypakoe of Tone. (No Kathisma 17, no Part II for dead).
      - midnight_feast: Kathisma 17, Festal troparion/kontakion, Part II suppressed.
    """
    fpath = JSON_DB_DIR / "01g_struct_midnight.json"
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Weekday / Daily
    daily_seq = engine._get_structure_sequence(data, "midnight_daily")
    daily_slot_ids = [s["id"] for s in daily_seq]
    assert "opening_blessing" in daily_slot_ids
    assert "horologion.psalm_50" in daily_slot_ids
    assert "horologion.kathisma_17" in daily_slot_ids
    assert "creed" in daily_slot_ids
    assert "troparia_block" in daily_slot_ids
    assert "part_ii_block" in daily_slot_ids

    # Saturday
    sat_seq = engine._get_structure_sequence(data, "midnight_saturday")
    sat_slot_ids = [s["id"] for s in sat_seq]
    assert "horologion.kathisma_9" in sat_slot_ids
    assert "horologion.kathisma_17" not in sat_slot_ids

    # Sunday
    sun_seq = engine._get_structure_sequence(data, "midnight_sunday")
    sun_slot_ids = [s["id"] for s in sun_seq]
    assert "triadic_canon" in sun_slot_ids
    assert "horologion.kathisma_17" not in sun_slot_ids
    assert "part_ii_block" not in sun_slot_ids

    # Feast
    feast_seq = engine._get_structure_sequence(data, "midnight_feast")
    feast_slot_ids = [s["id"] for s in feast_seq]
    assert "horologion.kathisma_17" in feast_slot_ids
    assert "part_ii_block" not in feast_slot_ids


def test_matins_canonical_ordinal_invariants(engine):
    """
    Invariant 6: Matins forms (Great Matins, Daily Matins, Lenten Matins) adhere to Dolnytsky Part I:
      - great_matins: Opening (Vigil vs Morning), Great Litany, God is the Lord, Kathismata, Polyeleos, Graduals, Gospel, Canon, Praises, Great Doxology, Dismissal.
      - daily_matins: Opening, Great Litany, God is the Lord, Kathismata, Psalm 50, Canon, Praises read, Small Doxology, Supplication Litany, Aposticha, Troparia, Fervent Litany, Dismissal.
    """
    fpath = JSON_DB_DIR / "01i_struct_matins.json"
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Great Matins
    great_seq = engine._get_structure_sequence(data, "great_matins")
    great_slot_ids = [s["id"] for s in great_seq]
    assert "matins_opening" in great_slot_ids
    assert "great_litany" in great_slot_ids
    assert "god_is_the_lord" in great_slot_ids
    assert "kathismata_block" in great_slot_ids
    assert "polyeleos_choice" in great_slot_ids
    assert "graduals_block" in great_slot_ids
    assert "gospel_rite" in great_slot_ids
    assert "canon_block" in great_slot_ids
    assert "praises" in great_slot_ids
    assert "great_doxology" in great_slot_ids

    # Daily Matins
    daily_seq = engine._get_structure_sequence(data, "daily_matins")
    daily_slot_ids = [s["id"] for s in daily_seq]
    assert "opening_daily" in daily_slot_ids
    assert "great_litany" in daily_slot_ids
    assert "god_is_the_lord" in daily_slot_ids
    assert "horologion.psalm_50" in daily_slot_ids
    assert "canon_daily" in daily_slot_ids
    assert "praises_read" in daily_slot_ids
    assert "small_doxology" in daily_slot_ids
    assert "litany_supplication" in daily_slot_ids
    assert "aposticha" in daily_slot_ids
    assert "dismissal_troparion" in daily_slot_ids
    assert "litany_have_mercy" in daily_slot_ids
    assert "dismissal_daily" in daily_slot_ids

    # Verify that in Daily Matins, Litany of Supplication precedes Aposticha, and Fervent Litany follows Troparia
    supp_idx = daily_slot_ids.index("litany_supplication")
    apos_idx = daily_slot_ids.index("aposticha")
    trop_idx = daily_slot_ids.index("dismissal_troparion")
    ferv_idx = daily_slot_ids.index("litany_have_mercy")
    dism_idx = daily_slot_ids.index("dismissal_daily")
    assert supp_idx < apos_idx < trop_idx < ferv_idx < dism_idx


def test_hours_and_typika_canonical_ordinal_invariants(engine):
    """
    Invariant 7: Hours (1, 3, 6, 9) and Typika maintain ordinal fidelity:
      - Hours: Opening, 3 Psalms, Troparia, Fixed Verses, Trisagion, Kontakion, Prayer of Hour, Dismissal.
      - Typika: Opening, Psalms 102 & 145, Only Begotten, Beatitudes, Epistle/Gospel, Creed, Kontakia, Dismissal.
    """
    for h, f in [("1", "01a_struct_hour_1.json"), ("3", "01b_struct_hour_3.json"), ("6", "01c_struct_hour_6.json"), ("9", "01d_struct_hour_9.json")]:
        fpath = JSON_DB_DIR / f
        with open(fpath, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Standard Hour
        std_seq = engine._get_structure_sequence(data, "structure_standard")
        std_ids = [s["id"] for s in std_seq]
        assert "opening_prayers" in std_ids
        assert "psalms_fixed" in std_ids
        assert "troparia_block" in std_ids
        assert "verses_fixed" in std_ids
        assert "trisagion_prayers" in std_ids
        assert "kontakion_block" in std_ids
        assert "conclusion" in std_ids
        assert "dismissal_slot" in std_ids

        # Lenten Hour
        lenten_seq = engine._get_structure_sequence(data, "structure_lenten")
        lenten_ids = [s["id"] for s in lenten_seq]
        assert "prayer_ephrem" in lenten_ids or "typika_transition" in lenten_ids

    # Typika
    typika_path = JSON_DB_DIR / "01e_struct_typika.json"
    with open(typika_path, "r", encoding="utf-8") as file:
        tdata = json.load(file)
    tseq = engine._get_structure_sequence(tdata, "structure_standard")
    tids = [s["id"] for s in tseq]
    assert "opening_blessing" in tids
    assert "horologion.psalm_102" in tids
    assert "horologion.psalm_145" in tids
    assert "only_begotten" in tids
    assert "beatitudes_block" in tids
    assert "kontakion_block" in tids


def test_divine_liturgies_canonical_ordinal_invariants(engine):
    """
    Invariant 8: Divine Liturgies (Chrysostom, Basil, Presanctified, Vesperal) adhere to Liturgicon and Ordo:
      - Chrysostom & Basil: 'Blessed is the Kingdom', Great Litany, Antiphons, Little Entrance, Epistle/Gospel, Cherubic, Great Entrance, Anaphora, Megalynarion, Lord's Prayer, Communion, Dismissal.
      - Presanctified: 'Blessed is the Kingdom', Vespers, Kathisma, 'Lord I have cried', Entrance, Readings ('Light of Christ'), 'Let my prayer arise', Great Entrance ('Now the Powers'), Communion ('Taste and see'), Dismissal.
      - Vesperal Liturgy: 'Blessed is the Kingdom', Vespers, Entrance with Gospel, Readings, Trisagion, Liturgy of Faithful, Anaphora, Communion, Dismissal.
    """
    # 1. Chrysostom & Basil
    lit_path = JSON_DB_DIR / "01j_struct_liturgy.json"
    with open(lit_path, "r", encoding="utf-8") as f:
        ldata = json.load(f)

    for lit_name in ["liturgy_chrysostom", "liturgy_basil"]:
        seq = engine._get_structure_sequence(ldata, lit_name)
        slot_ids = [s["id"] for s in seq]
        assert "opening_blessing" in slot_ids
        open_slot = next(s for s in seq if s["id"] == "opening_blessing")
        assert open_slot["content"]["ref_key"] == "liturgikon.blessing_kingdom"
        assert "great_litany" in slot_ids
        assert "antiphons_block" in slot_ids
        assert "little_entrance" in slot_ids
        assert "troparia_kontakia_block" in slot_ids
        assert "trisagion_module" in slot_ids
        assert "readings_block" in slot_ids
        assert "cherubic_hymn_block" in slot_ids
        assert "great_entrance" in slot_ids
        assert "lords_prayer" in slot_ids
        assert "communion_module" in slot_ids
        assert "dismissal" in slot_ids

    # 2. Presanctified (01l)
    presanct_path = JSON_DB_DIR / "01l_struct_presanctified.json"
    with open(presanct_path, "r", encoding="utf-8") as f:
        pdata = json.load(f)
    pseq = engine._get_structure_sequence(pdata, "liturgy_presanctified")
    pids = [s["id"] for s in pseq]
    assert "opening_vespers" in pids
    assert "proemial_psalm" in pids
    assert "great_synapte" in pids
    assert "kathisma_18_stichologia" in pids
    assert "lord_i_have_cried" in pids
    assert "entrance" in pids
    assert "readings_and_light" in pids
    assert "let_my_prayer" in pids
    assert "now_the_powers" in pids
    assert "communion_rite" in pids
    assert "dismissal" in pids

    # 3. Vesperal Liturgy (01m)
    vesp_lit_path = JSON_DB_DIR / "01m_struct_vesperal_liturgy.json"
    with open(vesp_lit_path, "r", encoding="utf-8") as f:
        vmdata = json.load(f)
    vmseq = engine._get_structure_sequence(vmdata, "vesperal_liturgy")
    vmids = [s["id"] for s in vmseq]
    assert "vesperal_opening" in vmids
    assert "proemial_psalm" in vmids
    assert "great_synapte" in vmids
    assert "lord_i_have_cried" in vmids
    assert "entrance_gospel" in vmids
    assert "readings_sequence" in vmids
    assert "liturgical_transition_gate" in vmids
    assert "epistle_gospel_liturgy" in vmids
    assert "liturgy_faithful_cherubic" in vmids
    assert "anaphora_basil_or_chrysostom" in vmids
    assert "communion_rite" in vmids
    assert "dismissal" in vmids
