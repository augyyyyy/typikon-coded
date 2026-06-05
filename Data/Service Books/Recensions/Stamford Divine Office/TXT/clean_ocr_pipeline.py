import os
import re
from openai import OpenAI

# Initialize local LM Studio client
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="not-needed")
# Check project_brainprint.md for the model name usually used by the user. 
# They mentioned qwen2.5-coder-14b-instruct
MODEL_NAME = "qwen2.5-coder-14b-instruct"

SYSTEM_PROMPT = """You are an expert liturgical text editor and OCR cleaner. 
Your task is to fix OCR errors in the provided text (such as 'l' instead of '1', 'rn' instead of 'm', random spaces inside words, or broken line breaks mid-sentence).

CRITICAL RULES:
1. STAMFORD VERBATIM RULE: You must NOT alter the translation, theology, or vocabulary in any way. Preserve all English terminology exactly as printed (e.g., "Sessional Hymn", not "Kathisma").
2. Do not summarize. Do not skip text. Output the full text with only the OCR typos and formatting fixed.
3. Preserve the ALL-CAPS headings exactly as they are.
4. HIERATIC CAPITALIZATION & NEGATIVE CONSTRAINTS: Capitalize pronouns referring to the Holy Trinity (He, Him, Who). You MUST strictly enforce negative constraints: pronouns referring to the Theotokos (Virgin Mary), saints, angels, humans, and the devil must remain lowercase (e.g., you, your, whom). Do NOT over-capitalize (e.g. "your Creator" referring to Mary's Creator should be lowercase 'your').
5. Return ONLY the cleaned text, with no conversational filler or markdown code blocks (unless formatting requires it)."""

def chunk_text(text, max_words=800):
    """Splits text by ALL CAPS headings, then by double-newlines if still too long."""
    lines = text.splitlines()
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for line in lines:
        stripped = line.strip()
        is_heading = stripped.isupper() and len(stripped) > 3
        
        # If it's a heading and the current chunk has substantial text, start a new chunk
        if is_heading and current_word_count > 50:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_word_count = len(line.split())
        else:
            current_chunk.append(line)
            current_word_count += len(line.split())
            
            # Fallback if a section is just too long
            if current_word_count > max_words and not line.strip():
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_word_count = 0
                
    if current_chunk:
        chunks.append("\n".join(current_chunk))
        
    return chunks

def process_chunk(chunk_text):
    print(f"Sending chunk of {len(chunk_text.split())} words to LM Studio...")
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Please clean this OCR text:\n\n{chunk_text}"}
            ],
            temperature=0.1,
            max_tokens=2048,
            timeout=120.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error processing chunk: {e}")
        return chunk_text  # Return original on failure

import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python clean_ocr_pipeline.py <filename.txt>")
        sys.exit(1)
        
    filename = sys.argv[1]
    base_dir = r"C:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\Typikon Coded\Data\Service Books\Recensions\Stamford Divine Office\TXT"
    output_dir = os.path.join(base_dir, "Cleaned_TXT")
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(base_dir, filename)
    output_path = os.path.join(output_dir, filename)
    part_path = output_path + ".part"
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        sys.exit(1)
        
    if os.path.exists(output_path):
        print(f"Skipping {filename}, already fully cleaned.")
        sys.exit(0)
        
    print(f"\n--- Processing {filename} ---")
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
        
    chunks = chunk_text(text)
    print(f"Split {filename} into {len(chunks)} chunks.")
    
    # Check for incremental progress
    completed_chunks = 0
    if os.path.exists(part_path):
        with open(part_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # If the part file exists, we assume chunks are separated by the ALL-CAPS headers. 
            # But simpler: we can just count how many times we appended to it by keeping a separate progress tracker, 
            # or just read the raw text. To be robust, let's track progress in a tiny metadata file or just count chunks.
            # Actually, let's keep a `.progress` file that just holds the integer of completed chunks.
    
    progress_file = output_path + ".progress"
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            try:
                completed_chunks = int(f.read().strip())
            except:
                completed_chunks = 0
                
    if completed_chunks > 0:
        print(f"Resuming from chunk {completed_chunks + 1}...")
        
    for i in range(completed_chunks, len(chunks)):
        chunk = chunks[i]
        print(f"Chunk {i+1}/{len(chunks)}...")
        cleaned = process_chunk(chunk)
        
        # Incrementally append to the .part file
        mode = 'a' if i > 0 else 'w'
        with open(part_path, mode, encoding='utf-8') as f:
            if i > 0:
                f.write("\n")
            f.write(cleaned)
            
        # Update progress file
        with open(progress_file, 'w') as f:
            f.write(str(i + 1))
            
    # When fully complete, rename .part to final and remove progress file
    if os.path.exists(output_path):
        os.remove(output_path)
    os.rename(part_path, output_path)
    if os.path.exists(progress_file):
        os.remove(progress_file)
        
    print(f"Finished {filename}. Saved to {output_path}")

if __name__ == '__main__':
    main()
