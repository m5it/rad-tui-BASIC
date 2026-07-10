# Advanced Controls Guide for RAD-TUI v2.2.0

## Table of Contents

1. [Introduction](#introduction)
2. [TreeView](#treeview)
3. [TabControl](#tabcontrol)
4. [Splitter](#splitter)
5. [Toolbar](#toolbar)
6. [StatusBar](#statusbar)
7. [Combining Advanced Controls](#combining-advanced-controls)
8. [Best Practices](#best-practices)

---

## Introduction

RAD-TUI v2.2.0 introduces five advanced layout and navigation controls that enable complex user interfaces in terminal applications. This guide covers TreeView, TabControl, Splitter, Toolbar, and StatusBar with practical examples.

---

## TreeView

Hierarchical data display with expandable nodes.

### Basic Usage

```python
# Create TreeView
tree = TreeView(
    name_id="fileTree",
    x=2,
    y=2,
    width=30,
    height=15
)

# Add root nodes
root = tree.add_root_node("My Computer", icon="C")
documents = tree.add_root_node("Documents", icon="D")

# Add child nodes
work = root.add_child("Work", icon="F")
work.add_child("Project A", icon="f")
work.add_child("Project B", icon="f")

# Personal folder
personal = documents.add_child("Personal", icon="F")
personal.add_child("Photos", icon="P")
personal.add_child("Music", icon="M")

# Expand by default
tree.expand_node(root)
tree.expand_node(documents)
```

### Icons

```python
# Common icon characters
icons = {
    'C': '🖥',  # Computer
    'D': '📁',  # Directory
    'F': '📂',  # Folder
    'f': '📄',  # File
    'P': '📷',  # Pictures
    'M': '🎵',  # Music
    'T': '🗀',  # Trash
    'H': '🏠',  # Home
    '*': '⭐',  # Favorite
}
```

### Event Handling

```python
def on_node_click_tree():
    """Handle node click"""
    node = tree.get_selected()
    if node:
        print(f"Selected: {node.text}")
        
        # Check if has children
        if node.has_children():
            print(f"  Contains {len(node.children)} items")
            
        # Get full path
        path = get_full_path(node)
        print(f"  Path: {path}")

def on_node_expand_tree():
    """Lazy loading example"""
    node = tree.get_selected()
    if node and node.tag == "needs_loading":
        # Load children dynamically
        load_directory_contents(node)
        
def get_full_path(node):
    """Build full path from root"""
    parts = []
    current = node
    while current:
        parts.append(current.text)
        current = current.parent
    return " > ".join(reversed(parts))
```

### Selection and Navigation

```python
# Programmatic selection
node = tree.get_node_at_index(5)
tree.select_node(node)

# Get selected
selected = tree.get_selected()
if selected:
    print(f"Currently selected: {selected.text}")

# Expand/collapse
tree.expand_node(node)      # Expand specific node
tree.collapse_node(node)    # Collapse specific node
tree.toggle_node(node)      # Toggle state

# Expand/collapse all
expand_all_nodes(tree)
collapse_all_nodes(tree)
```

### Search

```python
def find_node(tree, text):
    """Find node by text"""
    def search_recursive(nodes):
        for node in nodes:
            if node.text == text:
                return node
            if node.children:
                found = search_recursive(node.children)
                if found:
                    return found
        return None
    
    return search_recursive(tree.root_nodes)

# Usage
found = find_node(tree, "Project A")
if found:
    tree.select_node(found)
    tree.expand_node(found.parent)
```

### Practical Example: File Browser

```python
class FileBrowser:
    def __init__(self):
        self.tree = TreeView(name_id="treeFiles", x=2, y=2, width=35, height=18)
        self.current_path = ""
        
    def load_directory(self, path, parent_node=None):
        """Load directory contents"""
        import os
        
        if parent_node is None:
            self.tree.clear()
            parent_node = self.tree.add_root_node(os.path.basename(path) or path, icon="D")
            parent_node.tag = path
            
        try:
            items = os.listdir(path)
            for item in sorted(items):
                item_path = os.path.join(path, item)
                is_dir = os.path.isdir(item_path)
                
                icon = "F" if is_dir else "f"
                child = parent_node.add_child(item, icon=icon)
                child.tag = item_path
                
                if is_dir:
                    # Add placeholder for lazy loading
                    child.add_child("Loading...", icon=" ")
                    
        except PermissionError:
            parent_node.add_child("(Access Denied)", icon="X")
            
    def on_node_click(self):
        """Handle selection"""
        node = self.tree.get_selected()
        if node and node.tag:
            if os.path.isdir(node.tag):
                self.load_directory(node.tag, node)
                self.tree.expand_node(node)
            else:
                self.open_file(node.tag)
```

---

## TabControl

Multi-page interface with tabbed navigation.

### Basic Usage

```python
# Create TabControl
tabs = TabControl(
    name_id="tabMain",
    x=2,
    y=2,
    width=50,
    height=15
)

# Add tabs
tab_general = tabs.add_tab("General", "tabGeneral")
tab_advanced = tabs.add_tab("Advanced", "tabAdvanced")
tab_about = tabs.add_tab("About", "tabAbout")

# Add controls to tabs
name_label = Label(name_id="lblName", caption="Name:", x=4, y=5)
name_input = TextBox(name_id="txtName", x=15, y=5, width=30)

tab_general.add_control(name_label)
tab_general.add_control(name_input)

# Set active tab
tabs.set_active_tab(0)  # General
```

### Tab Pages

```python
# Access tab pages
current_tab = tabs.get_active_tab()
current_index = tabs.get_active_index()

# Navigate
tabs.next_tab()      # Go to next tab
tabs.prev_tab()      # Go to previous tab

# Count
print(f"Total tabs: {tabs.get_tab_count()}")

# Get specific tab
tab = tabs.get_tab(1)  # By index
```

### Dynamic Tabs

```python
def add_document_tab(self, filename):
    """Add new tab for document"""
    tab = tabs.add_tab(filename, f"tab_{filename}")
    
    # Add editor
    editor = TextArea(name_id=f"editor_{filename}", x=4, y=5, width=45, height=10)
    tab.add_control(editor)
    
    # Switch to new tab
    tabs.set_active_tab(tabs.get_tab_count() - 1)

def close_current_tab(self):
    """Close active tab"""
    if tabs.get_tab_count() > 1:  # Keep at least one
        tabs.remove_tab(tabs.get_active_index())
```

### Closable Tabs

```python
# Enable close buttons
tabs.closable_tabs = True
tabs.show_close_button = True

def on_tab_close_tab():
    """Handle tab close"""
    tab = tabMain.get_active_tab()
    if confirm_dialog(f"Close {tab.caption}?", "Confirm"):
        tabMain.remove_tab(tabMain.get_active_index())
```

### Practical Example: Settings Dialog

```python
def create_settings_dialog():
    """Create settings with tabs"""
    dialog = Form("Settings", width=60, height=20)
    
    tabs = TabControl(name_id="tabSettings", x=2, y=2, width=56, height=16)
    
    # General tab
    general = tabs.add_tab("General")
    general.add_control(Label(x=4, y=4, caption="Username:"))
    general.add_control(TextBox(name_id="txtUsername", x=15, y=4))
    general.add_control(CheckBox(name_id="chkAutoSave", x=4, y=6, caption="Auto-save"))
    
    # Appearance tab
    appearance = tabs.add_tab("Appearance")
    appearance.add_control(Label(x=4, y=4, caption="Theme:"))
    appearance.add_control(ComboBox(name_id="cboTheme", x=15, y=4, 
                                   items=["Light", "Dark", "High Contrast"]))
    
    # Network tab
    network = tabs.add_tab("Network")
    network.add_control(Label(x=4, y=4, caption="Proxy:"))
    network.add_control(TextBox(name_id="txtProxy", x=15, y=4))
    network.add_control(CheckBox(name_id="chkUseSSL", x=4, y=6, caption="Use SSL"))
    
    dialog.add_control(tabs)
    return dialog
```

---

## Splitter

Resizable panel divider for flexible layouts.

### Basic Usage

```python
# Create two panels
left_panel = Panel(x=2, y=2, width=20, height=15)
right_panel = Panel(x=25, y=2, width=30, height=15)

# Create vertical splitter
splitter = Splitter(
    name_id="splitterMain",
    x=23,
    y=2,
    width=1,
    height=15
)
splitter.set_orientation(Splitter.VERTICAL)
splitter.set_position(0.4)  # 40% to left panel

# Associate panels
splitter.set_panel1(left_panel)
splitter.set_panel2(right_panel)
```

### Orientation

```python
# Vertical splitter (divides horizontally)
splitter.set_orientation(Splitter.VERTICAL)
# Creates left and right panels

# Horizontal splitter (divides vertically)
splitter.set_orientation(Splitter.HORIZONTAL)
# Creates top and bottom panels
```

### Position Control

```python
# Set position as percentage (0.0 - 1.0)
splitter.set_position(0.3)  # 30%

# Set position in pixels (if use_percentage is False)
splitter.use_percentage = False
splitter.set_position(25)  # 25 pixels

# Get current position
percent = splitter.get_position()  # 0.0 - 1.0
pixels = splitter.get_pixel_position()  # In pixels

# Constraints
splitter.set_min_size(10)  # Minimum panel size
splitter.set_range(0.2, 0.8)  # Allowed range
```

### Event Handling

```python
def on_splitter_moved_splitter():
    """Called when splitter released"""
    pos = splitter.get_position()
    print(f"Splitter at {pos*100:.0f}%")

def on_splitter_moving_splitter():
    """Called during drag"""
    # Update layout in real-time
    update_layout()
```

### Practical Example: File Manager Layout

```python
class FileManagerLayout:
    def __init__(self):
        # Left panel - directory tree
        self.tree = TreeView(name_id="treeDirs", width=25, height=18)
        
        # Right panel - file list
        self.file_list = Grid(name_id="gridFiles", width=50, height=18)
        
        # Splitter
        self.splitter = Splitter(name_id="splitter", height=18)
        self.splitter.set_orientation(Splitter.VERTICAL)
        self.splitter.set_position(0.3)
        self.splitter.set_panel1(self.tree)
        self.splitter.set_panel2(self.file_list)
        
        # Status bar at bottom
        self.status = StatusBar(name_id="statusBar", y=20)
        self.status.add_panel("Ready", width=40, auto_size=1)
        self.status.add_panel("Items: 0", width=12)
        
    def render(self, screen):
        self.tree.render(screen)
        self.file_list.render(screen)
        self.splitter.render(screen)
        self.status.render(screen)
```

### SplitContainer Helper

```python
# Using SplitContainer convenience class
container = SplitContainer(orientation=Splitter.VERTICAL)

left = Panel(width=30, height=15)
right = Panel(width=40, height=15)

container.set_panels(left, right)
container.set_position(0.4)

# Render all at once
container.render(screen)
```

---

## Toolbar

Icon button strip for common actions.

### Basic Usage

```python
# Create toolbar
toolbar = Toolbar(
    name_id="toolbarMain",
    x=2,
    y=1,
    width=70,
    height=1
)

# Add buttons
toolbar.add_button("New", icon="N", tooltip="New File")
toolbar.add_button("Open", icon="O", tooltip="Open File")
toolbar.add_separator()
toolbar.add_button("Save", icon="S", tooltip="Save")
toolbar.add_button("Save As", icon="A", tooltip="Save As")

# Toggle button
toolbar.add_button("Bold", icon="B", button_type=ToolbarButton.TOGGLE)
toolbar.add_button("Italic", icon="I", button_type=ToolbarButton.TOGGLE)
```

### Button Types

```python
# Push button (default)
btn_push = toolbar.add_button("Action", button_type=ToolbarButton.PUSH)

# Toggle button (stays pressed)
btn_toggle = toolbar.add_button("Toggle", button_type=ToolbarButton.TOGGLE)

# Separator (visual only)
toolbar.add_separator()
```

### Event Handling

```python
def on_button_click_toolbar(index, button):
    """Handle button click"""
    print(f"Clicked: {button.caption}")
    
    if button.caption == "New":
        new_file()
    elif button.caption == "Open":
        open_file_dialog()
    elif button.caption == "Save":
        save_file()

def on_button_check_toolbar(index, button, checked):
    """Handle toggle button"""
    if button.caption == "Bold":
        set_bold(checked)
    elif button.caption == "Italic":
        set_italic(checked)
```

### Button State

```python
# Enable/disable
toolbar.enable_button(0)   # By index
toolbar.disable_button(2)

# Toggle state
toolbar.set_button_checked(5, True)   # Check
toolbar.set_button_checked(5, False)  # Uncheck

# Get button
btn = toolbar.get_button(0)
if btn:
    print(f"Button: {btn.caption}, Enabled: {btn.enabled}")
```

### Practical Example: Text Editor Toolbar

```python
def create_editor_toolbar():
    """Create toolbar for text editor"""
    toolbar = Toolbar(name_id="toolbarEditor", x=2, y=1, width=76)
    
    # File operations
    toolbar.add_button("New", icon="N", tooltip="New Document (Ctrl+N)")
    toolbar.add_button("Open", icon="O", tooltip="Open (Ctrl+O)")
    toolbar.add_button("Save", icon="S", tooltip="Save (Ctrl+S)")
    toolbar.add_separator()
    
    # Edit operations
    toolbar.add_button("Cut", icon="X", tooltip="Cut (Ctrl+X)")
    toolbar.add_button("Copy", icon="C", tooltip="Copy (Ctrl+C)")
    toolbar.add_button("Paste", icon="V", tooltip="Paste (Ctrl+V)")
    toolbar.add_separator()
    
    # Formatting
    toolbar.add_button("Bold", icon="B", tooltip="Bold (Ctrl+B)", 
                      button_type=ToolbarButton.TOGGLE)
    toolbar.add_button("Italic", icon="I", tooltip="Italic (Ctrl+I)",
                      button_type=ToolbarButton.TOGGLE)
    toolbar.add_button("Underline", icon="U", tooltip="Underline (Ctrl+U)",
                      button_type=ToolbarButton.TOGGLE)
    
    return toolbar
```

---

## StatusBar

Multi-panel information display at form bottom.

### Basic Usage

```python
# Create status bar
status = StatusBar(
    name_id="statusBar",
    x=2,
    y=22,
    width=76,
    height=1
)

# Add panels
status.add_panel("Ready", width=30, auto_size=1)      # Spring panel
status.add_panel("Ln 1, Col 1", width=12)              # Fixed
status.add_panel("UTF-8", width=8)                     # Fixed
status.add_panel("INS", width=5)                       # Fixed
```

### Panel Types

```python
# Fixed width panel
status.add_panel("Fixed", width=15, auto_size=StatusPanel.FIXED)

# Spring panel (expands to fill space)
status.add_panel("Spring", width=10, auto_size=StatusPanel.SPRING)

# Percentage width
status.add_panel("25%", width=25, auto_size=StatusPanel.PERCENTAGE)
```

### Updating Panels

```python
# Update text
status.set_panel_text(0, "Editing file.txt")
status.set_panel_text(1, "Ln 45, Col 12")

# Get text
current = status.get_panel_text(0)

# Simple mode (single panel)
status.simple_mode = True
status.set_simple_text("Simple status message")
```

### Practical Example: IDE Status Bar

```python
class IDEStatusBar:
    def __init__(self):
        self.status = StatusBar(name_id="statusIDE", x=2, y=23, width=76)
        
        # Message panel (spring)
        self.status.add_panel("Ready", width=40, auto_size=1)
        
        # Cursor position
        self.status.add_panel("Ln 1, Col 1", width=14)
        
        # File encoding
        self.status.add_panel("UTF-8", width=8)
        
        # Line endings
        self.status.add_panel("LF", width=4)
        
        # Insert/Overwrite mode
        self.status.add_panel("INS", width=5)
        
    def update_cursor(self, line, col):
        """Update cursor position"""
        self.status.set_panel_text(1, f"Ln {line}, Col {col}")
        
    def update_encoding(self, encoding):
        """Update file encoding"""
        self.status.set_panel_text(2, encoding)
        
    def set_insert_mode(self, insert):
        """Update insert/overwrite mode"""
        mode = "INS" if insert else "OVR"
        self.status.set_panel_text(4, mode)
        
    def show_message(self, message, duration=3000):
        """Show temporary message"""
        old_text = self.status.get_panel_text(0)
        self.status.set_panel_text(0, message)
        
        # Restore after duration (would use timer in real app)
        # self.status.set_panel_text(0, old_text)
```

---

## Combining Advanced Controls

### Complete Application Layout

```python
class MainApplication:
    def __init__(self):
        # Toolbar at top
        self.toolbar = Toolbar(name_id="toolbarMain", x=2, y=1, width=76)
        self.setup_toolbar()
        
        # Main area with splitter
        self.tree = TreeView(name_id="treeMain", x=2, y=3, width=25, height=16)
        self.content = TabControl(name_id="tabContent", x=28, y=3, width=50, height=16)
        
        self.splitter = Splitter(name_id="splitter", x=27, y=3, height=16)
        self.splitter.set_orientation(Splitter.VERTICAL)
        self.splitter.set_position(0.3)
        self.splitter.set_panel1(self.tree)
        self.splitter.set_panel2(self.content)
        
        # Status bar at bottom
        self.status = StatusBar(name_id="statusBar", x=2, y=20, width=76)
        self.status.add_panel("Ready", width=40, auto_size=1)
        self.status.add_panel("Items: 0", width=12)
        
    def setup_toolbar(self):
        """Configure toolbar"""
        self.toolbar.add_button("New", icon="N")
        self.toolbar.add_button("Open", icon="O")
        self.toolbar.add_button("Save", icon="S")
        self.toolbar.add_separator()
        self.toolbar.add_button("Cut", icon="X")
        self.toolbar.add_button("Copy", icon="C")
        self.toolbar.add_button("Paste", icon="V")
        
    def render(self, screen):
        """Render all controls"""
        self.toolbar.render(screen)
        self.tree.render(screen)
        self.content.render(screen)
        self.splitter.render(screen)
        self.status.render(screen)
```

### File Manager Example

```python
class FileManager:
    def __init__(self):
        # Toolbar
        self.toolbar = self.create_toolbar()
        
        # Splitter with tree and list
        self.tree = TreeView(x=2, y=3, width=25, height=15)
        self.file_list = Grid(x=28, y=3, width=50, height=15)
        
        self.splitter = Splitter(x=27, y=3, height=15)
        self.splitter.set_orientation(Splitter.VERTICAL)
        self.splitter.set_position(0.3)
        self.splitter.set_panel1(self.tree)
        self.splitter.set_panel2(self.file_list)
        
        # Status bar
        self.status = StatusBar(x=2, y=19, width=76)
        self.status.add_panel("Ready", width=35, auto_size=1)
        self.status.add_panel("0 items", width=12)
        self.status.add_panel("0 bytes", width=15)
        
        self.load_root()
        
    def create_toolbar(self):
        tb = Toolbar(x=2, y=1, width=76)
        tb.add_button("Back", icon="<")
        tb.add_button("Forward", icon=">")
        tb.add_button("Up", icon="^")
        tb.add_separator()
        tb.add_button("Cut", icon="X")
        tb.add_button("Copy", icon="C")
        tb.add_button("Paste", icon="V")
        tb.add_separator()
        tb.add_button("Delete", icon="D")
        tb.add_button("Rename", icon="R")
        return tb
        
    def load_root(self):
        """Load root directories"""
        self.tree.clear()
        
        computer = self.tree.add_root_node("Computer", icon="C")
        docs = computer.add_child("Documents", icon="D")
        docs.add_child("Work", icon="F")
        docs.add_child("Personal", icon="F")
        
        self.tree.expand_node(computer)
```

---

## Best Practices

### Layout

1. **Consistent spacing**: Use 2-character margins
2. **Responsive design**: Handle resize with percentage-based layouts
3. **Minimum sizes**: Set minimum panel sizes for splitters
4. **Z-order**: Render in correct order (background to foreground)

### TreeView

1. **Lazy loading**: Load children on expand for large datasets
2. **Icons**: Use consistent icon scheme
3. **Selection feedback**: Highlight selected node
4. **Keyboard navigation**: Support arrow keys

### TabControl

1. **Meaningful names**: Use clear tab captions
2. **Logical order**: Group related tabs together
3. **State persistence**: Save active tab between sessions
4. **Close confirmation**: Prompt before closing unsaved tabs

### Splitter

1. **Visual feedback**: Show resize cursor
2. **Constraints**: Set reasonable min/max sizes
3. **Persistence**: Remember user-adjusted positions
4. **Accessibility**: Support keyboard resizing

### Toolbar

1. **Standard icons**: Use familiar symbols (N=New, O=Open, S=Save)
2. **Tooltips**: Always provide helpful descriptions
3. **Grouping**: Group related actions with separators
4. **Disable states**: Disable unavailable actions

### StatusBar

1. **Right-side info**: Put changing info on right (Ln/Col)
2. **Spring panels**: Use spring for message area
3. **Click actions**: Make panels clickable for related actions
4. **Update frequency**: Don't update too frequently (performance)

---

## Resources

- [TreeView Patterns](https://ui-patterns.com/patterns/tree)
- [Tab Interface Guidelines](https://www.nngroup.com/articles/tabs-used-right/)
- [Toolbar Design](https://developer.apple.com/design/human-interface-guidelines/toolbars)
- [RAD-TUI API Reference](API_REFERENCE_V22.md)

---

*Last Updated: 2025*
