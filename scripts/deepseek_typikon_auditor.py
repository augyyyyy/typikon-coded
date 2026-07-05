import os
import sys
import re
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Robust DeepSeek key loader
def get_deepseek_key():
    key = os.getenv("DEEPSEEK_API_KEY")
    if key and key != "your_deepseek_api_key_here":
        return key

    global_env = Path("C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/.env")
    if global_env.exists():
        try:
            with open(global_env, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k_clean = k.strip().replace("[", "").replace("]", "")
                        if k_clean in ("deepseek-v4-pro", "DEEPSEEK_API_KEY"):
                            val = v.strip()
                            if val:
                                return val
        except Exception:
            pass

    if os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k_clean = k.strip().replace("[", "").replace("]", "")
                        if k_clean in ("deepseek-v4-pro", "DEEPSEEK_API_KEY"):
                            val = v.strip()
                            if val and val != "your_deepseek_api_key_here":
                                return val
        except Exception:
            pass

    return None

# Load environment
ENV_PATH = Path("C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/.env")
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

DEEPSEEK_API_KEY = get_deepseek_key()
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

class TypikonCodebaseAuditor:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.audit_results_dir = PROJECT_ROOT / "audit_results"
        self.audit_results_dir.mkdir(exist_ok=True)
        
        # Source file paths
        self.dolnytsky_path = PROJECT_ROOT / "Data" / "Service Books" / "Typikon" / "Dolnytsky_Typikon_Master.md"
        self.ordo_path = PROJECT_ROOT / "Data" / "Service Books" / "Typikon" / "Ordo" / "Ordo_Celebrationis_1996_CLEAN.md"
        
        self.dolnytsky_content = ""
        self.ordo_content = ""
        self.load_source_texts()
 
    def load_source_texts(self):
        if self.dolnytsky_path.exists():
            self.dolnytsky_content = self.dolnytsky_path.read_text(encoding="utf-8")
        else:
            print(f"Warning: Dolnytsky master file not found at {self.dolnytsky_path}")

        if self.ordo_path.exists():
            self.ordo_content = self.ordo_path.read_text(encoding="utf-8")
        else:
            print(f"Warning: Ordo Celebrationis clean file not found at {self.ordo_path}")

    def slice_dolnytsky(self, keyword_start, keyword_end):
        """Slice segments of Dolnytsky Typikon by headers."""
        if not self.dolnytsky_content:
            return ""
        lines = self.dolnytsky_content.splitlines()
        start_idx = -1
        end_idx = -1
        
        for idx, line in enumerate(lines):
            trimmed = line.strip().upper()
            if keyword_start.upper() in trimmed:
                start_idx = idx
                break
                
        if start_idx == -1:
            return ""
            
        for idx in range(start_idx + 1, len(lines)):
            trimmed = lines[idx].strip().upper()
            if keyword_end.upper() in trimmed:
                end_idx = idx
                break
                
        slice_lines = lines[start_idx:end_idx] if end_idx != -1 else lines[start_idx:]
        return "\n".join(slice_lines)

    def slice_ordo(self, keyword_start, keyword_end):
        """Slice segments of Ordo Celebrationis by section markers."""
        if not self.ordo_content:
            return ""
        lines = self.ordo_content.splitlines()
        start_idx = -1
        end_idx = -1
        
        for idx, line in enumerate(lines):
            trimmed = line.strip().upper()
            if keyword_start.upper() in trimmed:
                start_idx = idx
                break
                
        if start_idx == -1:
            return ""
            
        for idx in range(start_idx + 1, len(lines)):
            trimmed = lines[idx].strip().upper()
            if keyword_end.upper() in trimmed:
                end_idx = idx
                break
                
        slice_lines = lines[start_idx:end_idx] if end_idx != -1 else lines[start_idx:]
        return "\n".join(slice_lines)

    def get_codebase_files(self, paths):
        """Compile a markdown block of specified files from the codebase."""
        compiled = []
        for p in paths:
            file_path = PROJECT_ROOT / p
            if file_path.exists() and file_path.is_file():
                try:
                    content = file_path.read_text(encoding="utf-8")
                    compiled.append(f"### File: {p}\n```\n{content}\n```\n")
                except Exception as e:
                    print(f"Error reading codebase file {p}: {e}")
        return "\n".join(compiled)

    def call_deepseek(self, system_prompt, user_prompt):
        if not self.api_key:
            raise ValueError("DeepSeek API Key not found.")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "thinking": {"type": "enabled"},
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        res_json = response.json()
        
        content = res_json['choices'][0]['message'].get('content') or "{}"
        return json.loads(content)

    def execute_topic_audit(self, topic_name, src_text, codebase_text):
        """Perform first-pass audit on a given topic."""
        print(f"--- Running Codebase Coverage Audit for: {topic_name} ---")
        
        system_prompt = (
            "You are the senior Byzantine-Ruthenian liturgical auditor. "
            "Your task is to verify if the provided liturgical rules (from the Typikon and Ordo Celebrationis) "
            "are fully, partially, or not implemented in the codebase files provided. "
            "You must simulate a temperature=0.0 greedy token selection. Base every claim on literal file content. "
            "If a rule is not actively implemented in the code or JSON templates, you MUST label it UNIMPLEMENTED. "
            "Ensure you do not hallucinate function names or JSON keys.\n\n"
            "You MUST respond ONLY with a JSON object conforming strictly to this schema:\n"
            "{\n"
            "  \"topic\": \"string\",\n"
            "  \"rules\": [\n"
            "    {\n"
            "      \"rule_id\": \"string (e.g. Ordo §22 or Dolnytsky Chapter 2 §3)\",\n"
            "      \"description\": \"string (summary of the rule)\",\n"
            "      \"status\": \"CODED\" | \"PARTIAL\" | \"UNIMPLEMENTED\",\n"
            "      \"grounding\": {\n"
            "        \"file\": \"string (relative file path, e.g. engine/resolvers/vespers.py)\",\n"
            "        \"symbol\": \"string (exact Python method name, variable name, or JSON key)\",\n"
            "        \"notes\": \"string (short description of how/where it is coded)\"\n"
            "      },\n"
            "      \"gaps\": \"string (any missing edge cases or stubs, or N/A)\",\n"
            "      \"missing_assets\": [\"string (list of missing translation asset keys, if any)\"]\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        
        user_prompt = f"""
Liturgical Topic: {topic_name}

=== LITURGICAL RULES SOURCES ===
{src_text}

=== CODEBASE CONTEXT ===
{codebase_text}

Analyze the rules above. For each rule, cross-reference the codebase context.
Find exact matching methods, resolver registrations, or JSON keys.
Only mark CODED or PARTIAL if you see direct evidence in the codebase.
"""
        return self.call_deepseek(system_prompt, user_prompt)

    def deterministic_grounding_validation(self, audit_result):
        """Verify that every cited code symbol and file actually exists in the local codebase."""
        validated_rules = []
        hallucination_count = 0
        
        for rule in audit_result.get("rules", []):
            status = rule.get("status")
            grounding = rule.get("grounding", {})
            file_rel_path = grounding.get("file")
            symbol = grounding.get("symbol")
            
            if status in ("CODED", "PARTIAL") and file_rel_path and symbol:
                file_abs_path = PROJECT_ROOT / file_rel_path
                if not file_abs_path.exists():
                    # File doesn't exist
                    rule["status"] = "UNIMPLEMENTED"
                    rule["gaps"] = f"[HALLUCINATION WARNING] Cited file '{file_rel_path}' does not exist."
                    rule["grounding"] = {}
                    hallucination_count += 1
                else:
                    try:
                        content = file_abs_path.read_text(encoding="utf-8")
                        # Perform substring match to check if the method or key exists
                        clean_symbol = symbol.strip().strip("'\"")
                        if clean_symbol not in content:
                            rule["status"] = "UNIMPLEMENTED"
                            rule["gaps"] = f"[HALLUCINATION WARNING] Cited symbol '{symbol}' not found inside '{file_rel_path}'."
                            rule["grounding"] = {}
                            hallucination_count += 1
                    except Exception as e:
                        rule["status"] = "UNIMPLEMENTED"
                        rule["gaps"] = f"[ERROR] Failed to read cited file '{file_rel_path}': {e}"
                        rule["grounding"] = {}
                        hallucination_count += 1
            validated_rules.append(rule)
            
        audit_result["rules"] = validated_rules
        if hallucination_count > 0:
            print(f"   [Grounding Validation] Flagged and corrected {hallucination_count} hallucinated linkages.")
        return audit_result

    def run_adversarial_review(self, topic_name, src_text, validated_result):
        """Run second-pass double-blind review to find false positive coverage reports."""
        print(f"   Running adversarial review for: {topic_name}")
        
        system_prompt = (
            "You are the senior adversarial liturgical auditor. "
            "Your sole task is to verify if the provided first-pass coverage audit contains "
            "false positives, speculative claims, or confirmation bias. "
            "Inspect the rules marked CODED or PARTIAL. Verify if they truly satisfy the liturgical "
            "precedence or physical choreography requirements of the rule source.\n\n"
            "You MUST respond ONLY with a JSON object of this exact schema:\n"
            "{\n"
            "  \"corrections\": [\n"
            "    {\n"
            "      \"rule_id\": \"string (matching the rule_id in the input)\",\n"
            "      \"new_status\": \"CODED\" | \"PARTIAL\" | \"UNIMPLEMENTED\",\n"
            "      \"justification\": \"string (reason why the status was adjusted due to gaps)\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        
        user_prompt = f"""
Liturgical Topic: {topic_name}

=== LITURGICAL RULES SOURCES ===
{src_text}

=== FIRST-PASS AUDIT MATRIX ===
{json.dumps(validated_result, indent=2)}

Disprove the first-pass claims. If a rule requires complex combinations (like saint transfers or sanctuary actions) 
but the grounding code only has basic stubs, downgrade the status to PARTIAL or UNIMPLEMENTED and justify it.
"""
        try:
            adv_res = self.call_deepseek(system_prompt, user_prompt)
            corrections = {c.get("rule_id"): c for c in adv_res.get("corrections", [])}
            
            for rule in validated_result.get("rules", []):
                rule_id = rule.get("rule_id")
                if rule_id in corrections:
                    corr = corrections[rule_id]
                    old_status = rule["status"]
                    new_status = corr.get("new_status")
                    if old_status != new_status:
                        print(f"   [Adversarial Review] Downgraded {rule_id} from {old_status} to {new_status}: {corr.get('justification')}")
                        rule["status"] = new_status
                        rule["gaps"] = f"[Adversarial Audit Correction] {corr.get('justification')}"
        except Exception as e:
            print(f"   Warning: Adversarial pass failed: {e}")
            
        return validated_result

    def generate_final_report(self, full_matrix):
        """Outputs structured JSON matrix and beautiful markdown coverage report."""
        # 1. Save JSON matrix
        matrix_path = self.audit_results_dir / "typikon_coverage_matrix.json"
        with open(matrix_path, "w", encoding="utf-8") as f:
            json.dump(full_matrix, f, indent=2)
            
        # 2. Render Markdown report
        md_lines = [
            "# Typikon Coded — Liturgical Coverage and Verification Matrix",
            "",
            "This report documents the exact coverage of the codebase and database templates against ",
            "the authoritative sources (*Isidor Dolnytsky Typikon 1899* and *Ordo Celebrationis 1996*). ",
            "The coverage matrix is verified through a dynamic code-grounding validation script ",
            "and a double-blind adversarial audit pass.",
            "",
            "## Summary Metrics",
            "",
        ]
        
        total_rules = 0
        status_counts = {"CODED": 0, "PARTIAL": 0, "UNIMPLEMENTED": 0}
        
        for topic in full_matrix:
            for rule in topic.get("rules", []):
                total_rules += 1
                status = rule.get("status", "UNIMPLEMENTED")
                status_counts[status] = status_counts.get(status, 0) + 1
                
        coded_pct = (status_counts["CODED"] / total_rules * 100) if total_rules > 0 else 0
        partial_pct = (status_counts["PARTIAL"] / total_rules * 100) if total_rules > 0 else 0
        unimplemented_pct = (status_counts["UNIMPLEMENTED"] / total_rules * 100) if total_rules > 0 else 0
        
        md_lines.extend([
            f"- **Total Liturgical Rules Audited**: {total_rules}",
            f"- **100% Coded Rules**: {status_counts['CODED']} ({coded_pct:.1f}%)",
            f"- **Partially Coded Rules**: {status_counts['PARTIAL']} ({partial_pct:.1f}%)",
            f"- **Unimplemented Rules / Gaps**: {status_counts['UNIMPLEMENTED']} ({unimplemented_pct:.1f}%)",
            "",
            "---",
            "",
            "## Topic Breakdown",
            ""
        ])
        
        for topic in full_matrix:
            md_lines.append(f"### 📌 {topic.get('topic')}")
            md_lines.append("")
            
            t_rules = topic.get("rules", [])
            t_coded = sum(1 for r in t_rules if r.get("status") == "CODED")
            t_partial = sum(1 for r in t_rules if r.get("status") == "PARTIAL")
            t_unimp = sum(1 for r in t_rules if r.get("status") == "UNIMPLEMENTED")
            
            md_lines.append(f"*(Coded: {t_coded} \| Partial: {t_partial} \| Gaps: {t_unimp})*")
            md_lines.append("")
            
            # Format rules table
            md_lines.extend([
                "| Rule ID | Description | Status | Grounding Location / Gaps |",
                "| :--- | :--- | :--- | :--- |"
            ])
            
            for rule in t_rules:
                status = rule.get("status")
                status_badge = "✅ CODED" if status == "CODED" else ("⚠️ PARTIAL" if status == "PARTIAL" else "❌ GAP")
                
                grounding = rule.get("grounding", {})
                loc = "N/A"
                if grounding.get("file") and grounding.get("symbol"):
                    loc = f"`{grounding.get('file')}`: `{grounding.get('symbol')}`"
                    
                gaps = rule.get("gaps", "N/A")
                notes = grounding.get("notes", "")
                
                detail = f"**Grounding**: {loc}"
                if notes:
                    detail += f"<br>*{notes}*"
                if gaps and gaps != "N/A":
                    detail += f"<br>**Gap**: {gaps}"
                    
                md_lines.append(f"| {rule.get('rule_id')} | {rule.get('description')} | {status_badge} | {detail} |")
                
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")
            
        report_path = self.audit_results_dir / "typikon_coverage_report.md"
        report_path.write_text("\n".join(md_lines), encoding="utf-8")
        
        print(f"\n[SUCCESS] Typikon Coverage Audit completed successfully:")
        print(f"  - JSON Matrix: {matrix_path}")
        print(f"  - Markdown Report: {report_path}")

    def run_all(self):
        """Execute the entire partitioned coverage audit pipeline."""
        if not self.api_key:
            print("Error: DEEPSEEK_API_KEY or deepseek-v4-pro key not found in env or global .env.", file=sys.stderr)
            sys.exit(1)
            
        topics = [
            {
                "name": "General Vespers Rubrics & Physical Choreography",
                "src_slice": (
                    self.slice_ordo("Preliminary Notes 1", "=== SECTION IV") + "\n" +
                    self.slice_dolnytsky("Chapter II", "Chapter III")
                ),
                "codebase_files": [
                    "engine/resolvers/vespers.py",
                    "json_db/01h_struct_vespers.json",
                    "json_db/04_logic_vespers.json"
                ]
            },
            {
                "name": "General Matins Rubrics & Physical Choreography",
                "src_slice": (
                    self.slice_ordo("=== SECTION IV", "V. The Order of the Divine") + "\n" +
                    self.slice_dolnytsky("Chapter III", "Chapter IV")
                ),
                "codebase_files": [
                    "engine/resolvers/matins.py",
                    "json_db/01i_struct_matins.json",
                    "json_db/02e_logic_matins.json"
                ]
            },
            {
                "name": "Divine Liturgy & Physical Choreography",
                "src_slice": (
                    self.slice_ordo("V. The Order of the Divine Liturgy of Saint John", "Glossary") + "\n" +
                    self.slice_dolnytsky("Chapter IV", "PART III")
                ),
                "codebase_files": [
                    "engine/resolvers/liturgy.py",
                    "json_db/01j_struct_liturgy.json",
                    "json_db/02f_logic_liturgy.json"
                ]
            },
            {
                "name": "Movable Feasts & Precedence Cycles",
                "src_slice": self.slice_dolnytsky("PART IV", "PART V"),
                "codebase_files": [
                    "engine/calendar.py",
                    "json_db/02c_logic_triodion.json"
                ]
            },
            {
                "name": "Specific Menaion Feasts & Saints (Part III)",
                "src_slice": self.slice_dolnytsky("PART III", "PART IV"),
                "codebase_files": [
                    "json_db/02b_05_january.json",
                    "json_db/02b_06_february.json",
                    "json_db/02b_10_june.json",
                    "json_db/02k_logic_collisions.json"
                ]
            },
            {
                "name": "Other Daily Cycle Services (Midnight Office, Compline, Hours)",
                "src_slice": self.slice_dolnytsky("Chapter I", "Chapter II"),
                "codebase_files": [
                    "engine/resolvers/hours.py",
                    "json_db/01a_struct_hour_1.json",
                    "json_db/01f_struct_compline.json",
                    "json_db/01g_struct_midnight.json",
                    "json_db/02h_logic_hours.json",
                    "json_db/02i_logic_compline.json",
                    "json_db/02j_logic_midnight.json"
                ]
            }
        ]
        
        full_matrix = []
        
        for t in topics:
            codebase_text = self.get_codebase_files(t["codebase_files"])
            raw_audit = self.execute_topic_audit(t["name"], t["src_slice"], codebase_text)
            validated = self.deterministic_grounding_validation(raw_audit)
            reviewed = self.run_adversarial_review(t["name"], t["src_slice"], validated)
            full_matrix.append(reviewed)
            
        self.generate_final_report(full_matrix)

if __name__ == "__main__":
    auditor = TypikonCodebaseAuditor()
    auditor.run_all()
