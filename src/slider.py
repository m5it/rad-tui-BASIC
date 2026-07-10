"""
Slider/Trackbar Control Module for RAD-TUI v2.2.0
Provides numeric value selection via dragging
"""

class Slider:
    """Slider control for selecting numeric values"""
    
    TOOL_TYPE = 20
    
    # Orientations
    HORIZONTAL = 0
    VERTICAL = 1
    
    def __init__(self, name_id="slider1", x=0, y=0, width=30, height=1):
        self.name_id = name_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Value range
        self.min_value = 0
        self.max_value = 100
        self.current_value = 50
        self.step_increment = 1
        
        # Appearance
        self.orientation = self.HORIZONTAL
        self.show_ticks = False
        self.tick_frequency = 10
        self.tick_char = "|"
        self.track_char = "-"
        self.thumb_char = "\u25CF"  # Circle
        
        # Events
        self.on_value_change = None
        self.on_track = None      # Called during dragging
        self.on_change_complete = None  # Called when released
        
        # State
        self.enabled = True
        self.visible = True
        self.dragging = False
        
    def set_range(self, min_val, max_val):
        """Set the minimum and maximum values"""
        self.min_value = min_val
        self.max_value = max_val
        self.current_value = max(self.min_value, 
                                min(self.current_value, self.max_value))
        
    def set_value(self, value, trigger_event=True):
        """Set the current value"""
        old_value = self.current_value
        # Round to step increment
        value = round(value / self.step_increment) * self.step_increment
        self.current_value = max(self.min_value, min(value, self.max_value))
        
        if trigger_event and old_value != self.current_value:
            if self.on_value_change:
                self.on_value_change(self.current_value)
                
    def get_value(self):
        """Get current value"""
        return self.current_value
        
    def get_percentage(self):
        """Get value as percentage of range"""
        if self.max_value == self.min_value:
            return 0.0
        return ((self.current_value - self.min_value) / 
                (self.max_value - self.min_value) * 100)
        
    def increment(self):
        """Increment by step"""
        self.set_value(self.current_value + self.step_increment)
        
    def decrement(self):
        """Decrement by step"""
        self.set_value(self.current_value - self.step_increment)
        
    def set_step(self, step):
        """Set step increment"""
        self.step_increment = step
        
    def get_step(self):
        """Get step increment"""
        return self.step_increment
        
    def begin_drag(self):
        """Begin drag operation"""
        self.dragging = True
        
    def end_drag(self):
        """End drag operation"""
        if self.dragging:
            self.dragging = False
            if self.on_change_complete:
                self.on_change_complete(self.current_value)
                
    def handle_drag(self, x, y):
        """Handle drag to position"""
        if not self.dragging:
            return
            
        # Calculate value from position
        if self.orientation == self.HORIZONTAL:
            # Calculate relative position in track
            track_width = self.width - 1  # Leave room for thumb
            rel_x = x - self.x
            
            if track_width > 0:
                percentage = max(0, min(100, (rel_x / track_width) * 100))
                value = self.min_value + (self.max_value - self.min_value) * (percentage / 100)
                self.set_value(value, trigger_event=False)
                
                if self.on_track:
                    self.on_track(self.current_value)
        else:
            # Vertical orientation
            track_height = self.height - 1
            rel_y = y - self.y
            
            if track_height > 0:
                percentage = max(0, min(100, (rel_y / track_height) * 100))
                value = self.min_value + (self.max_value - self.min_value) * (percentage / 100)
                self.set_value(value, trigger_event=False)
                
                if self.on_track:
                    self.on_track(self.current_value)
                    
    def handle_click(self, x, y):
        """Handle mouse click"""
        # Check if click is on slider
        if (self.x <= x < self.x + self.width and 
            self.y <= y < self.y + self.height):
            
            self.begin_drag()
            self.handle_drag(x, y)
            self.end_drag()
            return True
            
        return False
        
    def render(self, screen):
        """Render the slider"""
        if not self.visible:
            return
            
        if self.orientation == self.HORIZONTAL:
            self._render_horizontal(screen)
        else:
            self._render_vertical(screen)
            
    def _render_horizontal(self, screen):
        """Render horizontal slider"""
        # Calculate thumb position
        percentage = self.get_percentage()
        track_width = self.width - 1
        thumb_pos = int(track_width * percentage / 100)
        
        # Build track line
        line = ""
        
        # Add ticks if enabled
        if self.show_ticks:
            for i in range(self.width):
                if i % (self.width // (100 // self.tick_frequency)) == 0:
                    line += self.tick_char
                else:
                    line += self.track_char
        else:
            line = self.track_char * self.width
            
        # Place thumb
        if thumb_pos < len(line):
            line = line[:thumb_pos] + self.thumb_char + line[thumb_pos+1:]
            
        # Output to screen at self.x, self.y
        
    def _render_vertical(self, screen):
        """Render vertical slider"""
        percentage = self.get_percentage()
        track_height = self.height - 1
        thumb_pos = int(track_height * percentage / 100)
        
        for row in range(self.height):
            y = self.y + track_height - row
            
            if row == thumb_pos:
                char = self.thumb_char
            elif self.show_ticks and row % (self.height // (100 // self.tick_frequency)) == 0:
                char = self.tick_char
            else:
                char = self.track_char
                
            # Output char at self.x, y


# Utility functions

def create_volume_slider(name_id="volumeSlider"):
    """Create a slider configured for volume control (0-100)"""
    slider = Slider(name_id=name_id)
    slider.set_range(0, 100)
    slider.set_step(5)
    slider.show_ticks = True
    slider.tick_frequency = 25
    return slider


def create_zoom_slider(name_id="zoomSlider"):
    """Create a slider configured for zoom control (25-400%)"""
    slider = Slider(name_id=name_id)
    slider.set_range(25, 400)
    slider.set_step(25)
    slider.show_ticks = True
    slider.tick_frequency = 100
    return slider
