#!/usr/bin/env python3
"""
Function Coverage Verification Script
======================================
Cross-references JSON database function calls with Python engine implementations.

Usage:
    python scripts/verify_function_coverage.py

Output:
    - Detailed gap report showing implemented vs missing functions
    - Line numbers for both JSON calls and Python definitions
    - Status markers for each function (IMPLEMENTED, MISSING, PLACEHOLDER)
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def extract_function_calls_from_json(json_dir="json_db"):
    """
    Extract all function calls from JSON structure files.
    Returns: dict of {function_name: [(file, line_context), ...]}
    """
    function_calls = defaultdict(list)
    
    for root, dirs, files in os.walk(json_dir):
        for filename in files:
            if filename.endswith('.json') and filename.startswith('01'):
                filepath = os.path.join(root, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                    
                    # Find all "function": "function_name" patterns
                    for i, line in enumerate(lines, 1):
                        match = re.search(r'"function"\s*:\s*"([^"]+)"', line)
                        if match:
                            func_name = match.group(1)
                            context = line.strip()[:80]  # First 80 chars
                            function_calls[func_name].append((filename, i, context))
                
                except Exception as e:
                    print(f"{Colors.YELLOW}Warning: Could not parse {filepath}: {e}{Colors.RESET}")
    
    return function_calls

def extract_function_definitions_from_engine(engine_file="ruthenian_engine.py"):
    """
    Extract all function definitions from the Python engine.
    Returns: dict of {function_name: (line_number, signature)}
    """
    function_defs = {}
    
    if not os.path.exists(engine_file):
        print(f"{Colors.RED}Error: Engine file not found: {engine_file}{Colors.RESET}")
        return function_defs
    
    try:
        with open(engine_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find all method definitions (def resolve_*, def check_*, def calculate_*, etc.)
        for i, line in enumerate(lines, 1):
            match = re.match(r'\s*def\s+(resolve_\w+|check_\w+|calculate_\w+|identify_\w+|update_\w+)\s*\(', line)
            if match:
                func_name = match.group(1)
                signature = line.strip()
                function_defs[func_name] = (i, signature)
    
    except Exception as e:
        print(f"{Colors.RED}Error reading engine file: {e}{Colors.RESET}")
    
    return function_defs

def check_if_placeholder(engine_file, func_name, line_number):
    """
    Check if a function implementation is just a placeholder.
    Returns True if function contains [MISSING] or similar markers.
    """
    try:
        with open(engine_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Read next ~20 lines after the function definition
        start = line_number
        end = min(line_number + 20, len(lines))
        func_body = ''.join(lines[start:end])
        
        # Check for placeholder patterns
        placeholder_patterns = [
            r'\[MISSING',
            r'TODO:.*implement',
            r'Placeholder',
            r'raise NotImplementedError',
            r'pass\s*#.*stub',
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, func_body, re.IGNORECASE):
                return True
        
        return False
    
    except Exception:
        return False

def generate_report(function_calls, function_defs, engine_file="ruthenian_engine.py"):
    """
    Generate comprehensive coverage report.
    """
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}FUNCTION COVERAGE AUDIT REPORT{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")
    
    # Categorize functions
    implemented = []
    placeholders = []
    missing = []
    
    all_called_functions = sorted(function_calls.keys())
    
    for func_name in all_called_functions:
        calls = function_calls[func_name]
        
        if func_name in function_defs:
            line_num, signature = function_defs[func_name]
            is_placeholder = check_if_placeholder(engine_file, func_name, line_num)
            
            if is_placeholder:
                placeholders.append((func_name, line_num, calls))
            else:
                implemented.append((func_name, line_num, calls))
        else:
            missing.append((func_name, calls))
    
    # Print statistics
    total = len(all_called_functions)
    impl_count = len(implemented)
    place_count = len(placeholders)
    miss_count = len(missing)
    
    print(f"{Colors.BOLD}SUMMARY:{Colors.RESET}")
    print(f"  Total functions called in JSON DB: {Colors.BOLD}{total}{Colors.RESET}")
    print(f"  {Colors.GREEN}[+] Fully Implemented:{Colors.RESET} {impl_count} ({impl_count*100//total if total else 0}%)")
    print(f"  {Colors.YELLOW}[!] Placeholder/Stub:{Colors.RESET} {place_count} ({place_count*100//total if total else 0}%)")
    print(f"  {Colors.RED}[-] Missing:{Colors.RESET} {miss_count} ({miss_count*100//total if total else 0}%)\n")
    
    # Detailed reports
    if implemented:
        print(f"{Colors.GREEN}{Colors.BOLD}IMPLEMENTED FUNCTIONS ({len(implemented)}):{Colors.RESET}")
        for func_name, line_num, calls in implemented:
            print(f"  {Colors.GREEN}[+]{Colors.RESET} {func_name} (L{line_num})")
            print(f"    Called in: {', '.join(set(c[0] for c in calls))}")
        print()
    
    if placeholders:
        print(f"{Colors.YELLOW}{Colors.BOLD}PLACEHOLDER/STUB FUNCTIONS ({len(placeholders)}):{Colors.RESET}")
        for func_name, line_num, calls in placeholders:
            print(f"  {Colors.YELLOW}[!]{Colors.RESET} {func_name} (L{line_num}) - Needs implementation")
            print(f"    Called in: {', '.join(set(c[0] for c in calls))}")
        print()
    
    if missing:
        print(f"{Colors.RED}{Colors.BOLD}MISSING FUNCTIONS ({len(missing)}):{Colors.RESET}")
        for func_name, calls in missing:
            print(f"  {Colors.RED}[-]{Colors.RESET} {func_name} - NOT DEFINED IN ENGINE")
            for filename, line, context in calls[:3]:  # Show first 3 occurrences
                print(f"    -> {filename}:{line}")
            if len(calls) > 3:
                print(f"    ... and {len(calls)-3} more occurrences")
        print()
    
    # Extra functions (defined but not called)
    all_defined = set(function_defs.keys())
    all_called = set(function_calls.keys())
    extra = all_defined - all_called
    
    if extra:
        print(f"{Colors.BLUE}{Colors.BOLD}EXTRA FUNCTIONS (Defined but not called in JSON):{Colors.RESET}")
        print(f"  Count: {len(extra)}")
        print(f"  {Colors.BLUE}[i]{Colors.RESET} These may be helper functions or legacy code")
        if len(extra) <= 10:
            for func_name in sorted(extra):
                line_num = function_defs[func_name][0]
                print(f"    - {func_name} (L{line_num})")
        else:
            print(f"    (Showing first 10 of {len(extra)})")
            for func_name in sorted(extra)[:10]:
                line_num = function_defs[func_name][0]
                print(f"    - {func_name} (L{line_num})")
        print()
    
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")
    
    # Return statistics for programmatic use
    return {
        'total': total,
        'implemented': impl_count,
        'placeholders': place_count,
        'missing': miss_count,
        'extra': len(extra),
        'missing_list': [name for name, calls in missing],
        'placeholder_list': [name for name, line, calls in placeholders]
    }

def main():
    """Main execution function."""
    print(f"{Colors.CYAN}Starting function coverage verification...{Colors.RESET}\n")
    
    # Extract data
    print("[*] Extracting function calls from JSON database...")
    function_calls = extract_function_calls_from_json()
    print(f"   Found {len(function_calls)} unique function calls\n")
    
    print("[*] Extracting function definitions from Python engine...")
    function_defs = extract_function_definitions_from_engine()
    print(f"   Found {len(function_defs)} function definitions\n")
    
    # Generate report
    stats = generate_report(function_calls, function_defs)
    
    # Save detailed report to file
    report_path = "audit_results/function_coverage_report.txt"
    os.makedirs("audit_results", exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("FUNCTION COVERAGE AUDIT REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Total: {stats['total']}\n")
        f.write(f"Implemented: {stats['implemented']} ({stats['implemented']*100//stats['total'] if stats['total'] else 0}%)\n")
        f.write(f"Placeholders: {stats['placeholders']}\n")
        f.write(f"Missing: {stats['missing']}\n")
        f.write(f"Extra (unused): {stats['extra']}\n\n")
        
        if stats['missing_list']:
            f.write("MISSING FUNCTIONS:\n")
            for func in stats['missing_list']:
                f.write(f"  - {func}\n")
            f.write("\n")
        
        if stats['placeholder_list']:
            f.write("PLACEHOLDER FUNCTIONS:\n")
            for func in stats['placeholder_list']:
                f.write(f"  - {func}\n")
    
    print(f"{Colors.GREEN}[+] Detailed report saved to: {report_path}{Colors.RESET}")
    
    return stats

if __name__ == "__main__":
    main()
