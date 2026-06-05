import os
import re

def clean_toc_entry(line):
    # Remove dots and page numbers
    line = re.sub(r'[\.\,0-9]+', '', line)
    # Remove hyphens and weird OCR artifacts
    line = line.replace('’', '').replace('~', '').replace('^', '').replace('-', '')
    line = line.strip().upper()
    return line

def clean_heading(line):
    # Remove leading/trailing non-alphanumeric except spaces
    line = re.sub(r'^[^a-zA-Z]+', '', line)
    line = re.sub(r'[^a-zA-Z]+$', '', line)
    return line.strip().upper()

def extract_toc(filepath):
    expected_services = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            # Skip short lines or lines like "Contents"
            if len(line.strip()) < 5 or "Contents" in line:
                continue
            cleaned = clean_toc_entry(line)
            if cleaned and len(cleaned) > 3:
                expected_services.append(cleaned)
    return expected_services

def extract_headings_from_txt(directory):
    found_headings = set()
    for filename in os.listdir(directory):
        if filename.endswith(".txt") and filename != "TABLE_OF_CONTENTS.txt":
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                for line in f:
                    stripped = line.strip()
                    # A heading is all caps and reasonably long
                    if stripped.isupper() and len(stripped) > 3:
                        cleaned = clean_heading(stripped)
                        if cleaned:
                            found_headings.add(cleaned)
    return found_headings

def main():
    base_dir = r"C:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\Typikon Coded\Data\Service Books\Recensions\Stamford Divine Office\TXT"
    toc_path = os.path.join(base_dir, "TABLE_OF_CONTENTS.txt")
    
    print("Extracting expected services from TOC...")
    expected_services = extract_toc(toc_path)
    
    print("Extracting actual headings from TXT files...")
    found_headings = extract_headings_from_txt(base_dir)
    
    missing = []
    found = []
    
    for expected in expected_services:
        # Check if the expected service name is a substring of any found heading, or vice versa
        match = False
        for found_head in found_headings:
            if expected in found_head or found_head in expected:
                match = True
                break
        
        if match:
            found.append(expected)
        else:
            missing.append(expected)
            
    # Write report
    report_path = os.path.join(base_dir, "Audit_Report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Stamford Divine Office - OCR Completeness Audit\n\n")
        f.write(f"**Total Expected Services from TOC:** {len(expected_services)}\n")
        f.write(f"**Successfully Found:** {len(found)}\n")
        f.write(f"**Missing / Unmatched:** {len(missing)}\n\n")
        
        f.write("## Missing / Unmatched Services\n")
        f.write("The following services listed in the TOC could not be programmatically found as ALL-CAPS headers in the text files. (Note: Some of these may just be OCR variations or formatting differences).\n\n")
        for m in missing:
            f.write(f"- {m}\n")
            
    print(f"Audit complete. Found {len(found)}/{len(expected_services)}. Report saved to Audit_Report.md")

if __name__ == '__main__':
    main()
