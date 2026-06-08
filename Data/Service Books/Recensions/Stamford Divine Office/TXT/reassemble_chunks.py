import os
import sys

def reassemble(book_name):
    base_dir = r"C:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\Typikon Coded\Data\Service Books\Recensions\Stamford Divine Office\TXT"
    cleaned_chunks_dir = os.path.join(base_dir, "Cleaned_Chunks", book_name)
    output_path = os.path.join(base_dir, "Cleaned_TXT", f"{book_name}.txt")
    
    if not os.path.exists(cleaned_chunks_dir):
        print(f"Error: {cleaned_chunks_dir} does not exist.")
        return
        
    chunk_files = sorted([f for f in os.listdir(cleaned_chunks_dir) if f.startswith("chunk_") and f.endswith(".txt")])
    if not chunk_files:
        print(f"No chunks found in {cleaned_chunks_dir}")
        return
        
    print(f"Stitching {len(chunk_files)} chunks for {book_name}...")
    full_text = []
    
    for filename in chunk_files:
        chunk_path = os.path.join(cleaned_chunks_dir, filename)
        with open(chunk_path, 'r', encoding='utf-8') as f:
            full_text.append(f.read())
            
    # Join chunks with newline
    final_text = "\n".join(full_text)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_text)
        
    print(f"Reassembled and saved to {output_path} ({len(final_text)} chars).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reassemble_chunks.py <BookName>")
        sys.exit(1)
    book_name = sys.argv[1]
    reassemble(book_name)
