"""
Toolbar Control Module for RAD-TUI v2.2.0
Provides icon button strip for common actions
"""

class ToolbarButton:
    """Represents a button on the toolbar"""
    
    # Button types
    PUSH = 0      # Normal push button
    TOGGLE = 1    # Toggle/stay-pressed button
    SEPARATOR = 2 # Visual separator
    
    def __init__(self, caption="", icon="", tooltip="", button_type=0):
        self.caption = caption
        self.icon = icon  # Single character icon
        self.tooltip = tooltip
        self.button_type = button_type
        self.enabled = True
        self.checked = False  # For toggle buttons
        self.visible = True
        
        # Size
        self.width = len(icon) + 2 if icon else len(caption) + 2
        self.height = 1
        
        # Tag for user data
        self.tag = None
        
    def toggle(self):
        """Toggle checked state (for toggle buttons)"""
        if self.button_type == self.TOGGLE:
            self.checked = not self.checked
            
    def set_checked(self, checked):
        """Set checked state"""
        if self.button_type == self.TOGGLE:
            self.checked = checked
            
    def is_separator(self):
        """Check if this is a separator"""
        return self.button_type == self.SEPARATOR


class Toolbar:
    """Toolbar control with icon buttons"""
    
    TOOL_TYPE = 21
    
    # Orientations
    HORIZONTAL = 0
    VERTICAL = 1
    
    def __init__(self, name_id="toolbar1", x=0, y=0, width=40, height=1):
        self.name_id = name_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Buttons
        self.buttons = []
        
        # Appearance
        self.orientation = self.HORIZONTAL
        self.button_spacing = 1
        self.show_captions = False  # Show text below icons
        self.show_tooltips = True
        self.flat_style = True  # Flat or 3D buttons
        
        # Separator character
        self.separator_char = "|"
        
        # Events
        self.on_button_click = None
        self.on_button_check = None  # For toggle buttons
        
        # State
        self.enabled = True
        self.visible = True
        self.hovered_button = None
        
    def add_button(self, caption="", icon="", tooltip="", button_type=0):
        """Add a button to the toolbar"""
        button = ToolbarButton(caption, icon, tooltip, button_type)
        self.buttons.append(button)
        return button
        
    def add_separator(self):
        """Add a separator"""
        sep = ToolbarButton(button_type=ToolbarButton.SEPARATOR)
        self.buttons.append(sep)
        return sep
        
    def remove_button(self, button):
        """Remove a button"""
        if button in self.buttons:
            self.buttons.remove(button)
            
    def clear(self):
        """Remove all buttons"""
        self.buttons = []
        
    def enable_button(self, index):
        """Enable button by index"""
        if 0 <= index < len(self.buttons):
            self.buttons[index].enabled = True
            
    def disable_button(self, index):
        """Disable button by index"""
        if 0 <= index < len(self.buttons):
            self.buttons[index].enabled = False
            
    def set_button_checked(self, index, checked):
        """Set checked state for toggle button"""
        if 0 <= index < len(self.buttons):
            self.buttons[index].set_checked(checked)
            
    def get_button(self, index):
        """Get button by index"""
        if 0 <= index < len(self.buttons):
            return self.buttons[index]
        return None
        
    def find_button_by_tag(self, tag):
        """Find button by tag value"""
        for button in self.buttons:
            if button.tag == tag:
                return button
        return None
        
    def handle_click(self, x, y):
        """Handle mouse click"""
        button, index = self._get_button_at_position(x, y)
        
        if button and button.enabled and not button.is_separator():
            if button.button_type == ToolbarButton.TOGGLE:
                button.toggle()
                if self.on_button_check:
                    self.on_button_check(index, button, button.checked)
            else:
                if self.on_button_click:
                    self.on_button_click(index, button)
            return True
            
        return False
        
    def handle_hover(self, x, y):
        """Handle mouse hover for tooltips"""
        button, index = self._get_button_at_position(x, y)
        
        if button != self.hovered_button:
            self.hovered_button = button
            
        return button.tooltip if (button and button.tooltip) else None
        
    def _get_button_at_position(self, x, y):
        """Get button at screen position"""
        if self.orientation == self.HORIZONTAL:
            current_x = self.x
            
            for i, button in enumerate(self.buttons):
                if button.is_separator():
                    width = 1
                else:
                    width = button.width
                    
                if current_x <= x < current_x + width:
                    if self.y <= y < self.y + self.height:
                        return button, i
                        
                current_x += width + self.button_spacing
        else:
            # Vertical orientation
            current_y = self.y
            
            for i, button in enumerate(self.buttons):
                height = 1  # Each button takes 1 row
                
                if current_y <= y < current_y + height:
                    if self.x <= x < self.x + self.width:
                        return button, i
                        
                current_y += height + self.button_spacing
                
        return None, -1
        
    def render(self, screen):
        """Render the toolbar"""
        if not self.visible:
            return
            
        current_x = self.x
        current_y = self.y
        
        for button in self.buttons:
            if not button.visible:
                continue
                
            if button.is_separator():
                self._render_separator(screen, current_x, current_y)
                current_x += 1 + self.button_spacing
            else:
                self._render_button(screen, button, current_x, current_y)
                
                if self.orientation == self.HORIZONTAL:
                    current_x += button.width + self.button_spacing
                else:
                    current_y += 1 + self.button_spacing
                    
    def _render_button(self, screen, button, x, y):
        """Render a single button"""
        # Determine style based on state
        if not button.enabled:
            style = "disabled"
        elif button.checked:
            style = "checked"
        elif button == self.hovered_button:
            style = "hover"
        else:
            style = "normal"
            
        # Build display text
        if button.icon:
            text = f" {button.icon} "
        else:
            text = f" {button.caption} "
            
        # Truncate if needed
        if len(text) > button.width:
            text = text[:button.width]
            
        # Output with appropriate styling
        # Implementation depends on screen rendering system
        pass
        
    def _render_separator(self, screen, x, y):
        """Render a separator"""
        if self.orientation == self.HORIZONTAL:
            # Vertical line
            pass
        else:
            # Horizontal line
            pass


# Common toolbar button factories

def new_file_button():
    """Create New File button"""
    return ToolbarButton(icon="N", tooltip="New File")

def open_file_button():
    """Create Open File button"""
    return ToolbarButton(icon="O", tooltip="Open")

def save_file_button():
    """Create Save File button"""
    return ToolbarButton(icon="S", tooltip="Save")

def cut_button():
    """Create Cut button"""
    return ToolbarButton(icon="X", tooltip="Cut")

def copy_button():
    """Create Copy button"""
    return ToolbarButton(icon="C", tooltip="Copy")

def paste_button():
    """Create Paste button"""
    return ToolbarButton(icon="V", tooltip="Paste")

def undo_button():
    """Create Undo button"""
    return ToolbarButton(icon="U", tooltip="Undo")

def redo_button():
    """Create Redo button"""
    return ToolbarButton(icon="R", tooltip="Redo")
