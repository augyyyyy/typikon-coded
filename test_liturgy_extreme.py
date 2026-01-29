import pytest
from ruthenian_engine import RuthenianEngine

@pytest.fixture
def engine():
    return RuthenianEngine(".")

def test_LT1_sunday_saint_temple_stack(engine):
    """
    Scenario: Sunday in St. Nicholas Temple (Saint Patron).
    Expect: Res Trop, Temple Trop, Saint Trop, Res Kont, Glory Saint Kont, Both Now Temple Kont.
    """
    context = {"day_of_week": 0, "temple_type": "saint", "is_afterfeast": False}
    result = engine.resolve_liturgy_hymns(context, {})
    comps = result["components"]
    
    assert len(comps) == 6 # Res, Tpl, St, ResK, StK, TplK
    assert comps[1]["source"] == "temple" # Trop
    assert comps[-1]["source"] == "temple" # Both Now should be Temple Kontakion

def test_LT2_sunday_theotokos_temple_stack(engine):
    """
    Scenario: Sunday in Dormition Temple (Theotokos Patron).
    Expect: Res Trop, Temple Trop, Saint Trop, Res Kont, Glory Saint Kont, Both Now Steadfast Protectress.
    """
    context = {"day_of_week": 0, "temple_type": "theotokos", "is_afterfeast": False}
    result = engine.resolve_liturgy_hymns(context, {})
    comps = result["components"]
    
    # Check that Temple Kontakion is NOT present as 'Both Now', instead Steadfast Protectress
    sources = [c.get("key", c.get("source")) for c in comps]
    assert "steadfast_protectress" in sources
    assert sources[-1] == "steadfast_protectress"

def test_LT3_afterfeast_suppression(engine):
    """
    Scenario: Afterfeast present.
    Expect: "Both Now" logic excludes Temple/Steadfast. 
    (Note: In a full engine, we'd inject the Feast Kontakion here, but for now we verify suppression).
    """
    context = {"day_of_week": 0, "temple_type": "saint", "is_afterfeast": True}
    result = engine.resolve_liturgy_hymns(context, {})
    comps = result["components"]
    
    # Logic: Template has condition "not is_afterfeast". 
    # So the last item (Temple Both Now) should be stripped.
    # In reality, the engine stacker would append the Feast Kontakion externally or via a separate rule.
    # Here we verify the 'template' filter worked.
    sources = [c["source"] for c in comps]
    assert "temple" in sources # Trop is there
    # The last element in the template was temple_kontakion (Both Now)
    # It should be gone.
    # Wait, in Sunday Saint Temple: [Res, Tpl, St, ResK, StK, TplK, Steadfast]
    # Actually my template had TplK as Both Now.
    assert comps[-1]["source"] != "temple" 

def test_LT4_dismissal_theophany(engine):
    """
    Scenario: Theophany Dismissal Preamble.
    """
    context = {"title": "Theophany", "day_of_week": 2}   
    result = engine.resolve_liturgy_dismissal(context, {})
    assert "baptized by John" in result["content"]

def test_LT5_dismissal_sunday_standard(engine):
    """
    Scenario: Standard Sunday Dismissal (Rose from the dead).
    """
    context = {"day_of_week": 0, "title": "Sunday"}
    result = engine.resolve_liturgy_dismissal(context, {})
    assert "rose from the dead" in result["content"]
    assert "baptized" not in result["content"]
