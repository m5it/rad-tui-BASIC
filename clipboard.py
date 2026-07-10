#!/usr/bin/env python3
"""
Clipboard module for VB1-DOS Clone v2.1.0
Cross-platform clipboard support with fallback to internal clipboard
"""

import subprocess
import platform
import os

class ClipboardManager:
    """
    Cross-platform clipboard manager with internal fallback
    Supports: Linux (xclip/xsel), macOS (pbcopy/pbpaste), Windows (clip/get-clipboard)
    """
    
    def __init__(self):
        self.system = platform.system()
        self.internal_clipboard = ""
        self.available = False
        self.backend = None
        
        self._detect_backend()
    
    def _detect_backend(self):
        """Detect available clipboard backend"""
        if self.system == "Linux":
            # Check for xclip
            try:
                subprocess.run(["which", "xclip"], check=True, capture_output=True)
                self.backend = "xclip"
                self.available = True
                return
            except:
                pass
            
            # Check for xsel
            try:
                subprocess.run(["which", "xsel"], check=True, capture_output=True)
                self.backend = "xsel"
                self.available = True
                return
            except:
                pass
            
            # Check for wl-copy (Wayland)
            try:
                subprocess.run(["which", "wl-copy"], check=True, capture_output=True)
                self.backend = "wl-copy"
                self.available = True
                return
            except:
                pass
                
        elif self.system == "Darwin":  # macOS
            try:
                subprocess.run(["which", "pbcopy"], check=True, capture_output=True)
                self.backend = "pbcopy"
                self.available = True
                return
            except:
                pass
                
        elif self.system == "Windows":
            # Windows clipboard available via ctypes or win32clipboard
            try:
                import ctypes
                self.backend = "ctypes"
                self.available = True
                return
            except:
                pass
    
    def copy(self, text):
        """
        Copy text to clipboard
        Returns True if successful, False otherwise
        """
        if not text:
            text = ""
        
        # Always update internal clipboard
        self.internal_clipboard = text
        
        if not self.available:
            return True  # Internal clipboard only
        
        try:
            if self.system == "Linux":
                if self.backend == "xclip":
                    subprocess.run(
                        ["xclip", "-selection", "clipboard", "-in"],
                        input=text.encode('utf-8'),
                        check=True,
                        capture_output=True
                    )
                    return True
                    
                elif self.backend == "xsel":
                    subprocess.run(
                        ["xsel", "--clipboard", "--input"],
                        input=text.encode('utf-8'),
                        check=True,
                        capture_output=True
                    )
                    return True
                    
                elif self.backend == "wl-copy":
                    subprocess.run(
                        ["wl-copy"],
                        input=text.encode('utf-8'),
                        check=True,
                        capture_output=True
                    )
                    return True
                    
            elif self.system == "Darwin":  # macOS
                if self.backend == "pbcopy":
                    subprocess.run(
                        ["pbcopy"],
                        input=text.encode('utf-8'),
                        check=True,
                        capture_output=True
                    )
                    return True
                    
            elif self.system == "Windows":
                if self.backend == "ctypes":
                    return self._windows_copy(text)
                    
        except Exception as e:
            print(f"Clipboard copy error: {e}")
            return False
        
        return False
    
    def paste(self):
        """
        Get text from clipboard
        Returns text if successful, empty string otherwise
        """
        if not self.available:
            return self.internal_clipboard
        
        try:
            if self.system == "Linux":
                if self.backend == "xclip":
                    result = subprocess.run(
                        ["xclip", "-selection", "clipboard", "-out"],
                        capture_output=True,
                        check=True
                    )
                    return result.stdout.decode('utf-8')
                    
                elif self.backend == "xsel":
                    result = subprocess.run(
                        ["xsel", "--clipboard", "--output"],
                        capture_output=True,
                        check=True
                    )
                    return result.stdout.decode('utf-8')
                    
                elif self.backend == "wl-copy":
                    # wl-paste is the companion to wl-copy
                    result = subprocess.run(
                        ["wl-paste"],
                        capture_output=True,
                        check=True
                    )
                    return result.stdout.decode('utf-8')
                    
            elif self.system == "Darwin":  # macOS
                if self.backend == "pbcopy":
                    result = subprocess.run(
                        ["pbpaste"],
                        capture_output=True,
                        check=True
                    )
                    return result.stdout.decode('utf-8')
                    
            elif self.system == "Windows":
                if self.backend == "ctypes":
                    return self._windows_paste()
                    
        except Exception as e:
            print(f"Clipboard paste error: {e}")
            return self.internal_clipboard
        
        return self.internal_clipboard
    
    def clear(self):
        """Clear clipboard contents"""
        self.internal_clipboard = ""
        
        if not self.available:
            return True
        
        try:
            if self.system == "Linux":
                if self.backend in ["xclip", "xsel"]:
                    self.copy("")  # Copy empty string
                    return True
                elif self.backend == "wl-copy":
                    subprocess.run(["wl-copy", "--clear"], check=True)
                    return True
                    
            elif self.system == "Darwin":
                self.copy("")  # Copy empty string
                return True
                
            elif self.system == "Windows":
                self.copy("")  # Copy empty string
                return True
                
        except Exception as e:
            print(f"Clipboard clear error: {e}")
            return False
        
        return False
    
    def _windows_copy(self, text):
        """Windows clipboard copy using ctypes"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Open clipboard
            if not ctypes.windll.user32.OpenClipboard(0):
                return False
            
            try:
                # Empty clipboard
                ctypes.windll.user32.EmptyClipboard()
                
                # Allocate global memory
                text_bytes = text.encode('utf-16-le')
                size = len(text_bytes) + 2  # +2 for null terminator
                
                hGlobal = ctypes.windll.kernel32.GlobalAlloc(0x0002, size)  # GMEM_MOVEABLE
                if not hGlobal:
                    return False
                
                # Lock memory and copy text
                lpGlobal = ctypes.windll.kernel32.GlobalLock(hGlobal)
                if lpGlobal:
                    ctypes.memmove(lpGlobal, text_bytes, len(text_bytes))
                    ctypes.windll.kernel32.GlobalUnlock(hGlobal)
                
                # Set clipboard data
                CF_UNICODETEXT = 13
                if ctypes.windll.user32.SetClipboardData(CF_UNICODETEXT, hGlobal):
                    return True
                    
            finally:
                ctypes.windll.user32.CloseClipboard()
                
        except Exception as e:
            print(f"Windows clipboard copy error: {e}")
            return False
        
        return False
    
    def _windows_paste(self):
        """Windows clipboard paste using ctypes"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Open clipboard
            if not ctypes.windll.user32.OpenClipboard(0):
                return ""
            
            try:
                CF_UNICODETEXT = 13
                handle = ctypes.windll.user32.GetClipboardData(CF_UNICODETEXT)
                if not handle:
                    return ""
                
                # Lock memory and read text
                ptr = ctypes.windll.kernel32.GlobalLock(handle)
                if ptr:
                    text = ctypes.wstring_at(ptr)
                    ctypes.windll.kernel32.GlobalUnlock(handle)
                    return text
                    
            finally:
                ctypes.windll.user32.CloseClipboard()
                
        except Exception as e:
            print(f"Windows clipboard paste error: {e}")
            return ""
        
        return ""
    
    def get_status(self):
        """Get clipboard status information"""
        return {
            'system': self.system,
            'backend': self.backend,
            'available': self.available,
            'internal_has_content': bool(self.internal_clipboard)
        }


# Global clipboard instance
_clipboard = None

def get_clipboard():
    """Get global clipboard manager instance"""
    global _clipboard
    if _clipboard is None:
        _clipboard = ClipboardManager()
    return _clipboard

# Convenience functions for runtime
def clipboard_copy(text):
    """Copy text to clipboard"""
    return get_clipboard().copy(text)

def clipboard_paste():
    """Get text from clipboard"""
    return get_clipboard().paste()

def clipboard_clear():
    """Clear clipboard"""
    return get_clipboard().clear()

def clipboard_status():
    """Get clipboard status"""
    return get_clipboard().get_status()


# Test function
def test_clipboard():
    """Test clipboard functionality"""
    print("Clipboard Test")
    print("=" * 50)
    
    cb = get_clipboard()
    status = cb.get_status()
    print(f"System: {status['system']}")
    print(f"Backend: {status['backend']}")
    print(f"Available: {status['available']}")
    print()
    
    # Test copy
    test_text = "Hello from VB1-DOS Clone v2.1.0!"
    print(f"Copying: {test_text}")
    success = clipboard_copy(test_text)
    print(f"Copy result: {'Success' if success else 'Failed'}")
    print()
    
    # Test paste
    print("Pasting...")
    result = clipboard_paste()
    print(f"Pasted: {result}")
    print()
    
    # Verify
    if result == test_text:
        print("✓ Clipboard working correctly!")
    else:
        print("✗ Clipboard mismatch")
        print(f"  Expected: {test_text}")
        print(f"  Got: {result}")
    
    print()
    print("Internal clipboard always available as fallback")


if __name__ == "__main__":
    test_clipboard()
