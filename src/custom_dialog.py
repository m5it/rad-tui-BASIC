"""
Custom Dialog Module for RAD-TUI v2.2.0
Provides user-defined dialog boxes with custom layouts
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Callable


class DialogResult(Enum):
    """Standard dialog results"""
    NONE = 0
    OK = 1
    CANCEL = 2
    YES = 3
    NO = 4
    ABORT = 5
    RETRY = 6
    IGNORE = 7


class DialogButton:
    """Button in a custom dialog"""
    
    def __init__(self, text: str, result: DialogResult, 
                 default: bool = False, cancel: bool = False):
        self.text = text
        self.result = result
        self.default = default
        self.cancel = cancel
        self.enabled = True
        self.visible = True


class CustomDialog:
    """Custom dialog with user-defined layout"""
    
    def __init__(self, name_id: str = "customDialog1", 
                 title: str = "Dialog", width: int = 40, height: int = 15):
        self.name_id = name_id
        self.title = title
        self.width = width
        self.height = height
        
        self.controls = []
        self.buttons = []
        
        self.modal = True
        self.result = DialogResult.NONE
        self.values = {}
        self.visible = False
        
        self.x = 0
        self.y = 0
        self.center_on_parent = True
        
        self.on_dialog_open = None
        self.on_dialog_close = None
        self.on_dialog_result = None
        
        self._add_standard_buttons()
        
    def _add_standard_buttons(self):
        """Add OK and Cancel buttons by default"""
        self.buttons = [
            DialogButton("OK", DialogResult.OK, default=True),
            DialogButton("Cancel", DialogResult.CANCEL, cancel=True)
        ]
        
    def add_control(self, control):
        """Add a control to the dialog"""
        self.controls.append(control)
        control.parent = self
        
    def remove_control(self, control):
        """Remove a control from the dialog"""
        if control in self.controls:
            self.controls.remove(control)
            control.parent = None
            
    def add_button(self, text: str, result: DialogResult,
                   default: bool = False, cancel: bool = False):
        """Add a button to the dialog"""
        button = DialogButton(text, result, default, cancel)
        self.buttons.append(button)
        return button
        
    def clear_buttons(self):
        """Remove all buttons"""
        self.buttons = []
        
    def show_dialog(self, modal: bool = True, 
                   parent_x: int = 0, parent_y: int = 0,
                   parent_width: int = 80, parent_height: int = 24) -> DialogResult:
        """Show the dialog"""
        self.modal = modal
        
        if self.center_on_parent:
            self.x = parent_x + (parent_width - self.width) // 2
            self.y = parent_y + (parent_height - self.height) // 2
        else:
            self.x = parent_x + 10
            self.y = parent_y + 5
            
        self.visible = True
        self.result = DialogResult.NONE
        
        if self.on_dialog_open:
            self.on_dialog_open()
            
        return self.result
        
    def close_dialog(self, result: DialogResult = DialogResult.CANCEL):
        """Close the dialog with result"""
        self.result = result
        self.visible = False
        
        self._extract_values()
        
        if self.on_dialog_result:
            self.on_dialog_result(result, self.values)
            
        if self.on_dialog_close:
            self.on_dialog_close()
            
    def _extract_values(self):
        """Extract values from controls into values dict"""
        self.values = {}
        for control in self.controls:
            if hasattr(control, 'name_id') and hasattr(control, 'caption'):
                self.values[control.name_id] = control.caption
                
    def get_values(self) -> Dict[str, Any]:
        """Get extracted values from dialog"""
        return self.values
        
    def get_value(self, control_name: str) -> Any:
        """Get value of specific control"""
        return self.values.get(control_name)
        
    def set_value(self, control_name: str, value: Any):
        """Set value of specific control"""
        for control in self.controls:
            if hasattr(control, 'name_id') and control.name_id == control_name:
                if hasattr(control, 'caption'):
                    control.caption = str(value)
                break
                
    def handle_button_click(self, button: DialogButton):
        """Handle dialog button click"""
        self.close_dialog(button.result)
        
    def render(self, screen):
        """Render the dialog"""
        if not self.visible:
            return
            
        self._render_frame(screen)
        self._render_title(screen)
        
        for control in self.controls:
            if hasattr(control, 'render'):
                control.render(screen)
                
        self._render_buttons(screen)
        
    def _render_frame(self, screen):
        """Draw dialog border"""
        pass
        
    def _render_title(self, screen):
        """Draw title bar"""
        title_x = self.x + (self.width - len(self.title)) // 2
        title_y = self.y
        
    def _render_buttons(self, screen):
        """Draw dialog buttons at bottom"""
        if not self.buttons:
            return
            
        button_y = self.y + self.height - 2
        total_width = sum(len(b.text) + 4 for b in self.buttons) + len(self.buttons) - 1
        start_x = self.x + (self.width - total_width) // 2
        
        current_x = start_x
        for button in self.buttons:
            if not button.visible:
                continue
                
            text = f" {button.text} "
            current_x += len(text) + 1


def create_input_dialog(title: str, prompt: str, 
                       default_value: str = "") -> CustomDialog:
    """Create a simple input dialog"""
    dialog = CustomDialog(title=title, width=50, height=8)
    return dialog


def create_confirm_dialog(title: str, message: str,
                          yes_no: bool = False) -> CustomDialog:
    """Create a confirmation dialog"""
    dialog = CustomDialog(title=title, width=40, height=8)
    
    dialog.clear_buttons()
    if yes_no:
        dialog.add_button("Yes", DialogResult.YES, default=True)
        dialog.add_button("No", DialogResult.NO, cancel=True)
    else:
        dialog.add_button("OK", DialogResult.OK, default=True)
        dialog.add_button("Cancel", DialogResult.CANCEL, cancel=True)
        
    return dialog


def create_progress_dialog(title: str, message: str = "Please wait...") -> CustomDialog:
    """Create a progress dialog"""
    dialog = CustomDialog(title=title, width=50, height=6)
    dialog.clear_buttons()
    return dialog


def create_list_dialog(title: str, items: List[str],
                       multi_select: bool = False) -> CustomDialog:
    """Create a list selection dialog"""
    dialog = CustomDialog(title=title, width=40, height=15)
    return dialog


class DialogManager:
    """Manages multiple dialogs"""
    
    def __init__(self):
        self.dialogs = []
        self.active_dialog = None
        
    def show_dialog(self, dialog: CustomDialog) -> DialogResult:
        """Show dialog and manage stack"""
        self.dialogs.append(dialog)
        self.active_dialog = dialog
        
        result = dialog.show_dialog()
        
        if dialog in self.dialogs:
            self.dialogs.remove(dialog)
            
        self.active_dialog = self.dialogs[-1] if self.dialogs else None
        
        return result
        
    def close_all(self):
        """Close all open dialogs"""
        for dialog in self.dialogs:
            dialog.close_dialog(DialogResult.CANCEL)
        self.dialogs = []
        self.active_dialog = None
