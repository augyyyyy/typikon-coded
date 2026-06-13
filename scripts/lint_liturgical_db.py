import os
import json
import re

# File Paths
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(REPO_DIR, "Data", "Service Books", "Recensions", "Stamford Divine Office", "JSON", "assets")
AUDIT_DIR = os.path.join(REPO_DIR, "audit_results")

# Ensure audit directory exists
os.makedirs(AUDIT_DIR, exist_ok=True)

# 25 Monitored Terminology Drift Patterns (Rejected -> Canonical)
DRIFT_PATTERNS = {
    r"\bholy\s+doors\b": "Royal Doors",
    r"\bsamohlasen\b": "Idiomelon/Idiomela",
    r"\bpodiben\b": "Prosomoion/Prosomoia",
    r"\birmos\b": "Heirmos/Heirmoi/Heirmologion",
    r"\bleave-taking\b": "Apodosis",
    r"\bleavetaking\b": "Apodosis",
    r"\bviddannia\b": "Apodosis",
    r"\blytia\b": "Litiya",
    r"\blitia\b": "Litiya",
    r"\blity\b": "Litiya",
    r"\bprokimenon\b": "Prokeimenon",
    r"\bprokimena\b": "Prokeimena",
    r"\bexapostilarion\b": "Exaposteilarion",
    r"\bexapostolarion\b": "Exaposteilarion",
    r"\bvelychannye\b": "Magnification",
    r"\bvelychannia\b": "Magnification",
    r"\bstepenna\b": "Gradual",
    r"\bplaschanitsa\b": "Shroud",
    r"\bplashchanitsa\b": "Shroud",
    r"\bvsenichne\b": "All-Night Vigil",
    r"\bpovechiria\b": "Compline",
    r"\bpivnichna\b": "Midnight Office",
    r"\bobidnytsia\b": "Typika",
    r"\bperedsviattia\b": "Forefeast",
    r"\bposviattia\b": "Afterfeast",
    r"\beye of the church\b": "Tserkovne Oko",
    r"\bchurch eye\b": "Tserkovne Oko",
    r"\boko tserkovne\b": "Tserkovne Oko",
    r"\btrephologion\b": "Anthologion",
    r"\btrefoloy\b": "Anthologion",
    r"\bantolohion\b": "Anthologion",
    r"\bpochayiv\b": "Pochaiv",
    r"\bpochaev\b": "Pochaiv",
    r"\bpolyeleios\b": "Polyeleos",
    r"\bpolieleos\b": "Polyeleos",
    r"\bpolyeley\b": "Polyeleos",
    r"\bkafisma\b": "Kathisma",
    r"\bkafizma\b": "Kathisma",
    r"\bkatisma\b": "Kathisma",
    r"\bkrylos\b": "Kliros",
    r"\bkryloi\b": "Kliros"
}

# Pronouns & deity heuristics
PRONOUNS = [r"\byou\b", r"\byour\b", r"\byours\b", r"\bhim\b", r"\bhis\b", r"\bhe\b", r"\bwho\b", r"\bwhom\b"]
DEITY_CUES = [r"\bLord\b", r"\bGod\b", r"\bFather\b", r"\bSon\b", r"\bSpirit\b", r"\bChrist\b", r"\bYou\b", r"\bYour\b", r"\bHim\b", r"\bHis\b", r"\bSaviour\b", r"\bCreator\b", r"\bMaster\b", r"\bKing\b", r"\bTrinity\b", r"\bWord\b"]
NON_DEITY_CUES = [r"\bVirgin\b", r"\bMother\b", r"\bTheotokos\b", r"\bMary\b", r"\bapostle\b", r"\bmartyr\b", r"\bprophet\b", r"\bvenerable\b", r"\bsaint\b", r"\bpriest\b", r"\bdeacon\b", r"\bchoir\b", r"\breader\b", r"\bsinger\b", r"\bcantor\b", r"\bpeople\b", r"\bfaithful\b", r"\brighteous\b", r"\bhierarch\b", r"\bbishop\b", r"\bpope\b", r"\bpontiff\b", r"\bpatriarch\b", r"\bmetropolitan\b", r"\bgovernment\b", r"\bmilitary\b", r"\bnation\b"]

# Hieratic spaces & objects that must be capitalized
HIERATIC_OBJECTS = {
    r"\baltar\b": "Altar",
    r"\bholy table\b": "Holy Table",
    r"\bsanctuary\b": "Sanctuary",
    r"\bgospel book\b": "Gospel Book",
    r"\bchalice\b": "Chalice",
    r"\bholy gifts\b": "Holy Gifts",
    r"\btheotokos\b": "Theotokos"
}

def extract_strings(val):
    if isinstance(val, str):
        return [val]
    elif isinstance(val, list):
        res = []
        for x in val:
            res.extend(extract_strings(x))
        return res
    elif isinstance(val, dict):
        res = []
        for k, v in val.items():
            res.extend(extract_strings(v))
        return res
    return []

def run_linter():
    files = sorted([f for f in os.listdir(DB_DIR) if f.endswith(".json") and not f.endswith(".bak")])
    report = {
        "summary": {
            "total_files_checked": len(files),
            "total_terminology_issues": 0,
            "total_pronoun_issues": 0,
            "total_hieratic_issues": 0,
            "total_typography_issues": 0,
            "total_issues": 0
        },
        "files": {}
    }

    for filename in files:
        filepath = os.path.join(DB_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"Linter Error: Failed to parse {filename}: {e}")
                continue

        file_report = {
            "terminology": [],
            "pronoun": [],
            "hieratic": [],
            "typography": []
        }

        for key, entry in data.items():
            # 1. Check Key Names for Terminology Drift
            for pattern, canonical in DRIFT_PATTERNS.items():
                if re.search(pattern, key, re.IGNORECASE):
                    file_report["terminology"].append({
                        "key": key,
                        "type": "key_drift",
                        "match": re.search(pattern, key, re.IGNORECASE).group(0),
                        "message": f"Key name contains deprecated term. Suggest replacing key or alias with '{canonical}'."
                    })
                    report["summary"]["total_terminology_issues"] += 1

            # Extract text elements recursively
            texts = extract_strings(entry)
            for text in texts:
                # Skip rubrics or actor tags if they are separate dictionary items
                # Usually text is a paragraph. Split by sentences for analysis.
                sentences = re.split(r'[.!?\n]', text)
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    
                    # 2. Check Terminology inside Content
                    for pattern, canonical in DRIFT_PATTERNS.items():
                        match = re.search(pattern, sent, re.IGNORECASE)
                        if match:
                            # Context snippet
                            start = max(0, sent.find(match.group(0)) - 30)
                            end = min(len(sent), sent.find(match.group(0)) + len(match.group(0)) + 30)
                            file_report["terminology"].append({
                                "key": key,
                                "type": "content_drift",
                                "match": match.group(0),
                                "snippet": f"...{sent[start:end]}...",
                                "message": f"Found deprecated term '{match.group(0)}'. Replace with '{canonical}'."
                            })
                            report["summary"]["total_terminology_issues"] += 1

                    # 3. Check Deity Pronouns using Heuristics
                    # Avoid checking if it looks like a standard rubric
                    if any(x in sent.lower() for x in ["priest:", "deacon:", "choir:", "rubric", "bow", "censing", "kneel"]):
                        continue

                    # Check if it contains Deity cues
                    has_deity_cue = any(re.search(cue, sent) for cue in DEITY_CUES)
                    has_non_deity_cue = any(re.search(cue, sent, re.IGNORECASE) for cue in NON_DEITY_CUES)

                    if has_deity_cue:
                        # Find lowercase pronouns in this sentence
                        for pron in PRONOUNS:
                            matches = list(re.finditer(pron, sent))
                            for m in matches:
                                # Skip if it is the first word of a sentence (it would be capitalized)
                                # but if it's lowercase, it means it's in the middle of a sentence
                                word = m.group(0)
                                start = max(0, m.start() - 30)
                                end = min(len(sent), m.end() + 30)
                                snippet = sent[start:end]

                                # Determine confidence: if it has non-deity cues, it could refer to a saint or Mary.
                                confidence = "High"
                                if has_non_deity_cue:
                                    confidence = "Medium (Check context: may refer to Saint or Theotokos)"

                                file_report["pronoun"].append({
                                    "key": key,
                                    "pronoun": word,
                                    "confidence": confidence,
                                    "snippet": f"...{snippet}...",
                                    "message": f"Potential lowercase Deity pronoun '{word}' found in Deity context."
                                })
                                report["summary"]["total_pronoun_issues"] += 1

                    # 4. Check Hieratic Capitalization (altar, sanctuary, etc.)
                    for pattern, canonical in HIERATIC_OBJECTS.items():
                        match = re.search(pattern, sent)  # Case sensitive since we search for lowercase
                        if match:
                            start = max(0, sent.find(match.group(0)) - 30)
                            end = min(len(sent), sent.find(match.group(0)) + len(match.group(0)) + 30)
                            file_report["hieratic"].append({
                                "key": key,
                                "match": match.group(0),
                                "snippet": f"...{sent[start:end]}...",
                                "message": f"Liturgical object/space '{match.group(0)}' should be capitalized as '{canonical}'."
                            })
                            report["summary"]["total_hieratic_issues"] += 1

                    # 5. Check Typographical Symbols
                    # Legacy blessing cross '+' instead of '✚'
                    if "+" in sent:
                        # Make sure it isn't part of instructions or formulas (like pp. 413+ etc)
                        # Look for '+' in typical liturgical contexts or alone
                        if re.search(r'\s\+\s', sent) or sent.startswith("+") or re.search(r'\bSign\s+\+', sent, re.IGNORECASE):
                            file_report["typography"].append({
                                "key": key,
                                "type": "legacy_cross",
                                "match": "+",
                                "snippet": sent,
                                "message": "Legacy '+' blessing sign detected. Replace with Unicode symbol '✚'."
                            })
                            report["summary"]["total_typography_issues"] += 1

                    # Chanting breath marker spacing (should be ' * ')
                    # Check for asterisk not preceded by a space or not followed by a space
                    # Exclude case where it's at the start or end of the sentence
                    # e.g., 'word* word' or 'word *word'
                    bad_asterisk = re.search(r'(?<!\s)\*|\*(?!\s)', sent)
                    if bad_asterisk:
                        # Exclude markdown formatting like **bold** or *italic*
                        # Quick check: is it double asterisks?
                        if "**" not in sent and not re.search(r'^\*.*\*$', sent):
                            start = max(0, sent.find("*") - 15)
                            end = min(len(sent), sent.find("*") + 15)
                            file_report["typography"].append({
                                "key": key,
                                "type": "breath_marker_spacing",
                                "match": "*",
                                "snippet": f"...{sent[start:end]}...",
                                "message": "Chanting breath marker '*' should have spaces before and after (' * ')."
                            })
                            report["summary"]["total_typography_issues"] += 1

        # Only add files with issues
        total_file_issues = sum(len(x) for x in file_report.values())
        if total_file_issues > 0:
            report["files"][filename] = file_report

    # Pass 2: Audit frontend UI files for "robot speak" and banned developer terms
    frontend_dir = os.path.join(REPO_DIR, "cantor_dashboard")
    frontend_files = ["main.js", "index.html"]
    for fname in frontend_files:
        fpath = os.path.join(frontend_dir, fname)
        if not os.path.exists(fpath):
            continue
        report["summary"]["total_files_checked"] += 1
        ui_report = {
            "terminology": [],
            "pronoun": [],
            "hieratic": [],
            "typography": []
        }
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
                for idx, line in enumerate(lines):
                    # Check for "Active" in user-facing UI labels/values (ignoring typical programming identifiers)
                    if "Active" in line and not any(x in line for x in ["class", "activeClass", "activeCount", "active_saints", "ActiveCount", "Active (Dolnytsky"]):
                        if "badge" in line or "context-val" in line or "context-row" in line or "commemText" in line or "textContent" in line:
                            ui_report["terminology"].append({
                                "key": f"Line {idx+1}",
                                "type": "ui_robot_speak",
                                "snippet": line.strip(),
                                "message": "Raw developer jargon 'Active' detected in user-facing UI line."
                            })
                            report["summary"]["total_terminology_issues"] += 1
                    
                    # Check for "Max:" as raw shorthand in UI text
                    if "Max:" in line and "Dolnytsky Limit" not in line and "MaxMs" not in line:
                        ui_report["terminology"].append({
                            "key": f"Line {idx+1}",
                            "type": "ui_robot_speak",
                            "snippet": line.strip(),
                            "message": "Raw developer shorthand 'Max:' detected in UI line."
                        })
                        report["summary"]["total_terminology_issues"] += 1

                    # Check for "9 Services Max" cycle limit
                    if "9 Services Max" in line:
                        ui_report["terminology"].append({
                            "key": f"Line {idx+1}",
                            "type": "ui_robot_speak",
                            "snippet": line.strip(),
                            "message": "Useless static services cycle limit '9 Services Max' detected in UI line."
                        })
                        report["summary"]["total_terminology_issues"] += 1
        except Exception as e:
            print(f"Failed to lint UI file {fname}: {e}")

        # Add to file issues if found
        total_ui_issues = sum(len(x) for x in ui_report.values())
        if total_ui_issues > 0:
            report["files"][f"cantor_dashboard/{fname}"] = ui_report

    # Complete Summary calculation
    report["summary"]["total_issues"] = (
        report["summary"]["total_terminology_issues"] +
        report["summary"]["total_pronoun_issues"] +
        report["summary"]["total_hieratic_issues"] +
        report["summary"]["total_typography_issues"]
    )

    # Write JSON report
    json_path = os.path.join(AUDIT_DIR, "stamford_lint_report.json")
    with open(json_path, "w", encoding="utf-8") as out_j:
        json.dump(report, out_j, indent=2)

    # Write Markdown report
    md_path = os.path.join(AUDIT_DIR, "stamford_lint_report.md")
    with open(md_path, "w", encoding="utf-8") as out_m:
        out_m.write("# Liturgical Database Lint Report\n\n")
        out_m.write("## Summary Statistics\n\n")
        out_m.write(f"- **Total Files Checked**: {report['summary']['total_files_checked']}\n")
        out_m.write(f"- **Total Issues Found**: {report['summary']['total_issues']}\n")
        out_m.write(f"  - Terminology Drift Issues: {report['summary']['total_terminology_issues']}\n")
        out_m.write(f"  - Potential Lowercase Deity Pronouns: {report['summary']['total_pronoun_issues']}\n")
        out_m.write(f"  - Missing Hieratic Capitalizations: {report['summary']['total_hieratic_issues']}\n")
        out_m.write(f"  - Typographical Standards Issues: {report['summary']['total_typography_issues']}\n\n")
        
        out_m.write("## File Breakdown\n\n")
        for fname, issues in sorted(report["files"].items()):
            file_total = sum(len(x) for x in issues.values())
            out_m.write(f"### `{fname}` ({file_total} issues)\n\n")
            
            if issues["terminology"]:
                out_m.write("#### Terminology Drift\n")
                for item in issues["terminology"][:15]:
                    out_m.write(f"- **Key**: `{item['key']}`\n")
                    if "snippet" in item:
                        out_m.write(f"  - *Snippet*: {item['snippet']}\n")
                    out_m.write(f"  - *Message*: {item['message']}\n")
                if len(issues["terminology"]) > 15:
                    out_m.write(f"- *... and {len(issues['terminology']) - 15} more terminology issues.*\n")
                out_m.write("\n")

            if issues["pronoun"]:
                out_m.write("#### Lowercase Deity Pronouns\n")
                for item in issues["pronoun"][:15]:
                    out_m.write(f"- **Key**: `{item['key']}` (Confidence: {item['confidence']})\n")
                    out_m.write(f"  - *Snippet*: {item['snippet']}\n")
                    out_m.write(f"  - *Message*: {item['message']}\n")
                if len(issues["pronoun"]) > 15:
                    out_m.write(f"- *... and {len(issues['pronoun']) - 15} more pronoun issues.*\n")
                out_m.write("\n")

            if issues["hieratic"]:
                out_m.write("#### Hieratic Capitalization\n")
                for item in issues["hieratic"][:15]:
                    out_m.write(f"- **Key**: `{item['key']}`\n")
                    out_m.write(f"  - *Snippet*: {item['snippet']}\n")
                    out_m.write(f"  - *Message*: {item['message']}\n")
                if len(issues["hieratic"]) > 15:
                    out_m.write(f"- *... and {len(issues['hieratic']) - 15} more hieratic issues.*\n")
                out_m.write("\n")

            if issues["typography"]:
                out_m.write("#### Typographical & Symbol Normalization\n")
                for item in issues["typography"][:15]:
                    out_m.write(f"- **Key**: `{item['key']}`\n")
                    out_m.write(f"  - *Snippet*: `{item['snippet']}`\n")
                    out_m.write(f"  - *Message*: {item['message']}\n")
                if len(issues["typography"]) > 15:
                    out_m.write(f"- *... and {len(issues['typography']) - 15} more typography issues.*\n")
                out_m.write("\n")

    print(f"Linter complete. Found {report['summary']['total_issues']} issues across {len(report['files'])} files.")
    print(f"JSON report saved to: {json_path}")
    print(f"Markdown report saved to: {md_path}")

if __name__ == "__main__":
    run_linter()
