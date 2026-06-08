import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import time

BASE_URL = "https://www.st-sergius.org/"
PARSER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(PARSER_DIR)
PDF_DIR = os.path.join(PROJECT_ROOT, "Data", "Service Books", "Recensions", "St Sergius", "PDFs")

# The English pages mapped to their category names
CATEGORIES = {
    "Full Octoechos": "services2.html",
    "General Menaion": "services3.html",
    "Full Menaion": "services4.html",
    "Lenton Triodion": "services6.html",
    "Pentecostarion": "services5.html",
}

# Direct PDF links that don't need a sub-page scraped
DIRECT_LINKS = {
    "Common Theotokia": "services/oktiochos/Theotokia.pdf",
    "Katavasia": "services/Emenaion/Katavasia.pdf"
}

def download_pdf(url, dest_path):
    if os.path.exists(dest_path):
        print(f"  [SKIP] Already exists: {os.path.basename(dest_path)}")
        return False
        
    print(f"  [DOWNLOADING] {url} -> {os.path.basename(dest_path)}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        time.sleep(0.5) # Be polite to the server
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to download {url}: {e}")
        return False

def scrape_category(category_name, page_path):
    category_dir = os.path.join(PDF_DIR, category_name)
    os.makedirs(category_dir, exist_ok=True)
    
    page_url = urljoin(BASE_URL, page_path)
    print(f"\nScraping {category_name} from {page_url}...")
    
    try:
        response = requests.get(page_url, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {page_url}: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')
    
    pdf_count = 0
    for link in links:
        href = link.get('href')
        if not href:
            continue
            
        if href.lower().endswith('.pdf'):
            pdf_url = urljoin(page_url, href)
            # Some links might be absolute but HTTP instead of HTTPS, etc. Let urljoin handle it.
            
            # Clean filename
            filename = unquote(os.path.basename(pdf_url))
            if not filename.lower().endswith('.pdf'):
                filename += ".pdf"
                
            dest_path = os.path.join(category_dir, filename)
            download_pdf(pdf_url, dest_path)
            pdf_count += 1
            
    print(f"Found {pdf_count} PDFs in {category_name}.")

def main():
    print("Starting St Sergius Downloader...")
    os.makedirs(PDF_DIR, exist_ok=True)
    
    # 1. Scrape the HTML categories
    for cat_name, page_path in CATEGORIES.items():
        scrape_category(cat_name, page_path)
        
    # 2. Download the direct links
    for cat_name, pdf_path in DIRECT_LINKS.items():
        print(f"\nProcessing direct link: {cat_name}")
        category_dir = os.path.join(PDF_DIR, cat_name)
        os.makedirs(category_dir, exist_ok=True)
        
        pdf_url = urljoin(BASE_URL, pdf_path)
        filename = unquote(os.path.basename(pdf_url))
        dest_path = os.path.join(category_dir, filename)
        download_pdf(pdf_url, dest_path)

if __name__ == "__main__":
    main()
