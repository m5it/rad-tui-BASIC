#!/usr/bin/env python3
"""
Template Selection Dialog for VB1-DOS Clone v2.1.0
"""

import curses
import time

def template_selection_dialog(stdscr, colors, template_manager):
    """
    Show template selection dialog
    Returns selected template ID or None if cancelled
    """
    C_BORDER = colors['border']
    C_BG = colors['bg']
    C_ACTIVE = colors['active_tool']
    
    templates = template_manager.get_all_templates()
    template_list = list(templates.items())
    
    if not template_list:
        msgbox(stdscr, colors, "No templates available!", "Error", "ok")
        return None
    
    selected_idx = 0
    scroll_offset = 0
    category_filter = None
    
    w = 70
    h = 20
    x = max(0, (curses.COLS - w) // 2)
    y = max(0, (curses.LINES - h) // 2)
    
    visible_items = h - 8
    
    def get_categories():
        cats = set()
        for tid, t in template_list:
            cats.add(t.get('category', 'Uncategorized'))
        return sorted(['All'] + list(cats))
    
    categories = get_categories()
    selected_cat = 0
    
    def draw_dialog():
        # Border
        write_at(stdscr, x, y, '+' + '-' * (w - 2) + '+', C_BORDER)
        for i in range(1, h - 1):
            write_at(stdscr, x, y + i, '|', C_BORDER)
            write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
            write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
        write_at(stdscr, x, y + h - 1, '+' + '-' * (w - 2) + '+', C_BORDER)
        
        # Title
        title = " Select Template "
        write_at(stdscr, x + (w - len(title)) // 2, y, title, C_BORDER)
        
        # Category filter
        cat_text = f"Category: [{categories[selected_cat]}]"
        write_at(stdscr, x + 2, y + 1, cat_text, C_BORDER)
        
        # Template list
        filtered = [(tid, t) for tid, t in template_list 
                   if category_filter is None or t.get('category') == category_filter]
        
        for i in range(visible_items):
            idx = scroll_offset + i
            if idx < len(filtered):
                tid, template = filtered[idx]
                name = template.get('name', tid)
                desc = template.get('description', '')[:30]
                author = template.get('author', 'Unknown')
                
                is_selected = (idx == selected_idx)
                attr = C_ACTIVE if is_selected else C_BG
                
                prefix = "> " if is_selected else "  "
                line = f"{prefix}{name[:20]:<20} {desc:<30} by {author[:10]}"
                write_at(stdscr, x + 2, y + 3 + i, line[:w-4], attr)
            else:
                write_at(stdscr, x + 2, y + 3 + i, ' ' * (w-4), C_BG)
        
        # Preview area
        preview_y = y + h - 4
        if selected_idx < len(filtered):
            tid, template = filtered[selected_idx]
            preview = f"Description: {template.get('description', 'No description')[:50]}"
            write_at(stdscr, x + 2, preview_y, preview[:w-4], C_BG)
        
        # Instructions
        hint = "[Enter=Select, C=Category, Q=Cancel]"
        write_at(stdscr, x + 2, y + h - 2, hint, C_BORDER)
        
        stdscr.refresh()
    
    def write_at(stdscr, x, y, text, attr=0):
        try:
            if y >= 0 and x >= 0:
                stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass
    
    def msgbox(stdscr, colors, text, title, buttons):
        """Simple message box"""
        lines = text.split('\n')
        bw = max(len(l) for l in lines) + 4
        bh = len(lines) + 4
        bx = max(0, (curses.COLS - bw) // 2)
        by = max(0, (curses.LINES - bh) // 2)
        
        write_at(stdscr, bx, by, '+' + '-' * (bw - 2) + '+', C_BORDER)
        for i in range(1, bh - 1):
            write_at(stdscr, bx, by + i, '|', C_BORDER)
            write_at(stdscr, bx + 1, by + i, ' ' * (bw - 2), C_BG)
            write_at(stdscr, bx + bw - 1, by + i, '|', C_BORDER)
        write_at(stdscr, bx, by + bh - 1, '+' + '-' * (bw - 2) + '+', C_BORDER)
        
        title_x = bx + (bw - len(title)) // 2
        write_at(stdscr, title_x, by, f" {title} ", C_BORDER)
        
        for i, line in enumerate(lines):
            write_at(stdscr, bx + 2, by + 2 + i, line, C_BG)
        
        btn = "[ OK ]"
        write_at(stdscr, bx + (bw - len(btn)) // 2, by + bh - 2, btn, C_BORDER)
        stdscr.refresh()
        
        while True:
            ch = stdscr.getch()
            if ch in (10, 13, 27):
                return
    
    while True:
        draw_dialog()
        ch = stdscr.getch()
        
        filtered = [(tid, t) for tid, t in template_list 
                   if category_filter is None or t.get('category') == category_filter]
        
        if ch == 27 or ch == ord('q') or ch == ord('Q'):
            return None
        elif ch == ord('c') or ch == ord('C'):
            # Cycle categories
            selected_cat = (selected_cat + 1) % len(categories)
            category_filter = None if categories[selected_cat] == 'All' else categories[selected_cat]
            selected_idx = 0
            scroll_offset = 0
        elif ch == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
            if selected_idx < scroll_offset:
                scroll_offset = selected_idx
        elif ch == curses.KEY_DOWN and selected_idx < len(filtered) - 1:
            selected_idx += 1
            if selected_idx >= scroll_offset + visible_items:
                scroll_offset = selected_idx - visible_items + 1
        elif ch in (10, 13, curses.KEY_ENTER):
            if selected_idx < len(filtered):
                return filtered[selected_idx][0]
        
        time.sleep(0.01)


def form_wizard_dialog(stdscr, colors):
    """
    Step-by-step form creation wizard
    Returns form configuration or None
    """
    C_BORDER = colors['border']
    C_BG = colors['bg']
    C_ACTIVE = colors['active_tool']
    C_TB = colors['textbox']
    
    step = 0
    steps = ["Form Title", "Form Size", "Add Controls", "Finish"]
    
    # Form configuration
    form_config = {
        "title": "My Form",
        "width": 40,
        "height": 15,
        "controls": []
    }
    
    w = 60
    h = 16
    
    def draw_wizard():
        x = max(0, (curses.COLS - w) // 2)
        y = max(0, (curses.LINES - h) // 2)
        
        # Border
        write_at(stdscr, x, y, '+' + '-' * (w - 2) + '+', C_BORDER)
        for i in range(1, h - 1):
            write_at(stdscr, x, y + i, '|', C_BORDER)
            write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
            write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
        write_at(stdscr, x, y + h - 1, '+' + '-' * (w - 2) + '+', C_BORDER)
        
        # Title
        title = f" Form Wizard - Step {step + 1} of {len(steps)} "
        write_at(stdscr, x + (w - len(title)) // 2, y, title, C_BORDER)
        
        # Step name
        step_name = steps[step]
        write_at(stdscr, x + 2, y + 2, f"Step: {step_name}", C_BORDER)
        
        # Progress bar
        progress = int(((step + 1) / len(steps)) * (w - 6))
        bar = '[' + '=' * progress + '>' + ' ' * (w - 7 - progress) + ']'
        write_at(stdscr, x + 2, y + 3, bar, C_BG)
        
        # Step content
        if step == 0:  # Title
            write_at(stdscr, x + 2, y + 5, "Enter form title:", C_BG)
            display = (form_config['title'] + "_")[:40]
            write_at(stdscr, x + 2, y + 6, display.ljust(40), C_TB)
        elif step == 1:  # Size
            write_at(stdscr, x + 2, y + 5, f"Width: {form_config['width']}", C_BG)
            write_at(stdscr, x + 2, y + 6, f"Height: {form_config['height']}", C_BG)
            write_at(stdscr, x + 2, y + 8, "Use +/- to adjust", C_BG)
        elif step == 2:  # Controls
            write_at(stdscr, x + 2, y + 5, "Add controls:", C_BG)
            write_at(stdscr, x + 2, y + 6, "1. Button  2. Text Box  3. Label", C_BG)
            write_at(stdscr, x + 2, y + 7, f"Controls added: {len(form_config['controls'])}", C_BG)
        elif step == 3:  # Finish
            write_at(stdscr, x + 2, y + 5, "Configuration complete!", C_BG)
            write_at(stdscr, x + 2, y + 6, f"Title: {form_config['title']}", C_BG)
            write_at(stdscr, x + 2, y + 7, f"Size: {form_config['width']} x {form_config['height']}", C_BG)
            write_at(stdscr, x + 2, y + 8, f"Controls: {len(form_config['controls'])}", C_BG)
        
        # Instructions
        hint = "[N=Next, B=Back, Q=Cancel]" if step < 3 else "[F=Finish, B=Back]"
        write_at(stdscr, x + 2, y + h - 2, hint, C_BORDER)
        
        stdscr.refresh()
    
    def write_at(stdscr, x, y, text, attr=0):
        try:
            if y >= 0 and x >= 0:
                stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass
    
    editing = False
    edit_buffer = ""
    
    while True:
        draw_wizard()
        ch = stdscr.getch()
        
        if ch == 27 or ch == ord('q'):
            return None
        
        if step == 0:  # Title editing
            if not editing and ch == ord('e'):
                editing = True
                edit_buffer = form_config['title']
            elif editing:
                if ch in (10, 13):
                    form_config['title'] = edit_buffer
                    editing = False
                elif ch == 27:
                    editing = False
                elif ch in (8, 127):
                    edit_buffer = edit_buffer[:-1]
                elif 32 <= ch <= 126:
                    edit_buffer += chr(ch)
        
        elif step == 1:  # Size adjustment
            if ch == ord('+') or ch == ord('='):
                form_config['width'] = min(100, form_config['width'] + 5)
            elif ch == ord('-'):
                form_config['width'] = max(20, form_config['width'] - 5)
            elif ch == ord('h') or ch == ord('H'):
                form_config['height'] = min(50, form_config['height'] + 2)
        elif step == 2:  # Add controls
            if ch == ord('1'):
                form_config['controls'].append({"type": 3, "name": "btnNew", "caption": "Button"})
            elif ch == ord('2'):
                form_config['controls'].append({"type": 13, "name": "txtNew", "caption": ""})
            elif ch == ord('3'):
                form_config['controls'].append({"type": 9, "name": "lblNew", "caption": "Label"})
        
        # Navigation
        if ch == ord('n') or ch == ord('N'):
            if step < len(steps) - 1:
                step += 1
        elif ch == ord('b') or ch == ord('B'):
            if step > 0:
                step -= 1
        elif ch == ord('f') or ch == ord('F'):
            if step == 3:
                return form_config
        
        time.sleep(0.01)


# Test
if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    from templates import get_template_manager
    
    def main(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        
        colors = {
            'border': curses.A_BOLD,
            'bg': 0,
            'active_tool': curses.A_BOLD,
            'textbox': curses.A_REVERSE
        }
        
        tm = get_template_manager()
        
        # Test template selection
        result = template_selection_dialog(stdscr, colors, tm)
        if result:
            print(f"\nSelected template: {result}")
        else:
            print("\nCancelled")
        
        # Test wizard
        # result = form_wizard_dialog(stdscr, colors)
        # print(f"\nWizard result: {result}")
        
        stdscr.getch()
    
    curses.wrapper(main)
