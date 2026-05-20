import ast

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    ranges = [
        (8626, 8635), # resolve_litya_content stub
        (8637, 8667), # resolve_artoklasia stub
        (7614, 7651), # resolve_aposticha stub 1
        (9685, 9768), # resolve_aposticha stub 2
        (10899, 10936), # resolve_aposticha stub 3
    ]
    
    ranges.sort(key=lambda x: x[0], reverse=True)
    
    for start, end in ranges:
        del lines[start-1:end]
        
    with open(filepath, 'w', encoding='utf-8') as f:
        # Since readlines() keeps \n at the end of each line, we just writelines directly!
        f.writelines(lines)
        
    print(f"Patched {filepath} successfully.")

patch_file(r'E:\Google Antigravity\Projects\Typikon Coded\ruthenian_engine.py')
