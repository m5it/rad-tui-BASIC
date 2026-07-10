#!/usr/bin/env python3
"""
Image Display Module for VB1-DOS Clone v2.1.0
ASCII/Unicode art and text-based image support
"""

import os
import re

class ASCIIImage:
    """
    Represents an ASCII/Unicode art image
    """
    
    def __init__(self, width=0, height=0):
        self.width = width
        self.height = height
        self.pixels = []  # 2D array of characters
        self.palette = {}  # Color mappings
        self.transparent_char = None
    
    def load_from_file(self, filename):
        """
        Load image from file
        Supports: .txt (raw ASCII), .xpm (X PixMap format)
        """
        if not os.path.exists(filename):
            return False
        
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.xpm':
            return self._load_xpm(filename)
        elif ext == '.txt':
            return self._load_ascii(filename)
        else:
            # Try to auto-detect
            return self._load_ascii(filename)
    
    def _load_ascii(self, filename):
        """Load raw ASCII art file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            self.pixels = [list(line.rstrip('\n')) for line in lines]
            self.height = len(self.pixels)
            self.width = max(len(line) for line in self.pixels) if self.pixels else 0
            
            # Pad lines to same width
            for row in self.pixels:
                while len(row) < self.width:
                    row.append(' ')
            
            return True
            
        except Exception as e:
            print(f"Error loading ASCII file: {e}")
            return False
    
    def _load_xpm(self, filename):
        """
        Load XPM (X PixMap) file
        XPM format: C-style array with color definitions
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse XPM format
            # Look for width, height, colors, chars per pixel
            header_match = re.search(r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', content)
            if not header_match:
                return False
            
            width, height, num_colors, cpp = map(int, header_match.groups())
            
            self.width = width
            self.height = height
            
            # Parse color definitions
            colors_section = re.findall(r'"([^"]{1,2})\s+c\s+([^"]+)"', content)
            for char_code, color in colors_section:
                self.palette[char_code] = color.strip()
            
            # Parse pixel data
            pixel_lines = re.findall(r'"([^"]+)"\s*,?', content)
            # Skip header and color definitions
            start_idx = 1 + num_colors
            pixel_lines = pixel_lines[start_idx:start_idx + height]
            
            self.pixels = []
            for line in pixel_lines:
                row = []
                for i in range(0, len(line), cpp):
                    char_code = line[i:i+cpp]
                    # Map to display character
                    if char_code in self.palette:
                        color = self.palette[char_code]
                        if color.lower() in ['none', 'transparent']:
                            row.append(' ')
                        else:
                            # Use different characters based on color
                            row.append(self._color_to_char(color))
                    else:
                        row.append(char_code[0] if char_code else ' ')
                self.pixels.append(row)
            
            return True
            
        except Exception as e:
            print(f"Error loading XPM file: {e}")
            return False
    
    def _color_to_char(self, color):
        """Map color name to display character"""
        color_map = {
            'black': '█',
            'white': ' ',
            'red': '▓',
            'green': '░',
            'blue': '▒',
            'yellow': '▚',
            'cyan': '▞',
            'magenta': '▘',
            'gray': '▝',
            'grey': '▝',
        }
        return color_map.get(color.lower(), '▒')
    
    def resize(self, new_width, new_height):
        """
        Simple resize using nearest neighbor
        """
        if not self.pixels:
            return
        
        new_pixels = []
        for y in range(new_height):
            src_y = int(y * self.height / new_height)
            row = []
            for x in range(new_width):
                src_x = int(x * self.width / new_width)
                if src_y < len(self.pixels) and src_x < len(self.pixels[src_y]):
                    row.append(self.pixels[src_y][src_x])
                else:
                    row.append(' ')
            new_pixels.append(row)
        
        self.pixels = new_pixels
        self.width = new_width
        self.height = new_height
    
    def get_line(self, y):
        """Get line at y position"""
        if 0 <= y < len(self.pixels):
            return ''.join(self.pixels[y])
        return ' ' * self.width
    
    def crop(self, x, y, width, height):
        """Crop image to region"""
        cropped = ASCIIImage(width, height)
        cropped.pixels = []
        
        for row_y in range(y, min(y + height, self.height)):
            row = []
            for col_x in range(x, min(x + width, self.width)):
                if row_y < len(self.pixels) and col_x < len(self.pixels[row_y]):
                    row.append(self.pixels[row_y][col_x])
                else:
                    row.append(' ')
            cropped.pixels.append(row)
        
        return cropped


class ImageList:
    """
    List of images for animation/sprites
    """
    
    def __init__(self):
        self.images = []
        self.current_index = 0
    
    def add_image(self, image):
        """Add image to list"""
        self.images.append(image)
    
    def load_from_files(self, file_pattern):
        """
        Load multiple images matching pattern
        e.g., "sprite_*.txt"
        """
        import glob
        files = sorted(glob.glob(file_pattern))
        for f in files:
            img = ASCIIImage()
            if img.load_from_file(f):
                self.images.append(img)
    
    def get_current(self):
        """Get current image"""
        if 0 <= self.current_index < len(self.images):
            return self.images[self.current_index]
        return None
    
    def next_frame(self):
        """Advance to next frame"""
        if self.images:
            self.current_index = (self.current_index + 1) % len(self.images)
    
    def prev_frame(self):
        """Go to previous frame"""
        if self.images:
            self.current_index = (self.current_index - 1) % len(self.images)


class PictureBox:
    """
    Enhanced Picture Box control for ASCII/Unicode art
    """
    
    def __init__(self, x=1, y=1, w=20, h=10):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.image = None
        self.image_list = None
        self.auto_size = False
        self.stretch = False
        self.center = True
        self.border = True
        self.on_click = None
        self.animation_running = False
        self.animation_delay = 0.5  # seconds
    
    def load_image(self, filename):
        """Load image from file"""
        self.image = ASCIIImage()
        return self.image.load_from_file(filename)
    
    def set_image(self, image):
        """Set image directly"""
        self.image = image
        if self.auto_size and image:
            self.w = min(image.width + 2, 80)
            self.h = min(image.height + 2, 25)
    
    def create_animation(self, file_pattern):
        """Create animation from file pattern"""
        self.image_list = ImageList()
        self.image_list.load_from_files(file_pattern)
        if self.image_list.images:
            self.image = self.image_list.get_current()
    
    def start_animation(self):
        """Start animation playback"""
        self.animation_running = True
    
    def stop_animation(self):
        """Stop animation"""
        self.animation_running = False
    
    def update_animation(self):
        """Update animation frame"""
        if self.animation_running and self.image_list:
            self.image_list.next_frame()
            self.image = self.image_list.get_current()
    
    def draw(self, stdscr, colors, box_chars):
        """Draw picture box"""
        C_BORDER = colors.get('border', 0)
        C_BG = colors.get('bg', 0)
        
        # Draw border
        if self.border:
            top = box_chars['tl'] + box_chars['h'] * (self.w - 2) + box_chars['tr']
            stdscr.addstr(self.y, self.x, top, C_BORDER)
            for i in range(1, self.h - 1):
                stdscr.addstr(self.y + i, self.x, box_chars['v'], C_BORDER)
                stdscr.addstr(self.y + i, self.x + self.w - 1, box_chars['v'], C_BORDER)
            bottom = box_chars['bl'] + box_chars['h'] * (self.w - 2) + box_chars['br']
            stdscr.addstr(self.y + self.h - 1, self.x, bottom, C_BORDER)
        
        # Clear interior
        for row in range(1, self.h - 1):
            for col in range(1, self.w - 1):
                try:
                    stdscr.addstr(self.y + row, self.x + col, ' ', C_BG)
                except:
                    pass
        
        # Draw image
        if self.image:
            self._draw_image(stdscr, colors)
    
    def _draw_image(self, stdscr, colors):
        """Draw the image inside the box"""
        C_BG = colors.get('bg', 0)
        
        # Calculate position
        content_w = self.w - 2
        content_h = self.h - 2
        
        if self.stretch:
            # Resize image to fit
            self.image.resize(content_w, content_h)
        
        img_w = min(self.image.width, content_w)
        img_h = min(self.image.height, content_h)
        
        if self.center:
            start_x = self.x + 1 + (content_w - img_w) // 2
            start_y = self.y + 1 + (content_h - img_h) // 2
        else:
            start_x = self.x + 1
            start_y = self.y + 1
        
        # Draw image lines
        for row in range(img_h):
            line = self.image.get_line(row)[:img_w]
            try:
                stdscr.addstr(start_y + row, start_x, line, C_BG)
            except:
                pass
    
    def hit_test(self, mx, my):
        """Check if point is inside picture box"""
        return (self.x <= mx < self.x + self.w and 
                self.y <= my < self.y + self.h)
    
    def handle_click(self, mx, my):
        """Handle click event"""
        if self.hit_test(mx, my) and self.on_click:
            self.on_click(self)


# Sample ASCII art images
SAMPLE_IMAGES = {
    "smiley": """
  ██████  
 ██  █ ██ 
 █ ████ █ 
 ██  █ ██ 
  ██████  
""",
    
    "heart": """
 ██   ██  
████ ████ 
██████████ 
 ███████  
  █████   
   ███    
    █     
""",
    
    "star": """
    █    
   ███   
  █████  
█████████
  █████  
 ███████ 
█████████
""",
    
    "computer": """
  ████████
  █      █
  ████████
     ██   
  ████████
  █      █
  ████████
"""
}

def load_sample_image(name):
    """Load a sample image by name"""
    if name in SAMPLE_IMAGES:
        img = ASCIIImage()
        lines = SAMPLE_IMAGES[name].strip('\n').split('\n')
        img.pixels = [list(line) for line in lines]
        img.height = len(img.pixels)
        img.width = max(len(line) for line in img.pixels)
        
        # Pad lines
        for row in img.pixels:
            while len(row) < img.width:
                row.append(' ')
        
        return img
    return None


# Test
if __name__ == "__main__":
    import curses
    
    def main(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        
        colors = {
            'border': curses.A_BOLD,
            'bg': 0,
        }
        
        box_chars = {
            'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
            'h': '─', 'v': '│'
        }
        
        # Create picture boxes with sample images
        pictures = []
        
        for i, name in enumerate(['smiley', 'heart', 'star']):
            pic = PictureBox(5 + i * 15, 5, 12, 8)
            pic.set_image(load_sample_image(name))
            pictures.append(pic)
        
        # Animation picture
        anim_pic = PictureBox(5, 15, 12, 8)
        anim_pic.image_list = ImageList()
        for name in ['smiley', 'heart', 'star']:
            anim_pic.image_list.add_image(load_sample_image(name))
        anim_pic.image = anim_pic.image_list.get_current()
        anim_pic.start_animation()
        
        last_update = 0
        
        while True:
            stdscr.clear()
            
            # Draw all pictures
            for pic in pictures:
                pic.draw(stdscr, colors, box_chars)
            
            # Update and draw animation
            current_time = time.time()
            if current_time - last_update > 0.5:
                anim_pic.update_animation()
                last_update = current_time
            anim_pic.draw(stdscr, colors, box_chars)
            
            stdscr.addstr(0, 0, "Image Display Test - Q to quit")
            stdscr.refresh()
            
            ch = stdscr.getch()
            if ch == ord('q') or ch == ord('Q'):
                break
            
            time.sleep(0.05)
    
    import time
    curses.wrapper(main)
