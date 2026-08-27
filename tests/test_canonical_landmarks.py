"""
Ground-Truth Canonical Landmarks Tests against Dolnytsky Parts I-V and 2010 Lviv Typikon.
"""

import pytest
import datetime
from ruthenian_engine import RuthenianEngine
from digest import TypikonDigestGenerator

@pytest.fixture(scope="module")
def engine():
    return RuthenianEngine(version="royal_doors")

@pytest.fixture(scope="module")
def generator(engine):
    return TypikonDigestGenerator(engine=engine)


def test_holy_thursday_canonical_contract(engine, generator):
    """
    Validates Great and Holy Thursday (April 2, 2026 / Pascha -3)
    Authority: Dolnytsky Part IV (De Tempore Paschali, Great Thursday)
    """
    cur_date = datetime.date(2026, 4, 2)
    ctx = engine.get_liturgical_context(cur_date)
    rubrics = engine.resolve_rubrics(ctx)
    digest = generator.generate_full_service(ctx, rubrics)

    # 1. POSITIVE ASSERTIONS
    assert "GREAT AND HOLY THURSDAY" in digest
    assert "Great Thursday Triode from the Triodion" in digest
    assert "Kontakion of Great Thursday" in digest
    assert "Behold, the Bridegroom" in digest
    assert "When the glorious disciples were enlightened" in digest
    assert "Luke" in digest
    assert "Canon of St. Cosmas on 6" in digest
    assert "Come, O faithful, let us enjoy the Master's hospitality" in digest
    assert "(twice); Glory, Both now: once more the same" in digest
    assert "Jeremiah" in digest
    assert "10 Stichera from the Triodion" in digest
    assert "The Lamb, foretold by Isaiah" in digest
    assert "Truly, Judas is the son" in digest
    assert "Exodus" in digest
    assert "Job" in digest
    assert "Isaiah" in digest
    assert "1 Corinthians" in digest
    assert "Matthew" in digest
    assert "Of Thy Mystical Supper" in digest

    # 2. STRICT NEGATIVE PROHIBITIONS (Must NEVER appear on Holy Thursday)
    assert "Thursday service combined with" not in digest
    assert "Troparion of the Temple" not in digest
    assert "O God of our fathers" not in digest
    assert "Doxastikon of the Saint" not in digest
    assert "Theotokion from the Horologion or Octoechos" not in digest
    assert '**Post-Communion Hymn:** "We have seen' not in digest
    assert "We have seen the true light, we have received" not in digest
    assert "Let our mouths be filled with Thy praise" not in digest


def test_holy_friday_canonical_contract(engine, generator):
    """
    Validates Great and Holy Friday (April 3, 2026 / Pascha -2)
    Authority: Dolnytsky Part IV
    """
    cur_date = datetime.date(2026, 4, 3)
    ctx = engine.get_liturgical_context(cur_date)
    rubrics = engine.resolve_rubrics(ctx)
    digest = generator.generate_full_service(ctx, rubrics)

    assert "GREAT AND HOLY FRIDAY" in digest
    assert "TWELVE PASSION GOSPELS" in digest or "Passion Gospels" in digest
    assert "ROYAL HOURS" in digest
    assert "Zechariah" in digest
    assert "Galatians" in digest
    assert "HOLY SHROUD" in digest
    assert "The noble Joseph" in digest

    # NEGATIVE
    assert "Friday service combined with" not in digest
    assert "Divine Liturgy of St. John Chrysostom" not in digest
    assert "Divine Liturgy of St. Basil" not in digest


def test_holy_saturday_canonical_contract(engine, generator):
    """
    Validates Great and Holy Saturday (April 4, 2026 / Pascha -1)
    Authority: Dolnytsky Part IV
    """
    cr_date = datetime.date(2026, 4, 4)
    ctx = engine.get_liturgical_context(cr_date)
    rubrics = engine.resolve_rubrics(ctx)
    digest = generator.generate_full_service(ctx, rubrics)


    assert "GREAT AND HOLY SATURDAY" in digest
    assert "JERUSALEM MATINS" in digest or "Lamentations" in digest
    assert "Ezekiel" in digest
    assert "VESPERAL KITURGY" in digest or "St. Basil" in digest

    # NEGATIVE
    assert "Saturday service combined with" not in digest


def test_pascha_bright_week_canonical_contract(engine, generator):
    """
    Validates Pascha Sunday (April 5, 2026 / Pascha 0)
    Authority: Dolgytsky Part IV
    """
    pascha_date = datetime.date(2026, 4, 5)
    ctx = engine.get_liturgical_context(pascha_date)
    rubrics = engine.resolve_rubrics(ctx)
    digest = generator.generate_full_service(ctx, rubrics)

    assert "Christ is risen from the dead" in digest
    assert "PASCHAL MATINS" in digest
    assert "PASCHAL HOURS" in digest
    assert "DIVINE LITURGY" in digest
    assert "baptized" in digest.lower()

    # REST SUNDAY RESTICTIONS
    assert "Six Psalms" not in digest
    assert "Trisagion prayers" not in digest
    assert "Kathisma 1" not in digest
