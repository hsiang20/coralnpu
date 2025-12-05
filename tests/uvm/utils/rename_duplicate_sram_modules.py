#!/usr/bin/env python3
"""
Rename duplicate SRAM wrapper module definitions from generated Verilog.

Chisel sometimes generates both SRAM_xxx and Sram_xxx modules.
This script renames the uppercase SRAM_xxx wrapper versions to avoid linker conflicts.
"""

import sys
import re

def rename_duplicate_sram_modules(input_file, output_file):
    """Rename duplicate uppercase SRAM wrapper module definitions and their instantiations."""
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Mapping of uppercase wrapper module names to their new names
    # Only include modules that have duplicates causing linker conflicts
    module_replacements = {
        'SRAM_512x128': 'SRAM_512x128_wrapper',
        'SRAM_2048x128': 'SRAM_2048x128_wrapper',
        # Note: SRAM_1 is NOT included because it's not a duplicate
    }
    
    original_len = len(content)
    definitions_renamed = 0
    instances_renamed = 0
    ports_fixed = 0
    
    for old_name, new_name in module_replacements.items():
        # Step 1: Rename the module definition (e.g., "module SRAM_512x128" -> "module SRAM_512x128_wrapper")
        # Pattern to match module declaration: module SRAM_xxx (with word boundary)
        def_decl_pattern = rf'^module\s+{re.escape(old_name)}\b'
        def_decl_matches = list(re.finditer(def_decl_pattern, content, re.MULTILINE))
        
        if def_decl_matches:
            print(f"Found {len(def_decl_matches)} definition(s) of module '{old_name}', renaming to '{new_name}'")
            definitions_renamed += len(def_decl_matches)
            content = re.sub(def_decl_pattern, f'module {new_name}', content, flags=re.MULTILINE)
        
        # Step 2: Replace instantiations (e.g., "SRAM_512x128 instance_name" -> "SRAM_512x128_wrapper instance_name")
        # Match module instantiation pattern: whitespace + module_name + whitespace + instance_name
        inst_pattern = rf'(\s+){re.escape(old_name)}(\s+\w+\s*\()'
        inst_matches = list(re.finditer(inst_pattern, content))
        
        if inst_matches:
            print(f"Found {len(inst_matches)} instantiation(s) of '{old_name}', renaming to '{new_name}'")
            instances_renamed += len(inst_matches)
            content = re.sub(inst_pattern, rf'\1{new_name}\2', content)
    
    # Clean up multiple consecutive blank lines (more than 2)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Write output
    with open(output_file, 'w') as f:
        f.write(content)
    
    new_len = len(content)
    bytes_changed = abs(original_len - new_len)
    
    print(f"\nRenamed {definitions_renamed} module definition(s)")
    print(f"Renamed {instances_renamed} module instantiation(s)")
    print(f"Fixed {ports_fixed} port connection(s) (removed 'io_' prefix)")
    print(f"File size changed by {bytes_changed:,} bytes")
    print(f"Output written to: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 remove_duplicate_sram_modules.py <input_file> <output_file>")
        print("Example: python3 remove_duplicate_sram_modules.py RvvCoreMiniVerificationAxi.sv RvvCoreMiniVerificationAxi_fixed.sv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    rename_duplicate_sram_modules(input_file, output_file)

