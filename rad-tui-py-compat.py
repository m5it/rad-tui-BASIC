#!/usr/bin/env python3
"""
VB1-DOS Clone: Terminal-Compatible Version
Features:
- ASCII fallback for terminals without UTF-8
- Improved mouse handling for various terminals
- Performance optimizations
- Terminal capability detection
"""

import curses
import time
import re
import copy
import json
import os
import sys

# ==========================================================
# Terminal Compatibility Layer
# ==========================================================

class TerminalCompat:
    """Handle terminal differences"""
    
    def __init__(self):
        self.has_utf8 = self._detect_utf8()
        self.has_mouse = False
        self.has_colors = False
        self.term_name = os.environ.get('TERM', 'unknown')
        
    def _detect_utf8(self):
        """Detect UTF-8 support"""
        lang = os.environ.get('LANG', '') + os.environ.get('LC_ALL', '')
        return 'utf' in lang.lower() or 'utf-8' in lang.lower()
    
    def setup(self, stdscr):
        """Setup terminal capabilities"""
        # Check colors
        try:
            curses.start_color()
            self.has_colors = curses.has_colors() and curses.COLORS >= 8
        except:
            self.has_colors = False
            
        # Check mouse
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS)
            self.has_mouse = True
        except:
            self.has_mouse = False
            
        # Enable UTF-8 if available
        try:
            curses.meta(True)
        except:
            pass
            
        return self.has_colors
    
    def get_box_chars(self):
        """Get box drawing characters based on terminal capability"""
        if self.has_utf8:
            return {
                'h': '─', 'v': '│',
                'tl': '┌', 'tr': '┐',
                'bl': '└', 'br': '┘',
                'tee_r': '├', 'tee_l': '┤',
                'tee_d': '┬', 'tee_u': '┴',
                'cross': '┼',
                'block': '█', 'shade': '░',
                'handle': '■', 'arrow': '→',
                'check': '✓', 'bullet': '●'
            }
        else:
            # ASCII fallback
            return {
                'h': '-', 'v': '|',
                'tl': '+', 'tr': '+',
                'bl': '+', 'br': '+',
                'tee_r': '+', 'tee_l': '+',
                'tee_d': '+', 'tee_u': '+',
                'cross': '+',
                'block': '#', 'shade': ':',
                'handle': '#', 'arrow': '->',
                'check': 'OK', 'bullet': '*'
            }

# Global compatibility instance
TERM = TerminalCompat()

# ==========================================================
# Python Keywords for Syntax Highlighting
# ==========================================================

PYTHON_KEYWORDS = {
    "def", "class", "if", "elif", "else", "while", "for", "in", 
    "return", "pass", "import", "from", "and", "or", "not", 
    "True", "False", "None", "try", "except", "with", "as", 
    "global", "nonlocal", "break", "continue", "print", "exec",
    "yield", "lambda", "assert", "del", "raise", "finally"
}

def tokenize_python(line):
    """Tokenize Python code for syntax highlighting"""
    pattern = re.compile(r'(\s+|\w+|"[^"]*"|\'[^\']*\'|#[^\n]*|.)')
    tokens = []
    for token in pattern.findall(line):
        if not token:
            continue
        if token[0].isspace():
            tokens.append((token, 'text'))
        elif token.startswith('#'):
            tokens.append((token, 'comment'))
        elif token.startswith('"') or token.startswith("'"):
            tokens.append((token, 'string'))
        elif token in PYTHON_KEYWORDS:
            tokens.append((token, 'keyword'))
        elif re.match(r'^\d+(\.\d+)?$', token):
            tokens.append((token, 'number'))
        elif re.match(r'^\w+$', token):
            tokens.append((token, 'text'))
        else:
            tokens.append((token, 'text'))
    return tokens

# ==========================================================
# Core Classes
# ==========================================================

class MenuItem:
    def __init__(self, caption="", name_id="", parent=0):
        self.caption = caption
        self.name_id = name_id
        self.parent = parent
        self.has_submenu = False
        self.code = ""

class UIControl:
    def __init__(self, x, y, w, h, tool_type, name_id, caption):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.tool_type = tool_type
        self.name_id = name_id
        self.caption = caption
        self.code = ""
        self.checked = False
        self.group = ""
        self.parent = 0
        self.items = []
        self.selected_index = -1
        self.scroll_offset = 0

    def to_dict(self):
        return {
            'x': self.x, 'y': self.y, 'w': self.w, 'h': self.h,
            'tool_type': self.tool_type, 'name_id': self.name_id,
            'caption': self.caption, 'code': self.code,
            'checked': self.checked, 'group': self.group,
            'parent': self.parent,
            'items': self.items,
            'selected_index': self.selected_index,
            'scroll_offset': self.scroll_offset
        }

    @classmethod
    def from_dict(cls, data):
        c = cls(data['x'], data['y'], data['w'], data['h'], 
                data['tool_type'], data['name_id'], data['caption'])
        c.code = data.get('code', '')
        c.checked = data.get('checked', False)
        c.group = data.get('group', '')
        c.parent = data.get('parent', 0)
        c.items = data.get('items', [])
        c.selected_index = data.get('selected_index', -1)
        c.scroll_offset = data.get('scroll_offset', 0)
        return c

class Window:
    def __init__(self, x, y, w, h, title="untitled"):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.controls = []
        self.menu_items = []
        self._last_focused = -1  # For focus tracking

    def to_dict(self):
        return {
            'x': self.x, 'y': self.y, 'w': self.w, 'h': self.h,
            'title': self.title,
            'controls': [c.to_dict() for c in self.controls],
            'menu_items': [{'caption': m.caption, 'name_id': m.name_id, 
                          'parent': m.parent, 'has_submenu': m.has_submenu} 
                         for m in self.menu_items]
        }

    @classmethod
    def from_dict(cls, data):
        w = cls(data['x'], data['y'], data['w'], data['h'], data['title'])
        w.controls = [UIControl.from_dict(c) for c in data.get('controls', [])]
        w.menu_items = []
        for m in data.get('menu_items', []):
            mi = MenuItem(m['caption'], m['name_id'], m.get('parent', 0))
            mi.has_submenu = m.get('has_submenu', False)
            w.menu_items.append(mi)
        return w

    def add_menu_item(self, caption, name_id, parent=0):
        if len(self.menu_items) < 50:
            self.menu_items.append(MenuItem(caption, name_id, parent))
            if parent > 0 and parent <= len(self.menu_items):
                self.menu_items[parent - 1].has_submenu = True

    def draw_menu_bar(self, stdscr, colors, box_chars):
        C_BG = colors['bg']
        menu_text = ""
        for m in self.menu_items:
            if m.parent == 0:
                if menu_text:
                    menu_text += "  "
                menu_text += m.caption
        if menu_text:
            line = (menu_text + " " * (self.w - 2))[:self.w - 2]
            write_at(stdscr, self.x + 1, self.y + 1, line, C_BG)

    def add_control(self, cx, cy, ctype, ctitle):
        if len(self.controls) < 30:
            name_id = f"ctrl{len(self.controls) + 1}"
            
            if ctype == 1:
                ctrl = UIControl(cx, cy, 20, 1, ctype, name_id, "[ ] Check")
                ctrl.checked = False
            elif ctype == 2:
                ctrl = UIControl(cx, cy, 20, 1, ctype, name_id, "Combo")
                ctrl.items = ["Item 1", "Item 2", "Item 3"]
                ctrl.selected_index = -1
            elif ctype == 3:
                ctrl = UIControl(cx, cy, 12, 3, ctype, name_id, "Button")
            elif ctype == 7:
                ctrl = UIControl(cx, cy, 20, 10, ctype, name_id, "Frame")
                ctrl.parent = 0
            elif ctype == 10:
                ctrl = UIControl(cx, cy, 20, 6, ctype, name_id, "List")
                ctrl.items = ["Item 1", "Item 2", "Item 3", "Item 4"]
                ctrl.selected_index = -1
                ctrl.scroll_offset = 0
            elif ctype == 11:
                ctrl = UIControl(cx, cy, 20, 1, ctype, name_id, "( ) Option")
                ctrl.checked = False
                ctrl.group = ""
            elif ctype == 13:
                ctrl = UIControl(cx, cy, 15, 1, ctype, name_id, "Text1")
            elif ctype == 14:
                ctrl = UIControl(cx, cy, 10, 1, ctype, name_id, "Timer")
            else:
                ctrl = UIControl(cx, cy, 12, 1, ctype, name_id, ctitle)
            
            ctrl.code = ""
            self.controls.append(ctrl)
            self.redraw()

    def redraw(self, active_ctrl=-1):
        pass

    def hit_test(self, mx, my):
        return (self.x <= mx < self.x + self.w) and (self.y <= my < self.y + self.h)

    def hit_control(self, lx, ly):
        for i in range(len(self.controls) - 1, -1, -1):
            c = self.controls[i]
            if (c.x <= lx < c.x + c.w) and (c.y <= ly < c.y + c.h):
                return i
        return -1

class Toolbox:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 16
        self.h = 20
        self.active_tool = -1
        self.items = [
            "Move/Size", "Check Box", "Combo Box", "Command Btn",
            "Dir List", "Drive List", "File List", "Frame",
            "HScrollBar", "Label", "List Box", "Option Btn",
            "Picture Box", "Text Box", "Timer", "VScrollBar"
        ]

    def draw(self, stdscr, colors, box_chars):
        C_TB = colors['textbox']
        C_ACTIVE = colors['active_tool']

        # Top border
        top = box_chars['tl'] + box_chars['h'] * (self.w - 2) + box_chars['tr']
        write_at(stdscr, self.x, self.y, top, C_TB)
        
        # Title
        title = "-Tools-"
        write_at(stdscr, self.x + (self.w // 2) - 3, self.y, title, C_TB)
        
        curr_y = self.y + 1
        # First item
        text = (self.items[0] + " " * (self.w - 2))[:self.w - 2]
        line = box_chars['v'] + text + box_chars['v']
        write_at(stdscr, self.x, curr_y, line, C_ACTIVE if self.active_tool == 0 else C_TB)
        curr_y += 1
        
        # Separator
        sep = box_chars['tee_r'] + box_chars['h'] * (self.w - 2) + box_chars['tee_l']
        write_at(stdscr, self.x, curr_y, sep, C_TB)
        curr_y += 1
        
        # Remaining items
        for i in range(1, 16):
            text = (self.items[i] + " " * (self.w - 2))[:self.w - 2]
            line = box_chars['v'] + text + box_chars['v']
            write_at(stdscr, self.x, curr_y, line, C_ACTIVE if self.active_tool == i else C_TB)
            curr_y += 1
            
        # Bottom border
        bottom = box_chars['bl'] + box_chars['h'] * (self.w - 2) + box_chars['br']
        write_at(stdscr, self.x, curr_y, bottom, C_TB)

    def process_click(self, mx, my):
        if self.x <= mx < self.x + self.w:
            if my == self.y + 1:
                self.active_tool = 0
                return True
            elif self.y + 3 <= my <= self.y + 17:
                self.active_tool = my - (self.y + 2)
                return True
        return False

# ==========================================================
# Drawing Functions
# ==========================================================

def write_at(stdscr, x, y, text, attr=0):
    """Write text at position with error handling"""
    try:
        if y >= 0 and x >= 0:
            stdscr.addstr(y, x, text, attr)
    except curses.error:
        pass

def draw_properties(stdscr, prop_win, windows, selected_win_idx, selected_ctrl_idx, 
                    editing_prop, edit_buffer, colors, tools):
    C_BG = colors['bg']
    C_TB = colors['textbox']
    C_LABEL = colors['prop_label']
    
    for py in range(1, prop_win.h - 1):
        write_at(stdscr, prop_win.x + 1, prop_win.y + py, " " * (prop_win.w - 2), C_BG)

    if selected_win_idx >= 0 and selected_ctrl_idx >= 0:
        c = windows[selected_win_idx].controls[selected_ctrl_idx]
        tool_name = tools.items[c.tool_type].strip()
        
        write_at(stdscr, prop_win.x + 2, prop_win.y + 2, f"Type: {tool_name}", C_LABEL)
        write_at(stdscr, prop_win.x + 1, prop_win.y + 3, "-" * (prop_win.w - 2), C_BG)

        def draw_prop(ly, lbl, p_id, val_str):
            write_at(stdscr, prop_win.x + 2, prop_win.y + ly, lbl, C_LABEL)
            if editing_prop == p_id:
                eb = edit_buffer + "_"
                display_text = eb[-10:] if len(eb) > 10 else (eb + "          ")[:10]
            else:
                vs = str(val_str)
                display_text = vs[:10] if len(vs) > 10 else (vs + "          ")[:10]
            write_at(stdscr, prop_win.x + 8, prop_win.y + ly, display_text, C_TB)

        draw_prop(5, "Name:", 1, c.name_id)
        draw_prop(6, "Cap: ", 2, c.caption)
        draw_prop(7, "X:   ", 3, c.x)
        draw_prop(8, "Y:   ", 4, c.y)
        draw_prop(9, "W:   ", 5, c.w)
        draw_prop(10,"H:   ", 6, c.h)
    else:
        form_win = windows[0]
        write_at(stdscr, prop_win.x + 2, prop_win.y + 2, "Form Properties", C_LABEL)
        write_at(stdscr, prop_win.x + 1, prop_win.y + 3, "-" * (prop_win.w - 2), C_BG)
        write_at(stdscr, prop_win.x + 2, prop_win.y + 5, f"Menu items: {len(form_win.menu_items)}", C_LABEL)
        write_at(stdscr, prop_win.x + 2, prop_win.y + 7, " Click here to edit menu ", curses.color_pair(1) | curses.A_BOLD)

def draw_code_editor(stdscr, lines, cy, cx, target_name, box_x, box_y, box_w, box_h, colors, event_type="click"):
    C_BORDER = colors['border']
    C_BG = colors['bg']
    
    # Top border
    write_at(stdscr, box_x, box_y, "+" + "-" * (box_w - 2) + "+", C_BORDER)
    
    for i in range(1, box_h - 1):
        write_at(stdscr, box_x, box_y + i, "|", C_BORDER)
        write_at(stdscr, box_x + box_w - 1, box_y + i, "|", C_BORDER)
        
        line_idx = i - 1
        if line_idx < len(lines):
            line_text = lines[line_idx]
            tokens = tokenize_python(line_text)
            
            curr_x = box_x + 1
            chars_printed = 0
            
            for text_chunk, ttype in tokens:
                if chars_printed >= box_w - 2:
                    break
                    
                space_left = (box_w - 2) - chars_printed
                render_str = text_chunk[:space_left]
                
                attr = C_BG
                if TERM.has_colors:
                    if ttype == 'keyword': attr = colors['kw']
                    elif ttype == 'string': attr = colors['str']
                    elif ttype == 'number': attr = colors['num']
                    elif ttype == 'comment': attr = colors['comment']
                
                write_at(stdscr, curr_x, box_y + i, render_str, attr)
                curr_x += len(render_str)
                chars_printed += len(render_str)
            
            if chars_printed < box_w - 2:
                write_at(stdscr, curr_x, box_y + i, " " * ((box_w - 2) - chars_printed), C_BG)
        else:
            write_at(stdscr, box_x + 1, box_y + i, " " * (box_w - 2), C_BG)
            
    # Bottom border
    write_at(stdscr, box_x, box_y + box_h - 1, "+" + "-" * (box_w - 2) + "+", C_BORDER)
    
    title = f" Code: {target_name} ({event_type}) "
    write_at(stdscr, box_x + (box_w - len(title))//2, box_y, title, C_BORDER)
    write_at(stdscr, box_x + box_w - 4, box_y, "[X]", C_BORDER)

    if cy < box_h - 2:
        real_x = box_x + 1 + min(cx, box_w - 3)
        real_y = box_y + 1 + cy
        try:
            stdscr.move(real_y, real_x)
        except curses.error:
            pass

def draw_msgbox(stdscr, msg, colors):
    C_BORDER = colors['border']
    C_BG = colors['bg']
    lines = msg.split('\n')
    w = max([len(l) for l in lines] + [20]) + 4
    h = len(lines) + 4
    x = max(0, (curses.COLS - w) // 2)
    y = max(0, (curses.LINES - h) // 2)
    
    # Simple ASCII box
    write_at(stdscr, x, y, "+" + "-" * (w - 2) + "+", C_BORDER)
    for i in range(1, h - 1):
        write_at(stdscr, x, y + i, "|", C_BORDER)
        write_at(stdscr, x + 1, y + i, " " * (w - 2), C_BG)
        write_at(stdscr, x + w - 1, y + i, "|", C_BORDER)
    write_at(stdscr, x, y + h - 1, "+" + "-" * (w - 2) + "+", C_BORDER)
    
    for i, l in enumerate(lines):
        write_at(stdscr, x + 2, y + 2 + i, l, C_BG)
    
    write_at(stdscr, x + (w - 6) // 2, y + h - 2, "[ OK ]", C_BORDER)

def show_sync_msgbox(stdscr, msg, colors):
    draw_msgbox(stdscr, msg, colors)
    stdscr.refresh()
    while True:
        ch = stdscr.getch()
        if ch == curses.KEY_MOUSE:
            try:
                _, _, _, _, bstate = curses.getmouse()
                if bstate & curses.BUTTON1_PRESSED or bstate & curses.BUTTON1_CLICKED:
                    break
            except curses.error:
                pass
        elif ch in (10, 13, 27) and ch != -1:
            break
        time.sleep(0.01)

def handle_file_menu(stdscr, colors):
    C_BORDER = colors['border']
    C_BG = colors['bg']
    menu_items = [" Save Project As... ", " Load Project...    ", " Exit IDE           "]
    w = 22
    h = len(menu_items) + 2
    x = 1
    y = 1
    
    write_at(stdscr, x, y, "+" + "-" * (w - 2) + "+", C_BORDER)
    for i, item in enumerate(menu_items):
        write_at(stdscr, x, y + i + 1, "|", C_BORDER)
        write_at(stdscr, x + 1, y + i + 1, item, C_BG)
        write_at(stdscr, x + w - 1, y + i + 1, "|", C_BORDER)
    write_at(stdscr, x, y + h - 1, "+" + "-" * (w - 2) + "+", C_BORDER)
    stdscr.refresh()
    
    while True:
        ch = stdscr.getch()
        if ch == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                if bstate & curses.BUTTON1_PRESSED or bstate & curses.BUTTON1_CLICKED:
                    if x < mx < x + w and y < my < y + h:
                        idx = my - y - 1
                        if idx == 0: return 'save'
                        if idx == 1: return 'load'
                        if idx == 2: return 'exit'
                    return None
            except curses.error:
                pass
        elif ch == 27:
            return None
        time.sleep(0.01)

def prompt_input(stdscr, prompt_title, colors):
    C_BORDER = colors['border']
    C_BG = colors['bg']
    C_TB = colors['textbox']
    
    box_w = min(40, curses.COLS - 4)
    box_h = 5
    box_x = max(0, (curses.COLS - box_w) // 2)
    box_y = max(0, (curses.LINES - box_h) // 2)
    
    buffer = ""
    while True:
        write_at(stdscr, box_x, box_y, "+" + "-" * (box_w - 2) + "+", C_BORDER)
        for i in range(1, box_h - 1):
            write_at(stdscr, box_x, box_y + i, "|", C_BORDER)
            write_at(stdscr, box_x + 1, box_y + i, " " * (box_w - 2), C_BG)
            write_at(stdscr, box_x + box_w - 1, box_y + i, "|", C_BORDER)
        write_at(stdscr, box_x, box_y + box_h - 1, "+" + "-" * (box_w - 2) + "+", C_BORDER)
        
        title = f" {prompt_title} "
        write_at(stdscr, box_x + (box_w - len(title))//2, box_y, title, C_BORDER)
        write_at(stdscr, box_x + 2, box_y + 2, (buffer + "_").ljust(box_w - 4)[:box_w-4], C_TB)
        stdscr.refresh()
        
        ch = stdscr.getch()
        if ch == 27:
            return None
        elif ch in (10, 13, curses.KEY_ENTER):
            return buffer.strip()
        elif ch in (8, 127, curses.KEY_BACKSPACE):
            buffer = buffer[:-1]
        elif 32 <= ch <= 126 and ch != -1:
            if len(buffer) < box_w - 5:
                buffer += chr(ch)
        time.sleep(0.01)

def edit_menu_dialog(stdscr, form_win, colors):
    C_BORDER = colors['border']
    C_BG = colors['bg']
    C_ACTIVE = colors['active_tool']
    
    box_w = min(50, curses.COLS - 4)
    box_h = min(15, curses.LINES - 4)
    box_x = max(0, (curses.COLS - box_w) // 2)
    box_y = max(0, (curses.LINES - box_h) // 2)
    
    cursor = 0
    
    while True:
        write_at(stdscr, box_x, box_y, "+" + "-" * (box_w - 2) + "+", C_BORDER)
        for i in range(1, box_h - 1):
            write_at(stdscr, box_x, box_y + i, "|" + " " * (box_w - 2) + "|", C_BG)
        write_at(stdscr, box_x, box_y + box_h - 1, "+" + "-" * (box_w - 2) + "+", C_BORDER)
        
        write_at(stdscr, box_x + 2, box_y, " Menu Editor ", C_BORDER)
        write_at(stdscr, box_x + 2, box_y + box_h - 1, " A=Add | D=Delete | ESC=Close ", C_BG)
        
        row = 1
        for i, m in enumerate(form_win.menu_items[:20]):
            indent = "  -> " if m.parent > 0 else ""
            sel_mark = "> " if cursor == i else "  "
            text = sel_mark + indent + m.caption
            write_at(stdscr, box_x + 2, box_y + row, text.ljust(box_w - 6)[:box_w-6], 
                    C_ACTIVE if cursor == i else C_BG)
            row += 1
            if row >= box_h - 2:
                break
        
        stdscr.refresh()
        
        ch = stdscr.getch()
        if ch == 27:
            return
        elif ch == ord('a') or ch == ord('A'):
            cap = prompt_input(stdscr, "Menu Caption", colors)
            if cap:
                nid = prompt_input(stdscr, "Menu Name ID", colors)
                if nid:
                    parent_idx = 0
                    if cursor < len(form_win.menu_items) and form_win.menu_items[cursor].parent == 0:
                        write_at(stdscr, box_x + 5, box_y + box_h // 2, 
                                f"Add as submenu of {form_win.menu_items[cursor].caption}? (Y/N)", C_BORDER)
                        stdscr.refresh()
                        while True:
                            confirm = stdscr.getch()
                            if confirm in (ord('y'), ord('Y')):
                                parent_idx = cursor + 1
                                form_win.menu_items[cursor].has_submenu = True
                                break
                            elif confirm in (ord('n'), ord('N')):
                                break
                    form_win.add_menu_item(cap, nid, parent_idx)
        elif ch == ord('d') or ch == ord('D'):
            if 0 <= cursor < len(form_win.menu_items):
                form_win.menu_items.pop(cursor)
                if cursor >= len(form_win.menu_items):
                    cursor = max(0, len(form_win.menu_items) - 1)
        elif ch == curses.KEY_UP:
            if cursor > 0:
                cursor -= 1
        elif ch == curses.KEY_DOWN:
            if cursor < len(form_win.menu_items) - 1:
                cursor += 1
        
        time.sleep(0.01)

def draw_window(stdscr, win, colors, box_chars, active_ctrl=-1):
    C_BORDER = colors['border']
    C_BG = colors['bg']
    C_HANDLE = colors['handle']

    # Top border
    top = box_chars['tl'] + box_chars['h'] * (win.w - 2) + box_chars['tr']
    write_at(stdscr, win.x, win.y, top, C_BORDER)
    
    # Title
    title_x = win.x + (win.w - len(win.title)) // 2
    write_at(stdscr, title_x, win.y, win.title, C_BORDER)
    
    # Side borders
    for i in range(1, win.h - 1):
        write_at(stdscr, win.x, win.y + i, box_chars['v'], C_BORDER)
        write_at(stdscr, win.x + 1, win.y + i, " " * (win.w - 2), C_BG)
        write_at(stdscr, win.x + win.w - 1, win.y + i, box_chars['v'], C_BORDER)
    
    # Bottom border
    bottom = box_chars['bl'] + box_chars['h'] * (win.w - 2) + box_chars['br']
    write_at(stdscr, win.x, win.y + win.h - 1, bottom, C_BORDER)

    if win.menu_items:
        win.draw_menu_bar(stdscr, colors, box_chars)

    # Draw controls - frames first, then others
    for i, c in enumerate(win.controls):
        if c.tool_type == 7:
            draw_control(stdscr, win, c, i == active_ctrl, colors, box_chars)
    
    for i, c in enumerate(win.controls):
        if c.tool_type != 7:
            draw_control(stdscr, win, c, i == active_ctrl, colors, box_chars)

    # Draw resize handle
    if active_ctrl >= 0 and active_ctrl < len(win.controls):
        c = win.controls[active_ctrl]
        hx = win.x + c.x + c.w
        hy = win.y + c.y + c.h
        if hx < win.x + win.w and hy < win.y + win.h:
            write_at(stdscr, hx, hy, box_chars['handle'], C_HANDLE)

def draw_control(stdscr, win, c, is_active, colors, box_chars):
    C_BORDER = colors['border']
    C_BG = colors['bg']
    C_BTN_FACE = colors['btn_face']
    C_BTN_HL = colors['btn_hl']
    C_TEXTBOX = colors['textbox']
    
    draw_x = win.x + c.x
    draw_y = win.y + c.y
    
    # Adjust for parent frame
    if c.parent > 0 and c.parent <= len(win.controls):
        parent = win.controls[c.parent - 1]
        if c.x < parent.x + 1:
            draw_x = win.x + parent.x + 1
        if c.y < parent.y + 1:
            draw_y = win.y + parent.y + 1
    
    if c.tool_type == 1:  # Check Box
        check_state = "[X]" if c.checked else "[ ]"
        label = c.caption[3:] if c.caption.startswith('[ ]') or c.caption.startswith('[X]') else c.caption
        write_at(stdscr, draw_x, draw_y, f"{check_state}{label}", C_BG)
        
    elif c.tool_type == 2:  # Combo Box
        display_text = c.caption
        if c.selected_index >= 0 and c.selected_index < len(c.items):
            display_text = c.items[c.selected_index]
        if len(display_text) > c.w - 4:
            display_text = display_text[:c.w - 4]
        write_at(stdscr, draw_x, draw_y, " " + display_text.ljust(c.w - 4) + " [v]", C_BG)
        
    elif c.tool_type == 3:  # Command Button
        actual_h = max(3, c.h)
        top = box_chars['tl'] + box_chars['h'] * (c.w - 2) + box_chars['tr']
        write_at(stdscr, draw_x, draw_y, top, C_BTN_HL)
        for r in range(1, actual_h - 1):
            if r == actual_h // 2:
                btn_text = c.caption.center(c.w - 2)
                line = box_chars['v'] + btn_text + box_chars['v']
                write_at(stdscr, draw_x, draw_y + r, line, C_BTN_FACE)
            else:
                line = box_chars['v'] + " " * (c.w - 2) + box_chars['v']
                write_at(stdscr, draw_x, draw_y + r, line, C_BTN_FACE)
        bottom = box_chars['bl'] + box_chars['h'] * (c.w - 2) + box_chars['br']
        write_at(stdscr, draw_x, draw_y + actual_h - 1, bottom, C_BTN_FACE)
        
    elif c.tool_type == 7:  # Frame
        top = box_chars['tl'] + box_chars['h'] * (c.w - 2) + box_chars['tr']
        write_at(stdscr, draw_x, draw_y, top, C_BORDER)
        for r in range(1, c.h - 1):
            line = box_chars['v'] + " " * (c.w - 2) + box_chars['v']
            write_at(stdscr, draw_x, draw_y + r, line, C_BG)
        bottom = box_chars['bl'] + box_chars['h'] * (c.w - 2) + box_chars['br']
        write_at(stdscr, draw_x, draw_y + c.h - 1, bottom, C_BORDER)
        if c.caption:
            write_at(stdscr, draw_x + 2, draw_y, f" {c.caption} ", C_BORDER)
            
    elif c.tool_type == 10:  # List Box
        top = box_chars['tl'] + box_chars['h'] * (c.w - 3) + box_chars['tee_d'] + box_chars['tr']
        write_at(stdscr, draw_x, draw_y, top, C_BG)
        visible_rows = c.h - 2
        for r in range(visible_rows):
            item_idx = c.scroll_offset + r
            line = box_chars['v']
            if item_idx < len(c.items):
                item_text = c.items[item_idx]
                if len(item_text) > c.w - 4:
                    item_text = item_text[:c.w - 4]
                if item_idx == c.selected_index and TERM.has_colors:
                    attr = curses.color_pair(3) | curses.A_BOLD
                else:
                    attr = C_BG
                line += " " + item_text.ljust(c.w - 4)[:c.w-4]
            else:
                line += " " * (c.w - 3)
            line += box_chars['v'] + box_chars['v']
            write_at(stdscr, draw_x, draw_y + 1 + r, line, attr if item_idx == c.selected_index and TERM.has_colors else C_BG)
        
        bottom = box_chars['bl'] + box_chars['h'] * (c.w - 3) + box_chars['tee_u'] + box_chars['br']
        write_at(stdscr, draw_x, draw_y + c.h - 1, bottom, C_BG)
        
        # Scrollbar
        if len(c.items) > visible_rows:
            sb_height = visible_rows
            thumb_size = max(1, (visible_rows * sb_height) // len(c.items))
            if len(c.items) > visible_rows:
                thumb_pos = (c.scroll_offset * (sb_height - thumb_size)) // (len(c.items) - visible_rows)
            else:
                thumb_pos = 0
            for r in range(sb_height):
                ch = box_chars['block'] if r >= thumb_pos and r < thumb_pos + thumb_size else box_chars['shade']
                write_at(stdscr, draw_x + c.w - 1, draw_y + 1 + r, ch, C_BG)
                
    elif c.tool_type == 11:  # Option Button
        opt_state = "(*)" if c.checked else "( )"
        label = c.caption[3:] if c.caption.startswith('( )') or c.caption.startswith('(*)') else c.caption
        write_at(stdscr, draw_x, draw_y, f"{opt_state}{label}", C_BG)
        
    elif c.tool_type == 13:  # Text Box
        for r in range(c.h):
            if r == 0:
                display_text = c.caption
                if len(display_text) >= c.w:
                    display_text = display_text[-(c.w-1):]
                text = (display_text + " " * c.w)[:c.w]
                write_at(stdscr, draw_x, draw_y + r, text, C_TEXTBOX)
            else:
                write_at(stdscr, draw_x, draw_y + r, " " * c.w, C_TEXTBOX)
    else:
        for r in range(c.h):
            if r == 0:
                text = (c.caption + " " * c.w)[:c.w]
                write_at(stdscr, draw_x, draw_y + r, text, C_TEXTBOX)
            else:
                write_at(stdscr, draw_x, draw_y + r, " " * c.w, C_TEXTBOX)

# ==========================================================
# Main Application
# ==========================================================

def main(stdscr):
    # Initialize terminal compatibility
    TERM.setup(stdscr)
    box_chars = TERM.get_box_chars()
    
    curses.curs_set(0)
    stdscr.nodelay(True)
    
    # Setup mouse with error handling
    try:
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.mouseinterval(0)
        # Enable extended mouse mode
        print('\033[?1003h\033[?1015h\033[?1006h', end='', flush=True)
        TERM.has_mouse = True
    except Exception as e:
        TERM.has_mouse = False
        print(f"Mouse setup warning: {e}", file=sys.stderr)

    # Initialize colors if available
    if TERM.has_colors:
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)    
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)   
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_WHITE)   
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)    
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)   
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)    
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)   
        curses.init_pair(8, curses.COLOR_BLUE, curses.COLOR_WHITE)    
        curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_WHITE)   
        curses.init_pair(10, curses.COLOR_RED, curses.COLOR_WHITE)    
        curses.init_pair(11, curses.COLOR_MAGENTA, curses.COLOR_WHITE)

        C = {
            'border': curses.color_pair(1) | curses.A_BOLD,
            'bg': curses.color_pair(2),
            'btn_face': curses.color_pair(2),
            'btn_hl': curses.color_pair(3) | curses.A_BOLD,
            'textbox': curses.color_pair(4),
            'handle': curses.color_pair(5),
            'active_tool': curses.color_pair(6) | curses.A_BOLD,
            'prop_label': curses.color_pair(7),
            'kw': curses.color_pair(8) | curses.A_BOLD,
            'str': curses.color_pair(9),
            'comment': curses.color_pair(10),
            'num': curses.color_pair(11)
        }
    else:
        # Monochrome fallback
        C = {
            'border': curses.A_BOLD,
            'bg': 0,
            'btn_face': 0,
            'btn_hl': curses.A_BOLD,
            'textbox': curses.A_REVERSE,
            'handle': curses.A_BOLD,
            'active_tool': curses.A_BOLD,
            'prop_label': 0,
            'kw': curses.A_BOLD,
            'str': 0,
            'comment': curses.A_DIM,
    run_mode = False
    run_globals = {}
    run_focused_ctrl = -1 
    design_backup = None
    
    # File I/O handle management for runtime
    run_file_handles = {}
    run_file_counter = 0
    
    def open_file(filename, mode='r'):
    run_mode = False
    run_globals = {}
    run_focused_ctrl = -1 
    design_backup = None
    
    # File I/O handle management for runtime - must be in outer scope
    run_file_handles = {}
    run_file_counter = [0]  # Use list for mutable reference

    def commit_edit():
        nonlocal editing_prop, edit_buffer, selected_win_idx, selected_ctrl_idx
        Returns: "ok", "cancel", "yes", "no"
        """
        C_BORDER = C['border']
        C_BG = C['bg']
        
        lines = text.split('\n')
        content_w = max([len(l) for l in lines] + [len(title), 20])
        
        # Button configurations
        btn_configs = {
            'ok': ['[ OK ]'],
            'okcancel': ['[ OK ]', '[ Cancel ]'],
            'yesno': ['[ Yes ]', '[ No ]'],
            'yesnocancel': ['[ Yes ]', '[ No ]', '[ Cancel ]']
        }
        
        btn_list = btn_configs.get(buttons, ['[ OK ]'])
        btn_w = sum(len(b) + 2 for b in btn_list) - 2
        w = max(content_w + 4, btn_w + 4, len(title) + 4)
    def open_file(filename, mode='r'):
        """Open a file and return a handle"""
        try:
            f = open(filename, mode, encoding='utf-8')
            run_file_counter[0] += 1
            handle = f"file_{run_file_counter[0]}"
            run_file_handles[handle] = f
            return handle
        except Exception as e:
            run_globals['__msg__'] = f"File Error: Cannot open {filename}\n{e}"
            return None
    
    def read_line(file_handle):
        """Read a single line from file"""
        if file_handle in run_file_handles:
            try:
                line = run_file_handles[file_handle].readline()
                return line.rstrip('\n') if line else None
            except Exception as e:
                run_globals['__msg__'] = f"Read Error: {e}"
                return None
        return None
    
    def read_all(file_handle):
        """Read entire file content"""
        if file_handle in run_file_handles:
            try:
                return run_file_handles[file_handle].read()
            except Exception as e:
                run_globals['__msg__'] = f"Read Error: {e}"
    def create_file_dialog(mode='open', filter_ext=None):
        """Simple file dialog for runtime"""
        if mode == 'save':
            prompt = "Save file (enter path)"
        else:
            prompt = "Open file (enter path)"
        return prompt_input(stdscr, prompt, C)

    # ==========================================================
    # Modal Dialog Functions for Runtime
    # ==========================================================
    
    def msgbox(text, title="Message", buttons="ok"):
        """Enhanced message box with multiple button options"""
        C_BORDER = C['border']
        C_BG = C['bg']
        
        lines = text.split('\n')
        content_w = max([len(l) for l in lines] + [len(title), 20])
        
        btn_configs = {
            'ok': ['[ OK ]'],
            'okcancel': ['[ OK ]', '[ Cancel ]'],
            'yesno': ['[ Yes ]', '[ No ]'],
            'yesnocancel': ['[ Yes ]', '[ No ]', '[ Cancel ]']
        }
        
        btn_list = btn_configs.get(buttons, ['[ OK ]'])
        btn_w = sum(len(b) + 2 for b in btn_list) - 2
        w = max(content_w + 4, btn_w + 4, len(title) + 4)
        h = len(lines) + 6
        
        x = max(0, (curses.COLS - w) // 2)
        y = max(0, (curses.LINES - h) // 2)
        
        w = min(w, curses.COLS - 2)
        h = min(h, curses.LINES - 2)
        
        def draw_dialog(selected_btn=0):
            top = '+' + '-' * (w - 2) + '+'
            write_at(stdscr, x, y, top, C_BORDER)
            
            for i in range(1, h - 1):
                write_at(stdscr, x, y + i, '|', C_BORDER)
                write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
                write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
            
            bottom = '+' + '-' * (w - 2) + '+'
            write_at(stdscr, x, y + h - 1, bottom, C_BORDER)
            
            title_x = x + (w - len(title)) // 2
            write_at(stdscr, title_x, y, f" {title} ", C_BORDER)
            
            for i, line in enumerate(lines[:h-4]):
                write_at(stdscr, x + 2, y + 2 + i, line[:w-4], C_BG)
            
            btn_x = x + (w - btn_w) // 2
            btn_y = y + h - 2
            
            for i, btn in enumerate(btn_list):
                attr = C['active_tool'] if i == selected_btn else C_BG
                write_at(stdscr, btn_x, btn_y, btn, attr)
                btn_x += len(btn) + 2
            
            stdscr.refresh()
        
        selected = 0
        draw_dialog(selected)
        
        while True:
            ch = stdscr.getch()
            
            if ch == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                    if bstate & curses.BUTTON1_CLICKED:
                        btn_x = x + (w - btn_w) // 2
                        btn_y = y + h - 2
                        for i, btn in enumerate(btn_list):
                            if btn_y == my and btn_x <= mx < btn_x + len(btn):
                                btn_values = {
                                    'ok': ['ok'],
                                    'okcancel': ['ok', 'cancel'],
                                    'yesno': ['yes', 'no'],
                                    'yesnocancel': ['yes', 'no', 'cancel']
                                }
                                return btn_values.get(buttons, ['ok'])[i]
                            btn_x += len(btn) + 2
                except:
                    pass
            
            elif ch == curses.KEY_LEFT:
                selected = max(0, selected - 1)
                draw_dialog(selected)
            
            elif ch == curses.KEY_RIGHT:
                selected = min(len(btn_list) - 1, selected + 1)
                draw_dialog(selected)
            
            elif ch == 9:
                selected = (selected + 1) % len(btn_list)
                draw_dialog(selected)
            
            elif ch in (10, 13, curses.KEY_ENTER):
                btn_values = {
                    'ok': ['ok'],
                    'okcancel': ['ok', 'cancel'],
                    'yesno': ['yes', 'no'],
                    'yesnocancel': ['yes', 'no', 'cancel']
                }
                return btn_values.get(buttons, ['ok'])[selected]
            
            elif ch == 27:
                if buttons in ['okcancel', 'yesnocancel']:
                    return 'cancel'
                elif buttons == 'yesno':
                    return 'no'
                return 'ok'
            
            time.sleep(0.01)
                return True
            except Exception as e:
                run_globals['__msg__'] = f"Close Error: {e}"
                return False
        return False
    
    def file_exists(filename):
        """Check if file exists"""
        return os.path.exists(filename)
                line_text = line[:w-4]
                write_at(stdscr, x + 2, y + 2 + i, line_text, C_BG)
            
            # Buttons
            btn_x = x + (w - btn_w) // 2
            btn_y = y + h - 2
            
            for i, btn in enumerate(btn_list):
                attr = C['active_tool'] if i == selected_btn else C_BG
                write_at(stdscr, btn_x, btn_y, btn, attr)
                btn_x += len(btn) + 2
            
            stdscr.refresh()
        
        selected = 0
        draw_dialog(selected)
        
        while True:
            ch = stdscr.getch()
            
            if ch == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                    if bstate & curses.BUTTON1_CLICKED:
                        # Check button clicks
                        btn_x = x + (w - btn_w) // 2
                        btn_y = y + h - 2
                        for i, btn in enumerate(btn_list):
                            if btn_y == my and btn_x <= mx < btn_x + len(btn):
                                return ['ok', 'yes', 'no', 'cancel'][i % 4] if buttons != 'okcancel' else (['ok', 'cancel'][i] if i < 2 else 'ok')
                            btn_x += len(btn) + 2
                except:
                    pass
            
            elif ch == curses.KEY_LEFT:
                selected = max(0, selected - 1)
                draw_dialog(selected)
            
            elif ch == curses.KEY_RIGHT:
                selected = min(len(btn_list) - 1, selected + 1)
                draw_dialog(selected)
            
            elif ch == 9:  # Tab
                selected = (selected + 1) % len(btn_list)
                draw_dialog(selected)
            
            elif ch in (10, 13, curses.KEY_ENTER):  # Enter
                btn_values = {
                    'ok': ['ok'],
                    'okcancel': ['ok', 'cancel'],
                    'yesno': ['yes', 'no'],
                    'yesnocancel': ['yes', 'no', 'cancel']
                }
                values = btn_values.get(buttons, ['ok'])
                return values[selected] if selected < len(values) else 'ok'
            
            elif ch == 27:  # Escape
                if buttons in ['okcancel', 'yesnocancel']:
                    return 'cancel'
                elif buttons == 'yesno':
                    return 'no'
                else:
                    return 'ok'
            
            time.sleep(0.01)
    
    def inputbox(prompt, title="Input", default=""):
        """
        Text input dialog with prompt and default value
        Returns: entered text or None if cancelled
        """
        C_BORDER = C['border']
        C_BG = C['bg']
        C_TB = C['textbox']
        
        prompt_lines = prompt.split('\n')
        content_w = max([len(l) for l in prompt_lines] + [len(title), 40])
        w = min(content_w + 4, curses.COLS - 4)
        h = len(prompt_lines) + 6
        
        x = max(0, (curses.COLS - w) // 2)
        y = max(0, (curses.LINES - h) // 2)
        
        buffer = default
        
        def draw_input_dialog():
            # Border
            write_at(stdscr, x, y, '+' + '-' * (w - 2) + '+', C_BORDER)
            for i in range(1, h - 1):
                write_at(stdscr, x, y + i, '|', C_BORDER)
                write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
                write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
            write_at(stdscr, x, y + h - 1, '+' + '-' * (w - 2) + '+', C_BORDER)
            
            # Title
            title_x = x + (w - len(title)) // 2
            write_at(stdscr, title_x, y, f" {title} ", C_BORDER)
            
            # Prompt
            for i, line in enumerate(prompt_lines):
                write_at(stdscr, x + 2, y + 2 + i, line[:w-4], C_BG)
            
            # Input field
            input_y = y + h - 3
            write_at(stdscr, x + 2, input_y, ' ' * (w - 4), C_TB)
            display_text = (buffer + "_")[:w-4]
            write_at(stdscr, x + 2, input_y, display_text, C_TB)
            
            # Buttons hint
            hint = "[Enter=OK, Esc=Cancel]"
            hint_x = x + (w - len(hint)) // 2
            write_at(stdscr, hint_x, y + h - 2, hint, C_BG)
            
            stdscr.refresh()
        
        while True:
            draw_input_dialog()
            ch = stdscr.getch()
            
            if ch == 27:  # Escape
                return None
            
            elif ch in (10, 13, curses.KEY_ENTER):  # Enter
                return buffer
            
            elif ch in (8, 127, curses.KEY_BACKSPACE):  # Backspace
                buffer = buffer[:-1]
            
            elif 32 <= ch <= 126:  # Printable characters
                if len(buffer) < w - 5:
                    buffer += chr(ch)
            
            time.sleep(0.01)
    
    def file_dialog(mode='open', filter_ext=None, start_dir=None):
        """
        Simple file browser dialog
        mode: 'open' or 'save'
        filter_ext: list of extensions like ['.txt', '.json']
        Returns: selected filepath or None if cancelled
        """
        C_BORDER = C['border']
        C_BG = C['bg']
        C_ACTIVE = C['active_tool']
        
        current_dir = start_dir or os.getcwd()
        selected_file = ""
        files = []
        cursor = 0
        scroll_offset = 0
        
        w = min(60, curses.COLS - 4)
        h = min(20, curses.LINES - 4)
        x = max(0, (curses.COLS - w) // 2)
        y = max(0, (curses.LINES - h) // 2)
        
        visible_rows = h - 6  # Space for header, path, and buttons
        
        def refresh_files():
            nonlocal files
            try:
                entries = os.listdir(current_dir)
                files = ['..']  # Parent directory
                dirs = [e for e in entries if os.path.isdir(os.path.join(current_dir, e))]
                file_list = [e for e in entries if os.path.isfile(os.path.join(current_dir, e))]
                
                # Apply filter if specified
                if filter_ext:
                    file_list = [f for f in file_list if any(f.endswith(ext) for ext in filter_ext)]
                
                dirs.sort()
                file_list.sort()
                files.extend(dirs)
                files.extend(file_list)
            except Exception as e:
                files = ['..', f'Error: {e}']
        
        def draw_file_dialog():
            # Border
            write_at(stdscr, x, y, '+' + '-' * (w - 2) + '+', C_BORDER)
            for i in range(1, h - 1):
                write_at(stdscr, x, y + i, '|', C_BORDER)
                write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
                write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
            write_at(stdscr, x, y + h - 1, '+' + '-' * (w - 2) + '+', C_BORDER)
            
            # Title
            title = "Open File" if mode == 'open' else "Save File"
            title_x = x + (w - len(title)) // 2
            write_at(stdscr, title_x, y, f" {title} ", C_BORDER)
            
            # Current path
            path_text = current_dir[-(w-4):] if len(current_dir) > w - 4 else current_dir
            write_at(stdscr, x + 2, y + 1, path_text[:w-4], C_BORDER)
            
            # File list
            for i in range(visible_rows):
                file_idx = scroll_offset + i
                if file_idx < len(files):
                    fname = files[file_idx]
                    is_dir = os.path.isdir(os.path.join(current_dir, fname)) if fname != '..' else True
                    prefix = '/' if is_dir else ' '
                    display = (prefix + fname)[:w-4]
                    
                    attr = C_ACTIVE if file_idx == cursor else C_BG
                    write_at(stdscr, x + 2, y + 3 + i, display.ljust(w-4), attr)
                else:
                    write_at(stdscr, x + 2, y + 3 + i, ' ' * (w-4), C_BG)
            
            # Selected file
            file_label = "File: " + selected_file
            write_at(stdscr, x + 2, y + h - 3, file_label[:w-4], C_BG)
            
            # Buttons
            btn_text = "[ OK ]  [ Cancel ]"
            btn_x = x + (w - len(btn_text)) // 2
            write_at(stdscr, btn_x, y + h - 2, btn_text, C_BORDER)
            
            stdscr.refresh()
        
        refresh_files()
        
        while True:
            draw_file_dialog()
            ch = stdscr.getch()
            
            if ch == 27:  # Escape
                return None
            
            elif ch == curses.KEY_UP:
                if cursor > 0:
                    cursor -= 1
                    if cursor < scroll_offset:
                        scroll_offset = cursor
            
            elif ch == curses.KEY_DOWN:
                if cursor < len(files) - 1:
                    cursor += 1
                    if cursor >= scroll_offset + visible_rows:
                        scroll_offset = cursor - visible_rows + 1
            
            elif ch == curses.KEY_HOME:
                cursor = 0
                scroll_offset = 0
            
            elif ch == curses.KEY_END:
                cursor = len(files) - 1
                if cursor >= visible_rows:
                    scroll_offset = cursor - visible_rows + 1
            
            elif ch in (10, 13, curses.KEY_ENTER):  # Enter
                fname = files[cursor]
                if fname == '..':
                    current_dir = os.path.dirname(current_dir)
                    refresh_files()
                    cursor = 0
                    scroll_offset = 0
                elif os.path.isdir(os.path.join(current_dir, fname)):
                    current_dir = os.path.join(current_dir, fname)
                    refresh_files()
                    cursor = 0
                    scroll_offset = 0
                else:
                    # File selected
                    return os.path.join(current_dir, fname)
            
            elif ch == ord(' '):  # Space to select file for save mode
                if mode == 'save':
                    fname = files[cursor]
                    if fname != '..' and os.path.isfile(os.path.join(current_dir, fname)):
                        selected_file = fname
            
            time.sleep(0.01)
    
    def color_picker():
        """
        Simple color picker dialog
        Returns: color name string or None if cancelled
        """
        colors = [
            'black', 'red', 'green', 'yellow', 
            'blue', 'magenta', 'cyan', 'white',
            'gray', 'light_red', 'light_green', 'light_yellow',
            'light_blue', 'light_magenta', 'light_cyan', 'bright_white'
        ]
        
        C_BORDER = C['border']
        C_BG = C['bg']
        C_ACTIVE = C['active_tool']
        
        w = 40
        h = 14
        x = max(0, (curses.COLS - w) // 2)
        y = max(0, (curses.LINES - h) // 2)
        
        cols = 4
        rows = 4
        cursor = 0
        
        def draw_color_dialog():
            # Border
            write_at(stdscr, x, y, '+' + '-' * (w - 2) + '+', C_BORDER)
            for i in range(1, h - 1):
                write_at(stdscr, x, y + i, '|', C_BORDER)
                write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
                write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
            write_at(stdscr, x, y + h - 1, '+' + '-' * (w - 2) + '+', C_BORDER)
            
            # Title
            title = " Select Color "
            title_x = x + (w - len(title)) // 2
            write_at(stdscr, title_x, y, title, C_BORDER)
            
            # Color grid
            cell_w = (w - 4) // cols
            for i, color in enumerate(colors):
                row = i // cols
                col = i % cols
                cell_x = x + 2 + col * cell_w
                cell_y = y + 2 + row
                
                attr = C_ACTIVE if i == cursor else C_BG
                display = color[:cell_w-1].center(cell_w-1)
                write_at(stdscr, cell_x, cell_y, display, attr)
            
            # Preview
            preview_text = " Preview "
            write_at(stdscr, x + 2, y + h - 3, preview_text, C_BG)
            
            # Buttons
            btn_text = "[ OK ]  [ Cancel ]"
            btn_x = x + (w - len(btn_text)) // 2
            write_at(stdscr, btn_x, y + h - 2, btn_text, C_BORDER)
            
            stdscr.refresh()
        
        while True:
            draw_color_dialog()
            ch = stdscr.getch()
            
            if ch == 27:  # Escape
                return None
            
            elif ch == curses.KEY_UP:
                cursor = max(0, cursor - cols)
            
            elif ch == curses.KEY_DOWN:
                cursor = min(len(colors) - 1, cursor + cols)
            
            elif ch == curses.KEY_LEFT:
                cursor = max(0, cursor - 1)
            
            elif ch == curses.KEY_RIGHT:
                cursor = min(len(colors) - 1, cursor + 1)
            
            elif ch in (10, 13, curses.KEY_ENTER):
                return colors[cursor]
            
            time.sleep(0.01)
    
    def font_dialog():
        """
        Simple font selection dialog
        Returns: dict with 'size' and 'family' or None if cancelled
        """
        C_BORDER = C['border']
        C_BG = C['bg']
        C_ACTIVE = C['active_tool']
        
        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24]
        families = ['monospace', 'serif', 'sans-serif', 'courier', 'helvetica']
        
        w = 50
        h = 16
        x = max(0, (curses.COLS - w) // 2)
        y = max(0, (curses.LINES - h) // 2)
        
        selected_size = 6  # Default to 14
        selected_family = 0
        
        def draw_font_dialog():
            # Border
            write_at(stdscr, x, y, '+' + '-' * (w - 2) + '+', C_BORDER)
            for i in range(1, h - 1):
                write_at(stdscr, x, y + i, '|', C_BORDER)
                write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
                write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
            write_at(stdscr, x, y + h - 1, '+' + '-' * (w - 2) + '+', C_BORDER)
            
            # Title
            title = " Font Selection "
            title_x = x + (w - len(title)) // 2
            write_at(stdscr, title_x, y, title, C_BORDER)
            
            # Size section
            write_at(stdscr, x + 2, y + 2, "Size:", C_BORDER)
            size_text = ' '.join(str(s) if i != selected_size else f'[{s}]' for i, s in enumerate(sizes))
            write_at(stdscr, x + 8, y + 2, size_text[:w-10], C_BG)
            
            # Family section
            write_at(stdscr, x + 2, y + 4, "Family:", C_BORDER)
            for i, family in enumerate(families):
                attr = C_ACTIVE if i == selected_family else C_BG
                prefix = '> ' if i == selected_family else '  '
                write_at(stdscr, x + 10, y + 5 + i, prefix + family, attr)
            
            # Preview
            preview = f"Preview: Size {sizes[selected_size]}, {families[selected_family]}"
            write_at(stdscr, x + 2, y + h - 4, preview[:w-4], C_BG)
            
            # Buttons
            btn_text = "[ OK ]  [ Cancel ]"
            btn_x = x + (w - len(btn_text)) // 2
            write_at(stdscr, btn_x, y + h - 2, btn_text, C_BORDER)
            
            stdscr.refresh()
        
        while True:
            draw_font_dialog()
            ch = stdscr.getch()
            
            if ch == 27:  # Escape
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
                return {
                    'size': sizes[selected_size],
                    'family': families[selected_family]
                }
            
            time.sleep(0.01)

    def commit_edit():
        nonlocal editing_prop, edit_buffer, selected_win_idx, selected_ctrl_idx
        return ""
    
    def write_line(file_handle, text):
        """Write a line with newline"""
        if file_handle in run_file_handles:
            try:
                run_file_handles[file_handle].write(text + '\n')
                return True
            except Exception as e:
                        elif run_mode:
                            if run_globals.get('__msg__'):
                                run_globals['__msg__'] = None 
                                stdscr.clear()
                            elif 18 <= mx <= 23 and my == 0:
                                # Exit run mode - close all file handles
                                for handle in list(run_file_handles.keys()):
                                    close_file(handle)
                                run_file_handles.clear()
                                
                                run_mode = False
                                run_focused_ctrl = -1
                                if design_backup is not None:
                                    windows[0] = copy.deepcopy(design_backup)
                                stdscr.clear()
                return True
            except Exception as e:
                run_globals['__msg__'] = f"Close Error: {e}"
                return False
        return False
    
    def file_exists(filename):
        """Check if file exists"""
        return os.path.exists(filename)
    
    def create_file_dialog(mode='open', filter_ext=None):
        """Simple file dialog for runtime"""
        # For now, use the existing prompt_input with a simple interface
        # In a full implementation, this would show a file browser dialog
        if mode == 'save':
            prompt = "Save file (enter path)"
        else:
            prompt = "Open file (enter path)"
        
        # Return the filename entered by user
        # This is a simplified version - full implementation would have browse capability
        return prompt_input(stdscr, prompt, C)

    def commit_edit():
        nonlocal editing_prop, edit_buffer, selected_win_idx, selected_ctrl_idx

    last_click_time = 0.0
    last_click_x = -1
    last_click_y = -1
                                run_mode = True
                                run_focused_ctrl = -1
                                stdscr.clear()
                                run_globals = {'__msg__': None}
                                
                                # File I/O handle management for runtime
                                run_file_handles = {}
                                run_file_counter = 0
                                run_globals['open_file'] = open_file
                                run_globals['read_line'] = read_line
                                run_globals['read_all'] = read_all
                                run_globals['write_line'] = write_line
                                run_globals['write_text'] = write_text
                                run_globals['close_file'] = close_file
                                run_globals['file_exists'] = file_exists
                                run_globals['create_file_dialog'] = create_file_dialog
                                
                                # Add dialog functions to runtime
                                run_globals['msgbox'] = msgbox
                                run_globals['inputbox'] = inputbox
                                run_globals['file_dialog'] = file_dialog
                                run_globals['color_picker'] = color_picker
                                run_globals['font_dialog'] = font_dialog
                                
                                # Add control references
                                for w in windows:
                                    for c in w.controls:
                                        run_globals[c.name_id] = c
    def execute_event(event_name, form_win):
        """Execute event handler by name"""
        if event_name in run_globals:
            try:
                run_globals[event_name]()
            except Exception as e:
                run_globals['__msg__'] = f"Event Error ({event_name}):\n{e}"

    stdscr.clear()

    # Main loop with frame rate limiting
    last_draw = 0
    frame_delay = 1/30  # 30 FPS max
    
    while True:
        current_time = time.time()
        
        # Calculate dialog dimensions
        box_w = max(50, curses.COLS - 10)
        box_h = max(15, curses.LINES - 6)
        box_x = (curses.COLS - box_w) // 2
        box_y = (curses.LINES - box_h) // 2

        # Draw only when needed or at frame rate
        if current_time - last_draw >= frame_delay or code_mode:
            if code_mode:
                draw_code_editor(stdscr, code_lines, code_cy, code_cx, 
                               code_target_ctrl.name_id, box_x, box_y, 
                               box_w, box_h, C, code_event_type)
                curses.curs_set(1) 
            else:
                if run_mode and run_focused_ctrl >= 0:
                    curses.curs_set(1)
                else:
                    curses.curs_set(0) 
                
                # Menu bar
                if run_mode:
                    menu_str = " File  Edit  View [STOP] Debug  Options"
                else:
                    menu_str = " File  Edit  View [RUN ] Debug  Options"
                    
                write_at(stdscr, 0, 0, menu_str + " " * max(0, curses.COLS - len(menu_str)), C['handle'])
                
                if not run_mode:
                    tools.draw(stdscr, C, box_chars)
                
                for i, win in enumerate(windows):
                    if run_mode and i != 0:
                            elif 18 <= mx <= 23 and my == 0:
                                design_backup = copy.deepcopy(windows[0])
                                run_mode = True
                                run_focused_ctrl = -1
                                stdscr.clear()
                                run_globals = {'__msg__': None}
                                def _msgbox(text):
                                    run_globals['__msg__'] = str(text)
                                run_globals['msgbox'] = _msgbox
                                
                                # Add file I/O functions to runtime
                                run_globals['open_file'] = open_file
                                run_globals['read_line'] = read_line
                                run_globals['read_all'] = read_all
                                run_globals['write_line'] = write_line
                                run_globals['write_text'] = write_text
                                run_globals['close_file'] = close_file
                                run_globals['file_exists'] = file_exists
                                run_globals['create_file_dialog'] = create_file_dialog
                                
                                # Add control references
                                for w in windows:
                                    for c in w.controls:
                                        run_globals[c.name_id] = c
                                
                                # Fire on_load event
                                execute_event("on_load_form", windows[0])
                                
                                # Compile and execute control code
                                for w in windows:
                                    for c in w.controls:
                                        if c.code:
                                            try:
                                                exec(c.code, run_globals)
                                            except Exception as e:
                                                _msgbox(f"Compile Error in {c.name_id}:\n{e}")
                                clicked_handled = True
            last_draw = current_time

        # Input handling
        ch = stdscr.getch()
        
        if ch == curses.KEY_MOUSE and TERM.has_mouse:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                mouse_moved = (mx != old_mx or my != old_my)
                left_click = bool(bstate & curses.BUTTON1_PRESSED) or bool(bstate & curses.BUTTON1_CLICKED)
                mouse_released = bool(bstate & curses.BUTTON1_RELEASED)

                if left_click:
                    current_time = time.time()
                    is_double_click = False
                    if (current_time - last_click_time < 0.4) and (mx == last_click_x and my == last_click_y):
                        is_double_click = True
                    last_click_time = current_time
                    last_click_x = mx
                    last_click_y = my

                    if not mouse_down:
                        mouse_down = True
                        
                        if code_mode:
                            if box_x + box_w - 5 <= mx <= box_x + box_w - 1 and my == box_y:
                                code_target_ctrl.code = "\n".join(code_lines)
                                code_mode = False
                                stdscr.clear()
                        
                        elif run_mode:
                            if run_globals.get('__msg__'):
                                run_globals['__msg__'] = None 
                                stdscr.clear()
                            elif 18 <= mx <= 23 and my == 0:
                                run_mode = False
                                run_focused_ctrl = -1
                                if design_backup is not None:
                                    windows[0] = copy.deepcopy(design_backup)
                                stdscr.clear()
                            else:
                                win = windows[0]
                                if win.hit_test(mx, my):
                                    lx = mx - win.x
                                    ly = my - win.y
                                    
                                    # Check menu bar click
                                    if ly == 1 and win.menu_items:
                                        menu_x = 1
                                        for m in win.menu_items:
                                            if m.parent == 0:
                                                item_w = len(m.caption) + 2
                                                if lx >= menu_x and lx < menu_x + item_w:
                                                    execute_event(f"on_menu_{m.name_id}", win)
                                                    break
                                                menu_x += item_w + 2
                                        continue
                                    
                                    idx = win.hit_control(lx, ly)
                                    if idx >= 0:
                                        c = win.controls[idx]
                                        
                                        # Track focus changes
                                        if idx != win._last_focused:
                                            if win._last_focused >= 0:
                                                last_c = win.controls[win._last_focused]
                                                execute_event(f"on_blur_{last_c.name_id}", win)
                                            execute_event(f"on_focus_{c.name_id}", win)
                                            win._last_focused = idx
                                        
                                        if c.tool_type == 1:
                                            c.checked = not c.checked
                                            execute_event(f"on_change_{c.name_id}", win)
                                            win.redraw()
                                        elif c.tool_type == 2:
                                            c.selected_index += 1
                                            if c.selected_index >= len(c.items):
                                                c.selected_index = 0
                                            execute_event(f"on_change_{c.name_id}", win)
                                            win.redraw()
                                        elif c.tool_type == 3:
                                            execute_event(f"on_click_{c.name_id}", win)
                                            win.redraw()
                                        elif c.tool_type == 10:
                                            rel_y = ly - c.y - 1
                                            item_idx = c.scroll_offset + rel_y
                                            if 0 <= item_idx < len(c.items):
                                                c.selected_index = item_idx
                                                execute_event(f"on_change_{c.name_id}", win)
                                            win.redraw()
                                        elif c.tool_type == 11:
                                            c.checked = True
                                            for other in win.controls:
                                                if other.tool_type == 11 and other != c and other.group == c.group:
                                                    other.checked = False
                                            execute_event(f"on_change_{c.name_id}", win)
                                            win.redraw()
                                        elif c.tool_type == 13:
                                            run_focused_ctrl = idx
                                            execute_event(f"on_focus_{c.name_id}", win)
                                    else:
                                        if win._last_focused >= 0:
                                            last_c = win.controls[win._last_focused]
                                            execute_event(f"on_blur_{last_c.name_id}", win)
                                            win._last_focused = -1
                        
                        else:
                            # Design mode mouse handling
                            clicked_handled = False
                            prop_win = windows[1]
                            prop_local_y = my - prop_win.y
                            clicked_prop_row = False
                            if prop_win.hit_test(mx, my) and selected_ctrl_idx >= 0 and 5 <= prop_local_y <= 10:
                                clicked_prop_row = True
                            
                            edit_menu_clicked = False
                            if prop_win.hit_test(mx, my) and not selected_ctrl_idx >= 0:
                                if prop_local_y == 7:
                                    edit_menu_clicked = True
                                    edit_menu_dialog(stdscr, windows[0], C)
                                    stdscr.clear()
                            
                            if not clicked_prop_row and not edit_menu_clicked:
                                commit_edit()

                            if 1 <= mx <= 5 and my == 0:
                                choice = handle_file_menu(stdscr, C)
                                if choice == 'save':
                                    fname = prompt_input(stdscr, "Save Project As (*.json)", C)
                                    if fname:
                                        if not fname.endswith('.json'): fname += '.json'
                                        try:
                                            with open(fname, 'w', encoding='utf-8') as f:
                                                json.dump(windows[0].to_dict(), f, indent=2)
                                            show_sync_msgbox(stdscr, f"Project saved to {fname}", C)
                                        except Exception as e:
                                            show_sync_msgbox(stdscr, f"Save Error:\n{e}", C)
                                elif choice == 'load':
                                    fname = prompt_input(stdscr, "Load Project (*.json)", C)
                                    if fname:
                                        if not fname.endswith('.json'): fname += '.json'
                                        try:
                                            with open(fname, 'r', encoding='utf-8') as f:
                                                data = json.load(f)
                                            windows[0] = Window.from_dict(data)
                                            selected_ctrl_idx = -1
                                            show_sync_msgbox(stdscr, f"Project loaded from {fname}", C)
                                        except Exception as e:
                                            show_sync_msgbox(stdscr, f"Load Error:\n{e}", C)
                                elif choice == 'exit':
                                    return
                                stdscr.clear()
                                clicked_handled = True

                            elif 18 <= mx <= 23 and my == 0:
                                design_backup = copy.deepcopy(windows[0])
                                run_mode = True
                                run_focused_ctrl = -1
                                stdscr.clear()
                                run_globals = {'__msg__': None}
                                def _msgbox(text):
                                    run_globals['__msg__'] = str(text)
                                run_globals['msgbox'] = _msgbox
                                for w in windows:
                                    for c in w.controls:
                                        run_globals[c.name_id] = c
                                execute_event("on_load_form", windows[0])
                                for w in windows:
                                    for c in w.controls:
                                        if c.code:
                                            try:
                                                exec(c.code, run_globals)
                                            except Exception as e:
                                                _msgbox(f"Compile Error in {c.name_id}:\n{e}")
                                clicked_handled = True

                            elif tools.x <= mx < tools.x + tools.w and tools.y <= my < tools.y + tools.h:
                                if tools.process_click(mx, my):
                                    pass
                                else:
                                    dragged_tool = True
                                    drag_offset_x = mx - tools.x
                                    drag_offset_y = my - tools.y
                                clicked_handled = True
                                
                            if not clicked_handled and not edit_menu_clicked:
                                for i in range(1, -1, -1): 
                                    win = windows[i]
                                    if win.hit_test(mx, my):
                                        local_x = mx - win.x
                                        local_y = my - win.y
                                        
                                        if i == 0 and local_y == 1 and win.menu_items:
                                            menu_x = 1
                                            for m in win.menu_items:
                                                if m.parent == 0:
                                                    item_w = len(m.caption) + 2
                                                    if local_x >= menu_x and local_x < menu_x + item_w:
                                                        edit_menu_dialog(stdscr, win, C)
                                                        stdscr.clear()
                                                        clicked_handled = True
                                                        break
                                                    menu_x += item_w + 2
                                            if clicked_handled:
                                                break
                                        
                                        if i == 1: 
                                            if clicked_prop_row:
                                                c = windows[0].controls[selected_ctrl_idx]
                                                if prop_local_y == 5: editing_prop, edit_buffer = 1, c.name_id
                                                elif prop_local_y == 6: editing_prop, edit_buffer = 2, c.caption
                                                elif prop_local_y == 7: editing_prop, edit_buffer = 3, str(c.x)
                                                elif prop_local_y == 8: editing_prop, edit_buffer = 4, str(c.y)
                                                elif prop_local_y == 9: editing_prop, edit_buffer = 5, str(c.w)
                                                elif prop_local_y == 10: editing_prop, edit_buffer = 6, str(c.h)
                                            else:
                                                dragged_win = i
                                                drag_offset_x = local_x
                                                drag_offset_y = local_y
                                        else: 
                                            if tools.active_tool <= 0:
                                                matched_control = False
                                                if selected_win_idx == i and selected_ctrl_idx >= 0:
                                                    c = win.controls[selected_ctrl_idx]
                                                    if local_x == c.x + c.w and local_y == c.y + c.h:
                                                        resizing_ctrl = True
                                                        dragged_ctrl = selected_ctrl_idx
                                                        matched_control = True
                                                
                                                if not matched_control:
                                                    clicked_ctrl = win.hit_control(local_x, local_y)
                                                    if clicked_ctrl >= 0:
                                                        selected_win_idx = i
                                                        selected_ctrl_idx = clicked_ctrl
                                                        dragged_ctrl = clicked_ctrl
                                                        c = win.controls[clicked_ctrl]
                                                        drag_offset_x = local_x - c.x
                                                        drag_offset_y = local_y - c.y
                                                        matched_control = True
                                                        
                                                        if is_double_click and c.tool_type in [1, 2, 3, 10, 11, 13, 14]: 
                                                            code_mode = True
                                                            code_target_ctrl = c
                                                            code_event_type = "click"
                                                            if c.tool_type in [1, 2, 10, 11]:
                                                                code_event_type = "change"
                                                            elif c.tool_type == 13:
                                                                code_event_type = "change"
                                                            elif c.tool_type == 14:
                                                                code_event_type = "timer"
                                                            
                                                            if not c.code:
                                                                c.code = f"def on_{code_event_type}_{c.name_id}():\n    pass\n"
                                                            code_lines = c.code.split("\n")
                                                            code_cy = min(1, len(code_lines)-1)
                                                            code_cx = 4 
                                                            stdscr.clear()
                                                            
                                                if not matched_control:
                                                    dragged_win = i
                                                    drag_offset_x = local_x
                                                    drag_offset_y = local_y
                                                    selected_ctrl_idx = -1
                                            else:
                                                if 0 < local_x < win.w - 14 and 0 < local_y < win.h - 1:
                                                    win.add_control(local_x, local_y, tools.active_tool, tools.items[tools.active_tool])
                                                    selected_win_idx = i
                                                    selected_ctrl_idx = len(win.controls) - 1
                                                    
                                                    new_ctrl = win.controls[selected_ctrl_idx]
                                                    if new_ctrl.tool_type != 7:
                                                        for j in range(len(win.controls) - 2, -1, -1):
                                                            potential_parent = win.controls[j]
                                                            if potential_parent.tool_type == 7:
                                                                if (new_ctrl.x >= potential_parent.x + 1 and
                                                                    new_ctrl.x + new_ctrl.w <= potential_parent.x + potential_parent.w - 1 and
                                                                    new_ctrl.y >= potential_parent.y + 1 and
                                                                    new_ctrl.y + new_ctrl.h <= potential_parent.y + potential_parent.h - 1):
                                                                    new_ctrl.parent = j
                                                                    break
                                                    
                                                    tools.active_tool = 0
                                        break

                elif mouse_released:
                    mouse_down = False
                    dragged_win = -1
                    dragged_ctrl = -1
                    dragged_tool = False
                    resizing_ctrl = False

                if mouse_down and mouse_moved and not code_mode:
                    stdscr.clear() 
                    
                    if run_mode:
                        if dragged_win == 0:
                            windows[0].x = mx - drag_offset_x
                            windows[0].y = my - drag_offset_y
                            
                    else:
                        if resizing_ctrl and dragged_ctrl >= 0:
                            c = windows[selected_win_idx].controls[dragged_ctrl]
                            new_w = (mx - windows[selected_win_idx].x) - c.x
                            new_h = (my - windows[selected_win_idx].y) - c.y
                            c.w = max(4, min(new_w, windows[selected_win_idx].w - c.x - 1))
                            min_h = 3 if c.tool_type == 3 else 1
                            c.h = max(min_h, min(new_h, windows[selected_win_idx].h - c.y - 1))
                            
                        elif dragged_ctrl >= 0:
                            c = windows[selected_win_idx].controls[dragged_ctrl]
                            new_x = (mx - windows[selected_win_idx].x) - drag_offset_x
                            new_y = (my - windows[selected_win_idx].y) - drag_offset_y
                            if 0 < new_x and 0 < new_y and new_x + c.w < windows[selected_win_idx].w and new_y + c.h < windows[selected_win_idx].h:
                                c.x = new_x
                                c.y = new_y
                                
                        elif dragged_tool:
                            tools.x = max(0, min(mx - drag_offset_x, curses.COLS - tools.w))
                            tools.y = max(1, min(my - drag_offset_y, curses.LINES - tools.h))
                            
                        elif dragged_win >= 0:
                            windows[dragged_win].x = mx - drag_offset_x
                            windows[dragged_win].y = my - drag_offset_y

                old_mx = mx
                old_my = my

            except curses.error:
                pass

        elif ch == 27 and not code_mode: 
            break

        elif ch != -1:
            if code_mode:
                if ch == curses.KEY_UP:
                    code_cy = max(0, code_cy - 1)
                    code_cx = min(code_cx, len(code_lines[code_cy]))
                elif ch == curses.KEY_DOWN:
                    code_cy = min(len(code_lines) - 1, code_cy + 1)
                    code_cx = min(code_cx, len(code_lines[code_cy]))
                elif ch == curses.KEY_LEFT:
                    if code_cx > 0: code_cx -= 1
                elif ch == curses.KEY_RIGHT:
                    if code_cx < len(code_lines[code_cy]): code_cx += 1
                elif ch in (10, 13, curses.KEY_ENTER):
                    left_part = code_lines[code_cy][:code_cx]
                    right_part = code_lines[code_cy][code_cx:]
                    code_lines[code_cy] = left_part
                    code_lines.insert(code_cy + 1, right_part)
                    code_cy += 1
                    code_cx = 0
                    stdscr.clear() 
                elif ch in (8, 127, curses.KEY_BACKSPACE):
                    if code_cx > 0:
                        line = code_lines[code_cy]
                        code_lines[code_cy] = line[:code_cx-1] + line[code_cx:]
                        code_cx -= 1
                    elif code_cy > 0:
                        code_cx = len(code_lines[code_cy-1])
                        code_lines[code_cy-1] += code_lines[code_cy]
                        code_lines.pop(code_cy)
                        code_cy -= 1
                        stdscr.clear()
                elif 32 <= ch <= 126:
                    line = code_lines[code_cy]
                    code_lines[code_cy] = line[:code_cx] + chr(ch) + line[code_cx:]
                    code_cx += 1

            elif run_mode:
                if run_focused_ctrl >= 0:
                    c = windows[0].controls[run_focused_ctrl]
                    if c.tool_type == 13:
                        old_caption = c.caption
                        if ch in (8, 127, curses.KEY_BACKSPACE):
                            c.caption = c.caption[:-1]
                        elif 32 <= ch <= 126:
                            c.caption += chr(ch)
                        if c.caption != old_caption:
                            execute_event(f"on_change_{c.name_id}", windows[0])
            else:
                if editing_prop > 0:
                    if ch in (10, 13, curses.KEY_ENTER):
                        commit_edit()
                    elif ch in (8, 127, curses.KEY_BACKSPACE):
                        edit_buffer = edit_buffer[:-1]
                    elif 32 <= ch <= 126:
                        if editing_prop >= 3:
                            if chr(ch).isdigit() or chr(ch) == '-':
                                edit_buffer += chr(ch)
                        else:
                            edit_buffer += chr(ch)

        # Frame rate limiting
        elapsed = time.time() - current_time
        if elapsed < frame_delay:
            time.sleep(frame_delay - elapsed)

    # Cleanup
    if TERM.has_mouse:
        print('\033[?1003l', end='', flush=True)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
