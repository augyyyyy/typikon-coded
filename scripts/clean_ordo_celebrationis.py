#!/usr/bin/env python3
"""
Clean and structure the 1996 English Ordo Celebrationis OCR transcription.

Transforms the RAW OCR file into a properly tagged, machine-readable
master reference document with:
- Structural section/variant markers
- Normalized footnotes
- Page numbers and running headers stripped
- Illustration captions tagged
- OCR line-break artifacts fixed

Input:  Data/Service Books/Ordo/1996 ENG RAW Ordo Celebrationis.txt
Output: Data/Service Books/Ordo/Ordo_Celebrationis_1996_CLEAN.txt
"""

import re
import os

INPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Data", "Service Books", "Ordo", "1996 ENG RAW Ordo Celebrationis.txt"
)
OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Data", "Service Books", "Ordo", "Ordo_Celebrationis_1996_CLEAN.txt"
)

# ─── Running headers to strip (exact match after stripping whitespace) ───
RUNNING_HEADERS = {
    "Ordo Celebrationis",
    "I. Preliminary Notes",
    "II. The Order of Vespers When There Is No Vigil[39]",
    "III. The Order of Vespers With All-Night Vigil[86]",
    "IV. The Order of Orthros for Sundays and Feast Days",
    "V. Order of the Divine Liturgies",
    "V. Order of the Divine Liturgy of Saint John Chrysostom and Saint Basil the",
    "VI. Order of the Divine Liturgy of the Presanctified Gifts",
    "Glossary",
    "Appendix",
    "Notes",
}

# ─── Page numbers: standalone lines that are just a roman or arabic numeral ───
PAGE_NUM_PATTERN = re.compile(
    r"^\s*(?:[ivxlcdm]+|[0-9]{1,3})\s*$", re.IGNORECASE
)

# ─── Section headers to auto-tag ───
SECTION_MARKERS = [
    # Major sections
    (r"^I\.\s*Preliminary Notes\s*$",
     "=== SECTION I: PRELIMINARY NOTES ==="),
    (r"^II\.\s*The Order of Vespers When There Is No Vigil",
     "=== SECTION II: VESPERS WITHOUT VIGIL ==="),
    (r"^III\.\s*The Order of Vespers With All-Night Vigil",
     "=== SECTION III: VESPERS WITH ALL-NIGHT VIGIL ==="),
    (r"^IV\.\s*The Order of Orthros for Sundays and Feast Days",
     "=== SECTION IV: ORTHROS FOR SUNDAYS AND FEAST DAYS ==="),
    (r"^V\.\s*Order of the Divine Liturgy of Saint John Chrysostom",
     "=== SECTION V: DIVINE LITURGY (CHRYSOSTOM & BASIL) ==="),
    (r"^VI\.\s*Order of the Divine Liturgy of the Presanctified Gifts",
     "=== SECTION VI: LITURGY OF THE PRESANCTIFIED GIFTS ==="),
    (r"^Glossary\s*$",
     "=== GLOSSARY ==="),
    (r"^Notes to Chapter I\s*$",
     "=== NOTES ===\n\n--- Notes to Chapter I ---"),
    (r"^Notes to Chapter II\s*$",
     "--- Notes to Chapter II ---"),
    (r"^Notes to Chapter III\s*$",
     "--- Notes to Chapter III ---"),
    (r"^Notes to Chapter IV\s*$",
     "--- Notes to Chapter IV ---"),
    (r"^Notes to Chapter V\s*$",
     "--- Notes to Chapter V ---"),
    (r"^Notes to Chapter VI\s*$",
     "--- Notes to Chapter VI ---"),
    (r"^Notes to the Appendix\s*$",
     "--- Notes to the Appendix ---"),
]

# ─── Clergy variant headers ───
VARIANT_MARKERS = [
    (r"^With the Ministry of One Deacon\s*$",
     "--- VARIANT: With One Deacon ---"),
    (r"^With the Ministry of Two Deacons\s*$",
     "--- VARIANT: With Two Deacons ---"),
    (r"^Without the Ministry of a Deacon\s*$",
     "--- VARIANT: Without a Deacon ---"),
    (r"^With Concelebrating Priests\s*(?:\[.*\])?\s*$",
     "--- VARIANT: With Concelebrating Priests ---"),
    (r"^With One Deacon Serving\s*$",
     "--- VARIANT: With One Deacon ---"),
    (r"^The Order of the Divine Liturgy Celebrated Without Solemnity",
     "--- VARIANT: Simple/Private Liturgy ---"),
    (r"^In Solemn Form\s*$",
     "--- VARIANT: Concelebration – Solemn Form ---"),
    (r"^In the Simple or Private Form\s*$",
     "--- VARIANT: Concelebration – Simple/Private Form ---"),
]

# ─── Illustration captions: lines that describe diagrams/figures ───
ILLUSTRATION_PATTERNS = [
    r"^The (?:priest|deacon|clergy).*(?:cens|stand|recit|read|pray|say|invit|elevat|break|arrang)",
    r"^Arrangement of (?:clergy|the (?:Particles|clergy))",
    r"^Position of Lamb",
    r"^At the \"We Magnify",
    r"^(?:The )?Entrance with",
    r"^The Great Entrance",
    r"^(?:The )?Dismissal at",
    r"^During the (?:Lord's Prayer|Profession of Faith)",
    r"^(?:The )?Ambo Prayer\s*$",
    r"^Elevatrion of the Lamb",  # sic — OCR artifact
    r"^Candlebearer\s+Candlebearer\s*$",
    r"^Priest \d+\s+Priest \d+\s*$",
    r"^(?:Second Deacon\s+)?Celebrant\s+(?:First )?Deacon\s*$",
    r"^Two deacons saying",
]

# ─── Appendix section markers ───
APPENDIX_MARKERS = [
    (r"^I\.\s*$", "--- APPENDIX I: Circular of the Sacred Congregation ---"),
    (r"^II\.\s*$", "--- APPENDIX II: Letter of Bishop Ivancho ---"),
    (r"^III\.\s*$", "--- APPENDIX III: Response from the Sacred Congregation ---"),
    (r"^IV\.\s*$", "--- APPENDIX IV: Promulgation Letter of Bishop Mihalik ---"),
]


def is_running_header(line: str) -> bool:
    """Check if line is a running page header."""
    stripped = line.strip()
    return stripped in RUNNING_HEADERS


def is_page_number(line: str) -> bool:
    """Check if line is just a standalone page number."""
    return bool(PAGE_NUM_PATTERN.match(line))


def is_illustration_caption(line: str) -> bool:
    """Check if line is an illustration/diagram caption."""
    stripped = line.strip()
    for pattern in ILLUSTRATION_PATTERNS:
        if re.match(pattern, stripped, re.IGNORECASE):
            return True
    return False


def tag_section(line: str) -> str | None:
    """If line is a section header, return the structural tag."""
    stripped = line.strip()
    for pattern, tag in SECTION_MARKERS:
        if re.match(pattern, stripped):
            return tag
    return None


def tag_variant(line: str) -> str | None:
    """If line is a clergy variant header, return the variant tag."""
    stripped = line.strip()
    for pattern, tag in VARIANT_MARKERS:
        if re.match(pattern, stripped):
            return tag
    return None


def tag_appendix(line: str, in_appendix_section: bool) -> str | None:
    """If line is an appendix marker (I., II., etc.), return the tag."""
    if not in_appendix_section:
        return None
    stripped = line.strip()
    for pattern, tag in APPENDIX_MARKERS:
        if re.match(pattern, stripped):
            return tag
    return None


def fix_line_breaks(lines: list[str]) -> list[str]:
    """
    Rejoin lines that were broken mid-sentence by OCR.
    Heuristic: if a line doesn't end with a period, colon, semicolon,
    question mark, or structural marker, and the next line starts with
    a lowercase letter, join them.
    """
    result = []
    i = 0
    while i < len(lines):
        current = lines[i]
        # Don't merge structural tags, blank lines, or footnotes
        if (current.startswith("===") or current.startswith("---") or
                current.startswith("[ILLUSTRATION:") or
                current.strip() == "" or
                re.match(r"^\[\d+\]", current.strip())):
            result.append(current)
            i += 1
            continue

        # Check if next line should be merged
        while (i + 1 < len(lines) and
               lines[i + 1].strip() and
               not lines[i + 1].startswith("===") and
               not lines[i + 1].startswith("---") and
               not lines[i + 1].startswith("[ILLUSTRATION:") and
               not re.match(r"^\[\d+\]", lines[i + 1].strip()) and
               not re.match(r"^\d+\.\s", lines[i + 1].strip()) and  # §-numbers
               current.strip() and
               not current.strip()[-1] in ".;:?!\")" and
               lines[i + 1].strip()[0:1].islower()):
            current = current.rstrip() + " " + lines[i + 1].strip()
            i += 1

        result.append(current)
        i += 1
    return result


def collapse_blank_lines(lines: list[str]) -> list[str]:
    """Collapse runs of 3+ blank lines down to 1."""
    result = []
    blank_count = 0
    for line in lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 1:
                result.append("")
        else:
            blank_count = 0
            result.append(line)
    return result


def main():
    print(f"Reading: {INPUT_PATH}")
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    print(f"  Raw lines: {len(raw_lines)}")

    # ─── Pass 1: Strip \r\n, remove page numbers & running headers ───
    cleaned = []
    in_appendix = False
    stripped_headers = 0
    stripped_pages = 0

    for line in raw_lines:
        line = line.rstrip("\r\n")
        stripped = line.strip()

        # Track when we enter the Appendix section
        if stripped == "Appendix":
            in_appendix = True

        # Strip running headers
        if is_running_header(line):
            stripped_headers += 1
            continue

        # Strip standalone page numbers
        if is_page_number(line) and len(stripped) <= 4:
            stripped_pages += 1
            continue

        # Tag section headers
        section_tag = tag_section(line)
        if section_tag:
            cleaned.append("")
            cleaned.append(section_tag)
            cleaned.append("")
            continue

        # Tag variant headers
        variant_tag = tag_variant(line)
        if variant_tag:
            cleaned.append("")
            cleaned.append(variant_tag)
            cleaned.append("")
            continue

        # Tag appendix sub-sections
        appendix_tag = tag_appendix(line, in_appendix)
        if appendix_tag:
            cleaned.append("")
            cleaned.append(appendix_tag)
            cleaned.append("")
            continue

        # Tag illustration captions
        if is_illustration_caption(line):
            cleaned.append(f"[ILLUSTRATION: {stripped}]")
            continue

        cleaned.append(line)

    print(f"  Stripped {stripped_headers} running headers, {stripped_pages} page numbers")

    # ─── Pass 2: Fix line breaks ───
    cleaned = fix_line_breaks(cleaned)

    # ─── Pass 3: Collapse excessive blank lines ───
    cleaned = collapse_blank_lines(cleaned)

    # ─── Validation ───
    full_text = "\n".join(cleaned)

    # Count §-numbers (pattern: number followed by period and space at start of line)
    section_numbers = set()
    for line in cleaned:
        m = re.match(r"^(\d+)\.\s", line.strip())
        if m:
            num = int(m.group(1))
            if 1 <= num <= 261:
                section_numbers.add(num)

    # Count footnotes
    footnote_refs = set()
    for m in re.finditer(r"\[(\d+)\]", full_text):
        num = int(m.group(1))
        if 1 <= num <= 400:
            footnote_refs.add(num)

    print(f"\n  Validation:")
    print(f"    §-numbers found: {len(section_numbers)} (expect ~260, §75 omitted in original)")
    print(f"    Footnotes found: {len(footnote_refs)} (expect ~392)")
    print(f"    Output lines: {len(cleaned)}")

    # ─── Write output ───
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned))

    print(f"\n  Written to: {OUTPUT_PATH}")
    print(f"  File size: {os.path.getsize(OUTPUT_PATH):,} bytes")


if __name__ == "__main__":
    main()
