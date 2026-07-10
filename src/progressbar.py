"""
ProgressBar Control Module for RAD-TUI v2.2.0
Provides visual progress indication
"""

class ProgressBar:
    """ProgressBar control for showing completion status"""
    
    TOOL_TYPE = 19
    
    # Orientations
    HORIZONTAL = 0
    VERTICAL = 1
    
    def __init__(self, name_id="progressBar1", x=0, y=0, width=30, height=1):
        self.name_id = name_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Value range
        self.min_value = 0
        self.max_value = 100
        self.current_value = 0
        
        # Appearance
        self.orientation = self.HORIZONTAL
        self.show_percentage = True
        self.bar_char = "\u2588"  # Full block
        self.fill_char = "\u2591"  # Light shade
        self.percentage_format = "{:.0f}%"  # Format string for percentage
        
        # Events
        self.on_value_change = None
        self.on_complete = None
        
        # State
        self.enabled = True
        self.visible = True
        
    def set_range(self, min_val, max_val):
        """Set the minimum and maximum values"""
        self.min_value = min_val
        self.max_value = max_val
        
        # Clamp current value to new range
        self.current_value = max(self.min_value, 
                                min(self.current_value, self.max_value))
        
    def set_value(self, value):
        """Set the current progress value"""
        old_value = self.current_value
        self.current_value = max(self.min_value, min(value, self.max_value))
        
        # Trigger event if value changed
        if old_value != self.current_value:
            if self.on_value_change:
                self.on_value_change(self.current_value)
                
            # Check for completion
            if self.current_value >= self.max_value:
                if self.on_complete:
                    self.on_complete()
                    
    def get_value(self):
        """Get current progress value"""
        return self.current_value
        
    def get_percentage(self):
        """Get progress as percentage (0.0 - 100.0)"""
        if self.max_value == self.min_value:
            return 0.0
        return ((self.current_value - self.min_value) / 
                (self.max_value - self.min_value) * 100)
        
    def increment(self, amount=1):
        """Increment progress by amount"""
        self.set_value(self.current_value + amount)
        
    def decrement(self, amount=1):
        """Decrement progress by amount"""
        self.set_value(self.current_value - amount)
        
    def reset(self):
        """Reset progress to minimum value"""
        self.set_value(self.min_value)
        
    def is_complete(self):
        """Check if progress is complete"""
        return self.current_value >= self.max_value
        
    def set_percentage(self, percentage):
        """Set progress by percentage (0-100)"""
        value = self.min_value + (self.max_value - self.min_value) * (percentage / 100)
        self.set_value(value)
        
    def render(self, screen):
        """Render the progress bar"""
        if not self.visible:
            return
            
        percentage = self.get_percentage()
        
        if self.orientation == self.HORIZONTAL:
            self._render_horizontal(screen, percentage)
        else:
            self._render_vertical(screen, percentage)
            
    def _render_horizontal(self, screen, percentage):
        """Render horizontal progress bar"""
        # Calculate filled width
        if self.show_percentage:
            # Reserve space for percentage text
            text = self.percentage_format.format(percentage)
            text_width = len(text) + 2  # +2 for spacing
            bar_width = self.width - text_width
        else:
            bar_width = self.width
            
        filled_width = int(bar_width * percentage / 100)
        
        # Build bar string
        bar = self.bar_char * filled_width
        bar += self.fill_char * (bar_width - filled_width)
        
        # Add percentage if enabled
        if self.show_percentage:
            bar += " " + self.percentage_format.format(percentage)
            
        # Output to screen (implementation depends on screen buffer)
        # Place bar at self.x, self.y
        
    def _render_vertical(self, screen, percentage):
        """Render vertical progress bar"""
        filled_height = int(self.height * percentage / 100)
        
        for row in range(self.height):
            y = self.y + self.height - 1 - row  # Fill from bottom
            
            if row < filled_height:
                # Filled portion
                line = self.bar_char * self.width
            else:
                # Empty portion
                line = self.fill_char * self.width
                
            # Output line at self.x, y
            
    def simulate_progress(self, delay_ms=100, increment=1):
        """
        Simulate progress for demonstration/testing
        
        Args:
            delay_ms: Delay between increments in milliseconds
            increment: Amount to increment each step
        """
        import time
        
        self.reset()
        while not self.is_complete():
            self.increment(increment)
            time.sleep(delay_ms / 1000)


# Utility functions

def create_progress_dialog(title="Progress", message="Please wait..."):
    """
    Create a simple progress dialog
    
    Returns:
        dict with 'dialog', 'progressbar', 'update' function
    """
    # This would integrate with custom_dialog module
    # For now, return a simple structure
    pb = ProgressBar(width=40)
    
    def update(value):
        pb.set_value(value)
        
    return {
        'progressbar': pb,
        'update': update
    }


def download_with_progress(url, filename, progressbar):
    """
    Download file with progress updates
    
    Args:
        url: URL to download from
        filename: Local filename to save to
        progressbar: ProgressBar instance to update
    """
    # This would integrate with network module
    # Placeholder for the pattern
    pass
