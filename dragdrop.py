#!/usr/bin/env python3
"""
Drag and Drop System for VB1-DOS Clone v2.1.0
Supports dragging between controls with visual feedback
"""

import curses
import time

class DragDropManager:
    """
    Manages drag and drop operations between controls
    """
    
    # Drag data formats
    FORMAT_TEXT = "text/plain"
    FORMAT_LIST_ITEM = "text/list-item"
    FORMAT_FILE = "text/uri-list"
    FORMAT_CONTROL = "text/control-ref"
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.dragging = False
        self.drag_data = None
        self.drag_format = None
        self.drag_source = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.current_x = 0
        self.current_y = 0
        self.drop_targets = []
        self.valid_targets = []
        self.ghost_image = None
        
        # Event handlers
        self.on_drag_start = None
        self.on_drag_over = None
        self.on_drop = None
    
    def start_drag(self, x, y, data, data_format, source):
        """
        Start a drag operation
        - x, y: starting position
        - data: the data being dragged
        - data_format: format of the data
        - source: source control reference
        """
        self.dragging = True
        self.drag_start_x = x
        self.drag_start_y = y
        self.current_x = x
        self.current_y = y
        self.drag_data = data
        self.drag_format = data_format
        self.drag_source = source
        
        # Create ghost image
        self._create_ghost_image()
        
        # Find valid drop targets
        self._find_valid_targets()
        
        # Fire drag start event
        if self.on_drag_start:
            self.on_drag_start(self.drag_source, self.drag_data, self.drag_format)
        
        return True
    
    def update_drag(self, x, y):
        """Update drag position"""
        if not self.dragging:
            return
        
        self.current_x = x
        self.current_y = y
        
        # Check if over valid target
        target = self._get_target_at(x, y)
        
        # Fire drag over event
        if self.on_drag_over:
            self.on_drag_over(target, self.drag_data, self.drag_format)
    
    def end_drag(self, x, y):
        """
        End drag operation (drop)
        Returns True if dropped on valid target, False otherwise
        """
        if not self.dragging:
            return False
        
        self.dragging = False
        
        # Find drop target
        target = self._get_target_at(x, y)
        
        # Check if target accepts this data format
        if target and self._is_valid_target(target):
            # Fire drop event
            if self.on_drop:
                self.on_drop(target, self.drag_source, self.drag_data, self.drag_format)
            
            self._cleanup()
            return True
        
        self._cleanup()
        return False
    
    def cancel_drag(self):
        """Cancel ongoing drag operation"""
        self.dragging = False
        self._cleanup()
    
    def _create_ghost_image(self):
        """Create ghost image of dragged item"""
        if self.drag_format == self.FORMAT_TEXT:
            text = str(self.drag_data)[:20]  # Truncate for display
            self.ghost_image = f"[{text}]"
        elif self.drag_format == self.FORMAT_LIST_ITEM:
            self.ghost_image = f"[* {self.drag_data}]"
        elif self.drag_format == self.FORMAT_FILE:
            filename = self.drag_data.split('/')[-1] if '/' in self.drag_data else self.drag_data
            self.ghost_image = f"[📄 {filename[:15]}]"
        else:
            self.ghost_image = "[...]"
    
    def _find_valid_targets(self):
        """Find all valid drop targets for current drag data"""
        self.valid_targets = []
        # This would be populated based on form controls
        # For now, we'll check during drop
    
    def _get_target_at(self, x, y):
        """Get control at position (x, y)"""
        # This would check form controls
        # Returns control reference or None
        return None
    
    def _is_valid_target(self, target):
        """Check if target accepts the current drag format"""
        # Check target's accepted formats
        accepted_formats = getattr(target, 'accepted_drop_formats', [])
        return self.drag_format in accepted_formats
    
    def _cleanup(self):
        """Clean up drag state"""
        self.drag_data = None
        self.drag_format = None
        self.drag_source = None
        self.ghost_image = None
        self.valid_targets = []
    
    def draw_ghost(self, colors):
        """Draw ghost image at current position"""
        if not self.dragging or not self.ghost_image:
            return
        
        try:
            # Draw ghost with transparency effect
            attr = colors.get('active_tool', curses.A_BOLD) | curses.A_DIM
            self.stdscr.addstr(self.current_y, self.current_x, self.ghost_image, attr)
        except curses.error:
            pass
    
    def draw_drop_indicators(self, colors):
        """Draw indicators on valid drop targets"""
        if not self.dragging:
            return
        
        C_ACTIVE = colors.get('active_tool', curses.A_BOLD)
        
        for target in self.valid_targets:
            if self._is_valid_target(target):
                # Draw highlight border around valid target
                try:
                    # This would draw around the control
                    pass
                except:
                    pass


class DraggableControl:
    """
    Mixin for controls that support drag operations
    """
    
    def __init__(self):
        self.draggable = False
        self.drag_data_format = None
        self.accepted_drop_formats = []
        self.on_drag_start = None
        self.on_drop = None
    
    def enable_drag(self, data_format):
        """Enable dragging from this control"""
        self.draggable = True
        self.drag_data_format = data_format
    
    def enable_drop(self, formats):
        """Enable dropping onto this control"""
        if isinstance(formats, str):
            self.accepted_drop_formats = [formats]
        else:
            self.accepted_drop_formats = formats
    
    def get_drag_data(self):
        """Get data to drag - override in subclass"""
        return None
    
    def handle_drop(self, data, data_format, source):
        """Handle dropped data - override in subclass"""
        if self.on_drop:
            self.on_drop(data, data_format, source)
        return True


class DraggableListBox(DraggableControl):
    """List Box with drag support"""
    
    def __init__(self, control):
        DraggableControl.__init__(self)
        self.control = control
        self.enable_drag(DragDropManager.FORMAT_LIST_ITEM)
        self.enable_drop([DragDropManager.FORMAT_LIST_ITEM])
    
    def get_drag_data(self, index):
        """Get item at index as drag data"""
        if 0 <= index < len(self.control.items):
            return {
                'index': index,
                'text': self.control.items[index],
                'control': self.control.name_id
            }
        return None
    
    def handle_drop(self, data, data_format, source):
        """Handle drop - add item to list"""
        if data_format == DragDropManager.FORMAT_LIST_ITEM:
            if isinstance(data, dict) and 'text' in data:
                self.control.items.append(data['text'])
                return True
        return False


class DraggableTextBox(DraggableControl):
    """Text Box with drag/drop support"""
    
    def __init__(self, control):
        DraggableControl.__init__(self)
        self.control = control
        self.enable_drag(DragDropManager.FORMAT_TEXT)
        self.enable_drop([DragDropManager.FORMAT_TEXT, DragDropManager.FORMAT_LIST_ITEM])
    
    def get_drag_data(self):
        """Get current text as drag data"""
        return self.control.caption
    
    def handle_drop(self, data, data_format, source):
        """Handle drop - set text or append"""
        if data_format == DragDropManager.FORMAT_TEXT:
            self.control.caption = str(data)
            return True
        elif data_format == DragDropManager.FORMAT_LIST_ITEM:
            if isinstance(data, dict) and 'text' in data:
                self.control.caption = data['text']
                return True
        return False


def draw_drag_feedback(stdscr, drag_manager, colors, box_chars):
    """
    Draw visual feedback for drag and drop
    Call this during main render loop
    """
    if not drag_manager.dragging:
        return
    
    # Draw ghost image
    drag_manager.draw_ghost(colors)
    
    # Draw drop indicators
    drag_manager.draw_drop_indicators(colors)
    
    # Draw connection line from source to current position
    try:
        C_DIM = colors.get('comment', curses.A_DIM)
        
        # Simple line drawing
        x1 = drag_manager.drag_start_x
        y1 = drag_manager.drag_start_y
        x2 = drag_manager.current_x
        y2 = drag_manager.current_y
        
        # Draw dashed line
        steps = max(abs(x2 - x1), abs(y2 - y1))
        if steps > 0:
            for i in range(0, steps, 2):
                x = int(x1 + (x2 - x1) * i / steps)
                y = int(y1 + (y2 - y1) * i / steps)
                try:
                    stdscr.addstr(y, x, "·", C_DIM)
                except:
                    pass
    except:
        pass


def create_drag_source_handler(control, drag_manager, get_data_func):
    """
    Create mouse handler for drag source
    """
    def handler(mx, my, button):
        if button == 1:  # Left button
            data = get_data_func()
            if data:
                return drag_manager.start_drag(mx, my, data, control.drag_data_format, control)
        return False
    return handler


def create_drop_target_handler(control, drag_manager, accept_func):
    """
    Create mouse handler for drop target
    """
    def handler(mx, my, button):
        if button == 1 and drag_manager.dragging:  # Drop on release
            if drag_manager.end_drag(mx, my):
                return accept_func(drag_manager.drag_data, drag_manager.drag_format)
        return False
    return handler


# Test
if __name__ == "__main__":
    def main(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        
        colors = {
            'border': curses.A_BOLD,
            'bg': 0,
            'active_tool': curses.A_BOLD | curses.A_REVERSE,
            'comment': curses.A_DIM
        }
        
        # Create drag manager
        drag_mgr = DragDropManager(stdscr)
        
        # Test drag
        drag_mgr.start_drag(10, 10, "Test Item", DragDropManager.FORMAT_TEXT, None)
        
        running = True
        while running:
            stdscr.clear()
            
            # Update drag
            drag_mgr.update_drag(15, 12)
            
            # Draw
            draw_drag_feedback(stdscr, drag_mgr, colors, {})
            
            stdscr.addstr(0, 0, "Drag and Drop Test - Press Q to quit")
            stdscr.refresh()
            
            ch = stdscr.getch()
            if ch == ord('q') or ch == ord('Q'):
                running = False
            elif ch == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                    if bstate & curses.BUTTON1_RELEASED:
                        drag_mgr.end_drag(mx, my)
                except:
                    pass
            
            time.sleep(0.05)
    
    curses.wrapper(main)
