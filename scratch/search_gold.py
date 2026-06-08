import os

gold_dir = r"C:\Users\augus\.gemini\antigravity\brain\d3732588-375b-4ff8-b136-9081fb3c4696\scratch"
with open("scratch/search_results.txt", "w", encoding="utf-8") as out:
    for fn in os.listdir(gold_dir):
        if fn.startswith("TYPICON") and fn.endswith(".txt"):
            out.write(f"\n=== {fn} ===\n")
            with open(os.path.join(gold_dir, fn), "r", encoding="utf-8") as f:
                for line in f:
                    if "Glory" in line or "doxas" in line or "Both now" in line:
                        out.write(line.strip() + "\n")
