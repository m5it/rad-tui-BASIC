# Testing Guide for VB1-DOS Clone

## Overview

This document describes the testing procedures for VB1-DOS Clone to ensure compatibility across different terminals and platforms.

## Test Categories

### 1. Project File Interchange Tests

**Script:** `test_project_interchange.py`

Tests JSON project file compatibility:
- Load/save round-trip verification
- Schema validation
- Control name uniqueness
- Menu structure validation
- Code syntax detection (Python vs FreeBASIC)

**Run:**
```bash
python test_project_interchange.py
```

**Expected Output:**
```
============================================================
VB1-DOS Clone Project Interchange Test
============================================================

Testing: examples/hello_world.json
--------------------------------------------------
✓ Load successful
✓ Validation passed
✓ Round-trip save/load successful
...
============================================================
Test Summary
============================================================
  [PASS] hello_world.json
  [PASS] calculator.json
  [PASS] text_editor.json
  [PASS] database_browser.json
  [PASS] timer_demo.json

Total: 5/5 passed
```

### 2. Terminal Compatibility Tests

**Script:** `test_terminal_compat.py`

Tests terminal capabilities:
- UTF-8 support detection
- Color support (number of colors/pairs)
- Mouse support
- Box drawing character rendering
- Mouse event handling

**Run:**
```bash
python test_terminal_compat.py
```

**Tested Terminals:**

| Terminal | UTF-8 | Colors | Mouse | Status |
|----------|-------|--------|-------|--------|
| xterm | ✓ | 256 | ✓ | Full support |
| gnome-terminal | ✓ | 256 | ✓ | Full support |
| konsole | ✓ | 256 | ✓ | Full support |
| alacritty | ✓ | 256 | ✓ | Full support |
| tmux | ✓ | 256 | ✓ | Full support |
| screen | ✓ | 256 | ✗ | No mouse |
| Linux console | ✗ | 8 | ✗ | ASCII fallback |
| Windows Terminal | ✓ | 256 | ✓ | Full support |

### 3. UTF-8 Box Drawing Tests

**Characters Tested:**
- `─` (U+2500) - Horizontal line
- `│` (U+2502) - Vertical line
- `┌` (U+250C) - Top-left corner
- `┐` (U+2510) - Top-right corner
- `└` (U+2514) - Bottom-left corner
- `┘` (U+2518) - Bottom-right corner
- `├` (U+251C) - T-junction right
- `┤` (U+2524) - T-junction left
- `┬` (U+252C) - T-junction down
- `┴` (U+2534) - T-junction up
- `┼` (U+253C) - Cross
- `█` (U+2588) - Full block
- `░` (U+2591) - Light shade
- `■` (U+25A0) - Black square

### 4. Mouse Handling Tests

**Test Cases:**
1. Single click on buttons
2. Double-click to open code editor
3. Drag to move controls
4. Drag resize handle
5. Click menu items
6. Click in list boxes
7. Click on check boxes

**Terminal-Specific Mouse Modes:**
- Mode 1003 (all mouse events)
- Mode 1015 (extended mouse protocol)
- Mode 1006 (SGR mouse protocol)

### 5. Performance Tests

**Metrics:**
- Frame rate (target: 30 FPS)
- Memory usage
- Project load time
- Save time

**Optimization Techniques:**
- Frame rate limiting (30 FPS max)
- Dirty rectangle tracking
- Minimal redraw regions
- Lazy evaluation for properties

## Terminal Compatibility Layer

The `rad-tui-py-compat.py` version includes:

### UTF-8 Detection
```python
def _detect_utf8(self):
    lang = os.environ.get('LANG', '') + os.environ.get('LC_ALL', '')
    return 'utf' in lang.lower()
```

### ASCII Fallback
When UTF-8 is not available:
- `┌┐└┘` → `++++`
- `─│` → `-|`
- `█` → `#`
- `░` → `:`

### Color Fallback
When colors not available:
- Uses `curses.A_BOLD` for emphasis
- Uses `curses.A_REVERSE` for selection
- Monochrome mode

## Known Issues and Workarounds

### Issue: UTF-8 Characters Not Displaying

**Symptom:** Box drawing characters show as `?` or squares.

**Solution:**
```bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

Or use the compatible version:
```bash
python rad-tui-py-compat.py
```

### Issue: Mouse Not Working

**Symptom:** Mouse clicks not registered.

**Causes:**
1. Terminal doesn't support mouse
2. Mouse mode not enabled
3. TERM variable incorrect

**Solutions:**
1. Check terminal capabilities: `infocmp | grep -i mouse`
2. Set TERM: `export TERM=xterm-256color`
3. Use keyboard shortcuts instead

### Issue: Colors Not Displaying

**Symptom:** Everything appears monochrome.

**Solution:**
```bash
export TERM=xterm-256color
# or
export TERM=screen-256color
```

### Issue: Screen Flickering

**Symptom:** Excessive redraw causing flicker.

**Solution:** Use the compatible version with frame rate limiting:
```bash
python rad-tui-py-compat.py
```

## Platform-Specific Notes

### Linux

**Requirements:**
- Python 3.6+ with curses support
- UTF-8 locale configured
- Terminal with mouse support (optional)

**Tested Distributions:**
- Ubuntu 20.04+
- Debian 10+
- Fedora 32+
- Arch Linux

### macOS

**Requirements:**
- Python 3.6+ from Homebrew or python.org
- Terminal.app or iTerm2

**Notes:**
- Terminal.app has limited mouse support
- iTerm2 recommended for full functionality

### Windows

**Requirements:**
- Windows Terminal or WSL
- Python 3.6+

**Notes:**
- Windows Terminal has excellent support
- WSL works with all features
- CMD.exe and PowerShell console have limited support

## Automated Testing

### CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Test VB1-DOS Clone

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      
      - name: Install dependencies
        run: pip install pytest
      
      - name: Run project tests
        run: python test_project_interchange.py
      
      - name: Validate examples
        run: |
          for f in examples/*.json; do
            python -c "import json; json.load(open('$f'))"
          done
```

## Debugging Tips

### Enable Debug Mode

Add to your code:
```python
import curses
curses.trace(2)  # Enable tracing
```

### Check Terminal Info

```bash
echo $TERM
echo $LANG
infocmp $TERM
```

### Test Mouse Support

```bash
# In terminal
printf '\e[?1003h'  # Enable mouse
# Click around, then:
printf '\e[?1003l'  # Disable mouse
```

### Test UTF-8

```bash
echo -e '\u2500\u2502\u250c\u2510\u2514\u2518'
```

Should display box drawing characters.

## Performance Benchmarks

| Operation | Time (ms) | Notes |
|-----------|-----------|-------|
| Load small project | ~50 | 5-10 controls |
| Load large project | ~200 | 50+ controls |
| Save project | ~30 | |
| Add control | ~10 | |
| Switch to run mode | ~100 | Includes code compile |
| Open code editor | ~50 | |

## Regression Testing Checklist

Before releases, verify:

- [ ] All example projects load correctly
- [ ] Save/Load round-trip preserves data
- [ ] UTF-8 characters display correctly
- [ ] Mouse works in supported terminals
- [ ] Keyboard shortcuts function
- [ ] Code editor opens and saves
- [ ] Run mode executes events
- [ ] Properties update in real-time
- [ ] Menu editor functions
- [ ] Frame rate stays above 20 FPS
- [ ] Memory usage remains stable

## Reporting Issues

When reporting terminal compatibility issues, include:

1. Terminal emulator name and version
2. Output of `echo $TERM`
3. Output of `echo $LANG`
4. Python version (`python --version`)
5. Screenshot if possible
6. Steps to reproduce
