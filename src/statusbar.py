"""
StatusBar Control Module for RAD-TUI v2.2.0
Provides multi-panel information display at bottom of forms
"""

class StatusPanel:
    """Represents a panel in the StatusBar"""
    
    # Auto-size modes
    FIXED = 0      # Fixed width
    SPRING = 1     # Expands to fill space
    PERCENTAGE = 2 # Percentage of total width
    
    def __init__(self, text="", width=10, auto_size=0):
        self.text = text
        self.width = width
        self.auto_size = auto_size
        self.alignment = "left"  # left, center, right
        self.border = True
        self.min_width = 3
        self.tag = None
        
    def set_text(self, text):
        """Set panel text"""
        self.text = str(text)
        
    def get_text(self):
        """Get panel text"""
        return self.text


class StatusBar:
    """StatusBar control for displaying information"""
    
    TOOL_TYPE = 22
    
    def __init__(self, name_id="statusBar1", x=0, y=0, width=80, height=1):
        self.name_id = name_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Panels
        self.panels = []
        
        # Simple mode (single panel)
        self.simple_mode = False
        self.simple_text = ""
        
        # Appearance
        self.show_size_grip = True  # Resize handle at right
        self.size_grip_char = "\u25E5"  # Corner triangle
        
        # Events
        self.on_panel_click = None
        
        # State
        self.enabled = True
        self.visible = True
        
    def add_panel(self, text="", width=10, auto_size=0):
        """Add a panel to the status bar"""
        panel = StatusPanel(text, width, auto_size)
        self.panels.append(panel)
        self._recalculate_sizes()
        return panel
        
    def remove_panel(self, index):
        """Remove panel by index"""
        if 0 <= index < len(self.panels):
            del self.panels[index]
            self._recalculate_sizes()
            
    def clear_panels(self):
        """Remove all panels"""
        self.panels = []
        
    def get_panel(self, index):
        """Get panel by index"""
        if 0 <= index < len(self.panels):
            return self.panels[index]
        return None
        
    def get_panel_count(self):
        """Get number of panels"""
        return len(self.panels)
        
    def set_panel_text(self, index, text):
        """Set text of a panel"""
        panel = self.get_panel(index)
        if panel:
            panel.set_text(text)
            
    def get_panel_text(self, index):
        """Get text of a panel"""
        panel = self.get_panel(index)
        if panel:
            return panel.get_text()
        return ""
        
    def set_simple_text(self, text):
        """Set text for simple mode"""
        self.simple_text = str(text)
        
    def get_simple_text(self):
        """Get simple mode text"""
        return self.simple_text
        
    def set_simple_mode(self, simple):
        """Enable/disable simple mode"""
        self.simple_mode = simple
        
    def _recalculate_sizes(self):
        """Recalculate panel sizes based on auto-size settings"""
        if not self.panels:
            return
            
        # Calculate fixed and percentage widths
        fixed_width = 0
        spring_count = 0
        
        for panel in self.panels:
            if panel.auto_size == StatusPanel.FIXED:
                fixed_width += panel.width
            elif panel.auto_size == StatusPanel.PERCENTAGE:
                # Calculate actual width from percentage
                actual_width = int(self.width * panel.width / 100)
                fixed_width += actual_width
            elif panel.auto_size == StatusPanel.SPRING:
                spring_count += 1
                
        # Distribute remaining space among spring panels
        if spring_count > 0:
            remaining = self.width - fixed_width - len(self.panels)  # Account for borders
            if self.show_size_grip:
                remaining -= 1
                
            spring_width = max(3, remaining // spring_count)
            
            for panel in self.panels:
                if panel.auto_size == StatusPanel.SPRING:
                    panel.width = spring_width
                    
    def handle_click(self, x, y):
        """Handle mouse click on status bar"""
        if y != self.y:
            return False
            
        # Find which panel was clicked
        current_x = self.x
        
        for i, panel in enumerate(self.panels):
            panel_width = panel.width
            
            if current_x <= x < current_x + panel_width:
                if self.on_panel_click:
                    self.on_panel_click(i, panel)
                return True
                
            current_x += panel_width + 1  # +1 for border
            
        return False
        
    def render(self, screen):
        """Render the status bar"""
        if not self.visible:
            return
            
        if self.simple_mode:
            self._render_simple(screen)
        else:
            self._render_panels(screen)
            
    def _render_simple(self, screen):
        """Render in simple mode (single text)"""
        text = self.simple_text[:self.width]
        
        # Pad to full width
        text = text.ljust(self.width)
        
        # Add size grip if enabled
        if self.show_size_grip:
            text = text[:-1] + self.size_grip_char
            
        # Output at self.x, self.y
        
    def _render_panels(self, screen):
        """Render with multiple panels"""
        self._recalculate_sizes()
        
        current_x = self.x
        
        for i, panel in enumerate(self.panels):
            # Render panel
            text = panel.text[:panel.width]
            
            # Apply alignment
            if panel.alignment == "center":
                text = text.center(panel.width)
            elif panel.alignment == "right":
                text = text.rjust(panel.width)
            else:
                text = text.ljust(panel.width)
                
            # Output panel text at current_x, self.y
            
            current_x += panel.width
            
            # Render border between panels (except after last)
            if i < len(self.panels) - 1:
                # Draw vertical line
                current_x += 1
                
        # Render size grip
        if self.show_size_grip:
            # Place at right edge
            pass


# Utility functions

def create_standard_statusbar():
    """
    Create a standard status bar with common panels
    
    Returns StatusBar with panels for:
    - Message/status text (spring)
    - Line/column info (fixed)
    - Insert/overwrite mode (fixed)
    """
    sb = StatusBar()
    
    # Main message panel (spring)
    sb.add_panel("Ready", width=50, auto_size=StatusPanel.SPRING)
    
    # Line/column info (fixed)
    sb.add_panel("Ln 1, Col 1", width=12, auto_size=StatusPanel.FIXED)
    
    # Mode indicator (fixed)
    sb.add_panel("INS", width=5, auto_size=StatusPanel.FIXED)
    
    return sb


def create_progress_statusbar():
    """
    Create a status bar with progress panel
    
    Returns StatusBar with progress text panel
    """
    sb = StatusBar()
    
    # Progress message
    sb.add_panel("Progress: 0%", width=20, auto_size=StatusPanel.SPRING)
    
    # Status
    sb.add_panel("Working...", width=12, auto_size=StatusPanel.FIXED)
    
    return sb
