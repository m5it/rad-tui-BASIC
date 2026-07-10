"""
Splitter Control Module for RAD-TUI v2.2.0
Provides resizable panel divider for complex layouts
"""

class Splitter:
    """Splitter control for resizable panels"""
    
    TOOL_TYPE = 23
    
    # Orientations
    HORIZONTAL = 0  # Divides vertically, moves horizontally
    VERTICAL = 1    # Divides horizontally, moves vertically
    
    def __init__(self, name_id="splitter1", x=0, y=0, width=1, height=10):
        self.name_id = name_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Orientation
        self.orientation = self.VERTICAL
        
        # Position (0.0 to 1.0 for percentage, or pixel position)
        self.position = 0.5  # 50% by default
        self.use_percentage = True
        
        # Constraints
        self.min_position = 0.1   # Minimum 10%
        self.max_position = 0.9   # Maximum 90%
        self.min_pixels = 5       # Minimum pixels
        
        # Appearance
        self.splitter_char = "\u2502"  # Vertical bar for vertical splitter
        self.splitter_char_h = "\u2500"  # Horizontal bar for horizontal
        self.handle_char = "\u254B"      # Cross for handle
        
        # Events
        self.on_splitter_moving = None   # During drag
        self.on_splitter_moved = None    # After release
        
        # State
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_start_position = 0
        
        # Associated panels (optional references)
        self.panel1 = None  # Left or top panel
        self.panel2 = None  # Right or bottom panel
        
    def set_orientation(self, orientation):
        """Set splitter orientation"""
        self.orientation = orientation
        
        # Adjust dimensions
        if orientation == self.HORIZONTAL:
            self.width = max(self.width, 3)  # Wider for horizontal
            self.height = 1
        else:
            self.width = 1
            self.height = max(self.height, 3)
            
    def set_position(self, position):
        """Set splitter position"""
        if self.use_percentage:
            self.position = max(self.min_position, min(position, self.max_position))
        else:
            max_pixels = self._get_max_pixels()
            self.position = max(self.min_pixels, min(position, max_pixels - self.min_pixels))
            
        self._update_panels()
        
    def get_position(self):
        """Get current position"""
        if self.use_percentage:
            return self.position
        else:
            return self.position
            
    def get_pixel_position(self):
        """Get position in pixels"""
        if self.use_percentage:
            max_pixels = self._get_max_pixels()
            return int(self.position * max_pixels)
        else:
            return int(self.position)
            
    def _get_max_pixels(self):
        """Get maximum pixel position"""
        if self.orientation == self.HORIZONTAL:
            return self.width
        else:
            return self.height
            
    def set_min_size(self, min_size):
        """Set minimum panel size in pixels"""
        self.min_pixels = min_size
        
    def set_range(self, min_pos, max_pos):
        """Set position range (0.0-1.0 for percentage)"""
        self.min_position = min_pos
        self.max_position = max_pos
        
    def begin_drag(self, x, y):
        """Begin drag operation"""
        self.dragging = True
        self.drag_start_x = x
        self.drag_start_y = y
        self.drag_start_position = self.position
        
    def end_drag(self):
        """End drag operation"""
        if self.dragging:
            self.dragging = False
            if self.on_splitter_moved:
                self.on_splitter_moved(self.position)
                
    def handle_drag(self, x, y):
        """Handle drag to new position"""
        if not self.dragging:
            return
            
        # Calculate new position
        if self.orientation == self.HORIZONTAL:
            # Horizontal splitter, dragging vertically
            delta = y - self.drag_start_y
            max_pixels = self.height
            
            if self.use_percentage:
                delta_pct = delta / max_pixels if max_pixels > 0 else 0
                new_position = self.drag_start_position + delta_pct
            else:
                new_position = self.drag_start_position + delta
        else:
            # Vertical splitter, dragging horizontally
            delta = x - self.drag_start_x
            max_pixels = self.width
            
            if self.use_percentage:
                delta_pct = delta / max_pixels if max_pixels > 0 else 0
                new_position = self.drag_start_position + delta_pct
            else:
                new_position = self.drag_start_position + delta
                
        # Apply constraints
        self.set_position(new_position)
        
        if self.on_splitter_moving:
            self.on_splitter_moving(self.position)
            
    def handle_click(self, x, y):
        """Handle mouse click"""
        # Check if click is on splitter
        if self._is_on_splitter(x, y):
            self.begin_drag(x, y)
            return True
        return False
        
    def handle_release(self, x, y):
        """Handle mouse release"""
        if self.dragging:
            self.end_drag()
            return True
        return False
        
    def _is_on_splitter(self, x, y):
        """Check if coordinates are on splitter"""
        if self.orientation == self.HORIZONTAL:
            # Horizontal line at y position
            pixel_pos = self.get_pixel_position()
            return (self.x <= x < self.x + self.width and 
                    y == self.y + pixel_pos)
        else:
            # Vertical line at x position
            pixel_pos = self.get_pixel_position()
            return (x == self.x + pixel_pos and 
                    self.y <= y < self.y + self.height)
                    
    def set_panel1(self, panel):
        """Set first panel (left or top)"""
        self.panel1 = panel
        self._update_panels()
        
    def set_panel2(self, panel):
        """Set second panel (right or bottom)"""
        self.panel2 = panel
        self._update_panels()
        
    def _update_panels(self):
        """Update panel sizes based on splitter position"""
        pixel_pos = self.get_pixel_position()
        
        if self.orientation == self.HORIZONTAL:
            # Horizontal splitter - divides vertically
            if self.panel1:
                self.panel1.height = pixel_pos
                
            if self.panel2:
                self.panel2.y = self.y + pixel_pos + 1
                self.panel2.height = self.height - pixel_pos - 1
        else:
            # Vertical splitter - divides horizontally
            if self.panel1:
                self.panel1.width = pixel_pos
                
            if self.panel2:
                self.panel2.x = self.x + pixel_pos + 1
                self.panel2.width = self.width - pixel_pos - 1
                
    def render(self, screen):
        """Render the splitter"""
        pixel_pos = self.get_pixel_position()
        
        if self.orientation == self.HORIZONTAL:
            # Draw horizontal line
            y = self.y + pixel_pos
            for x in range(self.x, self.x + self.width):
                char = self.splitter_char_h
                
                # Draw handle in center
                center = self.x + self.width // 2
                if x == center:
                    char = self.handle_char
                    
                # Output char at x, y
        else:
            # Draw vertical line
            x = self.x + pixel_pos
            for y in range(self.y, self.y + self.height):
                char = self.splitter_char
                
                # Draw handle in center
                center = self.y + self.height // 2
                if y == center:
                    char = self.handle_char
                    
                # Output char at x, y


# Utility functions

def create_horizontal_splitter(top_panel, bottom_panel, position=0.5):
    """
    Create a horizontal splitter dividing two panels vertically
    
    Args:
        top_panel: Panel above splitter
        bottom_panel: Panel below splitter
        position: Position (0.0-1.0)
        
    Returns:
        Splitter instance
    """
    splitter = Splitter()
    splitter.set_orientation(Splitter.HORIZONTAL)
    splitter.set_position(position)
    splitter.set_panel1(top_panel)
    splitter.set_panel2(bottom_panel)
    return splitter


def create_vertical_splitter(left_panel, right_panel, position=0.5):
    """
    Create a vertical splitter dividing two panels horizontally
    
    Args:
        left_panel: Panel left of splitter
        right_panel: Panel right of splitter
        position: Position (0.0-1.0)
        
    Returns:
        Splitter instance
    """
    splitter = Splitter()
    splitter.set_orientation(Splitter.VERTICAL)
    splitter.set_position(position)
    splitter.set_panel1(left_panel)
    splitter.set_panel2(right_panel)
    return splitter


class SplitContainer:
    """
    Convenience class combining splitter with two panels
    """
    
    def __init__(self, orientation=Splitter.VERTICAL):
        self.orientation = orientation
        self.panel1 = None  # Left or Top
        self.panel2 = None  # Right or Bottom
        self.splitter = Splitter()
        self.splitter.set_orientation(orientation)
        
    def set_panels(self, panel1, panel2):
        """Set both panels"""
        self.panel1 = panel1
        self.panel2 = panel2
        self.splitter.set_panel1(panel1)
        self.splitter.set_panel2(panel2)
        
    def set_position(self, position):
        """Set splitter position"""
        self.splitter.set_position(position)
        
    def render(self, screen):
        """Render container with panels and splitter"""
        if self.panel1 and hasattr(self.panel1, 'render'):
            self.panel1.render(screen)
            
        if self.panel2 and hasattr(self.panel2, 'render'):
            self.panel2.render(screen)
            
        self.splitter.render(screen)
