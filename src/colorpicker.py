"""
ColorPicker Control Module for RAD-TUI v2.2.0
Provides color selection interface
"""

class Color:
    """Represents a color with RGB values"""
    
    def __init__(self, r=0, g=0, b=0):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
        
    @classmethod
    def from_hex(cls, hex_string):
        """Create Color from hex string (#RRGGBB or #RGB)"""
        hex_string = hex_string.lstrip('#')
        
        if len(hex_string) == 3:
            # Short form #RGB
            r = int(hex_string[0] * 2, 16)
            g = int(hex_string[1] * 2, 16)
            b = int(hex_string[2] * 2, 16)
        elif len(hex_string) == 6:
            # Full form #RRGGBB
            r = int(hex_string[0:2], 16)
            g = int(hex_string[2:4], 16)
            b = int(hex_string[4:6], 16)
        else:
            raise ValueError(f"Invalid hex color: {hex_string}")
            
        return cls(r, g, b)
        
    @classmethod
    def from_name(cls, name):
        """Create Color from named color"""
        colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
            'gray': (128, 128, 128),
            'lightgray': (192, 192, 192),
            'darkgray': (64, 64, 64),
        }
        
        name = name.lower()
        if name in colors:
            return cls(*colors[name])
        else:
            raise ValueError(f"Unknown color name: {name}")
            
    def to_hex(self):
        """Convert to hex string #RRGGBB"""
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"
        
    def to_rgb(self):
        """Get RGB tuple"""
        return (self.r, self.g, self.b)
        
    def to_terminal_color(self):
        """
        Convert to terminal color code (0-255)
        Uses 6x6x6 color cube + grayscale
        """
        if self.r == self.g == self.b:
            # Grayscale (232-255)
            if self.r < 8:
                return 16
            elif self.r > 247:
                return 231
            else:
                return 232 + ((self.r - 8) // 10)
        else:
            # Color cube (16-231)
            r = self.r // 51  # 0-5
            g = self.g // 51
            b = self.b // 51
            return 16 + (r * 36) + (g * 6) + b
            
    def __str__(self):
        return self.to_hex()
        
    def __repr__(self):
        return f"Color(r={self.r}, g={self.g}, b={self.b})"


class ColorPicker:
    """ColorPicker control for selecting colors"""
    
    TOOL_TYPE = 24
    
    # Display modes
    PALETTE = 0      # Show color palette
    RGB_INPUT = 1    # Show RGB input fields
    HEX_INPUT = 2    # Show hex input field
    
    def __init__(self, name_id="colorPicker1", x=0, y=0, width=20, height=5):
        self.name_id = name_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Current color
        self.current_color = Color(128, 128, 128)  # Gray default
        
        # Color palette (preset colors)
        self.color_palette = [
            Color(0, 0, 0),       # Black
            Color(128, 0, 0),     # Dark Red
            Color(0, 128, 0),     # Dark Green
            Color(128, 128, 0),   # Olive
            Color(0, 0, 128),     # Dark Blue
            Color(128, 0, 128),   # Purple
            Color(0, 128, 128),   # Teal
            Color(192, 192, 192), # Light Gray
            Color(128, 128, 128), # Gray
            Color(255, 0, 0),     # Red
            Color(0, 255, 0),     # Green
            Color(255, 255, 0),   # Yellow
            Color(0, 0, 255),     # Blue
            Color(255, 0, 255),   # Magenta
            Color(0, 255, 255),   # Cyan
            Color(255, 255, 255), # White
        ]
        
        # Custom colors storage
        self.custom_colors = []
        self.max_custom_colors = 16
        
        # Display
        self.display_mode = self.PALETTE
        self.show_preview = True
        self.preview_size = 3
        
        # Events
        self.on_color_change = None
        self.on_color_select = None
        
        # State
        self.enabled = True
        self.visible = True
        
    def set_color(self, color):
        """Set current color"""
        if isinstance(color, str):
            if color.startswith('#'):
                color = Color.from_hex(color)
            else:
                color = Color.from_name(color)
        elif isinstance(color, tuple) and len(color) == 3:
            color = Color(*color)
            
        old_color = self.current_color
        self.current_color = color
        
        if old_color.to_hex() != color.to_hex():
            if self.on_color_change:
                self.on_color_change(color)
                
    def get_color(self):
        """Get current color"""
        return self.current_color
        
    def get_hex(self):
        """Get current color as hex string"""
        return self.current_color.to_hex()
        
    def add_custom_color(self, color):
        """Add color to custom palette"""
        if len(self.custom_colors) >= self.max_custom_colors:
            self.custom_colors.pop(0)  # Remove oldest
        self.custom_colors.append(color)
        
    def set_palette(self, colors):
        """Set custom color palette"""
        self.color_palette = [c if isinstance(c, Color) else Color.from_hex(c) 
                             for c in colors]
                             
    def handle_click(self, x, y):
        """Handle mouse click"""
        if self.display_mode == self.PALETTE:
            return self._handle_palette_click(x, y)
        return False
        
    def _handle_palette_click(self, x, y):
        """Handle click on color palette"""
        # Calculate grid position
        cols = min(8, self.width // 2)
        rows = (len(self.color_palette) + cols - 1) // cols
        
        rel_x = x - self.x
        rel_y = y - self.y
        
        col = rel_x // 2
        row = rel_y
        
        if 0 <= col < cols and 0 <= row < rows:
            index = row * cols + col
            if index < len(self.color_palette):
                self.set_color(self.color_palette[index])
                if self.on_color_select:
                    self.on_color_select(self.current_color)
                return True
                
        return False
        
    def show_color_dialog(self, title="Select Color"):
        """
        Show modal color selection dialog
        
        Returns:
            Selected Color or None if cancelled
        """
        # This would integrate with custom_dialog module
        # For now, return current color
        return self.current_color
        
    def render(self, screen):
        """Render the color picker"""
        if not self.visible:
            return
            
        if self.display_mode == self.PALETTE:
            self._render_palette(screen)
        elif self.display_mode == self.RGB_INPUT:
            self._render_rgb_input(screen)
        else:
            self._render_hex_input(screen)
            
    def _render_palette(self, screen):
        """Render color palette grid"""
        cols = min(8, self.width // 2)
        
        for i, color in enumerate(self.color_palette):
            row = i // cols
            col = i % cols
            
            x = self.x + col * 2
            y = self.y + row
            
            # Draw color block (using colored background)
            # Implementation depends on terminal color support
            pass
            
        # Render preview if enabled
        if self.show_preview:
            preview_y = self.y + (len(self.color_palette) + cols - 1) // cols + 1
            # Draw preview block
            
    def _render_rgb_input(self, screen):
        """Render RGB input fields"""
        # Show R, G, B input fields
        pass
        
    def _render_hex_input(self, screen):
        """Render hex input field"""
        # Show hex color input
        pass


# Utility functions

def color_to_ansi(color):
    """
    Convert Color to ANSI escape sequence
    
    Args:
        color: Color instance or hex string
        
    Returns:
        ANSI escape sequence string
    """
    if isinstance(color, str):
        color = Color.from_hex(color)
        
    code = color.to_terminal_color()
    return f"\033[38;5;{code}m"


def color_to_ansi_bg(color):
    """
    Convert Color to ANSI background escape sequence
    """
    if isinstance(color, str):
        color = Color.from_hex(color)
        
    code = color.to_terminal_color()
    return f"\033[48;5;{code}m"


# Common color constants

BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
YELLOW = Color(255, 255, 0)
CYAN = Color(0, 255, 255)
MAGENTA = Color(255, 0, 255)
GRAY = Color(128, 128, 128)
