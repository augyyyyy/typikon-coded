import os
import fitz  # PyMuPDF
import glob
import re

PARSER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(PARSER_DIR)
PDF_DIR = os.path.join(PROJECT_ROOT, "Data", "Service Books", "Recensions", "St Sergius", "PDFs")
TEXT_DIR = os.path.join(PROJECT_ROOT, "Data", "Service Books", "Recensions", "St Sergius", "Raw Text")

def extract_text_from_pdf(pdf_path, text_path):
    if os.path.exists(text_path):
        print(f"  [SKIP] Already extracted: {os.path.basename(text_path)}")
        return
        
    print(f"  [EXTRACTING] {os.path.basename(pdf_path)}")
    try:
        doc = fitz.open(pdf_path)
        full_text = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            # We append a page break marker for later heuristic use
            full_text.append(f"--- PAGE {page_num + 1} ---")
            full_text.append(text)
            
        with open(text_path, "w", encoding="utf-8") as f:
            f.write("\n".join(full_text))
            
    except Exception as e:
        print(f"  [ERROR] Failed to extract {pdf_path}: {e}")

def process_category(category_name):
    cat_pdf_dir = os.path.join(PDF_DIR, category_name)
    cat_text_dir = os.path.join(TEXT_DIR, category_name)
    
    if not os.path.exists(cat_pdf_dir):
        return
        
    os.makedirs(cat_text_dir, exist_ok=True)
    pdf_files = glob.glob(os.path.join(cat_pdf_dir, "*.pdf"))
    
    print(f"\nProcessing {category_name} ({len(pdf_files)} PDFs)...")
    for pdf_path in pdf_files:
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        text_path = os.path.join(cat_text_dir, base_name + ".txt")
        extract_text_from_pdf(pdf_path, text_path)

def main():
    print("Starting St Sergius Text Extractor...")
    os.makedirs(TEXT_DIR, exist_ok=True)
    
    if not os.path.exists(PDF_DIR):
        print(f"PDF Directory not found: {PDF_DIR}")
        return
        
    categories = [d for d in os.listdir(PDF_DIR) if os.path.isdir(os.path.join(PDF_DIR, d))]
    for category in categories:
        process_category(category)

if __name__ == "__main__":
    main()
