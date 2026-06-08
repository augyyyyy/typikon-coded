import os
import sys

def chunk_file(filename, max_words=3000):
    base_dir = r"C:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\Typikon Coded\Data\Service Books\Recensions\Stamford Divine Office\TXT"
    file_path = os.path.join(base_dir, filename)
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} does not exist.")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
        
    lines = text.splitlines()
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for line in lines:
        stripped = line.strip()
        is_heading = stripped.isupper() and len(stripped) > 3
        
        # If it's a heading and we already have a reasonable chunk size, split here
        if is_heading and current_word_count > 1000:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_word_count = len(line.split())
        else:
            current_chunk.append(line)
            current_word_count += len(line.split())
            
            # Fallback if a section is just too long without headings
            if current_word_count > max_words and not line.strip():
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_word_count = 0
                
    if current_chunk:
        chunks.append("\n".join(current_chunk))
        
    # Write chunks to disk
    name_no_ext = os.path.splitext(filename)[0]
    chunks_dir = os.path.join(base_dir, "Chunks", name_no_ext)
    os.makedirs(chunks_dir, exist_ok=True)
    
    # Clean old chunks in that folder first
    for f in os.listdir(chunks_dir):
        if f.endswith(".txt"):
            os.remove(os.path.join(chunks_dir, f))
            
    for i, chunk in enumerate(chunks):
        chunk_filename = f"chunk_{i+1:03d}.txt"
        chunk_path = os.path.join(chunks_dir, chunk_filename)
        with open(chunk_path, 'w', encoding='utf-8') as f:
            f.write(chunk)
            
    print(f"Split {filename} ({len(text)} chars) into {len(chunks)} chunks in {chunks_dir}")
    return len(chunks)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prepare_chunks.py <filename.txt> [max_words]")
        sys.exit(1)
    filename = sys.argv[1]
    max_words = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    chunk_file(filename, max_words)
