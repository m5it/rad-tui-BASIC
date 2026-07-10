#!/usr/bin/env python3
"""
Terminal Compatibility Test for VB1-DOS Clone
Tests UTF-8 box drawing, mouse support, and color capabilities
"""

import curses
import sys
import os

def test_terminal(stdscr):
    results = []
    
    # Test 1: UTF-8 support
    try:
        # Enable UTF-8 mode
        curses.meta(True)
        results.append(("UTF-8 Mode", "PASS", "curses.meta(True) succeeded"))
    except:
        results.append(("UTF-8 Mode", "WARN", "curses.meta() not available"))
    
    # Test 2: Color support
    try:
        curses.start_color()
        colors = curses.COLORS
        pairs = curses.COLOR_PAIRS
        results.append(("Color Support", "PASS", f"{colors} colors, {pairs} pairs"))
    except Exception as e:
        results.append(("Color Support", "FAIL", str(e)))
    
    # Test 3: Mouse support
    try:
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
        results.append(("Mouse Support", "PASS", "Mouse events enabled"))
    except Exception as e:
        results.append(("Mouse Support", "FAIL", str(e)))
    
    # Test 4: UTF-8 box drawing characters
    box_chars = {
        'horizontal': '─',
        'vertical': '│',
        'top_left': '┌',
        'top_right': '┐',
        'bottom_left': '└',
        'bottom_right': '┘',
        'tee_right': '├',
        'tee_left': '┤',
        'tee_down': '┬',
        'tee_up': '┴',
        'cross': '┼',
        'block_full': '█',
        'block_light': '░',
        'triangle_up': '▲',
        'triangle_down': '▼',
        'check': '✓',
        'arrow': '→',
        'bullet': '●',
        'handle': '■'
    }
    
    stdscr.clear()
    stdscr.addstr(0, 0, "Terminal Compatibility Test", curses.A_BOLD)
    stdscr.addstr(1, 0, "=" * 50)
    
    row = 3
    for name, status, info in results:
        color = curses.COLOR_GREEN if status == "PASS" else \
                curses.COLOR_YELLOW if status == "WARN" else curses.COLOR_RED
        try:
            curses.init_pair(1, color, curses.COLOR_BLACK)
            stdscr.addstr(row, 0, f"[{status:4}] {name:20} {info}", curses.color_pair(1))
        except:
            stdscr.addstr(row, 0, f"[{status:4}] {name:20} {info}")
        row += 1
    
    # Test box drawing characters
    stdscr.addstr(row + 1, 0, "Box Drawing Characters:", curses.A_BOLD)
    row += 3
    
    try:
        for name, char in box_chars.items():
            try:
                stdscr.addstr(row, 0, f"{name:15} : {char} {char}{char}{char}")
                row += 1
            except Exception as e:
                stdscr.addstr(row, 0, f"{name:15} : [ERROR - {e}]")
                row += 1
        
        # Draw sample box
        row += 1
        stdscr.addstr(row, 0, "Sample Box:", curses.A_BOLD)
        row += 1
        
        # Try to draw a box
        try:
            stdscr.addstr(row, 0, "┌────────┐")
            stdscr.addstr(row + 1, 0, "│  Test  │")
            stdscr.addstr(row + 2, 0, "└────────┘")
            results.append(("Box Drawing", "PASS", "All characters rendered"))
        except Exception as e:
            stdscr.addstr(row, 0, f"Box drawing failed: {e}")
            results.append(("Box Drawing", "FAIL", str(e)))
            
    except Exception as e:
        stdscr.addstr(row, 0, f"UTF-8 test error: {e}")
        results.append(("UTF-8 Test", "FAIL", str(e)))
    
    # Test mouse
    row += 5
    stdscr.addstr(row, 0, "Click anywhere to test mouse, or press 'q' to quit")
    stdscr.refresh()
    
    curses.mouseinterval(0)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    
    # Enable mouse reporting
    print('\033[?1003h\033[?1015h\033[?1006h', end='', flush=True)
    
    while True:
        ch = stdscr.getch()
        if ch == ord('q'):
            break
        elif ch == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                button = "LEFT" if bstate & curses.BUTTON1_PRESSED else \
                        "MIDDLE" if bstate & curses.BUTTON2_PRESSED else \
                        "RIGHT" if bstate & curses.BUTTON3_PRESSED else "UNKNOWN"
                stdscr.addstr(row - 2, 0, f"Mouse: {button} at ({mx}, {my})    ")
                stdscr.refresh()
            except Exception as e:
                stdscr.addstr(row - 2, 0, f"Mouse error: {e}        ")
                stdscr.refresh()
    
    # Disable mouse reporting
    print('\033[?1003l', end='', flush=True)
    
    return results

def check_terminal_env():
    """Check terminal environment variables"""
    env_info = {
        'TERM': os.environ.get('TERM', 'not set'),
        'COLORTERM': os.environ.get('COLORTERM', 'not set'),
        'LANG': os.environ.get('LANG', 'not set'),
        'LC_ALL': os.environ.get('LC_ALL', 'not set'),
    }
    return env_info

def main():
    print("Terminal Compatibility Test")
    print("=" * 50)
    print()
    
    env = check_terminal_env()
    print("Environment:")
    for key, value in env.items():
        print(f"  {key}={value}")
    print()
    
    print("Running curses test...")
    print("(Press 'q' to exit mouse test)")
    print()
    
    results = curses.wrapper(test_terminal)
    
    print()
    print("Test Summary:")
    print("-" * 50)
    for name, status, info in results:
        print(f"  [{status}] {name}: {info}")
    
    # Recommendations
    print()
    print("Recommendations:")
    print("-" * 50)
    
    if env['TERM'] in ('xterm', 'xterm-256color'):
        print("  ✓ xterm detected - should work well")
    elif env['TERM'] in ('gnome-terminal', 'gnome'):
        print("  ✓ GNOME terminal detected - should work well")
    elif env['TERM'] in ('konsole', 'konsole-256color'):
        print("  ✓ Konsole detected - should work well")
    elif 'alacritty' in env['TERM'].lower():
        print("  ⚠ Alacritty detected - may need UTF-8 config")
    else:
        print(f"  ? Unknown terminal: {env['TERM']}")
        print("    Try: export TERM=xterm-256color")
    
    if 'utf' not in env['LANG'].lower() and 'utf' not in env['LC_ALL'].lower():
        print("  ⚠ UTF-8 locale not set - box drawing may fail")
        print("    Try: export LANG=en_US.UTF-8")
    else:
        print("  ✓ UTF-8 locale configured")

if __name__ == "__main__":
    main()
