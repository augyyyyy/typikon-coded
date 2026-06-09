import pytest
import os
from ruthenian_engine import RuthenianEngine

def test_regional_chant_mixin_methods():
    # Initialize engine
    engine = RuthenianEngine(base_dir=".")
    
    # 1. Verify mixin methods are present
    assert hasattr(engine, "load_regional_chant_rules")
    assert hasattr(engine, "get_regional_chant_override")
    assert hasattr(engine, "get_solmization_guide")
    assert hasattr(engine, "get_neume_execution_rules")

def test_load_regional_chant_rules():
    engine = RuthenianEngine(base_dir=".")
    rules = engine.load_regional_chant_rules()
    
    # Verify rules are loaded and structured correctly
    assert isinstance(rules, dict)
    assert rules.get("project") == "Kyivan Musicology"
    assert "solmization_rules" in rules
    assert "neume_rules" in rules
    assert "regional_dialects" in rules

def test_regional_chant_overrides():
    engine = RuthenianEngine(base_dir=".")
    
    # Suprasl Overrides
    context_suprasl = {"regional_tradition": "suprasl", "tone": 1}
    psalm_103_suprasl = engine.get_regional_chant_override(context_suprasl, "psalm_103")
    assert psalm_103_suprasl is not None
    assert psalm_103_suprasl["style"] == "Suprasl Chant (prolonged)"
    assert psalm_103_suprasl["structure"] == "Through-composed (no verse/word repetitions)"
    assert 15 in psalm_103_suprasl["selected_verses"]
    assert 24 in psalm_103_suprasl["selected_verses"]

    blessed_suprasl = engine.get_regional_chant_override(context_suprasl, "blessed_is_the_man")
    assert blessed_suprasl["structure"] == "Through-composed (no repetitions of verses/words)"

    polyeleos_suprasl = engine.get_regional_chant_override(context_suprasl, "polyeleos")
    assert "Multanian" in polyeleos_suprasl["style"]

    # Zhirovitsi Overrides
    context_zhirovitsi = {"regional_tradition": "zhirovitsi", "tone": 1}
    polyeleos_zhirovitsi = engine.get_regional_chant_override(context_zhirovitsi, "polyeleos")
    assert polyeleos_zhirovitsi is not None
    assert "Bulgarian & Pidhirya" in polyeleos_zhirovitsi["style"]

    # Manyava Skete Overrides
    context_skete = {"regional_tradition": "manyava_skete", "tone": 1}
    canon_skete = engine.get_regional_chant_override(context_skete, "eucharistic_canon")
    assert canon_skete is not None
    assert "Skete Chant" in canon_skete["style"]

    # Lyubachiv Overrides
    context_lyubachiv = {"regional_tradition": "lyubachiv", "tone": 1}
    god_lord_lyubachiv = engine.get_regional_chant_override(context_lyubachiv, "god_is_the_lord")
    assert god_lord_lyubachiv is not None
    assert "Triple Chant" in god_lord_lyubachiv["style"]

def test_solmization_guide():
    engine = RuthenianEngine(base_dir=".")
    
    # Dural
    dural_guide = engine.get_solmization_guide(tone=1, is_bemoliar=False)
    assert dural_guide is not None
    assert dural_guide["hexachord_type"] == "Hard (Dural) Hexachord"
    assert "C" in dural_guide["scale_steps"]
    assert dural_guide["semitone_anchors"]["fa_pitch"] == "C"

    # Bemoliar
    bemoliar_guide = engine.get_solmization_guide(tone=1, is_bemoliar=True)
    assert bemoliar_guide is not None
    assert bemoliar_guide["hexachord_type"] == "Soft (Bemoliar) Hexachord"
    assert "B" in bemoliar_guide["scale_steps"]
    assert bemoliar_guide["semitone_anchors"]["fa_pitch"] == "B"

def test_neume_rules():
    engine = RuthenianEngine(base_dir=".")
    
    pauk_rules = engine.get_neume_execution_rules("pauk")
    assert pauk_rules is not None
    assert "pauk" in pauk_rules["names"]
    assert "phrase or line concluding cadence formula" in pauk_rules["function"].lower()
