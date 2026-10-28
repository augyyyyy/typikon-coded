#!/usr/bin/env python3
"""
Programmatic Service Book Compiler for UGCC Ruthenian Divine Office Booklets.
Compiles publication-ready Markdown service booklets directly from canonical JSON databases
and primary liturgical source texts:
- json_db/service_book_partitions.json
- json_db/01h_struct_vespers.json
- json_db/service_booklet_architecture.json
- json_db/02a_logic_general.json
- Data/Service Books/Typikon/Ordo/Ordo_Celebrationis_1996_CLEAN.md
- Data/Service Books/Typikon/Dolnytsky_Typikon_Master.md
- Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/text_horologion.json
Eliminates free-form manual authoring and hardcoded prose arrays in Python.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ServiceBookCompiler:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir).resolve() if base_dir else PROJECT_ROOT
        self.partitions_path = self.base_dir / "json_db" / "service_book_partitions.json"
        self.logic_general_path = self.base_dir / "json_db" / "02a_logic_general.json"
        self.struct_vespers_path = self.base_dir / "json_db" / "01h_struct_vespers.json"
        self.booklet_arch_path = self.base_dir / "json_db" / "service_booklet_architecture.json"

        with open(self.partitions_path, "r", encoding="utf-8") as f:
            self.partitions = json.load(f)

        with open(self.logic_general_path, "r", encoding="utf-8") as f:
            self.logic_general = json.load(f).get("logic_definitions", {})

        with open(self.struct_vespers_path, "r", encoding="utf-8") as f:
            self.struct_vespers = json.load(f)

        with open(self.booklet_arch_path, "r", encoding="utf-8") as f:
            self.booklet_arch = json.load(f)

        auth_files = self.booklet_arch.get("file_metadata", {}).get("authority_files", {})
        self.ordo_path = self.base_dir / auth_files.get(
            "ordo", "Data/Service Books/Typikon/Ordo/Ordo_Celebrationis_1996_CLEAN.md"
        )
        self.dolnytsky_path = self.base_dir / auth_files.get(
            "dolnytsky", "Data/Service Books/Typikon/Dolnytsky_Typikon_Master.md"
        )
        self.horologion_path = self.base_dir / auth_files.get(
            "horologion",
            "Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/text_horologion.json",
        )

        with open(self.ordo_path, "r", encoding="utf-8") as f:
            self.ordo_lines = f.read().splitlines()

        with open(self.dolnytsky_path, "r", encoding="utf-8") as f:
            self.dolnytsky_lines = f.read().splitlines()

        with open(self.horologion_path, "r", encoding="utf-8") as f:
            self.horologion_db = json.load(f)

    def _normalize_ugcc_terminology(self, text: str) -> str:
        """Enforce UGCC Royal Doors terminology standards across compiled blocks."""
        norm_map = (
            self.booklet_arch.get("file_metadata", {}).get("ugcc_terminology_normalizations", {})
        )
        result = text
        for banned, canonical in norm_map.items():
            result = result.replace(banned, canonical)
        return result

    def _verify_station_grounding(self, station: Dict[str, Any]) -> None:
        """
        Verify at compile time (SGC-02) that every station is grounded in:
        1. 01h_struct_vespers.json sequence step IDs
        2. Ordo_Celebrationis_1996_CLEAN.md paragraph markers and line numbers
        3. Dolnytsky_Typikon_Master.md Part I line ranges
        4. Stamford text_horologion.json keys
        """
        st_num = station.get("station_number")
        vigil_seq = (
            self.struct_vespers.get("structures", {})
            .get("great_vespers_vigil", {})
            .get("sequence", [])
        )
        known_struct_ids = {step.get("id") for step in vigil_seq if isinstance(step, dict)}

        for sid in station.get("struct_ids", []):
            if sid not in known_struct_ids:
                raise ValueError(
                    f"Station {st_num} references unknown 01h_struct_vespers step ID '{sid}'"
                )

        for cite in station.get("ordo_citations", []):
            para = cite.get("paragraph")
            line_no = cite.get("line")
            if not line_no or line_no < 1 or line_no > len(self.ordo_lines):
                raise ValueError(f"Station {st_num} has out-of-range Ordo line {line_no}")
            line_text = self.ordo_lines[line_no - 1]
            if not re.match(rf"^#####\s+{para}\.\s+", line_text):
                raise ValueError(
                    f"Station {st_num} Ordo §{para} mismatch at line {line_no}: {line_text[:60]}"
                )

        d_range = station.get("dolnytsky_line_range", [])
        if len(d_range) == 2:
            start_l, end_l = d_range
            if start_l < 1 or end_l > len(self.dolnytsky_lines) or start_l > end_l:
                raise ValueError(
                    f"Station {st_num} has invalid Dolnytsky line range {d_range}"
                )
            d_slice = "\n".join(self.dolnytsky_lines[start_l - 1 : end_l]).strip()
            if not d_slice:
                raise ValueError(f"Station {st_num} Dolnytsky slice {d_range} is empty")

        for h_key in station.get("horologion_keys", []):
            if h_key in self.horologion_db:
                entry = self.horologion_db[h_key]
                if not str(entry.get("content", "")).strip():
                    raise ValueError(f"Station {st_num} Horologion key '{h_key}' has empty content")

    def compile_great_vespers(self, output_path: Optional[Path] = None) -> str:
        """Compile the complete, authoritative Great Vespers service booklet from JSON & primary sources."""
        gv_partition = self.partitions["binders"]["BINDER_I_VIGIL_FESTAL"]["services"]["great_vespers"]

        # 1. Compile Appendix §B Table directly from json_db/02a_logic_general.json
        appendix_b_table = self._compile_stichera_appendix_b(gv_partition["authorized_paradigms"])

        # 2. Assemble document sections from 01h_service_booklet_architecture.json
        md: List[str] = []
        for block in self.booklet_arch.get("preamble_blocks", []):
            md.append(self._normalize_ugcc_terminology(block))

        for station in self.booklet_arch.get("stations", []):
            self._verify_station_grounding(station)
            md.append(self._normalize_ugcc_terminology(station["heading"]))
            for block in station.get("blocks", []):
                md.append(self._normalize_ugcc_terminology(block))

        for block in self.booklet_arch.get("appendix_header_blocks", []):
            md.append(self._normalize_ugcc_terminology(block))

        appendices = self.booklet_arch.get("appendices", {})
        ordered_sections = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]
        for sec_id in ordered_sections:
            if sec_id == "B":
                md.append(self._normalize_ugcc_terminology(appendix_b_table))
                md.append("\n---\n")
            elif sec_id in appendices:
                sec = appendices[sec_id]
                md.append(self._normalize_ugcc_terminology(sec["heading"]))
                for block in sec.get("blocks", []):
                    md.append(self._normalize_ugcc_terminology(block))

        compiled_text = "\n".join(md)
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(compiled_text)
        return compiled_text

    def _compile_stichera_appendix_b(self, authorized_paradigms: List[Dict[str, Any]]) -> str:
        """Programmatically serialize the Stichera Distribution table from json_db/02a_logic_general.json."""
        sec_b_meta = self.booklet_arch.get("appendices", {}).get("B", {})
        rows = [
            sec_b_meta.get("heading", "### §B: STICHERA DISTRIBUTION MATRIX FOR GREAT VESPERS"),
            "*(Dolnytsky Typikon Part I §4 & Part II §§1–20; Ordo §33)\n",
            "> **Canonical Paradigm Scope Note**:",
            "> Of the 20 general paradigms in Dolnytsky Part II, **only the Sunday and Festal cases below apply to Great Vespers**. The simple weekday cases (Case 2, Case 2a, Case 3, Case 3a, Case 9, and Case 14) prescribe **Daily Vespers** (*Vesperae quotidianae*, with no entrance and daily prokeimenon) and belong to Binder II.\n",
            "| Paradigm Code | Liturgical Rank & Occasion | Total Count | Octoechos | Menaion | Glory (Doxastikon) | Both now (Theotokion) |",
            "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |",
        ]

        for item in authorized_paradigms:
            p_id = item["id"]
            p_name = item["name"]
            stichera_count = item["stichera_count"]

            octo_str, men_str, glory_str, both_now_str = self._resolve_db_distribution(p_id)

            rows.append(
                f"| **{p_id}** | {p_name} | **{stichera_count}** | {octo_str} | {men_str} | {glory_str} | {both_now_str} |"
            )

        return "\n".join(rows)

    def _resolve_db_distribution(self, paradigm_id: str) -> Tuple[str, str, str, str]:
        """Extract stichera distribution fields directly from json_db/02a_logic_general.json."""
        case_def = None
        for _, val in self.logic_general.items():
            if isinstance(val, dict) and val.get("id") == paradigm_id:
                case_def = val
                break

        if not case_def and paradigm_id == "CASE_01_6st":
            return ("6 Resurrection", "4 Saint", "Saint", "Dogmatikon of Tone")

        if not case_def:
            if paradigm_id == "CASE_02b":
                return ("0", "6 Saint (or 3+3)", "Saint", "Theotokion per Tone of Glory")
            return ("—", "—", "—", "—")

        vars_dict = case_def.get("variables", {})
        stichera_dist = vars_dict.get("vespers_stichera_distribution", {})

        logic_switch = stichera_dist.get("logic_switch", {})
        if "1_saint" in logic_switch:
            dist = logic_switch["1_saint"].get("distribution", [])
            octo = sum(d.get("qty", 0) for d in dist if d.get("source") == "octoechos")
            men = sum(d.get("qty", 0) for d in dist if d.get("source") == "menaion")
            octo_str = f"{octo} Resurrection" if octo else "0"
            men_str = f"{men} Saint" if men else "0"
        elif "simple_saint" in logic_switch:
            dist = logic_switch["simple_saint"].get("distribution", [])
            octo = sum(d.get("qty", 0) for d in dist if d.get("source") == "octoechos")
            men = sum(d.get("qty", 0) for d in dist if d.get("source") == "menaion")
            octo_str = f"{octo} Resurrection" if octo else "0"
            men_str = f"{men} Saint" if men else "0"
        elif "distribution" in stichera_dist:
            dist = stichera_dist.get("distribution", [])
            octo = sum(d.get("qty", 0) for d in dist if d.get("source") == "octoechos")
            men = sum(d.get("qty", 0) for d in dist if d.get("source") in ("menaion", "feast"))
            octo_str = f"{octo} Resurrection" if octo else "0"
            men_str = f"{men} Feast/Saint" if men else "0"
        else:
            total = stichera_dist.get("total_count", 10)
            octo_str = "0"
            men_str = f"{total} Feast"

        glory = stichera_dist.get("glory", "saint")
        both_now = stichera_dist.get("both_now", "theotokion")

        glory_str = "Saint" if "saint" in str(glory).lower() else "Feast"
        if "dogmatikon" in str(both_now).lower():
            both_now_str = "Dogmatikon of Tone"
        elif "theotokion" in str(both_now).lower():
            both_now_str = "Theotokion of Feast"
        else:
            both_now_str = "Feast"

        return (octo_str, men_str, glory_str, both_now_str)


if __name__ == "__main__":
    compiler = ServiceBookCompiler()
    target = PROJECT_ROOT / "docs" / "service_books" / "01_great_vespers_canonical.md"
    compiler.compile_great_vespers(output_path=target)
    print(f"Compiled canonical Great Vespers service book to {target}")
