#!/usr/bin/env python3
"""
Print Module for VB1-DOS Clone v2.1.0
Text-based printing with pagination and formatting
"""

import subprocess
import os
import tempfile
import datetime

class PrintManager:
    """
    Text-based printing manager for terminal applications
    Generates formatted output suitable for lp/lpr
    """
    
    def __init__(self):
        self.page_width = 80
        self.page_height = 66  # 66 lines per page (standard)
        self.left_margin = 5
        self.right_margin = 5
        self.top_margin = 3
        self.bottom_margin = 3
        self.orientation = "portrait"  # or "landscape"
        self.header_text = ""
        self.footer_text = ""
        self.page_number = 1
    
    def set_page_setup(self, width=80, height=66, left=5, right=5, top=3, bottom=3, orientation="portrait"):
        """Configure page setup"""
        self.page_width = width
        self.page_height = height
        self.left_margin = left
        self.right_margin = right
        self.top_margin = top
        self.bottom_margin = bottom
        self.orientation = orientation
    
    def format_text(self, text, title="", add_header=True, add_footer=True):
        """
        Format text for printing with margins and pagination
        Returns list of pages (each page is a list of lines)
        """
        content_width = self.page_width - self.left_margin - self.right_margin
        content_height = self.page_height - self.top_margin - self.bottom_margin
        
        # Split text into lines
        if isinstance(text, list):
            lines = text
        else:
            lines = text.split('\n')
        
        # Wrap lines to content width
        wrapped_lines = []
        for line in lines:
            while len(line) > content_width:
                wrapped_lines.append(line[:content_width])
                line = line[content_width:]
            wrapped_lines.append(line)
        
        # Paginate
        pages = []
        current_page = []
        line_count = 0
        
        for line in wrapped_lines:
            if line_count >= content_height:
                # Start new page
                pages.append(current_page)
                current_page = []
                line_count = 0
            
            current_page.append(line)
            line_count += 1
        
        # Add last page
        if current_page:
            pages.append(current_page)
        
        # Add headers and footers
        formatted_pages = []
        for i, page in enumerate(pages):
            formatted_page = []
            
            # Top margin
            for _ in range(self.top_margin):
                formatted_page.append("")
            
            # Header
            if add_header:
                header = self._make_header(title, i + 1, len(pages))
                formatted_page.append(" " * self.left_margin + header)
                formatted_page.append("")  # Blank line after header
            
            # Content with left margin
            for line in page:
                formatted_line = " " * self.left_margin + line.ljust(content_width)
                formatted_page.append(formatted_line)
            
            # Fill remaining space to footer
            content_lines = len(page) + (2 if add_header else 0)
            remaining = content_height - content_lines
            for _ in range(remaining):
                formatted_page.append(" " * self.left_margin + " " * content_width)
            
            # Footer
            if add_footer:
                footer = self._make_footer(i + 1, len(pages))
                formatted_page.append("")
                formatted_page.append(" " * self.left_margin + footer)
            
            # Bottom margin
            for _ in range(self.bottom_margin):
                formatted_page.append("")
            
            formatted_pages.append(formatted_page)
        
        return formatted_pages
    
    def _make_header(self, title, page_num, total_pages):
        """Create page header"""
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        if title:
            header = f"{title[:30]:<30} {date_str:>20}"
        else:
            header = f"{'':<30} {date_str:>20}"
        return header[:self.page_width - self.left_margin - self.right_margin]
    
    def _make_footer(self, page_num, total_pages):
        """Create page footer"""
        footer = f"Page {page_num} of {total_pages}"
        return footer.center(self.page_width - self.left_margin - self.right_margin)
    
    def print_text(self, text, title="", printer=None, to_file=None):
        """
        Print text content
        - text: content to print
        - title: document title
        - printer: printer name (None for default)
        - to_file: filename to save to instead of printing
        Returns True if successful
        """
        pages = self.format_text(text, title)
        return self._send_to_printer(pages, printer, to_file)
    
    def print_form(self, form, title="", printer=None, to_file=None):
        """
        Print a form with all its controls
        - form: Window object
        - title: document title
        """
        lines = []
        lines.append("=" * 70)
        lines.append(f"FORM: {form.title}")
        lines.append("=" * 70)
        lines.append("")
        
        # Print controls
        for ctrl in form.controls:
            lines.append(f"Control: {ctrl.name_id} (Type {ctrl.tool_type})")
            lines.append(f"  Position: ({ctrl.x}, {ctrl.y})")
            lines.append(f"  Size: {ctrl.w} x {ctrl.h}")
            lines.append(f"  Caption: {ctrl.caption}")
            lines.append(f"  Value: {ctrl.caption if not ctrl.checked else '[X]'}")
            lines.append("")
        
        lines.append("=" * 70)
        lines.append(f"Generated: {datetime.datetime.now()}")
        lines.append("=" * 70)
        
        pages = self.format_text(lines, title or form.title)
        return self._send_to_printer(pages, printer, to_file)
    
    def _send_to_printer(self, pages, printer=None, to_file=None):
        """Send formatted pages to printer or file"""
        # Flatten pages
        all_lines = []
        for page in pages:
            all_lines.extend(page)
            all_lines.append("\f")  # Form feed between pages
        
        # Remove last form feed
        if all_lines:
            all_lines.pop()
        
        text = '\n'.join(all_lines)
        
        if to_file:
            # Save to file
            try:
                with open(to_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                return True
            except Exception as e:
                print(f"Error saving to file: {e}")
                return False
        
        # Send to printer
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(text)
                temp_file = f.name
            
            # Use lp or lpr
            cmd = ["lp"] if self._command_exists("lp") else ["lpr"]
            if printer:
                cmd.extend(["-d", printer])
            cmd.append(temp_file)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temp file
            os.unlink(temp_file)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Print error: {e}")
            # Fallback: save to print.txt
            try:
                with open("print_output.txt", 'w') as f:
                    f.write(text)
                print("Saved to print_output.txt")
                return True
            except:
                return False
    
    def _command_exists(self, cmd):
        """Check if command exists"""
        try:
            subprocess.run(["which", cmd], capture_output=True, check=True)
            return True
        except:
            return False
    
    def get_printers(self):
        """Get list of available printers"""
        printers = []
        try:
            result = subprocess.run(["lpstat", "-p"], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if line.startswith("printer"):
                    parts = line.split()
                    if len(parts) >= 2:
                        printers.append(parts[1])
        except:
            pass
        return printers


# Global print manager
_print_manager = None

def get_print_manager():
    global _print_manager
    if _print_manager is None:
        _print_manager = PrintManager()
    return _print_manager

# Runtime functions
def print_text(text, title="", printer=None, to_file=None):
    return get_print_manager().print_text(text, title, printer, to_file)

def print_form(form, title="", printer=None, to_file=None):
    return get_print_manager().print_form(form, title, printer, to_file)

def print_preview(text, title="", stdscr=None, colors=None):
    """
    Show print preview in a dialog
    Requires curses window and colors dict
    """
    if stdscr is None or colors is None:
        return False
    
    pm = get_print_manager()
    pages = pm.format_text(text, title)
    
    current_page = 0
    
    def draw_preview():
        C_BORDER = colors['border']
        C_BG = colors['bg']
        
        page = pages[current_page]
        
        # Calculate display area
        start_y = 2
        start_x = 2
        height = len(page) + 4
        width = pm.page_width + 4
        
        # Center on screen
        y = max(0, (curses.LINES - height) // 2)
        x = max(0, (curses.COLS - width) // 2)
        
        # Draw border
        write_at(stdscr, x, y, '+' + '-' * (width - 2) + '+', C_BORDER)
        for i in range(1, height - 1):
            write_at(stdscr, x, y + i, '|', C_BORDER)
            write_at(stdscr, x + width - 1, y + i, '|', C_BORDER)
        write_at(stdscr, x, y + height - 1, '+' + '-' * (width - 2) + '+', C_BORDER)
        
        # Title
        title_text = f" Print Preview - Page {current_page + 1}/{len(pages)} "
        write_at(stdscr, x + (width - len(title_text)) // 2, y, title_text, C_BORDER)
        
        # Page content
        for i, line in enumerate(page):
            write_at(stdscr, x + 2, y + 2 + i, line[:width-4], C_BG)
        
        # Instructions
        hint = "[PgUp/PgDn=Navigate, P=Print, S=Save, Q=Quit]"
        write_at(stdscr, x + (width - len(hint)) // 2, y + height - 2, hint, C_BORDER)
        
        stdscr.refresh()
    
    def write_at(stdscr, x, y, text, attr=0):
        try:
            if y >= 0 and x >= 0:
                stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass
    
    while True:
        draw_preview()
        ch = stdscr.getch()
        
        if ch == ord('q') or ch == ord('Q') or ch == 27:
            return None
        elif ch == curses.KEY_PPAGE and current_page > 0:
            current_page -= 1
        elif ch == curses.KEY_NPAGE and current_page < len(pages) - 1:
            current_page += 1
        elif ch == ord('p') or ch == ord('P'):
            return "print"
        elif ch == ord('s') or ch == ord('S'):
            return "save"
        
        time.sleep(0.01)

def page_setup_dialog(stdscr, colors):
    """Show page setup dialog"""
    C_BORDER = colors['border']
    C_BG = colors['bg']
    C_ACTIVE = colors['active_tool']
    
    pm = get_print_manager()
    
    # Current settings
    width = pm.page_width
    height = pm.page_height
    left = pm.left_margin
    right = pm.right_margin
    top = pm.top_margin
    bottom = pm.bottom_margin
    
    selected = 0
    options = [
        ("Page Width", width, 40, 132),
        ("Page Height", height, 40, 100),
        ("Left Margin", left, 0, 20),
        ("Right Margin", right, 0, 20),
        ("Top Margin", top, 0, 10),
        ("Bottom Margin", bottom, 0, 10),
    ]
    
    def draw_dialog():
        w = 50
        h = 16
        x = max(0, (curses.COLS - w) // 2)
        y = max(0, (curses.LINES - h) // 2)
        
        write_at(stdscr, x, y, '+' + '-' * (w - 2) + '+', C_BORDER)
        for i in range(1, h - 1):
            write_at(stdscr, x, y + i, '|', C_BORDER)
            write_at(stdscr, x + 1, y + i, ' ' * (w - 2), C_BG)
            write_at(stdscr, x + w - 1, y + i, '|', C_BORDER)
        write_at(stdscr, x, y + h - 1, '+' + '-' * (w - 2) + '+', C_BORDER)
        
        title = " Page Setup "
        write_at(stdscr, x + (w - len(title)) // 2, y, title, C_BORDER)
        
        for i, (label, value, min_val, max_val) in enumerate(options):
            attr = C_ACTIVE if i == selected else C_BG
            prefix = '> ' if i == selected else '  '
            text = f"{prefix}{label}: {value}"
            write_at(stdscr, x + 5, y + 2 + i, text, attr)
        
        hint = "[Arrows=Navigate, +/-=Change, Enter=OK, Q=Cancel]"
        write_at(stdscr, x + 2, y + h - 2, hint, C_BORDER)
        
        stdscr.refresh()
    
    def write_at(stdscr, x, y, text, attr=0):
        try:
            if y >= 0 and x >= 0:
                stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass
    
    while True:
        draw_dialog()
        ch = stdscr.getch()
        
        if ch == 27 or ch == ord('q') or ch == ord('Q'):
            return False
        elif ch == curses.KEY_UP and selected > 0:
            selected -= 1
        elif ch == curses.KEY_DOWN and selected < len(options) - 1:
            selected += 1
        elif ch == ord('+') or ch == ord('='):
            label, value, min_val, max_val = options[selected]
            if value < max_val:
                options[selected] = (label, value + 1, min_val, max_val)
        elif ch == ord('-'):
            label, value, min_val, max_val = options[selected]
            if value > min_val:
                options[selected] = (label, value - 1, min_val, max_val)
        elif ch in (10, 13, curses.KEY_ENTER):
            # Apply settings
            pm.page_width = options[0][1]
            pm.page_height = options[1][1]
            pm.left_margin = options[2][1]
            pm.right_margin = options[3][1]
            pm.top_margin = options[4][1]
            pm.bottom_margin = options[5][1]
            return True
        
        time.sleep(0.01)


# Test
if __name__ == "__main__":
    print("Print Module Test")
    print("=" * 50)
    
    pm = get_print_manager()
    
    # Test text
    sample_text = """
This is a sample document for testing the print functionality.

It includes multiple lines and should be properly formatted
with margins, headers, and footers when printed.

Features:
- Page setup configuration
- Automatic pagination
- Headers and footers
- Margin support
- Print to file or printer
""".strip()
    
    # Test formatting
    print("Formatting text...")
    pages = pm.format_text(sample_text, "Test Document")
    print(f"Generated {len(pages)} pages")
    
    # Show first page
    if pages:
        print("\nFirst page preview:")
        print("-" * 40)
        for line in pages[0][:20]:  # First 20 lines
            print(line)
        print("-" * 40)
    
    # Test print to file
    print("\nSaving to test_print.txt...")
    result = print_text(sample_text, "Test Document", to_file="test_print.txt")
    print(f"Result: {'Success' if result else 'Failed'}")
