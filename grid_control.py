#!/usr/bin/env python3
"""
Grid Control Implementation for VB1-DOS Clone v2.1.0
Type 16 - Spreadsheet-like data grid
"""

class GridControl:
    """
    Grid control for tabular data display and editing.
    Supports configurable rows/columns, sorting, selection modes,
    and cell editing.
    """
    
    def __init__(self, name_id="grid1", x=1, y=1, w=40, h=10):
        self.name_id = name_id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        
        # Grid dimensions
        self.row_count = 5
        self.col_count = 3
        
        # Data storage
        self.headers = ["Column 1", "Column 2", "Column 3"]
        self.data = []  # 2D list: data[row][col]
        self.col_widths = [12, 12, 12]
        
        # Scroll position
        self.scroll_row = 0
        self.scroll_col = 0
        
        # Selection
        self.selected_cell = (0, 0)  # (row, col)
        self.selected_range = None   # (r1, c1, r2, c2) for multi-select
        
        # Sorting
        self.sort_col = -1
        self.sort_asc = True
        
        # Editing
        self.edit_mode = False
        self.edit_buffer = ""
        
        # Initialize with sample data
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialize with sample data"""
        self.data = []
        for r in range(self.row_count):
            row = [f"R{r+1}C{c+1}" for c in range(self.col_count)]
            self.data.append(row)
    
    def set_data(self, data, headers=None):
        """Set grid data from 2D list"""
        self.data = [row[:] for row in data]  # Deep copy
        self.row_count = len(data)
        if data:
            self.col_count = len(data[0])
        if headers:
            self.headers = headers[:self.col_count]
            # Pad headers if needed
            while len(self.headers) < self.col_count:
                self.headers.append(f"Col{len(self.headers)+1}")
    
    def get_data(self):
        """Get grid data as 2D list"""
        return [row[:] for row in self.data]
    
    def get_cell(self, row, col):
        """Get cell value"""
        if 0 <= row < self.row_count and 0 <= col < self.col_count:
            return self.data[row][col]
        return ""
    
    def set_cell(self, row, col, value):
        """Set cell value"""
        if 0 <= row < self.row_count and 0 <= col < self.col_count:
            self.data[row][col] = str(value)
            return True
        return False
    
    def add_row(self, row_data=None):
        """Add a new row"""
        if row_data is None:
            row_data = [""] * self.col_count
        self.data.append(row_data[:self.col_count])
        self.row_count += 1
    
    def delete_row(self, row):
        """Delete a row"""
        if 0 <= row < self.row_count:
            del self.data[row]
            self.row_count -= 1
            # Adjust selection
            if self.selected_cell[0] >= self.row_count:
                self.selected_cell = (max(0, self.row_count-1), self.selected_cell[1])
    
    def add_column(self, header="New Col", width=10, default_value=""):
        """Add a new column"""
        self.headers.append(header)
        self.col_widths.append(width)
        for row in self.data:
            row.append(default_value)
        self.col_count += 1
    
    def delete_column(self, col):
        """Delete a column"""
        if 0 <= col < self.col_count:
            del self.headers[col]
            del self.col_widths[col]
            for row in self.data:
                del row[col]
            self.col_count -= 1
    
    def sort_by_column(self, col):
        """Sort data by column"""
        if 0 <= col < self.col_count:
            if self.sort_col == col:
                # Toggle direction
                self.sort_asc = not self.sort_asc
            else:
                self.sort_col = col
                self.sort_asc = True
            
            # Perform sort
            reverse = not self.sort_asc
            try:
                # Try numeric sort first
                self.data.sort(key=lambda row: float(row[col]) if row[col].replace('.','').replace('-','').isdigit() else row[col], 
                              reverse=reverse)
            except:
                # Fall back to string sort
                self.data.sort(key=lambda row: str(row[col]), reverse=reverse)
    
    def move_selection(self, d_row, d_col):
        """Move selection by delta"""
        new_row = max(0, min(self.row_count - 1, self.selected_cell[0] + d_row))
        new_col = max(0, min(self.col_count - 1, self.selected_cell[1] + d_col))
        self.selected_cell = (new_row, new_col)
        
        # Auto-scroll to keep selection visible
        self._ensure_visible(new_row, new_col)
    
    def _ensure_visible(self, row, col):
        """Ensure cell is visible, scroll if needed"""
        header_height = 3  # Border + header + separator
        
        # Vertical scroll
        visible_rows = self.h - header_height - 1
        if row < self.scroll_row:
            self.scroll_row = row
        elif row >= self.scroll_row + visible_rows:
            self.scroll_row = row - visible_rows + 1
        
        # Horizontal scroll
        visible_cols = self._calc_visible_cols()
        if col < self.scroll_col:
            self.scroll_col = col
        elif col >= self.scroll_col + visible_cols:
            self.scroll_col = col - visible_cols + 1
    
    def _calc_visible_cols(self):
        """Calculate number of visible columns"""
        total_width = 1  # Left border
        count = 0
        for col in range(self.scroll_col, self.col_count):
            total_width += self.col_widths[col]
            if total_width >= self.w - 1:  # -1 for right border
                break
            count += 1
        return max(1, count)
    
    def start_edit(self):
        """Start editing current cell"""
        row, col = self.selected_cell
        if 0 <= row < self.row_count and 0 <= col < self.col_count:
            self.edit_mode = True
            self.edit_buffer = str(self.data[row][col])
            return True
        return False
    
    def commit_edit(self):
        """Commit edit to cell"""
        if self.edit_mode:
            row, col = self.selected_cell
            self.data[row][col] = self.edit_buffer
            self.edit_mode = False
            self.edit_buffer = ""
    
    def cancel_edit(self):
        """Cancel editing"""
        self.edit_mode = False
        self.edit_buffer = ""
    
    def handle_key(self, key):
        """Handle keyboard input"""
        if self.edit_mode:
            if key in (10, 13):  # Enter
                self.commit_edit()
            elif key == 27:  # Escape
                self.cancel_edit()
            elif key in (8, 127):  # Backspace
                self.edit_buffer = self.edit_buffer[:-1]
            elif 32 <= key <= 126:  # Printable
                self.edit_buffer += chr(key)
            return True
        
        # Navigation mode
        if key == curses.KEY_UP:
            self.move_selection(-1, 0)
        elif key == curses.KEY_DOWN:
            self.move_selection(1, 0)
        elif key == curses.KEY_LEFT:
            self.move_selection(0, -1)
        elif key == curses.KEY_RIGHT:
            self.move_selection(0, 1)
        elif key == curses.KEY_HOME:
            self.selected_cell = (self.selected_cell[0], 0)
        elif key == curses.KEY_END:
            self.selected_cell = (self.selected_cell[0], self.col_count - 1)
        elif key == curses.KEY_PPAGE:  # Page Up
            visible_rows = self.h - 4
            self.move_selection(-visible_rows, 0)
        elif key == curses.KEY_NPAGE:  # Page Down
            visible_rows = self.h - 4
            self.move_selection(visible_rows, 0)
        elif key in (10, 13):  # Enter to edit
            self.start_edit()
        elif key == ord('\t'):  # Tab
            if self.selected_cell[1] < self.col_count - 1:
                self.move_selection(0, 1)
            else:
                self.selected_cell = (self.selected_cell[0] + 1, 0)
                self._ensure_visible(self.selected_cell[0], self.selected_cell[1])
        else:
            return False
        return True
    
    def load_from_file(self, filename, delimiter=","):
        """Load grid data from CSV file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                return False
            
            # Parse header
            self.headers = lines[0].strip().split(delimiter)
            self.col_count = len(self.headers)
            
            # Parse data
            self.data = []
            for line in lines[1:]:
                row = line.strip().split(delimiter)
                # Pad or truncate to match column count
                while len(row) < self.col_count:
                    row.append("")
                self.data.append(row[:self.col_count])
            
            self.row_count = len(self.data)
            
            # Set default column widths
            self.col_widths = [max(8, len(h) + 2) for h in self.headers]
            
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def save_to_file(self, filename, delimiter=","):
        """Save grid data to CSV file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Write header
                f.write(delimiter.join(self.headers) + '\n')
                # Write data
                for row in self.data:
                    f.write(delimiter.join(str(cell) for cell in row) + '\n')
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False


# Example usage and test
if __name__ == "__main__":
    import curses
    
    def draw_box(stdscr, y, x, h, w, title=""):
        """Draw a box with optional title"""
        try:
            stdscr.addstr(y, x, '+' + '-' * (w - 2) + '+')
            for i in range(1, h - 1):
                stdscr.addstr(y + i, x, '|')
                stdscr.addstr(y + i, x + w - 1, '|')
            stdscr.addstr(y + h - 1, x, '+' + '-' * (w - 2) + '+')
            if title:
                stdscr.addstr(y, x + 2, f" {title} ")
        except curses.error:
            pass
    
    def draw_grid_curses(stdscr, grid, offset_y=5, offset_x=5):
        """Draw grid using curses"""
        # Draw outer box
        draw_box(stdscr, offset_y, offset_x, grid.h, grid.w, "Data Grid")
        
        # Draw headers
        header_y = offset_y + 1
        curr_x = offset_x + 1
        for col in range(grid.scroll_col, min(grid.col_count, grid.scroll_col + len(grid.col_widths))):
            if col < len(grid.headers):
                header = grid.headers[col][:grid.col_widths[col]-1].center(grid.col_widths[col]-1)
                attr = curses.A_BOLD | curses.A_UNDERLINE if col == grid.sort_col else 0
                try:
                    stdscr.addstr(header_y, curr_x, header, attr)
                except:
                    pass
                curr_x += grid.col_widths[col]
        
        # Draw separator
        sep_y = offset_y + 2
        try:
            stdscr.addstr(sep_y, offset_x, '+' + '-' * (grid.w - 2) + '+')
        except:
            pass
        
        # Draw data
        visible_rows = grid.h - 4
        for row_idx in range(grid.scroll_row, min(grid.row_count, grid.scroll_row + visible_rows)):
            row_y = offset_y + 3 + (row_idx - grid.scroll_row)
            curr_x = offset_x + 1
            
            for col_idx in range(grid.scroll_col, grid.col_count):
                if col_idx < len(grid.col_widths):
                    width = grid.col_widths[col_idx]
                    value = str(grid.data[row_idx][col_idx]) if col_idx < len(grid.data[row_idx]) else ""
                    
                    # Truncate
                    if len(value) > width - 1:
                        value = value[:width-2] + ".."
                    else:
                        value = value.ljust(width - 1)
                    
                    # Highlight selected
                    is_selected = (row_idx == grid.selected_cell[0] and 
                                  col_idx == grid.selected_cell[1])
                    attr = curses.A_REVERSE if is_selected else 0
                    
                    try:
                        stdscr.addstr(row_y, curr_x, value, attr)
                    except:
                        pass
                    
                    curr_x += width
    
    def main(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        
        # Create grid
        grid = GridControl("grid1", 1, 1, 50, 12)
        grid.set_data([
            ["Alice", "25", "Engineer"],
            ["Bob", "30", "Designer"],
            ["Charlie", "35", "Manager"],
            ["Diana", "28", "Developer"],
            ["Eve", "32", "Analyst"]
        ], ["Name", "Age", "Job"])
        
        # Main loop
        while True:
            stdscr.clear()
            
            # Draw instructions
            stdscr.addstr(1, 2, "Grid Control Test - v2.1.0", curses.A_BOLD)
            stdscr.addstr(2, 2, "Arrow keys: Navigate | Enter: Edit | S: Sort | Q: Quit")
            
            # Draw grid
            draw_grid_curses(stdscr, grid)
            
            # Show current cell
            row, col = grid.selected_cell
            cell_val = grid.get_cell(row, col)
            stdscr.addstr(18, 2, f"Selected: ({row}, {col}) = '{cell_val}'    ")
            
            # Show edit mode
            if grid.edit_mode:
                stdscr.addstr(19, 2, f"EDIT MODE: {grid.edit_buffer}_    ")
            
            stdscr.refresh()
            
            # Handle input
            ch = stdscr.getch()
            if ch == ord('q') or ch == ord('Q'):
                break
            elif ch == ord('s') or ch == ord('S'):
                grid.sort_by_column(grid.selected_cell[1])
            elif ch == ord('a'):
                grid.add_row()
            elif ch == ord('d'):
                grid.delete_row(grid.selected_cell[0])
            else:
                grid.handle_key(ch)
            
            time.sleep(0.01)
    
    import time
    curses.wrapper(main)
