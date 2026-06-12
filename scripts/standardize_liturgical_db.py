import os
import json
import re
import shutil
import difflib

# File Paths
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(REPO_DIR, "json_db", "stamford")
BACKUP_DIR = os.path.join(REPO_DIR, "json_db", "stamford_backup")
AUDIT_DIR = os.path.join(REPO_DIR, "audit_results")

# Ensure directories exist
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(AUDIT_DIR, exist_ok=True)

# Terminology replacements (case-insensitive search, case-matching replacement)
# Maps pattern to canonical replacement
DRIFT_REPLACEMENTS = [
    (r"\bholy\s+doors\b", "Royal Doors"),
    (r"\bsamohlasen\b", "Idiomelon"),
    (r"\bsamohlasni\b", "Idiomela"),
    (r"\bsamohlasny\b", "Idiomelon"),
    (r"\bsamohlasne\b", "Idiomelon"),
    (r"\bpodiben\b", "Prosomoion"),
    (r"\bpodibni\b", "Prosomoia"),
    (r"\birmos\b", "Heirmos"),
    (r"\birmoi\b", "Heirmoi"),
    (r"\birmologion\b", "Heirmologion"),
    (r"\bleave-taking\b", "Apodosis"),
    (r"\bleavetaking\b", "Apodosis"),
    (r"\bleave\s+taking\b", "Apodosis"),
    (r"\bviddannia\b", "Apodosis"),
    (r"\blytia\b", "Litiya"),
    (r"\blitia\b", "Litiya"),
    (r"\blity\b", "Litiya"),
    (r"\bprokimenon\b", "Prokeimenon"),
    (r"\bprokimena\b", "Prokeimena"),
    (r"\bexapostilarion\b", "Exaposteilarion"),
    (r"\bexapostolarion\b", "Exaposteilarion"),
    (r"\bvelychannye\b", "Magnification"),
    (r"\bvelychannia\b", "Magnification"),
    (r"\bstepenna\b", "Gradual"),
    (r"\bplaschanitsa\b", "Shroud"),
    (r"\bplashchanitsa\b", "Shroud"),
    (r"\bvsenichne\b", "All-Night Vigil"),
    (r"\bpovechiria\b", "Compline"),
    (r"\bpivnichna\b", "Midnight Office"),
    (r"\bobidnytsia\b", "Typika"),
    (r"\bperedsviattia\b", "Forefeast"),
    (r"\bposviattia\b", "Afterfeast"),
    (r"\beye\s+of\s+the\s+church\b", "Tserkovne Oko"),
    (r"\bchurch\s+eye\b", "Tserkovne Oko"),
    (r"\boko\s+tserkovne\b", "Tserkovne Oko"),
    (r"\btrephologion\b", "Anthologion"),
    (r"\btrefoloy\b", "Anthologion"),
    (r"\bantolohion\b", "Anthologion"),
    (r"\bpochayiv\b", "Pochaiv"),
    (r"\bpochaev\b", "Pochaiv"),
    (r"\bpolyeleios\b", "Polyeleos"),
    (r"\bpolieleos\b", "Polyeleos"),
    (r"\bpolyeley\b", "Polyeleos"),
    (r"\bkafisma\b", "Kathisma"),
    (r"\bkafizma\b", "Kathisma"),
    (r"\bkatisma\b", "Kathisma"),
    (r"\bkrylos\b", "Kliros"),
    (r"\bkryloi\b", "Kliroi")
]

# Hieratic spaces & objects (lowercase to capitalized)
HIERATIC_OBJECTS = {
    r"\baltar\b": "Altar",
    r"\bholy table\b": "Holy Table",
    r"\bsanctuary\b": "Sanctuary",
    r"\bgospel book\b": "Gospel Book",
    r"\bchalice\b": "Chalice",
    r"\bholy gifts\b": "Holy Gifts",
    r"\btheotokos\b": "Theotokos"
}

# Deity pronoun cues
DEITY_CUES = [
    r"\bLord\b", r"\bGod\b", r"\bFather\b", r"\bSon\b", r"\bSpirit\b", 
    r"\bChrist\b", r"\bYou\b", r"\bYour\b", r"\bHim\b", r"\bHis\b", 
    r"\bSaviour\b", r"\bCreator\b", r"\bMaster\b", r"\bKing\b", 
    r"\bTrinity\b", r"\bWord\b", r"\bJesus\b"
]

NON_DEITY_CUES = [
    r"\bVirgin\b", r"\bMother\b", r"\bTheotokos\b", r"\bMary\b", 
    r"\bapostle\b", r"\bmartyr\b", r"\bprophet\b", r"\bvenerable\b", 
    r"\bsaint\b", r"\bpriest\b", r"\bdeacon\b", r"\bchoir\b", 
    r"\breader\b", r"\bsinger\b", r"\bcantor\b", r"\bpeople\b", 
    r"\bfaithful\b", r"\brighteous\b", r"\bhierarch\b", r"\bbishop\b", 
    r"\bpope\b", r"\bpontiff\b", r"\bpatriarch\b", r"\bmetropolitan\b", 
    r"\bgovernment\b", r"\bmilitary\b", r"\bnation\b"
]

RUBRIC_CUES = ["priest:", "deacon:", "choir:", "rubric", "bow", "censing", "kneel"]

TIER_1_PRONOUNS = [
    (r"\bto\s+you,\s+O\s+Lord\b", "to You, O Lord"),
    (r"\bfrom\s+you,\s+O\s+Lord\b", "from You, O Lord"),
    (r"\bto\s+you,\s+O\s+Christ\b", "to You, O Christ"),
    (r"\bto\s+you,\s+O\s+God\b", "to You, O God"),
    (r"\bglory\s+to\s+you\b", "glory to You"),
    (r"\bglory\s+be\s+to\s+you\b", "glory be to You"),
    (r"\bwe\s+pray\s+you\b", "we pray You"),
    (r"\bwe\s+beseech\s+you\b", "we beseech You"),
    (r"\bWho\s+art\s+in\s+heaven\b", "Who art in heaven"),
    (r"\bwho\s+art\s+in\s+heaven\b", "Who art in heaven")
]

def case_match_replace(text, pattern, replacement):
    def repl(match):
        m = match.group(0)
        if m.isupper():
            return replacement.upper()
        elif m[0].isupper():
            return replacement
        else:
            return replacement.lower()
    return re.sub(pattern, repl, text, flags=re.IGNORECASE)

def normalize_breath_markers(text):
    # Temporarily hide ** markdown bolding
    placeholder = "___DOUBLE_AST___"
    text = text.replace("**", placeholder)
    # Replace any single * and surrounding spaces with a standardized " * "
    text = re.sub(r'\s*\*\s*', ' * ', text)
    # Restore **
    text = text.replace(placeholder, "**")
    return text

def clean_header_fragments(text):
    # Remove stray heading fragments like ...”** or ...** or ...” or ... at the beginning of a stichera content
    # E.g. starts with "...”**\n\n"
    text = re.sub(r'^\.\.\.[”"]\*\*\n\n', '', text)
    text = re.sub(r'^\.\.\.\*\*\n\n', '', text)
    text = re.sub(r'^\.\.\.[”"]\n\n', '', text)
    text = re.sub(r'^\.\.\.\n\n', '', text)
    return text

def standardize_text(text):
    if not isinstance(text, str):
        return text

    # 1. Clean header fragments
    text = clean_header_fragments(text)

    # 2. Terminology Replacements
    for pattern, replacement in DRIFT_REPLACEMENTS:
        text = case_match_replace(text, pattern, replacement)

    # 3. Hieratic Capitalization (Spaces & Objects)
    for pattern, replacement in HIERATIC_OBJECTS.items():
        text = re.sub(pattern, replacement, text) # Case-sensitive on lowercase pattern

    # 4. Typographical Normalization
    # Blessing cross
    text = re.sub(r'\bSign\s*\+\b', 'Sign ✚', text, flags=re.IGNORECASE)
    text = re.sub(r'(^|\s)\+(\s|$)', r'\1✚\2', text)
    # Breath markers
    text = normalize_breath_markers(text)

    # 5. Deity Pronoun Capitalization (Two-Tier)
    # Tier 1: Always safe phrases
    for pattern, repl in TIER_1_PRONOUNS:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

    # Tier 2: Pure deity sentences
    sentences = re.split(r'([.!?\n]+)', text)
    new_sentences = []
    for i in range(len(sentences)):
        if i % 2 != 0:
            new_sentences.append(sentences[i])
            continue
        
        sent = sentences[i]
        sent_clean = sent.strip()
        if not sent_clean:
            new_sentences.append(sent)
            continue
        
        # Check context
        is_rubric = any(rc in sent_clean.lower() for rc in RUBRIC_CUES)
        has_deity = any(re.search(cue, sent_clean) for cue in DEITY_CUES)
        has_non_deity = any(re.search(cue, sent_clean, re.IGNORECASE) for cue in NON_DEITY_CUES)

        # Do not modify Our Father prayer register
        is_our_father = "our father" in sent_clean.lower() or "who art in heaven" in sent_clean.lower()

        if has_deity and not has_non_deity and not is_rubric and not is_our_father:
            # 1. Prepositional You/Your
            sent = re.sub(r'\b(to|from|in|with|by|of)\s+you\b', r'\1 You', sent)
            
            # 2. Deity nouns with Your
            nouns_pattern = r'\byour\s+(mercy|grace|name|salvation|power|love|house|temple|altar|sanctuary|holy\s+table|commandments|word|hand|right\s+hand|face|presence|truth|peace|light|cross|passion|resurrection|ascension|kingdom|will|glory)\b'
            def cap_your(m):
                return "Your " + m.group(1)
            sent = re.sub(nouns_pattern, cap_your, sent, flags=re.IGNORECASE)
            
            # 3. Verbs with You
            verbs_pattern = r'\b(praise|bless|worship|glorify|thank|pray|beseech)\s+you\b'
            def cap_verb_you(m):
                return m.group(1) + " You"
            sent = re.sub(verbs_pattern, cap_verb_you, sent, flags=re.IGNORECASE)
            
            # 4. Direct address You, O ...
            sent = re.sub(r'\byou,\s+O\s+(Lord|Christ|God|Father|King|Master|Saviour)\b', r'You, O \1', sent, flags=re.IGNORECASE)
            
            # 5. Prepositional Him
            sent = re.sub(r'\b(to|from|in|with|by|of|glory\s+to|glory\s+be\s+to)\s+him\b', lambda m: m.group(1) + ' Him', sent, flags=re.IGNORECASE)
            
            # 6. Deity nouns with His
            his_nouns_pattern = r'\bhis\s+(mercy|grace|name|salvation|power|love|commandments|word|hand|right\s+hand|face|truth|peace|light|cross|passion|resurrection|ascension|kingdom|will|glory)\b'
            def cap_his(m):
                return "His " + m.group(1)
            sent = re.sub(his_nouns_pattern, cap_his, sent, flags=re.IGNORECASE)
            
            # 7. Relative pronouns Who/Whom
            sent = re.sub(r'\b(Lord|God|Christ|Father|Son|Spirit|Him|He)\s+who\b', r'\1 Who', sent)
            sent = re.sub(r'\b(Lord|God|Christ|Father|Son|Spirit|Him|He),\s+who\b', r'\1, Who', sent)

            # 8. Pronouns at clauses
            sent = re.sub(r'\b(for|that|as|because)\s+he\b', r'\1 He', sent)
            sent = re.sub(r'\bhe\s+(has|is|was|will|did|came|descended|ascended|saved|redeemed|glorified|rose)\b', r'He \1', sent)

        new_sentences.append(sent)

    return "".join(new_sentences)

def process_value(val):
    if isinstance(val, str):
        return standardize_text(val)
    elif isinstance(val, list):
        return [process_value(x) for x in val]
    elif isinstance(val, dict):
        return {k: process_value(v) for k, v in val.items()}
    return val

def run_standardization():
    files = sorted([f for f in os.listdir(DB_DIR) if f.endswith(".json") and not f.endswith(".bak")])
    diff_report = []

    print("Beginning systematic database corrections...")

    for filename in files:
        filepath = os.path.join(DB_DIR, filename)
        backup_filepath = os.path.join(BACKUP_DIR, filename)

        # 1. Back up file
        shutil.copy2(filepath, backup_filepath)
        # Also copy as .bak in DB_DIR if desired, but BACKUP_DIR is cleaner
        print(f"Backed up {filename} to {backup_filepath}")

        # 2. Load original data
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 3. Deep copy and process
        standardized_data = {}
        for key, entry in data.items():
            standardized_data[key] = process_value(entry)

        # 4. Generate diff
        orig_str = json.dumps(data, indent=2, ensure_ascii=False)
        new_str = json.dumps(standardized_data, indent=2, ensure_ascii=False)

        if orig_str != new_str:
            diff = list(difflib.unified_diff(
                orig_str.splitlines(),
                new_str.splitlines(),
                fromfile=f"a/json_db/stamford/{filename}",
                tofile=f"b/json_db/stamford/{filename}",
                lineterm=""
            ))
            if diff:
                diff_report.append(f"=== File: {filename} ===")
                diff_report.extend(diff)
                diff_report.append("\n")

            # 5. Write standardized file back
            with open(filepath, "w", encoding="utf-8") as f_out:
                json.dump(standardized_data, f_out, indent=2, ensure_ascii=False)
            print(f"Standardized and saved: {filename}")
        else:
            print(f"No changes needed for: {filename}")

    # Write unified diff report
    diff_path = os.path.join(AUDIT_DIR, "standardization_diff.txt")
    with open(diff_path, "w", encoding="utf-8") as d_f:
        d_f.write("\n".join(diff_report))
    
    print(f"\nStandardization complete. Diffs written to: {diff_path}")

if __name__ == "__main__":
    run_standardization()
