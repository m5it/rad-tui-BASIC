#!/usr/bin/env python3
"""
Template System for VB1-DOS Clone v2.1.0
Built-in and custom templates for rapid application development
"""

import json
import os
from datetime import datetime

# ==========================================================
# BUILT-IN TEMPLATES
# ==========================================================

BUILTIN_TEMPLATES = {
    "text_editor": {
        "name": "Text Editor",
        "description": "Simple text editor with file operations",
        "category": "Productivity",
        "author": "VB1-DOS Clone",
        "version": "1.0",
        "form": {
            "x": 15,
            "y": 3,
            "w": 60,
            "h": 20,
            "title": "Text Editor",
            "menu_count": 3,
            "menu_items": [
                {"caption": "File", "name_id": "mnuFile", "parent": 0, "has_submenu": True},
                {"caption": "New", "name_id": "mnuNew", "parent": 1, "has_submenu": False},
                {"caption": "Open", "name_id": "mnuOpen", "parent": 1, "has_submenu": False},
                {"caption": "Save", "name_id": "mnuSave", "parent": 1, "has_submenu": False}
            ],
            "controls": [
                {
                    "x": 2, "y": 2, "w": 56, "h": 1,
                    "tool_type": 13, "name_id": "txtFilename",
                    "caption": "untitled.txt",
                    "code": "def on_change_txtFilename():\n    pass\n",
                    "checked": False, "group": "", "parent": 0,
                    "items": [], "selected_index": -1, "scroll_offset": 0
                },
                {
                    "x": 2, "y": 4, "w": 56, "h": 12,
                    "tool_type": 10, "name_id": "lstContent",
                    "caption": "Content",
                    "code": "def on_change_lstContent():\n    pass\n",
                    "items": ["Line 1", "Line 2", "Line 3"],
                    "selected_index": -1, "scroll_offset": 0
                },
                {
                    "x": 2, "y": 17, "w": 12, "h": 3,
                    "tool_type": 3, "name_id": "btnNew",
                    "caption": "New",
                    "code": "def on_click_btnNew():\n    lstContent.items = []\n    txtFilename.caption = 'untitled.txt'\n    msgbox('New file created')\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 16, "y": 17, "w": 12, "h": 3,
                    "tool_type": 3, "name_id": "btnOpen",
                    "caption": "Open",
                    "code": "def on_click_btnOpen():\n    filename = file_dialog('open', ['.txt'])\n    if filename:\n        txtFilename.caption = filename\n        handle = open_file(filename, 'r')\n        if handle:\n            lstContent.items = []\n            line = read_line(handle)\n            while line is not None:\n                lstContent.items.append(line)\n                line = read_line(handle)\n            close_file(handle)\n            msgbox('File loaded: ' + filename)\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 30, "y": 17, "w": 12, "h": 3,
                    "tool_type": 3, "name_id": "btnSave",
                    "caption": "Save",
                    "code": "def on_click_btnSave():\n    filename = txtFilename.caption\n    handle = open_file(filename, 'w')\n    if handle:\n        for line in lstContent.items:\n            write_line(handle, line)\n        close_file(handle)\n        msgbox('File saved: ' + filename)\n",
                    "checked": False, "group": "", "parent": 0
                }
            ]
        }
    },
    
    "database_browser": {
        "name": "Database Browser",
        "description": "Browse and edit database records",
        "category": "Database",
        "author": "VB1-DOS Clone",
        "version": "1.0",
        "form": {
            "x": 10,
            "y": 2,
            "w": 70,
            "h": 22,
            "title": "Customer Database",
            "menu_count": 0,
            "menu_items": [],
            "controls": [
                {
                    "x": 2, "y": 2, "w": 30, "h": 10,
                    "tool_type": 16, "name_id": "gridCustomers",
                    "caption": "Customers",
                    "code": "def on_cell_click_gridCustomers():\n    row, col = gridCustomers.grid_selected_cell\n    if row >= 0:\n        txtName.caption = gridCustomers.grid_data[row][0]\n        txtEmail.caption = gridCustomers.grid_data[row][1]\n        txtPhone.caption = gridCustomers.grid_data[row][2]\n",
                    "grid_data": [
                        ["John Smith", "john@email.com", "555-0101"],
                        ["Jane Doe", "jane@email.com", "555-0102"],
                        ["Bob Wilson", "bob@email.com", "555-0103"]
                    ],
                    "grid_headers": ["Name", "Email", "Phone"],
                    "grid_col_widths": [20, 25, 15],
                    "grid_row_count": 3,
                    "grid_col_count": 3
                },
                {
                    "x": 35, "y": 2, "w": 32, "h": 8,
                    "tool_type": 7, "name_id": "fraDetails",
                    "caption": "Details",
                    "code": "",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 37, "y": 4, "w": 28, "h": 1,
                    "tool_type": 13, "name_id": "txtName",
                    "caption": "",
                    "code": "",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 37, "y": 6, "w": 28, "h": 1,
                    "tool_type": 13, "name_id": "txtEmail",
                    "caption": "",
                    "code": "",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 37, "y": 8, "w": 28, "h": 1,
                    "tool_type": 13, "name_id": "txtPhone",
                    "caption": "",
                    "code": "",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 2, "y": 14, "w": 10, "h": 3,
                    "tool_type": 3, "name_id": "btnFirst",
                    "caption": "First",
                    "code": "def on_click_btnFirst():\n    if len(gridCustomers.grid_data) > 0:\n        gridCustomers.grid_selected_cell = (0, 0)\n        on_cell_click_gridCustomers()\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 14, "y": 14, "w": 10, "h": 3,
                    "tool_type": 3, "name_id": "btnPrev",
                    "caption": "Prev",
                    "code": "def on_click_btnPrev():\n    row, col = gridCustomers.grid_selected_cell\n    if row > 0:\n        gridCustomers.grid_selected_cell = (row - 1, col)\n        on_cell_click_gridCustomers()\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 26, "y": 14, "w": 10, "h": 3,
                    "tool_type": 3, "name_id": "btnNext",
                    "caption": "Next",
                    "code": "def on_click_btnNext():\n    row, col = gridCustomers.grid_selected_cell\n    if row < len(gridCustomers.grid_data) - 1:\n        gridCustomers.grid_selected_cell = (row + 1, col)\n        on_cell_click_gridCustomers()\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 38, "y": 14, "w": 10, "h": 3,
                    "tool_type": 3, "name_id": "btnLast",
                    "caption": "Last",
                    "code": "def on_click_btnLast():\n    if len(gridCustomers.grid_data) > 0:\n        gridCustomers.grid_selected_cell = (len(gridCustomers.grid_data) - 1, 0)\n        on_cell_click_gridCustomers()\n",
                    "checked": False, "group": "", "parent": 0
                }
            ]
        }
    },
    
    "calculator": {
        "name": "Calculator",
        "description": "Basic calculator with arithmetic operations",
        "category": "Utilities",
        "author": "VB1-DOS Clone",
        "version": "1.0",
        "form": {
            "x": 20,
            "y": 4,
            "w": 40,
            "h": 20,
            "title": "Calculator",
            "menu_count": 0,
            "menu_items": [],
            "controls": [
                {
                    "x": 2, "y": 2, "w": 36, "h": 1,
                    "tool_type": 13, "name_id": "txtDisplay",
                    "caption": "0",
                    "code": "",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 2, "y": 5, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btn7",
                    "caption": "7",
                    "code": "def on_click_btn7():\n    if txtDisplay.caption == '0':\n        txtDisplay.caption = '7'\n    else:\n        txtDisplay.caption = txtDisplay.caption + '7'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 11, "y": 5, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btn8",
                    "caption": "8",
                    "code": "def on_click_btn8():\n    if txtDisplay.caption == '0':\n        txtDisplay.caption = '8'\n    else:\n        txtDisplay.caption = txtDisplay.caption + '8'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 20, "y": 5, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btn9",
                    "caption": "9",
                    "code": "def on_click_btn9():\n    if txtDisplay.caption == '0':\n        txtDisplay.caption = '9'\n    else:\n        txtDisplay.caption = txtDisplay.caption + '9'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 29, "y": 5, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btnDiv",
                    "caption": "/",
                    "code": "def on_click_btnDiv():\n    txtDisplay.caption = txtDisplay.caption + '/'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 2, "y": 9, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btn4",
                    "caption": "4",
                    "code": "def on_click_btn4():\n    if txtDisplay.caption == '0':\n        txtDisplay.caption = '4'\n    else:\n        txtDisplay.caption = txtDisplay.caption + '4'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 11, "y": 9, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btn5",
                    "caption": "5",
                    "code": "def on_click_btn5():\n    if txtDisplay.caption == '0':\n        txtDisplay.caption = '5'\n    else:\n        txtDisplay.caption = txtDisplay.caption + '5'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 20, "y": 9, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btn6",
                    "caption": "6",
                    "code": "def on_click_btn6():\n    if txtDisplay.caption == '0':\n        txtDisplay.caption = '6'\n    else:\n        txtDisplay.caption = txtDisplay.caption + '6'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 29, "y": 9, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btnMul",
                    "caption": "*",
                    "code": "def on_click_btnMul():\n    txtDisplay.caption = txtDisplay.caption + '*'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 2, "y": 13, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btn1",
                    "caption": "1",
                    "code": "def on_click_btn1():\n    if txtDisplay.caption == '0':\n        txtDisplay.caption = '1'\n    else:\n        txtDisplay.caption = txtDisplay.caption + '1'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 11, "y": 13, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btn2",
                    "caption": "2",
                    "code": "def on_click_btn2():\n    if txtDisplay.caption == '0':\n        txtDisplay.caption = '2'\n    else:\n        txtDisplay.caption = txtDisplay.caption + '2'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 20, "y": 13, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btn3",
                    "caption": "3",
                    "code": "def on_click_btn3():\n    if txtDisplay.caption == '0':\n        txtDisplay.caption = '3'\n    else:\n        txtDisplay.caption = txtDisplay.caption + '3'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 29, "y": 13, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btnSub",
                    "caption": "-",
                    "code": "def on_click_btnSub():\n    txtDisplay.caption = txtDisplay.caption + '-'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 2, "y": 17, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btnClear",
                    "caption": "C",
                    "code": "def on_click_btnClear():\n    txtDisplay.caption = '0'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 11, "y": 17, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btn0",
                    "caption": "0",
                    "code": "def on_click_btn0():\n    if txtDisplay.caption != '0':\n        txtDisplay.caption = txtDisplay.caption + '0'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 20, "y": 17, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btnEquals",
                    "caption": "=",
                    "code": "def on_click_btnEquals():\n    try:\n        result = eval(txtDisplay.caption)\n        txtDisplay.caption = str(result)\n    except:\n        txtDisplay.caption = 'Error'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 29, "y": 17, "w": 8, "h": 3,
                    "tool_type": 3, "name_id": "btnAdd",
                    "caption": "+",
                    "code": "def on_click_btnAdd():\n    txtDisplay.caption = txtDisplay.caption + '+'\n",
                    "checked": False, "group": "", "parent": 0
                }
            ]
        }
    },
    
    "form_wizard": {
        "name": "Form Wizard",
        "description": "Multi-step data entry wizard",
        "category": "Wizard",
        "author": "VB1-DOS Clone",
        "version": "1.0",
        "form": {
            "x": 15,
            "y": 4,
            "w": 50,
            "h": 16,
            "title": "Registration Wizard",
            "menu_count": 0,
            "menu_items": [],
            "controls": [
                {
                    "x": 2, "y": 2, "w": 46, "h": 1,
                    "tool_type": 9, "name_id": "lblStep",
                    "caption": "Step 1 of 3: Personal Information",
                    "code": "",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 2, "y": 4, "w": 10, "h": 1,
                    "tool_type": 9, "name_id": "lblName",
                    "caption": "Name:",
                    "code": "",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 13, "y": 4, "w": 34, "h": 1,
                    "tool_type": 13, "name_id": "txtName",
                    "caption": "",
                    "code": "",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 2, "y": 6, "w": 10, "h": 1,
                    "tool_type": 9, "name_id": "lblEmail",
                    "caption": "Email:",
                    "code": "",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 13, "y": 6, "w": 34, "h": 1,
                    "tool_type": 13, "name_id": "txtEmail",
                    "caption": "",
                    "code": "",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 2, "y": 9, "w": 46, "h": 4,
                    "tool_type": 7, "name_id": "fraProgress",
                    "caption": "Progress",
                    "code": "",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 4, "y": 11, "w": 42, "h": 1,
                    "tool_type": 9, "name_id": "lblProgress",
                    "caption": "[====>     ] 33%",
                    "code": "",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 2, "y": 14, "w": 12, "h": 3,
                    "tool_type": 3, "name_id": "btnBack",
                    "caption": "< Back",
                    "code": "def on_click_btnBack():\n    msgbox('Going back to previous step')\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 19, "y": 14, "w": 12, "h": 3,
                    "tool_type": 3, "name_id": "btnNext",
                    "caption": "Next >",
                    "code": "def on_click_btnNext():\n    if len(txtName.caption) == 0:\n        msgbox('Please enter your name', 'Validation', 'ok')\n    elif len(txtEmail.caption) == 0:\n        msgbox('Please enter your email', 'Validation', 'ok')\n    else:\n        msgbox('Proceeding to next step...')\n        lblStep.caption = 'Step 2 of 3: Contact Information'\n        lblProgress.caption = '[=======>  ] 66%'\n",
                    "checked": False, "group": "", "parent": 0
                },
                {
                    "x": 36, "y": 14, "w": 12, "h": 3,
                    "tool_type": 3, "name_id": "btnCancel",
                    "caption": "Cancel",
                    "code": "def on_click_btnCancel():\n    result = msgbox('Cancel wizard?', 'Confirm', 'yesno')\n    if result == 'yes':\n        msgbox('Wizard cancelled')\n",
                    "checked": False, "group": "", "parent": 0
                }
            ]
        }
    }
}

# ==========================================================
# TEMPLATE MANAGER
# ==========================================================

class TemplateManager:
    def __init__(self, templates_dir="templates"):
        self.templates_dir = templates_dir
        self.custom_templates = {}
        self._ensure_directory()
        self._load_custom_templates()
    
    def _ensure_directory(self):
        """Ensure templates directory exists"""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
    
    def _load_custom_templates(self):
        """Load custom templates from directory"""
        if not os.path.exists(self.templates_dir):
            return
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                template_id = filename[:-5]
                try:
                    with open(os.path.join(self.templates_dir, filename), 'r') as f:
                        self.custom_templates[template_id] = json.load(f)
                except:
                    pass
    
    def get_all_templates(self):
        """Get all templates (built-in and custom)"""
        all_templates = {}
        all_templates.update(BUILTIN_TEMPLATES)
        all_templates.update(self.custom_templates)
        return all_templates
    
    def get_template(self, template_id):
        """Get a specific template"""
        if template_id in BUILTIN_TEMPLATES:
            return BUILTIN_TEMPLATES[template_id]
        return self.custom_templates.get(template_id)
    
    def save_as_template(self, form_data, name, description="", author="", category="Custom"):
        """Save current project as custom template"""
        template_id = name.lower().replace(" ", "_")
        
        template = {
            "name": name,
            "description": description,
            "category": category,
            "author": author,
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "form": form_data
        }
        
        # Save to file
        filename = os.path.join(self.templates_dir, f"{template_id}.json")
        try:
            with open(filename, 'w') as f:
                json.dump(template, f, indent=2)
            self.custom_templates[template_id] = template
            return True
        except Exception as e:
            print(f"Error saving template: {e}")
            return False
    
    def delete_template(self, template_id):
        """Delete a custom template"""
        if template_id in self.custom_templates:
            filename = os.path.join(self.templates_dir, f"{template_id}.json")
            try:
                os.remove(filename)
                del self.custom_templates[template_id]
                return True
            except:
                pass
        return False
    
    def get_categories(self):
        """Get list of template categories"""
        categories = set()
        for template in self.get_all_templates().values():
            categories.add(template.get("category", "Uncategorized"))
        return sorted(categories)


# Global template manager
_template_manager = None

def get_template_manager():
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
    return _template_manager


# Test
if __name__ == "__main__":
    print("Template System Test")
    print("=" * 50)
    
    tm = get_template_manager()
    
    print(f"\nAvailable templates: {len(tm.get_all_templates())}")
    print(f"Categories: {tm.get_categories()}")
    
    print("\nTemplates:")
    for tid, template in tm.get_all_templates().items():
        print(f"  - {tid}: {template['name']} ({template['category']})")
    
    # Test saving
    print("\nTesting save template...")
    test_form = {
        "x": 10, "y": 10, "w": 30, "h": 10,
        "title": "Test Form",
        "controls": []
    }
    result = tm.save_as_template(test_form, "My Test", "A test template", "User", "Test")
    print(f"Save result: {result}")
    
    print(f"\nTemplates after save: {len(tm.get_all_templates())}")
