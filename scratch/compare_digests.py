import os
import re

gold_dir = r"C:\Users\augus\.gemini\antigravity\brain\d3732588-375b-4ff8-b136-9081fb3c4696\scratch"
gen_dir = r"C:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\Typikon Coded"

mappings = [
    ("TYPICON February 1 Prodigal Son.txt", "Digest_2026-02-01.txt"),
    ("TYPICON February 8, 2026- Last Judgement.txt", "Digest_2026-02-08.txt"),
    ("TYPICON February 15, 2026- Cheesefare.txt", "Digest_2026-02-15.txt"),
    ("TYPICON February 22, 2026- Orthodoxy.txt", "Digest_2026-02-22.txt"),
    ("TYPICON March 1, 2026- Palamas.txt", "Digest_2026-03-01.txt"),
    ("TYPICON March 8, 2026- Veneration of the Cross.txt", "Digest_2026-03-08.txt"),
    ("TYPICON March 15, 2026- Ven. John of the Ladder.txt", "Digest_2026-03-15.txt"),
    ("TYPICON Lazarus Saturday.txt", "Digest_2026-03-28.txt"),
]

def clean_line(line):
    line = line.strip()
    line = re.sub(r'--- Page \d+ ---', '', line)
    line = line.replace('\xa0', ' ').replace('…', '...').replace('’', "'").replace('“', '"').replace('”', '"')
    line = " ".join(line.split())
    return line

with open("scratch/comparison_results.txt", "w", encoding="utf-8") as out:
    for gold_fn, gen_fn in mappings:
        out.write(f"\n==================================================\n")
        out.write(f"Comparing Gold: {gold_fn} vs Gen: {gen_fn}\n")
        out.write(f"==================================================\n")
        
        gold_path = os.path.join(gold_dir, gold_fn)
        gen_path = os.path.join(gen_dir, gen_fn)
        
        if not os.path.exists(gold_path):
            out.write(f"Gold standard path not found: {gold_path}\n")
            continue
        if not os.path.exists(gen_path):
            out.write(f"Generated digest path not found: {gen_path}\n")
            continue
            
        with open(gold_path, "r", encoding="utf-8") as f:
            gold_lines = [clean_line(l) for l in f if clean_line(l)]
            
        with open(gen_path, "r", encoding="utf-8") as f:
            gen_lines = [clean_line(l) for l in f if clean_line(l)]
            
        missing_points = []
        for g_line in gold_lines:
            if g_line.startswith("TYPICON:") or g_line.startswith("Sunday service combined with"):
                continue
            if "Holy Martyr Tryphon" in g_line or "Mother Brigid" in g_line or "transferred to the previous Friday" in g_line:
                found = any("Tryphon" in gen_l and "transferred" in gen_l for gen_l in gen_lines)
                if not found:
                    missing_points.append(g_line)
                continue
                
            words = [re.sub(r'[^\w]', '', w).lower() for w in g_line.split() if len(w) > 4]
            found = False
            for gen_l in gen_lines:
                gen_l_clean = re.sub(r'[^\w\s]', '', gen_l).lower()
                match_count = sum(1 for w in words if w in gen_l_clean)
                if len(words) > 0 and (match_count / len(words)) >= 0.7:
                    found = True
                    break
            if not found:
                missing_points.append(g_line)
                
        if missing_points:
            out.write(f"WARNING: Found {len(missing_points)} potential missing/mismatched points from Gold Standard:\n")
            for idx, mp in enumerate(missing_points):
                out.write(f"  {idx+1}. {mp}\n")
        else:
            out.write("SUCCESS: All key points from Gold Standard matched successfully!\n")
