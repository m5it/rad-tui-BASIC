#!/usr/bin/env python3
"""
Project File Interchange Test
Tests compatibility between Python and FreeBASIC versions
"""

import json
import sys
import os

def validate_project(data, filename):
    """Validate project file structure"""
    errors = []
    warnings = []
    
    # Check required fields
    required = ['x', 'y', 'w', 'h', 'title', 'controls']
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate controls
    if 'controls' in data:
        name_ids = set()
        for i, ctrl in enumerate(data['controls']):
            # Check control fields
            ctrl_required = ['x', 'y', 'w', 'h', 'tool_type', 'name_id', 'caption']
            for field in ctrl_required:
                if field not in ctrl:
                    errors.append(f"Control {i}: missing {field}")
            
            # Check name_id uniqueness
            if 'name_id' in ctrl:
                if ctrl['name_id'] in name_ids:
                    errors.append(f"Duplicate name_id: {ctrl['name_id']}")
                name_ids.add(ctrl['name_id'])
            
            # Validate tool_type
            if 'tool_type' in ctrl:
                valid_types = {1, 2, 3, 7, 9, 10, 11, 13, 14}
                if ctrl['tool_type'] not in valid_types:
                    warnings.append(f"Control {i}: unknown tool_type {ctrl['tool_type']}")
            
            # Check dimensions
            if 'w' in ctrl and ctrl['w'] < 4:
                warnings.append(f"Control {i}: width {ctrl['w']} is very small")
            if 'h' in ctrl and ctrl['h'] < 1:
                errors.append(f"Control {i}: height must be >= 1")
    
    # Validate menu items
    if 'menu_items' in data:
        for i, item in enumerate(data['menu_items']):
            if 'caption' not in item:
                errors.append(f"Menu item {i}: missing caption")
            if 'name_id' not in item:
                errors.append(f"Menu item {i}: missing name_id")
    
    return errors, warnings

def test_load_save(filepath):
    """Test loading and saving a project file"""
    print(f"\nTesting: {filepath}")
    print("-" * 50)
    
    try:
        # Load
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Load successful")
        
        # Validate
        errors, warnings = validate_project(data, filepath)
        
        if errors:
            print(f"✗ Validation errors:")
            for e in errors:
                print(f"    - {e}")
        else:
            print(f"✓ Validation passed")
        
        if warnings:
            print(f"⚠ Warnings:")
            for w in warnings:
                print(f"    - {w}")
        
        # Save to temp and reload
        temp_path = filepath + ".tmp"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        with open(temp_path, 'r', encoding='utf-8') as f:
            data2 = json.load(f)
        
        if data == data2:
            print(f"✓ Round-trip save/load successful")
        else:
            print(f"✗ Round-trip mismatch!")
            # Show differences
            import difflib
            s1 = json.dumps(data, sort_keys=True)
            s2 = json.dumps(data2, sort_keys=True)
            if s1 != s2:
                print("    Data changed during round-trip")
        
        os.remove(temp_path)
        
        # Summary
        stats = {
            'controls': len(data.get('controls', [])),
            'menu_items': len(data.get('menu_items', [])),
            'title': data.get('title', 'untitled'),
            'size': f"{data.get('w', 0)}x{data.get('h', 0)}"
        }
        print(f"  Stats: {stats['controls']} controls, {stats['menu_items']} menu items")
        print(f"  Form: '{stats['title']}' ({stats['size']})")
        
        return len(errors) == 0
        
    except json.JSONDecodeError as e:
        print(f"✗ JSON parse error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_code_compatibility(filepath):
    """Test code compatibility between Python and FreeBASIC"""
    print(f"\nCode Compatibility: {filepath}")
    print("-" * 50)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        python_funcs = []
        basic_funcs = []
        
        for ctrl in data.get('controls', []):
            code = ctrl.get('code', '')
            if not code:
                continue
            
            # Detect Python
            if 'def ' in code and ':' in code:
                python_funcs.append((ctrl['name_id'], code))
            
            # Detect FreeBASIC
            if 'Sub ' in code and 'End Sub' in code:
                basic_funcs.append((ctrl['name_id'], code))
        
        if python_funcs:
            print(f"Python functions found: {len(python_funcs)}")
            for name, code in python_funcs:
                lines = code.count('\n') + 1
                print(f"  - {name}: {lines} lines")
        
        if basic_funcs:
            print(f"FreeBASIC functions found: {len(basic_funcs)}")
            for name, code in basic_funcs:
                lines = code.count('\n') + 1
                print(f"  - {name}: {lines} lines")
        
        if not python_funcs and not basic_funcs:
            print("No code found in controls")
        
        # Check for mixed syntax
        if python_funcs and basic_funcs:
            print("⚠ Warning: Mixed Python and FreeBASIC syntax detected!")
            print("  This project may not run correctly in either version.")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    examples_dir = "examples"
    
    if not os.path.exists(examples_dir):
        print(f"Examples directory not found: {examples_dir}")
        sys.exit(1)
    
    test_files = [
        "hello_world.json",
        "calculator.json", 
        "text_editor.json",
        "database_browser.json",
        "timer_demo.json"
    ]
    
    print("=" * 60)
    print("VB1-DOS Clone Project Interchange Test")
    print("=" * 60)
    
    results = []
    
    for filename in test_files:
        filepath = os.path.join(examples_dir, filename)
        if os.path.exists(filepath):
            success = test_load_save(filepath)
            test_code_compatibility(filepath)
            results.append((filename, success))
        else:
            print(f"\n✗ File not found: {filename}")
            results.append((filename, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    for filename, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {filename}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
