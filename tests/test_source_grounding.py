import inspect
import os
import re
from pathlib import Path
import pytest

from engine.resolvers.matins import MatinsMixin
from engine.resolvers.liturgy import LiturgyMixin
from engine.resolvers.vespers import VespersMixin
from engine.resolvers.hours import HoursMixin
from engine.resolvers.ceremonial import CeremonialMixin
from engine.resolvers.common import CommonResolverMixin
from engine.resolvers.compline import ComplineMixin
from engine.resolvers.lenten import LentenMixin

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestSourceGrounding:

    def test_resolvers_are_grounded(self):
        """
        Ensures that every strictly enforced 'resolve_' function has the @liturgical_source decorator
        AND that every @liturgical_source citation resolves to real lines/sections/paragraphs in
        Dolnytsky_Typikon_Master.md and Ordo_Celebrationis_1996_CLEAN.md at runtime (SGC-02).
        """
        dolnytsky_path = (
            PROJECT_ROOT / "Data" / "Service Books" / "Typikon" / "Dolnytsky_Typikon_Master.md"
        )
        ordo_path = (
            PROJECT_ROOT
            / "Data"
            / "Service Books"
            / "Typikon"
            / "Ordo"
            / "Ordo_Celebrationis_1996_CLEAN.md"
        )

        with open(dolnytsky_path, "r", encoding="utf-8") as f:
            dolnytsky_lines = f.read().splitlines()
        with open(ordo_path, "r", encoding="utf-8") as f:
            ordo_lines = f.read().splitlines()

        methods = []
        for mixin in (
            MatinsMixin,
            LiturgyMixin,
            VespersMixin,
            HoursMixin,
            CeremonialMixin,
            CommonResolverMixin,
            ComplineMixin,
            LentenMixin,
        ):
            methods.extend(inspect.getmembers(mixin, predicate=inspect.isfunction))

        missing_decorators = []
        missing_ordo = []
        broken_line_anchors = []

        strictly_enforced_functions = [
            "resolve_service_type",
            "resolve_god_is_lord_tone",
            "calculate_canon_ratios",
            "resolve_canon_combination",
            "get_katavasia",
            "get_eothinon_exapostilarion",
            "resolve_praises",
            "get_eothinon_doxastikon",
            "resolve_doxology",
            "resolve_dismissal",
            "resolve_dismissal_troparion",
            "resolve_vesperal_liturgy_readings",
            "resolve_beatitudes",
            "resolve_12_passion_gospels",
            "resolve_passion_vespers_readings",
            "resolve_typika_kontakia",
            "resolve_royal_psalms",
            "resolve_royal_stichera",
            "resolve_royal_readings",
            "resolve_royal_troparia",
            "resolve_royal_kontakion",
            "check_royal_hours_trigger",
            "resolve_trisagion_type",
            "resolve_basil_megalynarion",
            "resolve_communion_hymn",
            "resolve_post_communion_hymn",
            "resolve_liturgy_readings",
            "resolve_reading_ot",
            "resolve_reading_epistle",
            "resolve_reading_gospel",
        ]

        seen_decorated = 0
        for name, func in methods:
            if name in strictly_enforced_functions and not hasattr(func, "__liturgical_source__"):
                missing_decorators.append(name)

            if hasattr(func, "__liturgical_source__"):
                seen_decorated += 1
                source_meta = func.__liturgical_source__
                if name in ["resolve_doxology", "resolve_dismissal", "resolve_12_passion_gospels"]:
                    if not source_meta.get("ordo"):
                        missing_ordo.append(name)

                # Runtime SGC-02 line-range & paragraph verification against primary source files
                ordo_cit = source_meta.get("ordo")
                if ordo_cit:
                    line_ranges = [
                        (int(m.group(1)), int(m.group(2) or m.group(1)))
                        for m in re.finditer(r"L(\d+)(?:-(\d+))?", ordo_cit)
                    ]
                    if not line_ranges:
                        broken_line_anchors.append(f"{name}: Ordo citation '{ordo_cit}' lacks L<start>-<end>")
                    for s_l, e_l in line_ranges:
                        if s_l < 1 or e_l > len(ordo_lines) or s_l > e_l:
                            broken_line_anchors.append(
                                f"{name}: Ordo line range L{s_l}-{e_l} out of bounds"
                            )
                        elif not "\n".join(ordo_lines[s_l - 1 : e_l]).strip():
                            broken_line_anchors.append(
                                f"{name}: Ordo line range L{s_l}-{e_l} is blank"
                            )

                    # Verify §<N> exists inside the cited Ordo line slices
                    sliced_ordo = "\n".join(
                        "\n".join(ordo_lines[s_l - 1 : e_l]) for s_l, e_l in line_ranges
                    )
                    for m_p in re.finditer(r"§(\d+)", ordo_cit):
                        p_num = int(m_p.group(1))
                        if not re.search(rf"^#####\s+{p_num}\.\s+", sliced_ordo, re.MULTILINE):
                            broken_line_anchors.append(
                                f"{name}: Ordo §{p_num} not found inside cited lines {line_ranges}"
                            )

                dol_cit = source_meta.get("dolnytsky")
                if dol_cit:
                    line_ranges = [
                        (int(m.group(1)), int(m.group(2) or m.group(1)))
                        for m in re.finditer(r"L(\d+)(?:-(\d+))?", dol_cit)
                    ]
                    if not line_ranges:
                        broken_line_anchors.append(
                            f"{name}: Dolnytsky citation '{dol_cit}' lacks L<start>-<end>"
                        )
                    for s_l, e_l in line_ranges:
                        if s_l < 1 or e_l > len(dolnytsky_lines) or s_l > e_l:
                            broken_line_anchors.append(
                                f"{name}: Dolnytsky line range L{s_l}-{e_l} out of bounds"
                            )
                        elif not "\n".join(dolnytsky_lines[s_l - 1 : e_l]).strip():
                            broken_line_anchors.append(
                                f"{name}: Dolnytsky line range L{s_l}-{e_l} is blank"
                            )

        assert seen_decorated >= 50
        assert not missing_decorators, (
            f"STRICT MODE FAIL: Functions lacking @liturgical_source: {list(set(missing_decorators))}"
        )
        assert not missing_ordo, (
            f"STRICT MODE FAIL: Choreographic functions lacking Ordo citation: {list(set(missing_ordo))}"
        )
        assert not broken_line_anchors, (
            f"SGC-02 LINE ANCHOR FAIL:\n" + "\n".join(broken_line_anchors)
        )

    def test_no_hardcoded_verses_in_formatter(self):
        """
        Verify that no hardcoded Elizabethan/arbitrary prokeimena verses exist in digest/formatters/common.py,
        and that it relies on dynamic lookups from the Horologion assets instead.
        """
        formatter_path = os.path.join("digest", "formatters", "common.py")
        with open(formatter_path, "r", encoding="utf-8") as f:
            content = f.read()

        banned_strings = [
            "hath girded Himself",
            "Holiness becometh Thy house",
            "Hearken unto my soul",
            "Thy salvation, O God, shall uphold me",
            "Let the poor see and be glad",
            "Thou hast made Thy power known",
            "barbarous people",
            "Thy wonders from the beginning",
        ]

        found_banned = [s for s in banned_strings if s in content]
        assert not found_banned, (
            f"Audit Fail: Hardcoded legacy prokeimena verses found in {formatter_path}: {found_banned}"
        )

        assert "horologion.psalm_116" in content, "Audit Fail: horologion.psalm_116 lookup is missing in common.py"
        assert "horologion.psalm_68" in content, "Audit Fail: horologion.psalm_68 lookup is missing in common.py"
        assert "saint_categories" in content, "Audit Fail: saint_categories lookup is missing in sessional formatter"
        assert "Venerable Woman" in content, "Audit Fail: Venerable Woman mapping is missing in sessional formatter"
        assert "Venerable Mother" in content, "Audit Fail: Venerable Mother mapping is missing in sessional formatter"
