# VB1-DOS Clone v2.1.0 API Reference

## New in v2.1.0

This version adds powerful new controls, file I/O capabilities, debugging features, and template system.

---

## Controls

### TextArea (Type 15) - NEW
Multi-line text editor with word wrap and scrollbars.

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `name_id` | String | Unique identifier |
| `caption` | String | Text content (lines joined with \n) |
| `cursor_x`, `cursor_y` | Integer | Cursor position |
| `scroll_x`, `scroll_y` | Integer | Scroll offset |
| `word_wrap` | Boolean | Enable word wrapping |
| `x`, `y` | Integer | Position coordinates |
| `w`, `h` | Integer | Size (h determines visible lines) |

**Events:**
- `on_change` - Fired when text changes
- `on_key_press` - Fired on key press
- `on_selection_change` - Fired when selection changes

**Methods:**
- `get_line(n)` - Get line at index n
- `set_line(n, text)` - Set line at index n
- `get_selected_text()` - Get selected text
- `insert_text(pos, text)` - Insert text at position
- `delete_text(start, end)` - Delete text range

**Example:**
```python
def on_change_txtEditor():
    # Count lines
    lines = txtEditor.caption.split('\n')
    lblStatus.caption = f"Lines: {len(lines)}"

def on_key_press_txtEditor():
    if key == "F5":
        # Run code
        execute(txtEditor.caption)
```

---

### Grid (Type 16) - NEW
Tabular data display with sorting and cell editing.

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `name_id` | String | Unique identifier |
| `grid_data` | 2D Array | Cell data[row][col] |
| `grid_headers` | Array | Column header strings |
| `grid_col_widths` | Array | Column width in characters |
| `grid_row_count` | Integer | Number of rows |
| `grid_col_count` | Integer | Number of columns |
| `grid_selected_cell` | Tuple | (row, col) of selected cell |
| `grid_sort_col` | Integer | Currently sorted column |
| `grid_sort_asc` | Boolean | Sort ascending flag |

**Events:**
- `on_cell_click` - Fired when cell clicked
- `on_cell_edit` - Fired when cell edited
- `on_header_click` - Fired when column header clicked
- `on_selection_change` - Fired when selection changes

**Methods:**
- `sort(col, ascending=True)` - Sort by column
- `add_row(data)` - Append row
- `delete_row(index)` - Remove row
- `get_cell(row, col)` - Get cell value
- `set_cell(row, col, value)` - Set cell value
- `load_csv(filename)` - Load from CSV file
- `save_csv(filename)` - Save to CSV file

**Example:**
```python
def on_cell_click_gridData():
    row, col = gridData.grid_selected_cell
    if row >= 0:
        lblSelected.caption = f"Selected: {gridData.get_cell(row, col)}"

def on_header_click_gridData():
    # Sort by clicked column
    col = gridData.grid_sort_col
    gridData.sort(col, not gridData.grid_sort_asc)

def on_click_btnLoad():
    filename = file_dialog('open', ['.csv'])
    if filename:
        gridData.load_csv(filename)
        msgbox(f"Loaded {gridData.grid_row_count} rows")
```

---

### Picture Box (Type 12) - ENHANCED
Display ASCII/Unicode art and XPM images.

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `name_id` | String | Unique identifier |
| `image_path` | String | Path to image file |
| `stretch` | Boolean | Resize image to fit |
| `center` | Boolean | Center image in box |
| `border` | Boolean | Show border |
| `auto_size` | Boolean | Adjust size to image |

**Events:**
- `on_image_click` - Fired when image clicked
- `on_image_load` - Fired when image loaded

**Methods:**
- `load_image(path)` - Load image from file
- `set_image(ascii_image)` - Set ASCIIImage object
- `resize(width, height)` - Resize image
- `create_animation(pattern)` - Create from file pattern

**Example:**
```python
def on_load_frmMain():
    # Load ASCII art
    picLogo.load_image("logo.txt")

def on_image_click_picGallery():
    # Cycle to next image
    picGallery.image_list.next_frame()
    picGallery.set_image(picGallery.image_list.get_current())
```

---

### Check Box (Type 1)
A binary toggle control with checked/unchecked states.

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `name_id` | String | Unique identifier |
| `caption` | String | Label text (prefix with "[ ]" or "[X]") |
| `checked` | Boolean | True if checked, False otherwise |
| `x`, `y` | Integer | Position coordinates |
| `w`, `h` | Integer | Size (typically h=1) |

**Events:**
- `on_change` - Fired when checked state changes

**Example:**
```python
def on_change_chkOption():
    if chkOption.checked:
        lblStatus.caption = "Enabled"
    else:
        lblStatus.caption = "Disabled"
```

---

### Combo Box (Type 2)
A dropdown list for selecting one item from many.

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `name_id` | String | Unique identifier |
| `caption` | String | Default text |
| `items` | List | String array of options |
| `selected_index` | Integer | Index of selected item (-1 for none) |
| `x`, `y` | Integer | Position coordinates |
| `w`, `h` | Integer | Size (typically h=1) |

**Events:**
- `on_change` - Fired when selection changes

---

### Command Button (Type 3)
A clickable button that triggers actions.

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `name_id` | String | Unique identifier |
| `caption` | String | Button text |
| `x`, `y` | Integer | Position coordinates |
| `w`, `h` | Integer | Size (typically h=3 for standard button) |

**Events:**
- `on_click` - Fired when button is clicked

---

### Frame (Type 7)
A container control for grouping related controls visually.

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `name_id` | String | Unique identifier |
| `caption` | String | Frame title (appears in border) |
| `x`, `y` | Integer | Position coordinates |
| `w`, `h` | Integer | Size |
| `parent` | Integer | Parent control index (0=none) |

---

### Label (Type 9)
Displays read-only text.

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `name_id` | String | Unique identifier |
| `caption` | String | Display text |
| `x`, `y` | Integer | Position coordinates |
| `w`, `h` | Integer | Size (typically h=1) |

---

### List Box (Type 10)
Displays a scrollable list of items.

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `name_id` | String | Unique identifier |
| `caption` | String | Label text |
| `items` | List | Array of string items |
| `selected_index` | Integer | Index of selected item (-1 for none) |
| `scroll_offset` | Integer | Scroll position |
| `x`, `y` | Integer | Position coordinates |
| `w`, `h` | Integer | Size (h determines visible rows) |

**Events:**
- `on_change` - Fired when selection changes
- `on_drag_start` - Fired when item dragged

---

### Option Button (Type 11)
A radio button for mutually exclusive selection.

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `name_id` | String | Unique identifier |
| `caption` | String | Label text (prefix with "( )" or "(*)") |
| `checked` | Boolean | True if selected |
| `group` | String | Group name for mutual exclusion |
| `x`, `y` | Integer | Position coordinates |
| `w`, `h` | Integer | Size (typically h=1) |

**Events:**
- `on_change` - Fired when selection changes

---

### Text Box (Type 13)
Single-line text input field.

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `name_id` | String | Unique identifier |
| `caption` | String | Current text content |
| `x`, `y` | Integer | Position coordinates |
| `w`, `h` | Integer | Size (typically h=1) |

**Events:**
- `on_change` - Fired when text changes
- `on_focus` - Fired when control receives focus
- `on_blur` - Fired when control loses focus
- `on_drag_start` - Fired when text dragged
- `on_drop` - Fired when text dropped

---

### Timer (Type 14)
Triggers periodic events.

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `name_id` | String | Unique identifier |
| `interval` | Integer | Milliseconds between ticks |
| `enabled` | Boolean | Timer active state |

**Events:**
- `on_timer` - Fired on each timer tick

---

## Global Functions

### Message and Input Functions

#### `msgbox(text, title="Message", buttons="ok")` - ENHANCED
Display a modal message dialog.

**Parameters:**
- `text` (String) - Message to display
- `title` (String) - Dialog title
- `buttons` (String) - Button type: "ok", "okcancel", "yesno", "retrycancel"

**Returns:** Button clicked ("ok", "cancel", "yes", "no", "retry")

**Example:**
```python
result = msgbox("Save changes?", "Confirm", "yesno")
if result == "yes":
    save_file()
```

#### `inputbox(prompt, title="Input", default="")` - NEW
Display an input dialog.

**Parameters:**
- `prompt` (String) - Prompt text
- `title` (String) - Dialog title
- `default` (String) - Default input value

**Returns:** User input string or None if cancelled

**Example:**
```python
name = inputbox("Enter your name:", "Welcome", "Guest")
if name:
    lblGreeting.caption = f"Hello, {name}!"
```

#### `file_dialog(mode, filters=["*"])` - NEW
Open file dialog for open/save operations.

**Parameters:**
- `mode` (String) - "open" or "save"
- `filters` (List) - File extensions to show, e.g., [".txt", ".csv"]

**Returns:** Selected filename or None if cancelled

**Example:**
```python
filename = file_dialog('open', ['.txt', '.csv'])
if filename:
    load_file(filename)
```

---

### File I/O Functions - NEW

#### `open_file(filename, mode="r")`
Open a file for reading or writing.

**Parameters:**
- `filename` (String) - File path
- `mode` (String) - "r" for read, "w" for write, "a" for append

**Returns:** File handle or None if failed

**Example:**
```python
handle = open_file("data.txt", "r")
if handle:
    content = read_file(handle)
    close_file(handle)
```

#### `read_line(handle)`
Read a single line from file.

**Parameters:**
- `handle` - File handle from open_file()

**Returns:** Line string or None if EOF

**Example:**
```python
handle = open_file("data.txt", "r")
line = read_line(handle)
while line is not None:
    lstLines.items.append(line)
    line = read_line(handle)
close_file(handle)
```

#### `write_line(handle, text)`
Write a line to file.

**Parameters:**
- `handle` - File handle from open_file()
- `text` (String) - Line to write

**Example:**
```python
handle = open_file("output.txt", "w")
for item in lstItems.items:
    write_line(handle, item)
close_file(handle)
```

#### `close_file(handle)`
Close an open file.

**Parameters:**
- `handle` - File handle from open_file()

#### `file_exists(filename)`
Check if file exists.

**Parameters:**
- `filename` (String) - File path

**Returns:** Boolean

#### `delete_file(filename)`
Delete a file.

**Parameters:**
- `filename` (String) - File path

**Returns:** Boolean success

#### `rename_file(old_name, new_name)`
Rename a file.

**Parameters:**
- `old_name` (String) - Current filename
- `new_name` (String) - New filename

**Returns:** Boolean success

#### `file_size(filename)`
Get file size in bytes.

**Parameters:**
- `filename` (String) - File path

**Returns:** Integer size or -1 if not found

#### `list_files(directory, pattern="*")`
List files in directory.

**Parameters:**
- `directory` (String) - Directory path
- `pattern` (String) - Filter pattern, e.g., "*.txt"

**Returns:** List of filenames

---

### Clipboard Functions - NEW

#### `clipboard_set(text)`
Copy text to clipboard.

**Parameters:**
- `text` (String) - Text to copy

**Example:**
```python
def on_click_btnCopy():
    if txtEditor.selection:
        clipboard_set(txtEditor.get_selected_text())
        lblStatus.caption = "Copied to clipboard"
```

#### `clipboard_get()`
Get text from clipboard.

**Returns:** Clipboard text or empty string

**Example:**
```python
def on_click_btnPaste():
    txtEditor.insert_text(txtEditor.cursor_pos, clipboard_get())
```

---

### String Functions - NEW

#### `split(text, delimiter)`
Split string into list.

**Parameters:**
- `text` (String) - String to split
- `delimiter` (String) - Delimiter character

**Returns:** List of strings

**Example:**
```python
parts = split("apple,banana,cherry", ",")
# Returns: ["apple", "banana", "cherry"]
```

#### `join(list, delimiter)`
Join list into string.

**Parameters:**
- `list` - List of strings
- `delimiter` (String) - Delimiter to insert

**Returns:** Joined string

**Example:**
```python
text = join(["apple", "banana"], ", ")
# Returns: "apple, banana"
```

#### `trim(text)`
Remove leading/trailing whitespace.

**Parameters:**
- `text` (String) - String to trim

**Returns:** Trimmed string

#### `replace(text, old, new)`
Replace substring.

**Parameters:**
- `text` (String) - Original string
- `old` (String) - Substring to replace
- `new` (String) - Replacement string

**Returns:** Modified string

#### `format_number(number, decimals=2)`
Format number with decimal places.

**Parameters:**
- `number` (Float/Int) - Number to format
- `decimals` (Integer) - Decimal places

**Returns:** Formatted string

**Example:**
```python
txtResult.caption = format_number(3.14159, 2)
# Returns: "3.14"
```

---

### Date/Time Functions - NEW

#### `get_date()`
Get current date.

**Returns:** String in format "YYYY-MM-DD"

#### `get_time()`
Get current time.

**Returns:** String in format "HH:MM:SS"

#### `get_datetime()`
Get current date and time.

**Returns:** String in format "YYYY-MM-DD HH:MM:SS"

---

### Debugging Functions - NEW

#### `debug_print(...args)`
Print to debug console.

**Parameters:**
- `args` - Values to print (any type)

**Example:**
```python
def on_click_btnCalculate():
    debug_print("Calculating with x =", x, "y =", y)
    result = x + y
    debug_print("Result:", result)
```

#### `set_breakpoint(filename, line)`
Set a breakpoint.

**Parameters:**
- `filename` (String) - Source file
- `line` (Integer) - Line number

#### `clear_breakpoint(filename, line)`
Clear a breakpoint.

#### `step_into()`
Step into function call.

#### `step_over()`
Step over function call.

#### `step_out()`
Step out of current function.

#### `continue_execution()`
Continue execution after pause.

---

### Template Functions - NEW

#### `save_as_template(name, description, category)`
Save current project as template.

**Parameters:**
- `name` (String) - Template name
- `description` (String) - Template description
- `category` (String) - Template category

**Returns:** Boolean success

#### `load_template(template_id)`
Load a template.

**Parameters:**
- `template_id` (String) - Template identifier

**Returns:** Project data or None

#### `get_templates()`
Get list of available templates.

**Returns:** List of template dictionaries

---

## Control Access

Access any control by its `name_id` as a global variable in event handlers:

```python
def on_click_btnUpdate():
    # Read from text box
    name = txtName.caption
    
    # Write to label
    lblOutput.caption = "Hello, " + name
    
    # Check check box
    if chkAgree.checked:
        lblStatus.caption = "Agreement accepted"
    
    # Get grid selection
    row, col = gridData.grid_selected_cell
    if row >= 0:
        value = gridData.get_cell(row, col)
```

---

## Property Summary Table

| Property | Applicable To | Read/Write |
|----------|---------------|------------|
| `caption` | All | Read/Write |
| `checked` | Check Box, Option Button | Read/Write |
| `selected_index` | List Box, Combo Box | Read/Write |
| `items` | List Box, Combo Box | Read/Write (append) |
| `scroll_offset` | List Box | Read/Write |
| `group` | Option Button | Read/Write |
| `parent` | All (container) | Read/Write |
| `grid_data` | Grid | Read/Write |
| `grid_selected_cell` | Grid | Read/Write |
| `word_wrap` | TextArea | Read/Write |
| `cursor_x`, `cursor_y` | TextArea, Text Box | Read/Write |
| `x`, `y`, `w`, `h` | All | Read-only at runtime |

---

## Event Summary Table

| Event | Triggered By | Applicable Controls |
|-------|--------------|---------------------|
| `on_click` | Mouse click | Button, Timer, Picture Box |
| `on_change` | Value change | Check Box, Combo Box, List Box, Option Button, Text Box, TextArea |
| `on_focus` | Receiving focus | Text Box, TextArea, all interactive |
| `on_blur` | Losing focus | Text Box, TextArea, all interactive |
| `on_timer` | Timer interval | Timer |
| `on_load` | Form initialization | Form |
| `on_menu` | Menu click | Menu items |
| `on_cell_click` | Cell click | Grid |
| `on_cell_edit` | Cell edit | Grid |
| `on_header_click` | Header click | Grid |
| `on_key_press` | Key press | TextArea |
| `on_image_click` | Image click | Picture Box |
| `on_drag_start` | Drag start | List Box, Text Box |
| `on_drag_over` | Drag over | All drop targets |
| `on_drop` | Drop | All drop targets |

---

## Constants

### Tool Types
```
1  = Check Box
2  = Combo Box
3  = Command Button
7  = Frame
9  = Label
10 = List Box
11 = Option Button
12 = Picture Box
13 = Text Box
14 = Timer
15 = TextArea (NEW in v2.1.0)
16 = Grid (NEW in v2.1.0)
```

### Drag Data Formats
```python
FORMAT_TEXT = "text/plain"
FORMAT_LIST_ITEM = "text/list-item"
FORMAT_FILE = "text/uri-list"
FORMAT_CONTROL = "text/control-ref"
```

---

## Migration from v2.0

### New Required Fields
None - v2.1.0 is fully backward compatible.

### New Optional Fields
- `word_wrap` for TextArea (default: True)
- `grid_sort_col` for Grid (default: -1)
- `interval` for Timer (default: 1000)

### Deprecated
None - all v2.0 features remain supported.
