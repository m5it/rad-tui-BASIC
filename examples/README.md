# VB1-DOS Clone Example Projects

This directory contains example projects demonstrating the capabilities of the VB1-DOS Clone IDE.

## Version 2.1.0 Examples (New!)

### notepad.json - Text Editor
A full-featured Notepad clone demonstrating:
- **TextArea control** - Multi-line text editing with word wrap
- **File I/O** - Open, save, and create new files
- **Menu system** - File and Edit menus with keyboard shortcuts
- **Clipboard** - Cut, copy, paste operations

**Features:**
- Open and save text files (.txt, .py, .bas)
- Status bar with line, column, word count
- Find dialog
- Keyboard shortcuts (Ctrl+S, Ctrl+O, Ctrl+N, Ctrl+F)

### csv_viewer.json - CSV Data Viewer
A spreadsheet-like data viewer demonstrating:
- **Grid control** - Tabular data display with columns
- **File I/O** - Load and save CSV files
- **Sorting** - Click column headers to sort
- **Data editing** - Add and delete rows

**Features:**
- Automatic header detection
- Sort by any column
- Add/delete rows
- Save to CSV format

### image_viewer.json - ASCII Image Viewer
An image viewer for ASCII art demonstrating:
- **Picture Box control** - Display ASCII/Unicode art
- **ImageList** - Multiple image management
- **Animation** - Navigate through image collection

**Features:**
- Sample ASCII art included
- Next/Previous navigation
- Click image to cycle
- Load external ASCII files

### calculator_v21.json - Calculator with Memory
An enhanced calculator demonstrating:
- **Clipboard operations** - Copy and paste values
- **Memory functions** - Store, recall, add to memory
- **Menu system** - Edit and Memory menus

**Features:**
- Standard arithmetic operations
- Memory (MC, MR, MS, M+)
- Copy/paste support
- Decimal point support

### file_manager.json - File Manager
A simple file browser demonstrating:
- **File dialogs** - Open and save dialogs
- **Drag and drop** - Drag files between lists
- **File operations** - List, check existence, get size

**Features:**
- List directory contents
- File information display
- Open/Save dialogs
- Drag and drop between lists

---

## Version 2.0 Examples

### 1. Hello World (`hello_world.json`)
A simple introduction to the IDE featuring:
- Label controls for displaying text
- Command buttons with click handlers
- Message box integration
- Event-driven programming basics

**Usage**: Click "Click Me!" to see a greeting, then "Exit" to close.

### 2. Calculator (`calculator.json`)
A functional calculator demonstrating:
- Grid layout of buttons
- Text box for display
- Mathematical operations
- Event handlers for each button
- Basic expression evaluation

**Usage**: Click number and operator buttons to build expressions, then "=" to calculate.

### 3. Text Editor (`text_editor.json`)
A simple text editor showing:
- Multi-line list box for text lines
- Menu bar with File menu
- Text input for filename
- Line manipulation (add, clear)
- Status bar updates

**Usage**: Use "Add Line" to add text, "Clear" to reset, select lines to view details.

### 4. Database Browser (`database_browser.json`)
A customer database browser featuring:
- List box for record selection
- Frame container for grouping
- Data binding simulation
- Navigation buttons (First, Previous, Next, Last)
- Detail display fields

**Usage**: Select a customer from the list to see their details. Use navigation buttons to move through records.

### 5. Timer Demo (`timer_demo.json`)
A demonstration of timer-like functionality:
- Counter with increment/decrement
- Check box for auto mode toggle
- Start/Stop/Reset controls
- Status updates
- Animation simulation

**Usage**: Click "Start" to enable auto mode, "Stop" to pause, "Reset" to clear counter. Use +/- buttons for manual control.

---

## Feature Matrix

| Feature | notepad | csv_viewer | image_viewer | calculator_v21 | file_manager | hello_world | calculator | text_editor | database_browser | timer_demo |
|---------|---------|------------|--------------|----------------|--------------|-------------|------------|-------------|------------------|------------|
| TextArea | ✓ | | | | | | | | | |
| Grid | | ✓ | | | | | | | | |
| Picture Box | | | ✓ | | | | | | ✓ | |
| File I/O | ✓ | ✓ | ✓ | | ✓ | | | | | |
| Clipboard | ✓ | | | ✓ | | | | | | |
| File Dialogs | ✓ | ✓ | ✓ | | ✓ | | | | | |
| String Functions | ✓ | ✓ | | ✓ | | | | | | |
| Drag & Drop | | | | | ✓ | | | | | |
| Menus | ✓ | ✓ | ✓ | ✓ | ✓ | | | ✓ | ✓ | |
| Memory | | | | ✓ | | | | | | |
| Timer | | | | | | | | | | ✓ |

---

## Loading Examples

1. Start the VB1-DOS Clone IDE
2. Click "File" in the menu bar
3. Select "Open Project..." (v2.1.0) or "Load Project..." (v2.0)
4. Navigate to the examples directory
5. Choose the desired `.json` file

**Note:** v2.1.0 examples require VB1-DOS Clone v2.1.0 or later due to new features.

---

## Creating Your Own Projects

To create your own projects:

1. Use the Toolbox to add controls to the form
2. Double-click controls to add event handlers
3. Use the Properties window to customize appearance
4. Save your project with File > Save Project As...

## Event Types Supported

- `on_click` - Button clicks, menu selections
- `on_change` - Text changes, check box toggles, list selections
- `on_focus` - Control receives focus
- `on_blur` - Control loses focus
- `on_timer` - Timer intervals
- `on_load` - Form initialization
- `on_menu` - Menu item clicks
- `on_cell_click` - Grid cell clicks (v2.1.0)
- `on_cell_edit` - Grid cell edits (v2.1.0)
- `on_header_click` - Grid header clicks (v2.1.0)
- `on_image_click` - Picture Box clicks (v2.1.0)
- `on_drag_start` - Drag initiation (v2.1.0)
- `on_drop` - Drop completion (v2.1.0)

## Tips

- Use `msgbox("text")` to display messages
- Use `inputbox("prompt", "title", "default")` for user input (v2.1.0)
- Use `file_dialog('open', ['.txt'])` for file selection (v2.1.0)
- Access control properties: `controlname.caption`
- Access list items: `listname.items[index]`
- Use Python syntax in code editors
- Test your code in Run mode before saving

---

## Version Compatibility

- **v2.1.0 examples**: Require VB1-DOS Clone v2.1.0+
  - notepad.json
  - csv_viewer.json
  - image_viewer.json
  - calculator_v21.json
  - file_manager.json

- **v2.0 examples**: Compatible with v2.0 and later
  - hello_world.json
  - calculator.json
  - text_editor.json
  - database_browser.json
  - timer_demo.json
