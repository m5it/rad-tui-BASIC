#!/usr/bin/env python3
"""
Test script for v2.1.0 dialog functions
"""

import curses
import time
import os

def write_at(stdscr, x, y, text, attr=0):
    try:
        if y >= 0 and x >= 0:
            stdscr.addstr(y, x, text, attr)
    except curses.error:
        pass

def msgbox(stdscr, colors, text, title="Message", buttons="ok"):
    """Enhanced message box with multiple button options"""
    C_BORDER = colors['border']
    C_BG = colors['bg']
    C_ACTIVE = colors.get('active_tool', curses.A_BOLD)
    
    lines = text.split('\n')
    content_w = max([len(l) for l in lines] + [len(title), 20])
    
    btn_configs = {
        'ok': ['[ OK ]'],
        'okcancel': ['[ OK ]', '[ Cancel ]'],
        'yesno': ['[ Yes ]', '[ No ]'],
        'yesnocancel': ['[ Yes ]', '[ No ]', '[ Cancel ]']
    }
    
    btn_list = btn_configs.get(buttons, ['[ OK ]'])
    btn_w = sum(len(b) + 2 for b in btn_list)
    w = max(content_w + 4, btn_w + 4, len(title) + 4)
    h = len(lines) + 6
    
    x = max(0, (curses.COLS - w) // 2)
    y = max(0, (curses.LINES - h) // 2)
    
    def draw(selected_btn=0):
        write_at(stdscr, x, y, '+' + '-' * (w - 2) + '+', C_BORDER)
        for i in range(1, h - 1):
            write_at(stdscr, x, y + i, '|', C_BORDER)
            write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
            write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
        write_at(stdscr, x, y + h - 1, '+' + '-' * (w - 2) + '+', C_BORDER)
        
        title_x = x + (w - len(title)) // 2
        write_at(stdscr, title_x, y, f" {title} ", C_BORDER)
        
        for i, line in enumerate(lines[:h-4]):
            write_at(stdscr, x + 2, y + 2 + i, line[:w-4], C_BG)
        
        btn_x = x + (w - btn_w) // 2
        for i, btn in enumerate(btn_list):
            attr = C_ACTIVE if i == selected_btn else C_BG
            write_at(stdscr, btn_x, y + h - 2, btn, attr)
            btn_x += len(btn) + 2
        
        stdscr.refresh()
    
    selected = 0
    draw(selected)
    
    while True:
        ch = stdscr.getch()
        
        if ch == curses.KEY_LEFT:
            selected = max(0, selected - 1)
            draw(selected)
        elif ch == curses.KEY_RIGHT:
            selected = min(len(btn_list) - 1, selected + 1)
            draw(selected)
        elif ch in (10, 13, curses.KEY_ENTER):
            values = {'ok': ['ok'], 'okcancel': ['ok', 'cancel'],
                     'yesno': ['yes', 'no'], 'yesnocancel': ['yes', 'no', 'cancel']}
            return values.get(buttons, ['ok'])[selected]
        elif ch == 27:
            if buttons in ['okcancel', 'yesnocancel']:
                return 'cancel'
            return 'ok'
        
        time.sleep(0.01)

def inputbox(stdscr, colors, prompt, title="Input", default=""):
    """Text input dialog"""
    C_BORDER = colors['border']
    C_BG = colors['bg']
    C_TB = colors.get('textbox', C_BG)
    
    prompt_lines = prompt.split('\n')
    w = min(50, curses.COLS - 4)
    h = len(prompt_lines) + 6
    
    x = max(0, (curses.COLS - w) // 2)
    y = max(0, (curses.LINES - h) // 2)
    
    buffer = default
    
    while True:
        write_at(stdscr, x, y, '+' + '-' * (w - 2) + '+', C_BORDER)
        for i in range(1, h - 1):
            write_at(stdscr, x, y + i, '|', C_BORDER)
            write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
            write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
        write_at(stdscr, x, y + h - 1, '+' + '-' * (w - 2) + '+', C_BORDER)
        
        title_x = x + (w - len(title)) // 2
        write_at(stdscr, title_x, y, f" {title} ", C_BORDER)
        
        for i, line in enumerate(prompt_lines):
            write_at(stdscr, x + 2, y + 2 + i, line[:w-4], C_BG)
        
        display = (buffer + "_")[:w-4]
        write_at(stdscr, x + 2, y + h - 3, display.ljust(w-4), C_TB)
        
        hint = "[Enter=OK, Esc=Cancel]"
        write_at(stdscr, x + (w - len(hint)) // 2, y + h - 2, hint, C_BG)
        
        stdscr.refresh()
        
        ch = stdscr.getch()
        
        if ch == 27:
            return None
        elif ch in (10, 13, curses.KEY_ENTER):
            return buffer
        elif ch in (8, 127, curses.KEY_BACKSPACE):
            buffer = buffer[:-1]
        elif 32 <= ch <= 126 and len(buffer) < w - 5:
            buffer += chr(ch)
        
        time.sleep(0.01)

def color_picker(stdscr, colors):
    """Simple color picker"""
    C_BORDER = colors['border']
    C_BG = colors['bg']
    C_ACTIVE = colors.get('active_tool', curses.A_BOLD)
    
    color_names = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    
    w = 40
    h = 12
    x = max(0, (curses.COLS - w) // 2)
    y = max(0, (curses.LINES - h) // 2)
    
    cursor = 0
    
    def draw():
        write_at(stdscr, x, y, '+' + '-' * (w - 2) + '+', C_BORDER)
        for i in range(1, h - 1):
            write_at(stdscr, x, y + i, '|', C_BORDER)
            write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
            write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
        write_at(stdscr, x, y + h - 1, '+' + '-' * (w - 2) + '+', C_BORDER)
        
        title = " Select Color "
        write_at(stdscr, x + (w - len(title)) // 2, y, title, C_BORDER)
        
        for i, color in enumerate(color_names):
            col = i % 4
            row = i // 4
            cell_x = x + 2 + col * 9
            cell_y = y + 2 + row
            
            attr = C_ACTIVE if i == cursor else C_BG
            display = color[:8].center(8)
            write_at(stdscr, cell_x, cell_y, display, attr)
        
        preview = f"Selected: {color_names[cursor]}"
        write_at(stdscr, x + 2, y + h - 3, preview[:w-4], C_BG)
        
        btn_text = "[ OK ]  [ Cancel ]"
        write_at(stdscr, x + (w - len(btn_text)) // 2, y + h - 2, btn_text, C_BORDER)
        
        stdscr.refresh()
    
    while True:
        draw()
        ch = stdscr.getch()
        
        if ch == 27:
            return None
        elif ch == curses.KEY_LEFT:
            cursor = max(0, cursor - 1)
        elif ch == curses.KEY_RIGHT:
            cursor = min(len(color_names) - 1, cursor + 1)
        elif ch == curses.KEY_UP:
            cursor = max(0, cursor - 4)
        elif ch == curses.KEY_DOWN:
            cursor = min(len(color_names) - 1, cursor + 4)
        elif ch in (10, 13, curses.KEY_ENTER):
            return color_names[cursor]
        
        time.sleep(0.01)

def font_dialog(stdscr, colors):
    """Font selection dialog"""
    C_BORDER = colors['border']
    C_BG = colors['bg']
    C_ACTIVE = colors.get('active_tool', curses.A_BOLD)
    
    sizes = [8, 10, 12, 14, 16, 18, 20, 24]
    families = ['monospace', 'serif', 'sans-serif', 'courier']
    
    w = 40
    h = 12
    x = max(0, (curses.COLS - w) // 2)
    y = max(0, (curses.LINES - h) // 2)
    
    selected_size = 2
    selected_family = 0
    
    def draw():
        write_at(stdscr, x, y, '+' + '-' * (w - 2) + '+', C_BORDER)
        for i in range(1, h - 1):
            write_at(stdscr, x, y + i, '|', C_BORDER)
            write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
            write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
        write_at(stdscr, x, y + h - 1, '+' + '-' * (w - 2) + '+', C_BORDER)
        
        title = " Font Selection "
        write_at(stdscr, x + (w - len(title)) // 2, y, title, C_BORDER)
        
        write_at(stdscr, x + 2, y + 2, "Size:", C_BORDER)
        size_str = ' '.join(str(s) if i != selected_size else f'[{s}]' 
                          for i, s in enumerate(sizes))
        write_at(stdscr, x + 8, y + 2, size_str[:w-10], C_BG)
        
        write_at(stdscr, x + 2, y + 4, "Family:", C_BORDER)
        for i, family in enumerate(families):
            attr = C_ACTIVE if i == selected_family else C_BG
            prefix = '> ' if i == selected_family else '  '
            write_at(stdscr, x + 10, y + 5 + i, prefix + family, attr)
        
        preview = f"{sizes[selected_size]}pt {families[selected_family]}"
        write_at(stdscr, x + 2, y + h - 3, preview[:w-4], C_BG)
        
        btn_text = "[ OK ]  [ Cancel ]"
        write_at(stdscr, x + (w - len(btn_text)) // 2, y + h - 2, btn_text, C_BORDER)
        
        stdscr.refresh()
    
    while True:
        draw()
        ch = stdscr.getch()
        
        if ch == 27:
            return None
        elif ch == curses.KEY_UP:
            selected_family = max(0, selected_family - 1)
        elif ch == curses.KEY_DOWN:
            selected_family = min(len(families) - 1, selected_family + 1)
        elif ch == curses.KEY_LEFT:
            selected_size = max(0, selected_size - 1)
        elif ch == curses.KEY_RIGHT:
            selected_size = min(len(sizes) - 1, selected_size + 1)
        elif ch in (10, 13, curses.KEY_ENTER):
            return {'size': sizes[selected_size], 'family': families[selected_family]}
        
        time.sleep(0.01)

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    
    # Setup colors
    try:
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        
        colors = {
            'border': curses.color_pair(1) | curses.A_BOLD,
            'bg': curses.color_pair(2),
            'active_tool': curses.color_pair(3) | curses.A_BOLD,
            'textbox': curses.A_REVERSE
        }
    except:
        colors = {
            'border': curses.A_BOLD, 'bg': 0,
            'active_tool': curses.A_BOLD, 'textbox': curses.A_REVERSE
        }
    
    # Main menu
    options = [
        "1. Test msgbox (OK)",
        "2. Test msgbox (OK/Cancel)",
        "3. Test msgbox (Yes/No)",
        "4. Test inputbox",
        "5. Test color_picker",
        "6. Test font_dialog",
        "7. Run All Tests",
        "Q. Quit"
    ]
    
    selected = 0
    
    while True:
        stdscr.clear()
        write_at(stdscr, 2, 2, "VB1-DOS Clone v2.1.0 - Dialog Test", colors['border'])
        write_at(stdscr, 2, 4, "Select a test:", colors['bg'])
        
        for i, opt in enumerate(options):
            attr = colors['active_tool'] if i == selected else colors['bg']
            write_at(stdscr, 4, 6 + i, opt, attr)
        
        write_at(stdscr, 2, 16, "Use arrow keys and Enter, or press number key", colors['bg'])
        stdscr.refresh()
        
        ch = stdscr.getch()
        
        if ch == curses.KEY_UP:
            selected = max(0, selected - 1)
        elif ch == curses.KEY_DOWN:
            selected = min(len(options) - 1, selected + 1)
        elif ch in (10, 13, curses.KEY_ENTER):
            if selected == 0:
                result = msgbox(stdscr, colors, "This is a simple message box!", "Info", "ok")
                msgbox(stdscr, colors, f"You clicked: {result}", "Result", "ok")
            elif selected == 1:
                result = msgbox(stdscr, colors, "Do you want to continue?", "Confirm", "okcancel")
                msgbox(stdscr, colors, f"You clicked: {result}", "Result", "ok")
            elif selected == 2:
                result = msgbox(stdscr, colors, "Are you sure?", "Question", "yesno")
                msgbox(stdscr, colors, f"You clicked: {result}", "Result", "ok")
            elif selected == 3:
                result = inputbox(stdscr, colors, "Enter your name:", "Input", "User")
                msgbox(stdscr, colors, f"You entered: {result}", "Result", "ok")
            elif selected == 4:
                result = color_picker(stdscr, colors)
                msgbox(stdscr, colors, f"You selected: {result}", "Result", "ok")
            elif selected == 5:
                result = font_dialog(stdscr, colors)
                msgbox(stdscr, colors, f"Font: {result}", "Result", "ok")
            elif selected == 6:
                # Run all tests
                msgbox(stdscr, colors, "Starting all tests...", "Test Suite", "ok")
                
                r1 = msgbox(stdscr, colors, "Test 1: OK button", "Test", "ok")
                r2 = msgbox(stdscr, colors, "Test 2: OK/Cancel", "Test", "okcancel")
                r3 = msgbox(stdscr, colors, "Test 3: Yes/No", "Test", "yesno")
                r4 = inputbox(stdscr, colors, "Test 4: Input", "Test", "default")
                r5 = color_picker(stdscr, colors)
                r6 = font_dialog(stdscr, colors)
                
                summary = f"Results:\nOK: {r1}\nOK/Cancel: {r2}\nYes/No: {r3}\nInput: {r4}\nColor: {r5}\nFont: {r6}"
                msgbox(stdscr, colors, summary, "All Tests Complete", "ok")
            elif selected == 7:
                break
        elif ch == ord('1'):
            selected = 0
        elif ch == ord('2'):
            selected = 1
        elif ch == ord('3'):
            selected = 2
        elif ch == ord('4'):
            selected = 3
        elif ch == ord('5'):
            selected = 4
        elif ch == ord('6'):
            selected = 5
        elif ch == ord('7'):
            selected = 6
        elif ch in (ord('q'), ord('Q')):
            break
        
        time.sleep(0.01)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nExiting...")
