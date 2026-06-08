import re

filepath = "Data/Service Books/Recensions/Stamford Divine Office/TXT/Cleaned_TXT/COMMON OF THE SAINTS.txt"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

categories = re.split(r'^(COMMON OF THE SAINTS|FEASTS OF THE MOTHER OF GOD|COMMON OF A PROPHET|COMMON OF AN APOSTLE|COMMON OF APOSTLES|COMMON FOR A HIERARCH|COMMON OF HIERARCHS|COMMON OF A VENERABLE|COMMON OF VENERABLES|COMMON OF A MARTYR|COMMON OF MARTYRS|COMMON OF A HIEROMARTYR|COMMON OF HIEROMARTYRS|COMMON OF A VENERABLE MARTYR|COMMON OF VENERABLE MARTYRS|COMMON OF A WOMAN MARTYR|COMMON OF WOMEN MARTYRS|COMMON OF A VENERABLE WOMAN|COMMON OF VENERABLE WOMEN|COMMON OF A VENERABLE WOMAN MARTYR|COMMON OF A CONFESSOR|COMMON OF SELFLESS PHYSICIANS AND WONDERWORKERS)\s*$', content, flags=re.MULTILINE)

keywords = ["VESPERS", "MATINS", "LITURGY", "Stichera", "Aposticha", "Sessional", "Exapostilarion", "Canon", "Praises", "Exaltation"]

for idx in range(1, len(categories), 2):
    cat_name = categories[idx].strip()
    cat_text = categories[idx+1]
    
    found_headers = []
    for line in cat_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if any(kw.lower() in line.lower() for kw in keywords) and len(line) < 100:
            found_headers.append(line)
            
    print(f"Category: {cat_name}")
    for fh in found_headers[:10]:
        print(f"  - {fh}")
    print("-" * 40)
