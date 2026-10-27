#!/usr/bin/env python3
"""
VB1-DOS Clone v2.1.0: With File I/O and Dialog System
"""

import curses
import time
import re
import copy
import json
import os
import sys

# Terminal Compatibility Layer (simplified for v2.1.0)
class TerminalCompat:
    def __init__(self):
        self.has_utf8 = 'utf' in (os.environ.get('LANG', '') + os.environ.get('LC_ALL', '')).lower()
        self.has_mouse = False
        self.has_colors = False
        
    def setup(self, stdscr):
        try:
            curses.start_color()
            self.has_colors = curses.has_colors()
        except:
            pass
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS)
            self.has_mouse = True
        except:
            pass
        return self.has_colors
    
    def get_box_chars(self):
        if self.has_utf8:
            return {'h': '─', 'v': '│', 'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
                    'tee_r': '├', 'tee_l': '┤', 'tee_d': '┬', 'tee_u': '┴',
                    'block': '█', 'shade': '░', 'handle': '■'}
        return {'h': '-', 'v': '|', 'tl': '+', 'tr': '+', 'bl': '+', 'br': '+',
                'tee_r': '+', 'tee_l': '+', 'tee_d': '+', 'tee_u': '+',
                'block': '#', 'shade': ':', 'handle': '#'}

TERM = TerminalCompat()

PYTHON_KEYWORDS = {"def", "class", "if", "elif", "else", "while", "for", "in", 
    "return", "pass", "import", "from", "and", "or", "not", "True", "False", 
    "None", "try", "except", "with", "as", "break", "continue"}

def tokenize_python(line):
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
        else:
            tokens.append((token, 'text'))
    return tokens

class MenuItem:
    def __init__(self, caption="", name_id="", parent=0):
        self.caption = caption
        self.name_id = name_id
        self.parent = parent
        self.has_submenu = False
        self.code = ""

class UIControl:
    def __init__(self, x, y, w, h, tool_type, name_id, caption):
        self.x, self.y, self.w, self.h = x, y, w, h
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
            'parent': self.parent, 'items': self.items,
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
        self.x, self.y, self.w, self.h = x, y, w, h
        self.title = title
        self.controls = []
        self.menu_items = []
        self._last_focused = -1

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

    def hit_test(self, mx, my):
        return (self.x <= mx < self.x + self.w) and (self.y <= my < self.y + self.h)

    def hit_control(self, lx, ly):
        for i in range(len(self.controls) - 1, -1, -1):
            c = self.controls[i]
            if (c.x <= lx < c.x + c.w) and (c.y <= ly < c.y + c.h):
                return i
        return -1

class UIControl:
    def __init__(self, x, y, w, h, tool_type, name_id, caption):
        self.x, self.y, self.w, self.h = x, y, w, h
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
        # Grid-specific properties (Type 16)
        self.grid_data = []  # 2D array of cell values
        self.grid_headers = []  # Column headers
        self.grid_col_widths = []  # Column widths
        self.grid_row_count = 0
        self.grid_col_count = 0
        self.grid_selected_cell = (-1, -1)  # (row, col)
        self.grid_selected_range = None  # (start_row, start_col, end_row, end_col)
        self.grid_scroll_row = 0
        self.grid_scroll_col = 0
        self.grid_edit_mode = False
        self.grid_sort_col = -1
        self.grid_sort_asc = True

    def to_dict(self):
        return {
            'x': self.x, 'y': self.y, 'w': self.w, 'h': self.h,
            'tool_type': self.tool_type, 'name_id': self.name_id,
            'caption': self.caption, 'code': self.code,
            'checked': self.checked, 'group': self.group,
            'parent': self.parent, 'items': self.items,
            'selected_index': self.selected_index,
            'scroll_offset': self.scroll_offset,
            'grid_data': self.grid_data,
            'grid_headers': self.grid_headers,
            'grid_col_widths': self.grid_col_widths,
            'grid_row_count': self.grid_row_count,
class Toolbox:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 16
        self.h = 22  # Increased for Grid control
        self.active_tool = -1
        self.items = [
            "Move/Size", "Check Box", "Combo Box", "Command Btn",
            "Dir List", "Drive List", "File List", "Frame",
            "HScrollBar", "Label", "List Box", "Option Btn",
            "Picture Box", "Text Box", "Timer", "VScrollBar",
            "Grid"  # Added Grid control
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
        
        # Remaining items (17 total now)
        for i in range(1, 17):
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
            elif self.y + 3 <= my <= self.y + 18:  # Adjusted for 17 tools
                self.active_tool = my - (self.y + 2)
                return True
        return False
            ch = stdscr.getch()
            
            if ch == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                    if bstate & curses.BUTTON1_CLICKED:
                        btn_x = x + (w - btn_w) // 2
                        for i, btn in enumerate(btn_list):
                            if y + h - 2 == my and btn_x <= mx < btn_x + len(btn):
                                values = {'ok': ['ok'], 'okcancel': ['ok', 'cancel'],
                                         'yesno': ['yes', 'no'], 'yesnocancel': ['yes', 'no', 'cancel']}
                                return values.get(buttons, ['ok'])[i]
                            btn_x += len(btn) + 2
                except:
                    pass
            
            elif ch == curses.KEY_LEFT:
                selected = max(0, selected - 1)
                draw_dialog(selected)
            elif ch == curses.KEY_RIGHT:
                selected = min(len(btn_list) - 1, selected + 1)
                draw_dialog(selected)
            elif ch in (10, 13, curses.KEY_ENTER):
                values = {'ok': ['ok'], 'okcancel': ['ok', 'cancel'],
                         'yesno': ['yes', 'no'], 'yesnocancel': ['yes', 'no', 'cancel']}
                return values.get(buttons, ['ok'])[selected]
            elif ch == 27:
                if buttons in ['okcancel', 'yesnocancel']:
                    return 'cancel'
                return 'ok' if buttons == 'ok' else 'no'
            
            time.sleep(0.01)
    
    return msgbox

def make_inputbox(stdscr, colors):
    """Create inputbox function bound to screen"""
    def inputbox(prompt, title="Input", default=""):
        C_BORDER = colors['border']
        C_BG = colors['bg']
        C_TB = colors['textbox']
        
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
    
    return inputbox

def make_file_dialog(stdscr, colors):
    """Create file dialog function bound to screen"""
    def file_dialog(mode='open', filter_ext=None, start_dir=None):
        C_BORDER = colors['border']
        C_BG = colors['bg']
        C_ACTIVE = colors['active_tool']
        
        current_dir = start_dir or os.getcwd()
        files = []
        cursor = 0
    return file_dialog

def make_color_picker(stdscr, colors):
    """Create color picker function bound to screen"""
    def color_picker():
        C_BORDER = colors['border']
        C_BG = colors['bg']
        C_ACTIVE = colors['active_tool']
        
        color_names = [
            'black', 'red', 'green', 'yellow', 
            'blue', 'magenta', 'cyan', 'white'
        ]
        
        w = 40
        h = 14
        x = max(0, (curses.COLS - w) // 2)
        y = max(0, (curses.LINES - h) // 2)
        
        cols = 4
        rows = 2
        cursor = 0
        
        def draw_picker():
            write_at(stdscr, x, y, '+' + '-' * (w - 2) + '+', C_BORDER)
            for i in range(1, h - 1):
                write_at(stdscr, x, y + i, '|', C_BORDER)
                write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
                write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
            write_at(stdscr, x, y + h - 1, '+' + '-' * (w - 2) + '+', C_BORDER)
            
            title = " Select Color "
            write_at(stdscr, x + (w - len(title)) // 2, y, title, C_BORDER)
            
            cell_w = (w - 4) // cols
            for i, color in enumerate(color_names):
                row = i // cols
                col = i % cols
                cell_x = x + 2 + col * cell_w
                cell_y = y + 2 + row
                
            elif ctype == 14:
                ctrl = UIControl(cx, cy, 10, 1, ctype, name_id, "Timer")
            elif ctype == 16:  # Grid Control
                ctrl = UIControl(cx, cy, 40, 10, ctype, name_id, "Grid")
                ctrl.grid_col_count = 3
                ctrl.grid_row_count = 5
                ctrl.grid_headers = ["Col1", "Col2", "Col3"]
                ctrl.grid_col_widths = [12, 12, 12]
                ctrl.grid_data = [[f"Row{r+1}" for c in range(3)] for r in range(5)]
            else:
                ctrl = UIControl(cx, cy, 12, 1, ctype, name_id, ctitle)
        families = ['monospace', 'serif', 'sans-serif', 'courier']
        
        w = 45
        h = 14
        x = max(0, (curses.COLS - w) // 2)
        y = max(0, (curses.LINES - h) // 2)
        
        selected_size = 2  # Default 12
        selected_family = 0
        
        def draw_dialog():
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
            write_at(stdscr, x + 9, y + 2, size_str[:w-11], C_BG)
            
            write_at(stdscr, x + 2, y + 4, "Family:", C_BORDER)
            for i, family in enumerate(families):
                attr = C_ACTIVE if i == selected_family else C_BG
                prefix = '> ' if i == selected_family else '  '
                write_at(stdscr, x + 10, y + 5 + i, prefix + family, attr)
            
            preview = f"Size {sizes[selected_size]}, {families[selected_family]}"
            write_at(stdscr, x + 2, y + h - 4, preview[:w-4], C_BG)
            
            btn_text = "[ OK ]  [ Cancel ]"
            write_at(stdscr, x + (w - len(btn_text)) // 2, y + h - 2, btn_text, C_BORDER)
            
            stdscr.refresh()
        
        while True:
            draw_dialog()
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
    
    return font_dialog
                files = ['..', f'Error: {e}']
        
        def draw_dialog():
            write_at(stdscr, x, y, '+' + '-' * (w - 2) + '+', C_BORDER)
            for i in range(1, h - 1):
                write_at(stdscr, x, y + i, '|', C_BORDER)
                write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
                write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
    # Create dialog functions bound to current screen
    msgbox = make_msgbox(stdscr, C)
    inputbox = make_inputbox(stdscr, C)
    file_dialog = make_file_dialog(stdscr, C)
    color_picker = make_color_picker(stdscr, C)
    font_dialog = make_font_dialog(stdscr, C)
            btn_text = "[ OK ]  [ Cancel ]"
            write_at(stdscr, x + (w - len(btn_text)) // 2, y + h - 2, btn_text, C_BORDER)
            
            stdscr.refresh()
        
        refresh_files()
        
        while True:
            draw_dialog()
            ch = stdscr.getch()
            
            if ch == 27:
                return None
            elif ch == curses.KEY_UP and cursor > 0:
                cursor -= 1
                if cursor < scroll_offset:
                    scroll_offset = cursor
            elif ch == curses.KEY_DOWN and cursor < len(files) - 1:
                cursor += 1
                if cursor >= scroll_offset + visible_rows:
                    scroll_offset = cursor - visible_rows + 1
            elif ch in (10, 13, curses.KEY_ENTER):
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
                    return os.path.join(current_dir, fname)
            
            time.sleep(0.01)
    
    return file_dialog

# ==========================================================
# MAIN APPLICATION
# ==========================================================

def main(stdscr):
    TERM.setup(stdscr)
    box_chars = TERM.get_box_chars()
    
    curses.curs_set(0)
    stdscr.nodelay(True)
    
    try:
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
        curses.mouseinterval(0)
        print('\033[?1003h\033[?1015h\033[?1006h', end='', flush=True)
        TERM.has_mouse = True
    except:
        pass

    if TERM.has_colors:
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)
                run_globals['msgbox'] = msgbox
                run_globals['inputbox'] = inputbox
                run_globals['file_dialog'] = file_dialog
                run_globals['color_picker'] = color_picker
                run_globals['font_dialog'] = font_dialog
                run_globals['open_file'] = open_file
                run_globals['read_line'] = read_line
                run_globals['read_all'] = read_all
                run_globals['write_line'] = write_line
                run_globals['close_file'] = close_file
                run_globals['file_exists'] = file_exists
                
                # Test dialogs
                result = msgbox("Welcome to v2.1.0!\nAll dialogs are now available:\n- msgbox\n- inputbox\n- file_dialog\n- color_picker\n- font_dialog", "v2.1.0 Demo", "ok")
            'btn_hl': curses.A_BOLD, 'textbox': curses.A_REVERSE,
            'handle': curses.A_BOLD, 'active_tool': curses.A_BOLD,
            'prop_label': 0, 'kw': curses.A_BOLD, 'str': 0,
            'comment': curses.A_DIM, 'num': 0
        }

    # Create dialog functions bound to current screen
    msgbox = make_msgbox(stdscr, C)
    inputbox = make_inputbox(stdscr, C)
    file_dialog = make_file_dialog(stdscr, C)

    windows = [
        Window(21, 4, 36, 17, "Form 1"),
        Window(59, 2, 20, 15, "Properties")
    ]

    run_mode = False
    run_globals = {}
    run_file_handles = {}
    run_file_counter = [0]

    def open_file(filename, mode='r'):
        try:
            f = open(filename, mode, encoding='utf-8')
            run_file_counter[0] += 1
            handle = f"file_{run_file_counter[0]}"
            run_file_handles[handle] = f
            return handle
        except Exception as e:
            run_globals['__msg__'] = f"File Error: {e}"
            return None

    def read_line(file_handle):
        if file_handle in run_file_handles:
            try:
                line = run_file_handles[file_handle].readline()
                return line.rstrip('\n') if line else None
            except Exception as e:
                run_globals['__msg__'] = f"Read Error: {e}"
                return None
        return None

    def read_all(file_handle):
        if file_handle in run_file_handles:
            try:
                return run_file_handles[file_handle].read()
            except Exception as e:
                run_globals['__msg__'] = f"Read Error: {e}"
                return ""
        return ""

    def write_line(file_handle, text):
        if file_handle in run_file_handles:
            try:
                run_file_handles[file_handle].write(text + '\n')
                return True
            except Exception as e:
                run_globals['__msg__'] = f"Write Error: {e}"
                return False
        return False

    def close_file(file_handle):
        if file_handle in run_file_handles:
            try:
                run_file_handles[file_handle].close()
                del run_file_handles[file_handle]
                return True
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
    
    elif c.tool_type == 16:  # Grid Control
        draw_grid(stdscr, win, c, is_active, colors, box_chars, draw_x, draw_y)
    
    else:
        for r in range(c.h):
            if r == 0:
                text = (c.caption + " " * c.w)[:c.w]
                write_at(stdscr, draw_x, draw_y + r, text, C_TEXTBOX)
            else:
                write_at(stdscr, draw_x, draw_y + r, " " * c.w, C_TEXTBOX)

def draw_grid(stdscr, win, c, is_active, colors, box_chars, draw_x, draw_y):
    """Draw a spreadsheet-like grid control"""
    C_BORDER = colors['border']
    C_BG = colors['bg']
    C_ACTIVE = colors['active_tool']
    C_TEXTBOX = colors['textbox']
    
    # Initialize grid if empty
    if c.grid_col_count == 0:
        c.grid_col_count = 3
        c.grid_row_count = 5
        c.grid_headers = ["Col1", "Col2", "Col3"]
        c.grid_col_widths = [10, 10, 10]
        c.grid_data = [[f"R{r+1}C{col+1}" for col in range(c.grid_col_count)] 
                       for r in range(c.grid_row_count)]
    
    # Calculate visible area
    header_height = 2
    row_height = 1
    visible_rows = c.h - header_height - 1  # -1 for border
    visible_cols = len(c.grid_col_widths)
    
    # Draw outer border
    top = box_chars['tl'] + box_chars['h'] * (c.w - 2) + box_chars['tr']
    write_at(stdscr, draw_x, draw_y, top, C_BORDER)
    
    for r in range(1, c.h - 1):
        write_at(stdscr, draw_x, draw_y + r, box_chars['v'], C_BORDER)
        write_at(stdscr, draw_x + c.w - 1, draw_y + r, box_chars['v'], C_BORDER)
    
    bottom = box_chars['bl'] + box_chars['h'] * (c.w - 2) + box_chars['br']
    write_at(stdscr, draw_x, draw_y + c.h - 1, bottom, C_BORDER)
    
    # Draw header row
    header_y = draw_y + 1
    curr_x = draw_x + 1
    for col in range(c.grid_scroll_col, min(visible_cols, c.grid_scroll_col + len(c.grid_col_widths))):
        if col < len(c.grid_headers):
            header_text = c.grid_headers[col]
            width = c.grid_col_widths[col] if col < len(c.grid_col_widths) else 10
            
            # Truncate or pad header
            if len(header_text) > width - 1:
                header_text = header_text[:width-1]
            else:
                header_text = header_text.center(width - 1)
            
            # Highlight sorted column
            attr = C_ACTIVE if col == c.grid_sort_col else C_BORDER
            write_at(stdscr, curr_x, header_y, header_text, attr)
            
            # Draw column separator
            if col < visible_cols - 1:
                write_at(stdscr, curr_x + width - 1, header_y, box_chars['v'], C_BORDER)
            
            curr_x += width
    
    # Draw header-data separator
    sep_y = draw_y + 2
    curr_x = draw_x
    sep_line = box_chars['tee_r']
    for col in range(c.grid_scroll_col, visible_cols):
        if col < len(c.grid_col_widths):
            width = c.grid_col_widths[col]
            sep_line += box_chars['h'] * (width - 1)
            if col < visible_cols - 1:
                sep_line += box_chars['cross']
            else:
                sep_line += box_chars['tee_l']
    write_at(stdscr, curr_x, sep_y, sep_line, C_BORDER)
    
    # Draw data rows
    for row_idx in range(c.grid_scroll_row, min(c.grid_row_count, c.grid_scroll_row + visible_rows)):
        row_y = draw_y + header_height + 1 + (row_idx - c.grid_scroll_row)
        curr_x = draw_x + 1
        
        for col_idx in range(c.grid_scroll_col, visible_cols):
            if col_idx < len(c.grid_col_widths) and col_idx < len(c.grid_data[row_idx]):
                width = c.grid_col_widths[col_idx]
                cell_value = str(c.grid_data[row_idx][col_idx])
                
                # Truncate cell value
                if len(cell_value) > width - 1:
                    cell_value = cell_value[:width-2] + ".."
                else:
                    cell_value = cell_value.ljust(width - 1)
                
                # Highlight selected cell
                is_selected = (row_idx == c.grid_selected_cell[0] and 
                              col_idx == c.grid_selected_cell[1])
                attr = C_ACTIVE if is_selected else C_BG
                
                write_at(stdscr, curr_x, row_y, cell_value[:width-1], attr)
                
                # Draw column separator
                if col_idx < visible_cols - 1:
                    sep_attr = C_ACTIVE if is_selected else C_BORDER
                    write_at(stdscr, curr_x + width - 1, row_y, box_chars['v'], sep_attr)
                
                curr_x += width
    
    # Draw scrollbars if needed
    # Vertical scrollbar
    if c.grid_row_count > visible_rows:
        sb_height = visible_rows
        total_rows = c.grid_row_count
        thumb_size = max(1, (visible_rows * sb_height) // total_rows)
        thumb_pos = (c.grid_scroll_row * (sb_height - thumb_size)) // (total_rows - visible_rows) if total_rows > visible_rows else 0
        
        for r in range(sb_height):
            sb_y = draw_y + header_height + 1 + r
            sb_x = draw_x + c.w - 2
            ch = box_chars['block'] if r >= thumb_pos and r < thumb_pos + thumb_size else box_chars['shade']
            write_at(stdscr, sb_x, sb_y, ch, C_BG)
    
    # Horizontal scrollbar indicator
    if c.grid_col_count > visible_cols:
        sb_width = c.w - 2
        thumb_size = max(3, (visible_cols * sb_width) // c.grid_col_count)
        thumb_pos = (c.grid_scroll_col * (sb_width - thumb_size)) // (c.grid_col_count - visible_cols) if c.grid_col_count > visible_cols else 0
        
        sb_y = draw_y + c.h - 2
        for i in range(sb_width):
            ch = box_chars['block'] if i >= thumb_pos and i < thumb_pos + thumb_size else box_chars['h']
            write_at(stdscr, draw_x + 1 + i, sb_y, ch, C_BG)
            if not run_mode:
                run_mode = True
                run_globals = {'__msg__': None}
                run_globals['msgbox'] = msgbox
                run_globals['inputbox'] = inputbox
                run_globals['file_dialog'] = file_dialog
                run_globals['open_file'] = open_file
                run_globals['read_line'] = read_line
                run_globals['read_all'] = read_all
                run_globals['write_line'] = write_line
                run_globals['close_file'] = close_file
                run_globals['file_exists'] = file_exists
                
                # Test dialogs
                result = msgbox("Welcome to v2.1.0!\nFile I/O and dialogs are now available.", "v2.1.0 Demo", "ok")
                print(f"\nMsgbox returned: {result}")
            else:
                # Cleanup file handles
                for handle in list(run_file_handles.keys()):
                    close_file(handle)
                run_file_handles.clear()
                run_mode = False
        
        time.sleep(0.01)

    if TERM.has_mouse:
        print('\033[?1003l', end='', flush=True)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nExiting...")
