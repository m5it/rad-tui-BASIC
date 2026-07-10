#!/usr/bin/env python3
"""
VB1-DOS Clone v2.1.0 Final
Features: File I/O, Dialogs, Grid Control, Clipboard, Print Support
"""

import curses
import time
import re
import json
import os
import sys
import subprocess
import platform
import copy

# ==========================================================
# TERMINAL COMPATIBILITY
# ==========================================================

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
                    'cross': '┼', 'block': '█', 'shade': '░', 'handle': '■'}
        return {'h': '-', 'v': '|', 'tl': '+', 'tr': '+', 'bl': '+', 'br': '+',
                'tee_r': '+', 'tee_l': '+', 'tee_d': '+', 'tee_u': '+',
                'cross': '+', 'block': '#', 'shade': ':', 'handle': '#'}

TERM = TerminalCompat()

# ==========================================================
# CLIPBOARD MODULE
# ==========================================================

class ClipboardManager:
    def __init__(self):
        self.system = platform.system()
        self.internal_clipboard = ""
        self.available = False
        self.backend = None
        self._detect_backend()
    
    def _detect_backend(self):
        if self.system == "Linux":
            try:
                subprocess.run(["which", "xclip"], check=True, capture_output=True)
                self.backend = "xclip"
                self.available = True
                return
            except:
                pass
            try:
                subprocess.run(["which", "xsel"], check=True, capture_output=True)
                self.backend = "xsel"
                self.available = True
                return
            except:
                pass
        elif self.system == "Darwin":
            try:
                subprocess.run(["which", "pbcopy"], check=True, capture_output=True)
                self.backend = "pbcopy"
                self.available = True
                return
            except:
                pass
    
    def copy(self, text):
        if not text:
            text = ""
        self.internal_clipboard = text
        if not self.available:
            return True
        try:
            if self.system == "Linux":
                if self.backend == "xclip":
                    subprocess.run(["xclip", "-selection", "clipboard", "-in"],
                        input=text.encode('utf-8'), check=True, capture_output=True)
                    return True
                elif self.backend == "xsel":
                    subprocess.run(["xsel", "--clipboard", "--input"],
                        input=text.encode('utf-8'), check=True, capture_output=True)
                    return True
            elif self.system == "Darwin":
                if self.backend == "pbcopy":
                    subprocess.run(["pbcopy"], input=text.encode('utf-8'),
                        check=True, capture_output=True)
                    return True
        except Exception as e:
            print(f"Clipboard error: {e}")
            return False
        return False
    
    def paste(self):
        if not self.available:
            return self.internal_clipboard
        try:
            if self.system == "Linux":
                if self.backend == "xclip":
                    result = subprocess.run(["xclip", "-selection", "clipboard", "-out"],
                        capture_output=True, check=True)
                    return result.stdout.decode('utf-8')
                elif self.backend == "xsel":
                    result = subprocess.run(["xsel", "--clipboard", "--output"],
                        capture_output=True, check=True)
                    return result.stdout.decode('utf-8')
            elif self.system == "Darwin":
                if self.backend == "pbcopy":
                    result = subprocess.run(["pbpaste"], capture_output=True, check=True)
                    return result.stdout.decode('utf-8')
        except Exception as e:
            return self.internal_clipboard
        return self.internal_clipboard
    
    def clear(self):
        self.internal_clipboard = ""
        if self.available:
            self.copy("")
        return True

_clipboard = None
def get_clipboard():
    global _clipboard
    if _clipboard is None:
        _clipboard = ClipboardManager()
    return _clipboard

def clipboard_copy(text):
    return get_clipboard().copy(text)

def clipboard_paste():
    return get_clipboard().paste()

def clipboard_clear():
    return get_clipboard().clear()

# ==========================================================
# PRINT MODULE
# ==========================================================

class PrintManager:
    def __init__(self):
        self.page_width = 80
        self.page_height = 66
        self.left_margin = 5
        self.right_margin = 5
        self.top_margin = 3
        self.bottom_margin = 3
    
    def format_text(self, text, title=""):
        content_width = self.page_width - self.left_margin - self.right_margin
        content_height = self.page_height - self.top_margin - self.bottom_margin
        
        lines = text.split('\n') if isinstance(text, str) else text
        wrapped_lines = []
        for line in lines:
            while len(line) > content_width:
                wrapped_lines.append(line[:content_width])
                line = line[content_width:]
            wrapped_lines.append(line)
        
        pages = []
        current_page = []
        line_count = 0
        
        for line in wrapped_lines:
            if line_count >= content_height:
                pages.append(current_page)
                current_page = []
                line_count = 0
            current_page.append(line)
            line_count += 1
        
        if current_page:
            pages.append(current_page)
        
        formatted_pages = []
        for i, page in enumerate(pages):
            formatted_page = []
            for _ in range(self.top_margin):
                formatted_page.append("")
            header = f"{title[:30]:<30} Page {i+1}/{len(pages)}"
            formatted_page.append(" " * self.left_margin + header)
            formatted_page.append("")
            for line in page:
                formatted_page.append(" " * self.left_margin + line.ljust(content_width))
            footer = f"Page {i+1} of {len(pages)}".center(content_width)
            formatted_page.append("")
            formatted_page.append(" " * self.left_margin + footer)
            for _ in range(self.bottom_margin):
                formatted_page.append("")
            formatted_pages.append(formatted_page)
        
        return formatted_pages
    
    def print_text(self, text, title="", to_file=None):
        pages = self.format_text(text, title)
        all_lines = []
        for page in pages:
            all_lines.extend(page)
            all_lines.append("\f")
        if all_lines:
            all_lines.pop()
        text_output = '\n'.join(all_lines)
        
        if to_file:
            try:
                with open(to_file, 'w', encoding='utf-8') as f:
                    f.write(text_output)
                return True
            except:
                return False
        
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(text_output)
                temp_file = f.name
            cmd = ["lp"] if self._cmd_exists("lp") else ["lpr"]
            cmd.append(temp_file)
            result = subprocess.run(cmd, capture_output=True)
            os.unlink(temp_file)
            return result.returncode == 0
        except:
            try:
                with open("print_output.txt", 'w') as f:
                    f.write(text_output)
                return True
            except:
                return False
    
    def _cmd_exists(self, cmd):
        try:
            subprocess.run(["which", cmd], capture_output=True, check=True)
            return True
        except:
            return False

_print_manager = None
def get_print_manager():
    global _print_manager
    if _print_manager is None:
        _print_manager = PrintManager()
    return _print_manager

def print_text(text, title="", to_file=None):
    return get_print_manager().print_text(text, title, to_file)

# ==========================================================
# FILE I/O FUNCTIONS
# ==========================================================

class FileIOManager:
    def __init__(self):
        self.handles = {}
        self.counter = 0
    
    def open_file(self, filename, mode='r'):
        try:
            f = open(filename, mode, encoding='utf-8')
            self.counter += 1
            handle = f"file_{self.counter}"
            self.handles[handle] = f
            return handle
        except Exception as e:
            return None
    
    def read_line(self, handle):
        if handle in self.handles:
            try:
                line = self.handles[handle].readline()
                return line.rstrip('\n') if line else None
            except:
                return None
        return None
    
    def read_all(self, handle):
        if handle in self.handles:
            try:
                return self.handles[handle].read()
            except:
                return ""
        return ""
    
    def write_line(self, handle, text):
        if handle in self.handles:
            try:
                self.handles[handle].write(text + '\n')
                return True
            except:
                return False
        return False
    
    def close_file(self, handle):
        if handle in self.handles:
            try:
                self.handles[handle].close()
                del self.handles[handle]
                return True
            except:
                return False
        return False
    
    def file_exists(self, filename):
        return os.path.exists(filename)
    
    def close_all(self):
        for handle in list(self.handles.keys()):
            self.close_file(handle)

# ==========================================================
# CORE CLASSES
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
        # Grid properties
        self.grid_data = []
        self.grid_headers = []
        self.grid_col_widths = []
        self.grid_row_count = 0
        self.grid_col_count = 0
        self.grid_selected_cell = (-1, -1)
        self.grid_scroll_row = 0
        self.grid_scroll_col = 0

class Window:
    def __init__(self, x, y, w, h, title="untitled"):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.title = title
        self.controls = []
        self.menu_items = []
        self._last_focused = -1
    
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
        self.x, self.y = x, y
        self.w = 16
        self.h = 22
        self.active_tool = -1
        self.items = [
            "Move/Size", "Check Box", "Combo Box", "Command Btn",
            "Dir List", "Drive List", "File List", "Frame",
            "HScrollBar", "Label", "List Box", "Option Btn",
            "Picture Box", "Text Box", "Timer", "VScrollBar",
            "Grid"
        ]

# ==========================================================
# DIALOG FUNCTIONS
# ==========================================================

def make_msgbox(stdscr, colors):
    def msgbox(text, title="Message", buttons="ok"):
        C_BORDER = colors['border']
        C_BG = colors['bg']
        C_ACTIVE = colors['active_tool']
        
        lines = text.split('\n')
        btn_configs = {
            'ok': ['[ OK ]'],
            'okcancel': ['[ OK ]', '[ Cancel ]'],
            'yesno': ['[ Yes ]', '[ No ]']
        }
        btn_list = btn_configs.get(buttons, ['[ OK ]'])
        btn_w = sum(len(b) + 2 for b in btn_list)
        w = max(max(len(l) for l in lines) + 4, btn_w + 4, len(title) + 4)
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
            
            for i, line in enumerate(lines):
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
                values = {'ok': ['ok'], 'okcancel': ['ok', 'cancel'], 'yesno': ['yes', 'no']}
                return values.get(buttons, ['ok'])[selected]
            elif ch == 27:
                return 'cancel' if buttons in ['okcancel'] else 'no' if buttons == 'yesno' else 'ok'
            time.sleep(0.01)
    
    return msgbox

def make_inputbox(stdscr, colors):
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
    def file_dialog(mode='open', filter_ext=None, start_dir=None):
        C_BORDER = colors['border']
        C_BG = colors['bg']
        C_ACTIVE = colors['active_tool']
        
        current_dir = start_dir or os.getcwd()
        files = []
        cursor = 0
        scroll_offset = 0
        
        w = min(60, curses.COLS - 4)
        h = min(20, curses.LINES - 4)
        x = max(0, (curses.COLS - w) // 2)
        y = max(0, (curses.LINES - h) // 2)
        
        visible_rows = h - 6
        
        def refresh_files():
            nonlocal files
            try:
                entries = os.listdir(current_dir)
                files = ['..']
                dirs = sorted([e for e in entries if os.path.isdir(os.path.join(current_dir, e))])
                file_list = sorted([e for e in entries if os.path.isfile(os.path.join(current_dir, e))])
                if filter_ext:
                    file_list = [f for f in file_list if any(f.endswith(ext) for ext in filter_ext)]
                files.extend(dirs)
                files.extend(file_list)
            except Exception as e:
                files = ['..', f'Error: {e}']
        
        def draw_dialog():
            write_at(stdscr, x, y, '+' + '-' * (w - 2) + '+', C_BORDER)
            for i in range(1, h - 1):
                write_at(stdscr, x, y + i, '|', C_BORDER)
                write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
                write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
            write_at(stdscr, x, y + h - 1, '+' + '-' * (w - 2) + '+', C_BORDER)
            
            title = "Open File" if mode == 'open' else "Save File"
            title_x = x + (w - len(title)) // 2
            write_at(stdscr, title_x, y, f" {title} ", C_BORDER)
            
            path_text = current_dir[-(w-4):] if len(current_dir) > w - 4 else current_dir
            write_at(stdscr, x + 2, y + 1, path_text[:w-4], C_BORDER)
            
            for i in range(visible_rows):
                file_idx = scroll_offset + i
                if file_idx < len(files):
                    fname = files[file_idx]
                    is_dir = fname == '..' or os.path.isdir(os.path.join(current_dir, fname))
                    prefix = '/' if is_dir else ' '
                    display = (prefix + fname)[:w-4]
                    attr = C_ACTIVE if file_idx == cursor else C_BG
                    write_at(stdscr, x + 2, y + 3 + i, display.ljust(w-4), attr)
                else:
                    write_at(stdscr, x + 2, y + 3 + i, ' ' * (w-4), C_BG)
            
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
# DRAWING FUNCTIONS
# ==========================================================

def write_at(stdscr, x, y, text, attr=0):
    try:
        if y >= 0 and x >= 0:
            stdscr.addstr(y, x, text, attr)
    except curses.error:
        pass

def draw_window(stdscr, win, colors, box_chars, active_ctrl=-1):
    C_BORDER = colors['border']
    C_BG = colors['bg']
    
    top = box_chars['tl'] + box_chars['h'] * (win.w - 2) + box_chars['tr']
    write_at(stdscr, win.x, win.y, top, C_BORDER)
    title_x = win.x + (win.w - len(win.title)) // 2
    write_at(stdscr, title_x, win.y, win.title, C_BORDER)
    
    for i in range(1, win.h - 1):
        write_at(stdscr, win.x, win.y + i, box_chars['v'], C_BORDER)
        write_at(stdscr, win.x + 1, win.y + i, " " * (win.w - 2), C_BG)
        write_at(stdscr, win.x + win.w - 1, win.y + i, box_chars['v'], C_BORDER)
    
    bottom = box_chars['bl'] + box_chars['h'] * (win.w - 2) + box_chars['br']
    write_at(stdscr, win.x, win.y + win.h - 1, bottom, C_BORDER)

def draw_control(stdscr, win, c, is_active, colors, box_chars):
    C_BORDER = colors['border']
    C_BG = colors['bg']
    C_BTN_FACE = colors['btn_face']
    C_BTN_HL = colors['btn_hl']
    C_ACTIVE = colors['active_tool']
    
    draw_x = win.x + c.x
    draw_y = win.y + c.y
    
    if c.tool_type == 1:  # Check Box
        check_state = "[X]" if c.checked else "[ ]"
        label = c.caption[3:] if c.caption.startswith('[ ]') or c.caption.startswith('[X]') else c.caption
        write_at(stdscr, draw_x, draw_y, f"{check_state}{label}", C_BG)
        
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
        
    elif c.tool_type == 16:  # Grid Control
        draw_grid(stdscr, c, colors, box_chars, draw_x, draw_y)
    
    else:
        for r in range(c.h):
            if r == 0:
                text = (c.caption + " " * c.w)[:c.w]
                write_at(stdscr, draw_x, draw_y + r, text, C_BG)
            else:
                write_at(stdscr, draw_x, draw_y + r, " " * c.w, C_BG)

def draw_grid(stdscr, c, colors, box_chars, draw_x, draw_y):
    """Draw spreadsheet-like grid"""
    C_BORDER = colors['border']
    C_BG = colors['bg']
    C_ACTIVE = colors['active_tool']
    
    if c.grid_col_count == 0:
        c.grid_col_count = 3
        c.grid_row_count = 5
        c.grid_headers = ["Col1", "Col2", "Col3"]
        c.grid_col_widths = [10, 10, 10]
        c.grid_data = [[f"R{r+1}C{col+1}" for col in range(c.grid_col_count)] 
                       for r in range(c.grid_row_count)]
    
    header_height = 2
    visible_rows = c.h - header_height - 1
    
    # Border
    top = box_chars['tl'] + box_chars['h'] * (c.w - 2) + box_chars['tr']
    write_at(stdscr, draw_x, draw_y, top, C_BORDER)
    for r in range(1, c.h - 1):
        write_at(stdscr, draw_x, draw_y + r, box_chars['v'], C_BORDER)
        write_at(stdscr, draw_x + c.w - 1, draw_y + r, box_chars['v'], C_BORDER)
    bottom = box_chars['bl'] + box_chars['h'] * (c.w - 2) + box_chars['br']
    write_at(stdscr, draw_x, draw_y + c.h - 1, bottom, C_BORDER)
    
    # Headers
    header_y = draw_y + 1
    curr_x = draw_x + 1
    for col in range(c.grid_scroll_col, min(c.grid_col_count, c.grid_scroll_col + len(c.grid_col_widths))):
        if col < len(c.grid_headers):
            header_text = c.grid_headers[col][:c.grid_col_widths[col]-1].center(c.grid_col_widths[col]-1)
            attr = C_ACTIVE if col == c.grid_sort_col else C_BORDER
            write_at(stdscr, curr_x, header_y, header_text, attr)
            curr_x += c.grid_col_widths[col]
    
    # Separator
    sep_y = draw_y + 2
    sep = box_chars['tee_r']
    for col in range(c.grid_scroll_col, c.grid_col_count):
        if col < len(c.grid_col_widths):
            sep += box_chars['h'] * (c.grid_col_widths[col] - 1)
            sep += box_chars['cross'] if col < c.grid_col_count - 1 else box_chars['tee_l']
    write_at(stdscr, draw_x, sep_y, sep, C_BORDER)
    
    # Data
    for row_idx in range(c.grid_scroll_row, min(c.grid_row_count, c.grid_scroll_row + visible_rows)):
        row_y = draw_y + header_height + 1 + (row_idx - c.grid_scroll_row)
        curr_x = draw_x + 1
        
        for col_idx in range(c.grid_scroll_col, c.grid_col_count):
            if col_idx < len(c.grid_col_widths):
                width = c.grid_col_widths[col_idx]
                cell_value = str(c.grid_data[row_idx][col_idx]) if col_idx < len(c.grid_data[row_idx]) else ""
                
                if len(cell_value) > width - 1:
                    cell_value = cell_value[:width-2] + ".."
                else:
                    cell_value = cell_value.ljust(width - 1)
                
                is_selected = (row_idx == c.grid_selected_cell[0] and 
                              col_idx == c.grid_selected_cell[1])
                attr = C_ACTIVE if is_selected else C_BG
                
                write_at(stdscr, curr_x, row_y, cell_value[:width-1], attr)
                curr_x += width

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
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        
        C = {
            'border': curses.color_pair(1) | curses.A_BOLD,
            'bg': curses.color_pair(2),
            'btn_face': curses.color_pair(2),
            'btn_hl': curses.color_pair(3) | curses.A_BOLD,
            'textbox': curses.color_pair(4),
            'handle': curses.color_pair(5),
            'active_tool': curses.color_pair(6) | curses.A_BOLD,
            'prop_label': curses.color_pair(2),
            'kw': curses.color_pair(1) | curses.A_BOLD,
            'str': curses.color_pair(6),
            'comment': curses.A_DIM,
            'num': curses.color_pair(5)
        }
    else:
        C = {
            'border': curses.A_BOLD, 'bg': 0,
            'btn_face': 0, 'btn_hl': curses.A_BOLD,
            'textbox': curses.A_REVERSE, 'handle': curses.A_BOLD,
            'active_tool': curses.A_BOLD, 'prop_label': 0,
            'kw': curses.A_BOLD, 'str': 0,
            'comment': curses.A_DIM, 'num': 0
        }

    # Create dialogs
    msgbox = make_msgbox(stdscr, C)
    inputbox = make_inputbox(stdscr, C)
    file_dialog = make_file_dialog(stdscr, C)

    # Setup windows
    tools = Toolbox(1, 2)
    windows = [
        Window(21, 4, 50, 20, "Form 1 (v2.1.0)"),
        Window(75, 2, 20, 15, "Properties")
    ]
    
    # Add sample controls
    windows[0].controls.append(UIControl(5, 5, 12, 3, 3, "btnTest", "Test"))
    windows[0].controls.append(UIControl(5, 10, 40, 8, 16, "gridData", "Data Grid"))

    # Runtime setup
    run_mode = False
    run_globals = {}
    file_io = FileIOManager()

    stdscr.clear()
    last_draw = 0
    frame_delay = 1/30
    
    while True:
        current_time = time.time()
        
        if current_time - last_draw >= frame_delay:
            menu_str = " File  Edit  View [RUN ] Debug  Options" if not run_mode else " File  Edit  View [STOP] Debug  Options"
            write_at(stdscr, 0, 0, menu_str + " " * max(0, curses.COLS - len(menu_str)), C['handle'])
            
            tools.draw(stdscr, C, box_chars)
            
            for win in windows:
                draw_window(stdscr, win, C, box_chars, -1)
            
            stdscr.refresh()
            last_draw = current_time

        ch = stdscr.getch()
        
        if ch == 27:
            break
        elif ch == ord('r') or ch == ord('R'):
            if not run_mode:
                run_mode = True
                run_globals = {'__msg__': None}
                run_globals['msgbox'] = msgbox
                run_globals['inputbox'] = inputbox
                run_globals['file_dialog'] = file_dialog
                run_globals['open_file'] = file_io.open_file
                run_globals['read_line'] = file_io.read_line
                run_globals['read_all'] = file_io.read_all
                run_globals['write_line'] = file_io.write_line
                run_globals['close_file'] = file_io.close_file
                run_globals['file_exists'] = file_io.file_exists
                run_globals['clipboard_copy'] = clipboard_copy
                run_globals['clipboard_paste'] = clipboard_paste
                run_globals['clipboard_clear'] = clipboard_clear
                run_globals['print_text'] = print_text
                
                for w in windows:
                    for c in w.controls:
                        run_globals[c.name_id] = c
                
                result = msgbox("Welcome to v2.1.0!\nFeatures:\n- File I/O\n- Dialogs\n- Grid Control\n- Clipboard\n- Print", "v2.1.0", "ok")
            else:
                file_io.close_all()
                run_mode = False
        elif ch == ord('t') or ch == ord('T'):
            result = msgbox("Test message box\nWith multiple lines", "Test", "yesno")
            if result == 'yes':
                text = inputbox("Enter something:", "Input", "default")
                msgbox(f"You entered: {text}", "Result", "ok")
        
        time.sleep(0.01)

    if TERM.has_mouse:
        print('\033[?1003l', end='', flush=True)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nExiting...")
