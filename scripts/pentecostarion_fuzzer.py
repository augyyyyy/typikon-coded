import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from datetime import date, timedelta
from ruthenian_engine import RuthenianEngine

def format_canon(canon_res):
    if not canon_res:
        return "None"
    return f"{canon_res.get('subject', 'unknown')} ({canon_res.get('book', 'unknown')})"

def format_katavasia(kat_res):
    if not kat_res:
        return "None"
    return f"Tone {kat_res.get('tone', '?')}: {kat_res.get('text', 'unknown')}"

def format_magnificat(mag_res):
    if not mag_res:
        return "None"
    mag_id = mag_res.get("magnificat_id", "default")
    t = mag_res.get("type", "default")
    if t in ("suppressed_magnificat", "paschal_magnificat", "festal_magnificat") or mag_id == "suppressed":
        return "Suppressed"
    return mag_id

def main():
    engine = RuthenianEngine(base_dir=".", paschalion="gregorian")
    
    # In 2026, Gregorian Pascha is April 5
    pascha_date = date(2026, 4, 5)
    
    output_lines = []
    output_lines.append("# Pentecostarion & Eucharist Season Fuzz Audit (2026)")
    output_lines.append("This table lists the resolved liturgical variables for every day of the season (offsets 0 to 67).\n")
    
    output_lines.append("| Date | Offset | Day | Feast / Saint Title | Tone | Rank | Compline Canon | Katavasia | Magnificat | Fasting |")
    output_lines.append("| :--- | :---: | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- |")
    
    for offset in range(0, 68):
        target_date = pascha_date + timedelta(days=offset)
        ctx = engine.get_liturgical_context(target_date)
        
        # Resolve variables
        compline_canon = engine.resolve_compline_canon(ctx)
        katavasia = engine.resolve_katavasia(ctx)
        magnificat = engine.resolve_magnificat(ctx)
        fasting = engine.resolve_fasting_rule(ctx)
        
        # Format variables
        day_name = target_date.strftime("%a")
        
        title = ctx.get("title_key", "Ordinary Day")
        if title.startswith("menaion."):
            title = title.replace("menaion.", "")
        elif title.startswith("pentecostarion."):
            title = title.replace("pentecostarion.", "")
        elif title.startswith("triodion."):
            title = title.replace("triodion.", "")
            
        rank = ctx.get("rank_id", "rank_none")
        
        row = (
            f"| {target_date} | {offset} | {day_name} | {title[:40]} | {ctx['tone']} | "
            f"{rank} | {format_canon(compline_canon)} | {format_katavasia(katavasia)} | "
            f"{format_magnificat(magnificat)} | {fasting['type']} |"
        )
        output_lines.append(row)
        
    output_content = "\n".join(output_lines) + "\n"
    
    # Path to artifacts dir
    dest_path = r"C:\Users\augus\.gemini\antigravity\brain\960bb940-280e-4e01-8bf8-55bdfe4cfe4d\pentecostarion_audit_2026.md"
    
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(output_content)
        
    print(f"Audit written successfully to: {dest_path}")
    
    # Path to repo dir
    repo_dest = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audit_results", "pentecostarion_audit_2026.md")
    os.makedirs(os.path.dirname(repo_dest), exist_ok=True)
    with open(repo_dest, "w", encoding="utf-8") as f:
        f.write(output_content)
        
    print(f"Audit written successfully to repo: {repo_dest}")

if __name__ == "__main__":
    main()
