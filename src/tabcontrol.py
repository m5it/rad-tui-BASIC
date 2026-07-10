"""
TabControl Module for RAD-TUI v2.2.0
Provides multi-page interface with tabbed navigation
"""

class TabPage:
    """Represents a single tab page"""
    
    def __init__(self, caption="Tab", name_id=""):
        self.caption = caption
        self.name_id = name_id or f"tab_{id(self)}"
        self.controls = []
        self.visible = False
        self.enabled = True
        self.tag = None
        
        # Appearance
        self.back_color = None
        self.fore_color = None
        
    def add_control(self, control):
        """Add a control to this tab page"""
        self.controls.append(control)
        control.parent = self
        
    def remove_control(self, control):
        """Remove a control from this tab page"""
        if control in self.controls:
            self.controls.remove(control)
            control.parent = None
            
    def show(self):
        """Show this tab page"""
        self.visible = True
        for control in self.controls:
            control.visible = True
            
    def hide(self):
        """Hide this tab page"""
        self.visible = False
        for control in self.controls:
            control.visible = False
            
    def clear(self):
        """Remove all controls from this tab"""
        self.controls = []


class TabControl:
    """TabControl for multi-page interfaces"""
    
    TOOL_TYPE = 18
    
    # Orientations
    HORIZONTAL = 0
    VERTICAL = 1
    
    def __init__(self, name_id="tabControl1", x=0, y=0, width=40, height=20):
        self.name_id = name_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Tabs
        self.tabs = []
        self.active_tab_index = -1
        
        # Appearance
        self.orientation = self.HORIZONTAL  # 0 = horizontal, 1 = vertical
        self.tab_height = 3  # Height of tab header
        self.tab_width = 15  # Width for vertical tabs
        self.show_close_button = False
        self.closable_tabs = False
        
        # Events
        self.on_tab_change = None
        self.on_tab_click = None
        self.on_tab_close = None
        
        # State
        self.focused = False
        
    def add_tab(self, caption, name_id=""):
        """Add a new tab page"""
        tab = TabPage(caption, name_id)
        self.tabs.append(tab)
        
        # If first tab, make it active
        if len(self.tabs) == 1:
            self.set_active_tab(0)
            
        return tab
        
    def remove_tab(self, index):
        """Remove a tab by index"""
        if 0 <= index < len(self.tabs):
            tab = self.tabs[index]
            
            # Hide tab before removing
            tab.hide()
            
            self.tabs.remove(tab)
            
            # Adjust active tab
            if self.active_tab_index == index:
                if len(self.tabs) > 0:
                    self.set_active_tab(min(index, len(self.tabs) - 1))
                else:
                    self.active_tab_index = -1
            elif self.active_tab_index > index:
                self.active_tab_index -= 1
                
            if self.on_tab_close:
                self.on_tab_close(tab)
                
    def set_active_tab(self, index):
        """Set the active tab by index"""
        if 0 <= index < len(self.tabs):
            # Hide current tab
            if self.active_tab_index >= 0:
                self.tabs[self.active_tab_index].hide()
                
            # Show new tab
            self.active_tab_index = index
            self.tabs[index].show()
            
            if self.on_tab_change:
                self.on_tab_change(index, self.tabs[index])
                
    def get_active_tab(self):
        """Get the currently active tab"""
        if 0 <= self.active_tab_index < len(self.tabs):
            return self.tabs[self.active_tab_index]
        return None
        
    def get_active_index(self):
        """Get index of active tab"""
        return self.active_tab_index
        
    def next_tab(self):
        """Switch to next tab"""
        if self.tabs:
            new_index = (self.active_tab_index + 1) % len(self.tabs)
            self.set_active_tab(new_index)
            
    def prev_tab(self):
        """Switch to previous tab"""
        if self.tabs:
            new_index = (self.active_tab_index - 1) % len(self.tabs)
            self.set_active_tab(new_index)
            
    def clear(self):
        """Remove all tabs"""
        self.tabs = []
        self.active_tab_index = -1
        
    def get_tab_count(self):
        """Get number of tabs"""
        return len(self.tabs)
        
    def get_tab(self, index):
        """Get tab by index"""
        if 0 <= index < len(self.tabs):
            return self.tabs[index]
        return None
        
    def get_tab_index(self, tab):
        """Get index of tab"""
        try:
            return self.tabs.index(tab)
        except ValueError:
            return -1
            
    def handle_click(self, x, y):
        """Handle mouse click"""
        # Check if click is on tab header area
        if self.orientation == self.HORIZONTAL:
            # Tabs at top
            if y < self.y + self.tab_height:
                tab_x = self.x
                for i, tab in enumerate(self.tabs):
                    tab_width = len(tab.caption) + 4  # Padding
                    if tab_x <= x < tab_x + tab_width:
                        if i != self.active_tab_index:
                            self.set_active_tab(i)
                            if self.on_tab_click:
                                self.on_tab_click(i, tab)
                        return True
                    tab_x += tab_width
        else:
            # Tabs on left side
            if x < self.x + self.tab_width:
                row = y - self.y
                if 0 <= row < len(self.tabs):
                    if row != self.active_tab_index:
                        self.set_active_tab(row)
                        if self.on_tab_click:
                            self.on_tab_click(row, self.tabs[row])
                    return True
                    
        return False
        
    def get_content_area(self):
        """Get the rectangle for tab content area"""
        if self.orientation == self.HORIZONTAL:
            return {
                'x': self.x,
                'y': self.y + self.tab_height,
                'width': self.width,
                'height': self.height - self.tab_height
            }
        else:
            return {
                'x': self.x + self.tab_width,
                'y': self.y,
                'width': self.width - self.tab_width,
                'height': self.height
            }
            
    def render(self, screen):
        """Render the TabControl"""
        self._render_tabs(screen)
        self._render_content_area(screen)
        
    def _render_tabs(self, screen):
        """Render tab headers"""
        if self.orientation == self.HORIZONTAL:
            # Horizontal tabs at top
            tab_x = self.x
            tab_y = self.y
            
            for i, tab in enumerate(self.tabs):
                is_active = (i == self.active_tab_index)
                tab_width = len(tab.caption) + 4
                
                # Draw tab border/background
                if is_active:
                    # Active tab style
                    pass
                else:
                    # Inactive tab style
                    pass
                    
                # Draw caption
                caption_x = tab_x + 2
                # Draw text at caption_x, tab_y + 1
                
                tab_x += tab_width
        else:
            # Vertical tabs on left
            for i, tab in enumerate(self.tabs):
                is_active = (i == self.active_tab_index)
                tab_y = self.y + (i * self.tab_height)
                
                # Draw tab
                if is_active:
                    pass
                else:
                    pass
                    
    def _render_content_area(self, screen):
        """Render the content area of active tab"""
        if self.active_tab_index >= 0:
            active_tab = self.tabs[self.active_tab_index]
            
            # Render controls in active tab
            for control in active_tab.controls:
                if hasattr(control, 'render'):
                    control.render(screen)


# Utility functions

def create_tabbed_dialog(tabs_data):
    """
    Create a TabControl with predefined tabs
    
    Args:
        tabs_data: List of dicts with 'caption' and optional 'name_id'
        
    Returns:
        TabControl instance
    """
    tc = TabControl()
    for data in tabs_data:
        tc.add_tab(data.get('caption', 'Tab'), 
                   data.get('name_id', ''))
    return tc


def find_tab_by_caption(tabcontrol, caption):
    """Find tab by caption text"""
    for i, tab in enumerate(tabcontrol.tabs):
        if tab.caption == caption:
            return i, tab
    return -1, None
