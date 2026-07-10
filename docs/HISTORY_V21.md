# Version History - VB1-DOS Clone v2.1.0

## Release Date: 2025-01-15

---

## What's New in v2.1.0

### New Controls

#### TextArea (Type 15)
- Multi-line text editor with word wrap
- Cursor navigation (arrow keys, Home, End, Page Up/Down)
- Text selection and clipboard operations
- Scrollbars for large documents
- Events: on_change, on_key_press, on_selection_change

#### Grid (Type 16)
- Tabular data display with configurable columns
- Cell selection and editing
- Column sorting (ascending/descending)
- CSV import/export
- Events: on_cell_click, on_cell_edit, on_header_click

### Runtime Capabilities

#### File I/O Functions
- `open_file(filename, mode)` - Open files for read/write
- `read_line(handle)` - Read line by line
- `write_line(handle, text)` - Write lines
- `close_file(handle)` - Close files
- `file_exists(filename)` - Check existence
- `delete_file(filename)` - Delete files
- `rename_file(old, new)` - Rename files
- `file_size(filename)` - Get file size
- `list_files(directory, pattern)` - List directory contents

#### Common Dialogs
- `msgbox(text, title, buttons)` - Enhanced with button types
- `inputbox(prompt, title, default)` - Text input dialog
- `file_dialog(mode, filters)` - File open/save dialogs

#### Clipboard Operations
- `clipboard_set(text)` - Copy to clipboard
- `clipboard_get()` - Paste from clipboard

#### String Functions
- `split(text, delimiter)` - Split strings
- `join(list, delimiter)` - Join strings
- `trim(text)` - Remove whitespace
- `replace(text, old, new)` - Replace substrings
- `format_number(number, decimals)` - Format numbers

#### Date/Time Functions
- `get_date()` - Current date
- `get_time()` - Current time
- `get_datetime()` - Current date and time

### Template System

#### Built-in Templates
- Text Editor - Full-featured text editing application
- Database Browser - Data viewing and editing
- Calculator - Arithmetic operations
- Form Wizard - Multi-step data entry

#### Template Features
- Template selection dialog
- Custom template support (save projects as templates)
- Template metadata (name, description, author, category)
- Form wizard for step-by-step creation

### Drag and Drop

#### Features
- Drag items between List Boxes
- Drag text between Text Boxes
- Drag files from dialogs
- Visual feedback (ghost images, drop indicators)
- Custom drag data formats

#### Events
- `on_drag_start` - Drag initiated
- `on_drag_over` - Drag over target
- `on_drop` - Drop completed

### Image Display

#### Picture Box Enhancements
- ASCII/Unicode art display
- XPM file support
- Image resizing (stretch, center)
- Animation support with ImageList
- `on_image_click` event

#### ImageList
- Multiple image management
- Frame-based animation
- Pattern-based loading

### Debugging

#### Debug Window
- Variables tab - inspect current scope
- Call Stack tab - view execution stack
- Watches tab - monitor expressions
- Output tab - debug messages

#### Breakpoints
- Set/clear breakpoints in code editor
- Step-through execution (Step Into, Step Over, Step Out)
- Continue execution

#### Debug Functions
- `debug_print(...)` - Output to debug console
- `set_breakpoint(file, line)` - Programmatic breakpoints
- `step_into()`, `step_over()`, `step_out()` - Execution control

### Documentation

#### New Guides
- API_REFERENCE_V21.md - Complete API reference
- TUTORIAL_TEXT_EDITOR.md - Build text editor tutorial
- FILE_IO_GUIDE.md - File operations guide
- GRID_CONTROL_GUIDE.md - Grid usage guide
- DEBUGGING_GUIDE.md - Debugging guide
- PROJECT_FORMAT_V21.md - Project format specification

---

## Changes from v2.0

### Added
- 2 new control types (TextArea, Grid)
- 30+ new functions
- Template system
- Drag and drop
- Image display enhancements
- Debugging capabilities
- Extended documentation

### Modified
- Enhanced `msgbox()` with button types
- Improved file dialogs
- Better error reporting

### Deprecated
- None - full backward compatibility

### Removed
- None

---

## Migration Guide

### From v2.0 to v2.1.0

1. **No breaking changes** - v2.0 projects work without modification
2. **New features are opt-in** - use when needed
3. **Update documentation references** - point to new guides

### Using New Features

#### Add TextArea to existing project:
```python
# Add control with tool_type 15
# Set word_wrap property
# Handle on_change event
```

#### Add Grid to existing project:
```python
# Add control with tool_type 16
# Set grid_headers and grid_col_widths
# Load data with grid_data property
```

#### Use File I/O:
```python
# Add to existing event handlers
handle = open_file("data.txt", "r")
# ... process ...
close_file(handle)
```

---

## Known Issues

1. **Large files** - TextArea may slow down with files > 100KB
2. **Grid sorting** - Sorts strings alphabetically (not numerically)
3. **Drag and drop** - Limited to same-form controls
4. **Image display** - Only ASCII/Unicode art, not binary images

---

## System Requirements

- Linux with terminal supporting:
  - Python 3.7+ (Python version)
  - FreeBASIC 1.08+ (FreeBASIC version)
  - 256-color terminal support
  - Mouse support (optional but recommended)

---

## Files in This Release

### Core Files
- `rad-tui-py.py` - Python implementation
- `rad-tui-BASIC.bas` - FreeBASIC implementation

### New Modules
- `templates.py` - Template system
- `template_dialog.py` - Template UI
- `dragdrop.py` - Drag and drop
- `image_display.py` - Image handling
- `debugger.py` - Debugging support

### Documentation
- `docs/API_REFERENCE_V21.md`
- `docs/TUTORIAL_TEXT_EDITOR.md`
- `docs/FILE_IO_GUIDE.md`
- `docs/GRID_CONTROL_GUIDE.md`
- `docs/DEBUGGING_GUIDE.md`
- `docs/PROJECT_FORMAT_V21.md`
- `docs/HISTORY_V21.md` (this file)

### Examples
- `examples/notepad.json` - Text editor example
- `examples/csv_viewer.json` - Grid example
- `examples/image_viewer.json` - Picture Box example
- `examples/calculator_v21.json` - Calculator with clipboard
- `examples/file_manager.json` - File operations example

---

## Contributors

- Original VB1-DOS Clone: Project Team
- v2.1.0 Enhancements: Project Team

---

## License

GPL v3 - See LICENSE file for details.

---

## Feedback

Report issues and suggestions at:
- GitHub Issues
- Project Discussion Forum

---

**Thank you for using VB1-DOS Clone v2.1.0!**
