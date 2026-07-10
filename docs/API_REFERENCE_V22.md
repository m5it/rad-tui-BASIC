# RAD-TUI v2.2.0 API Reference

## Table of Contents

- [New Controls (v2.2.0)](#new-controls-v220)
  - [TreeView](#treeview)
  - [TabControl](#tabcontrol)
  - [ProgressBar](#progressbar)
  - [Slider](#slider)
  - [Toolbar](#toolbar)
  - [StatusBar](#statusbar)
  - [Splitter](#splitter)
  - [ColorPicker](#colorpicker)
  - [Chart](#chart)
- [Database Module](#database-module)
- [Network Module](#network-module)
- [Regex Module](#regex-module)
- [Custom Dialog Module](#custom-dialog-module)

---

## New Controls (v2.2.0)

### TreeView

Hierarchical data display with expandable nodes.

**Control Type**: 17

**Key Classes**:
- `TreeNode` - Individual node in tree
- `TreeView` - Main control

**TreeNode Properties**:
| Property | Type | Description |
|----------|------|-------------|
| `text` | str | Node display text |
| `icon` | str | Single character icon |
| `expanded` | bool | Whether node is expanded |
| `selected` | bool | Whether node is selected |
| `parent` | TreeNode | Parent node (null for root) |
| `children` | list | Child nodes |
| `tag` | any | User data |

**TreeNode Methods**:
```python
add_child(text, icon="") → TreeNode    # Add child node
remove_child(child)                    # Remove child
expand()                               # Expand node
collapse()                             # Collapse node
toggle()                               # Toggle expand/collapse
has_children() → bool                  # Check if has children
get_level() → int                     # Get nesting depth
```

**TreeView Methods**:
```python
add_root_node(text, icon="") → TreeNode    # Add root node
remove_node(node)                          # Remove node
clear()                                    # Remove all nodes
expand_node(node)                          # Expand specific node
collapse_node(node)                        # Collapse specific node
toggle_node(node)                          # Toggle node state
select_node(node)                          # Select node
get_selected() → TreeNode                  # Get selected node
get_node_at_index(index) → TreeNode       # Get by visible index
```

**Events**:
- `on_node_click(node)` - Node clicked
- `on_node_expand(node)` - Node expanded
- `on_node_collapse(node)` - Node collapsed
- `on_node_select(node)` - Selection changed

**Example**:
```python
# Create tree
tree = TreeView(name_id="treeFiles", x=2, y=2, width=25, height=10)

# Add root
root = tree.add_root_node("Documents", icon="D")

# Add children
folder1 = root.add_child("Work", icon="F")
folder1.add_child("report.docx", icon="f")
folder1.add_child("budget.xlsx", icon="f")

# Expand root
tree.expand_node(root)

# Handle events
def on_node_click_treeFiles():
    node = treeFiles.get_selected()
    if node:
        print(f"Selected: {node.text}")
```

---

### TabControl

Multi-page interface with tabbed navigation.

**Control Type**: 18

**Key Classes**:
- `TabPage` - Individual tab page
- `TabControl` - Main control

**TabPage Properties**:
| Property | Type | Description |
|----------|------|-------------|
| `caption` | str | Tab title |
| `name_id` | str | Unique identifier |
| `controls` | list | Controls on this page |
| `visible` | bool | Whether page is visible |
| `enabled` | bool | Whether page is enabled |

**TabControl Methods**:
```python
add_tab(caption, name_id="") → TabPage      # Add new tab
remove_tab(index)                           # Remove tab by index
set_active_tab(index)                       # Switch to tab
get_active_tab() → TabPage                  # Get current tab
get_active_index() → int                    # Get current index
next_tab()                                  # Go to next tab
prev_tab()                                  # Go to previous tab
clear()                                     # Remove all tabs
get_tab_count() → int                       # Get number of tabs
```

**Events**:
- `on_tab_change(index, tab)` - Tab switched
- `on_tab_click(index, tab)` - Tab clicked
- `on_tab_close(tab)` - Tab closed (if closable)

**Example**:
```python
# Create tab control
tabs = TabControl(name_id="tabMain", x=2, y=2, width=50, height=15)

# Add pages
tab_general = tabs.add_tab("General", "tabGeneral")
tab_advanced = tabs.add_tab("Advanced", "tabAdvanced")

# Add controls to tabs
tab_general.add_control(txtName)
tab_advanced.add_control(chkOption)

# Event handler
def on_tab_change_tabMain():
    idx = tabMain.get_active_index()
    print(f"Switched to tab {idx}")
```

---

### ProgressBar

Visual progress indication.

**Control Type**: 19

**Properties**:
| Property | Type | Description |
|----------|------|-------------|
| `min_value` | int/float | Minimum value |
| `max_value` | int/float | Maximum value |
| `current_value` | int/float | Current progress |
| `orientation` | int | 0=horizontal, 1=vertical |
| `show_percentage` | bool | Show % text |
| `bar_char` | str | Character for filled portion |

**Methods**:
```python
set_range(min_val, max_val)      # Set value range
set_value(value)                 # Set current value
get_value() → number              # Get current value
get_percentage() → float          # Get as percentage (0-100)
increment(amount=1)               # Increase by amount
decrement(amount=1)               # Decrease by amount
reset()                           # Reset to minimum
is_complete() → bool              # Check if at maximum
```

**Events**:
- `on_value_change(value)` - Value changed
- `on_complete()` - Reached maximum

**Example**:
```python
# Create progress bar
progress = ProgressBar(name_id="progressBar", x=2, y=10, width=40)

# Set range
progress.set_range(0, 100)

# Update progress
for i in range(101):
    progress.set_value(i)
    sleep(0.05)

# Event handler
def on_complete_progressBar():
    msgbox("Download complete!", "Done")
```

---

### Slider

Numeric value selection via dragging.

**Control Type**: 20

**Properties**:
| Property | Type | Description |
|----------|------|-------------|
| `min_value` | int/float | Minimum value |
| `max_value` | int/float | Maximum value |
| `current_value` | int/float | Current position |
| `step_increment` | int/float | Step size |
| `orientation` | int | 0=horizontal, 1=vertical |
| `show_ticks` | bool | Show tick marks |
| `tick_frequency` | int | Tick spacing |

**Methods**:
```python
set_range(min_val, max_val)      # Set value range
set_value(value)                 # Set position
get_value() → number              # Get position
get_percentage() → float          # Get as percentage
increment()                      # Step up
decrement()                      # Step down
set_step(step)                   # Set step size
```

**Events**:
- `on_value_change(value)` - Value changed (after release)
- `on_track(value)` - Value changing (during drag)
- `on_change_complete(value)` - Finished dragging

**Example**:
```python
# Volume slider
volume = Slider(name_id="sliderVolume", x=10, y=5, width=30)
volume.set_range(0, 100)
volume.set_step(5)

def on_value_change_sliderVolume():
    vol = sliderVolume.get_value()
    set_system_volume(vol)
```

---

### Toolbar

Icon button strip for common actions.

**Control Type**: 21

**Key Classes**:
- `ToolbarButton` - Individual button
- `Toolbar` - Main control

**ToolbarButton Properties**:
| Property | Type | Description |
|----------|------|-------------|
| `caption` | str | Button text |
| `icon` | str | Single character icon |
| `tooltip` | str | Hover tooltip |
| `button_type` | int | 0=push, 1=toggle, 2=separator |
| `checked` | bool | For toggle buttons |
| `enabled` | bool | Whether clickable |

**Toolbar Methods**:
```python
add_button(caption, icon, tooltip, type) → ToolbarButton
add_separator()                              # Add visual separator
remove_button(button)                        # Remove button
enable_button(index)                         # Enable by index
disable_button(index)                        # Disable by index
set_button_checked(index, checked)           # Set toggle state
```

**Events**:
- `on_button_click(index, button)` - Button clicked
- `on_button_check(index, button, checked)` - Toggle changed

**Example**:
```python
# Create toolbar
toolbar = Toolbar(name_id="toolbarMain", x=2, y=1, width=50)

# Add buttons
toolbar.add_button("New", icon="N", tooltip="New File")
toolbar.add_button("Open", icon="O", tooltip="Open File")
toolbar.add_separator()
toolbar.add_button("Save", icon="S", tooltip="Save File")

def on_button_click_toolbarMain(index, button):
    if button.caption == "New":
        new_file()
    elif button.caption == "Open":
        open_file()
```

---

### StatusBar

Multi-panel information display at form bottom.

**Control Type**: 22

**Key Classes**:
- `StatusPanel` - Individual panel
- `StatusBar` - Main control

**StatusPanel Properties**:
| Property | Type | Description |
|----------|------|-------------|
| `text` | str | Display text |
| `width` | int | Panel width |
| `auto_size` | int | 0=fixed, 1=spring, 2=percentage |
| `alignment` | str | "left", "center", "right" |
| `border` | bool | Show border |

**StatusBar Methods**:
```python
add_panel(text, width, auto_size) → StatusPanel   # Add panel
remove_panel(index)                                # Remove panel
set_panel_text(index, text)                        # Set panel text
get_panel_text(index) → str                       # Get panel text
clear_panels()                                     # Remove all
```

**Example**:
```python
# Create status bar
status = StatusBar(name_id="statusBar", x=2, y=22, width=76)

# Add panels
status.add_panel("Ready", width=30, auto_size=1)      # Spring panel
status.add_panel("Ln 1, Col 1", width=12)              # Fixed
status.add_panel("INS", width=5)                       # Fixed

# Update status
status.set_panel_text(0, "Editing file.txt")
status.set_panel_text(1, "Ln 45, Col 12")
```

---

### Splitter

Resizable panel divider.

**Control Type**: 23

**Properties**:
| Property | Type | Description |
|----------|------|-------------|
| `orientation` | int | 0=horizontal, 1=vertical |
| `position` | float | Split position (0.0-1.0) |
| `min_position` | float | Minimum position |
| `max_position` | float | Maximum position |

**Methods**:
```python
set_orientation(orientation)     # Set orientation
set_position(position)           # Set split position
get_position() → float          # Get position
get_pixel_position() → int      # Get in pixels
set_min_size(pixels)             # Set minimum panel size
set_range(min, max)              # Set allowed range
set_panel1(panel)                # Set first panel
set_panel2(panel)                # Set second panel
```

**Events**:
- `on_splitter_moving(position)` - Being dragged
- `on_splitter_moved(position)` - Released

**Example**:
```python
# Create panels
left_panel = Panel(x=2, y=2, width=20, height=15)
right_panel = Panel(x=25, y=2, width=45, height=15)

# Create splitter
splitter = Splitter(name_id="splitterMain", x=23, y=2, height=15)
splitter.set_orientation(Splitter.VERTICAL)
splitter.set_position(0.3)  # 30% to left panel

# Associate panels
splitter.set_panel1(left_panel)
splitter.set_panel2(right_panel)
```

---

### ColorPicker

Color selection interface.

**Control Type**: 24

**Key Classes**:
- `Color` - Color representation
- `ColorPicker` - Main control

**Color Methods**:
```python
Color(r, g, b)                          # Create from RGB
Color.from_hex("#FF0000")               # Create from hex
Color.from_name("red")                  # Create from name
to_hex() → str                          # Get as #RRGGBB
to_rgb() → tuple                        # Get as (r, g, b)
to_terminal_color() → int               # Get terminal color code
```

**ColorPicker Methods**:
```python
set_color(color)                        # Set current color
get_color() → Color                     # Get current color
get_hex() → str                         # Get hex string
add_custom_color(color)                 # Add to custom palette
set_palette(colors)                     # Set color palette
show_color_dialog(title) → Color        # Show modal picker
```

**Events**:
- `on_color_change(color)` - Color changed
- `on_color_select(color)` - Color selected

**Example**:
```python
# Create color picker
picker = ColorPicker(name_id="colorPicker", x=2, y=2, width=20, height=8)

# Set initial color
picker.set_color("#FF5733")

# Get selected color
def on_color_select_colorPicker():
    color = colorPicker.get_color()
    print(f"Selected: {color.to_hex()}")
```

---

### Chart

Data visualization (bar, line, pie).

**Control Type**: 25

**Key Classes**:
- `ChartSeries` - Data series
- `Chart` - Main control

**Chart Types**:
- `Chart.BAR` = 0
- `Chart.LINE` = 1
- `Chart.PIE` = 2

**ChartSeries Methods**:
```python
add_point(x, y)                         # Add data point
clear()                                 # Remove all points
get_max_y() → number                    # Get max Y value
get_min_y() → number                    # Get min Y value
```

**Chart Methods**:
```python
add_series(name, data, color) → ChartSeries   # Add series
remove_series(index)                          # Remove series
clear_series()                                # Remove all series
set_chart_type(type)                          # Set chart type
set_range(min_y, max_y)                       # Set Y-axis range
auto_scale_range()                            # Auto-calculate range
```

**Events**:
- `on_point_click(point)` - Data point clicked
- `on_series_click(series)` - Series clicked

**Example**:
```python
# Create chart
chart = Chart(name_id="chartSales", x=2, y=2, width=40, height=15)
chart.set_chart_type(Chart.BAR)
chart.title = "Monthly Sales"

# Add data series
sales = chart.add_series("Sales", color="green")
sales.add_point(0, 100)
sales.add_point(1, 150)
sales.add_point(2, 120)
sales.add_point(3, 180)

# Enable features
chart.show_legend = True
chart.show_grid = True
```

---

## Database Module

SQLite database connectivity.

**Key Classes**:
- `Database` - Connection manager
- `QueryResult` - Query results

### Database Class

**Methods**:
```python
connect(database_path) → bool                 # Connect to database
disconnect()                                  # Close connection
is_connected() → bool                          # Check connection status

# Queries
execute_query(sql, params) → QueryResult       # SELECT query
execute_non_query(sql, params) → int           # INSERT/UPDATE/DELETE

# Convenience
insert(table, data) → int                     # Insert row (returns rowid)
update(table, data, where, params) → int       # Update rows
delete(table, where, params) → int             # Delete rows

# Schema
get_tables() → list                           # List tables
get_columns(table) → list                     # Get column info
get_table_schema(table) → str                 # Get CREATE TABLE

# Transactions
begin_transaction()                            # Start transaction
commit()                                       # Commit transaction
rollback()                                     # Rollback transaction
```

### QueryResult Class

**Properties**:
| Property | Type | Description |
|----------|------|-------------|
| `rows` | list | Result rows as tuples |
| `columns` | list | Column names |
| `row_count` | int | Number of rows |
| `column_count` | int | Number of columns |
| `error` | str | Error message if failed |

**Methods**:
```python
to_dict_list() → list                 # Convert to list of dicts
get_value(row, column) → any          # Get specific value
first() → tuple                       # Get first row
is_empty() → bool                   # Check if no rows
```

**Example**:
```python
# Connect to database
db = Database()
if db.connect("app.db"):
    
    # Execute query
    result = db.execute_query("SELECT * FROM users WHERE active = ?", (1,))
    
    if not result.error:
        for row in result.rows:
            print(f"User: {row[0]}, Name: {row[1]}")
    
    # Insert data
    row_id = db.insert("users", {
        "name": "John Doe",
        "email": "john@example.com"
    })
    
    # Update with transaction
    db.begin_transaction()
    db.update("users", {"active": 0}, "last_login < ?", ("2024-01-01",))
    db.commit()
    
    db.disconnect()
```

---

## Network Module

HTTP operations and web requests.

**Key Classes**:
- `HttpRequest` - Request configuration
- `HttpResponse` - Response data
- `NetworkManager` - Request manager

### NetworkManager Methods

```python
# Simple requests
get(url, headers, timeout) → HttpResponse
post(url, data, headers, timeout) → HttpResponse
put(url, data, headers, timeout) → HttpResponse
delete(url, headers, timeout) → HttpResponse

# Advanced
request(HttpRequest) → HttpResponse

# File operations
download_file(url, local_path, on_progress, chunk_size) → bool
upload_file(url, file_path, field_name, fields) → HttpResponse

# Configuration
set_default_header(key, value)
clear_default_headers()
```

### HttpResponse Properties

| Property | Type | Description |
|----------|------|-------------|
| `status_code` | int | HTTP status code |
| `headers` | dict | Response headers |
| `body` | str | Response body |
| `url` | str | Final URL |
| `error` | str | Error message |

**Methods**:
```python
json() → any                          # Parse as JSON
is_success() → bool                   # 2xx status
is_redirect() → bool                  # 3xx status
is_client_error() → bool              # 4xx status
is_server_error() → bool              # 5xx status
```

**Example**:
```python
nm = NetworkManager()

# Simple GET
response = nm.get("https://api.example.com/users")
if response.is_success():
    users = response.json()
    for user in users:
        print(user["name"])

# POST with JSON
data = {"name": "John", "email": "john@example.com"}
response = nm.post("https://api.example.com/users", data)

# Download with progress
def on_progress(loaded, total):
    percent = loaded / total * 100
    print(f"Downloaded: {percent:.1f}%")

nm.download_file("https://example.com/file.zip", "file.zip", on_progress)
```

---

## Regex Module

Regular expression operations.

**Key Classes**:
- `Regex` - Compiled pattern
- `Match` - Match result

### Regex Class

**Flags**:
- `CASE_INSENSITIVE` - Case-insensitive matching
- `MULTILINE` - ^ and $ match line boundaries
- `DOTALL` - . matches newlines
- `VERBOSE` - Allow comments and whitespace

**Methods**:
```python
Regex(pattern, flags)                 # Compile pattern

search(text) → Match                  # Find first match
match(text) → Match                   # Match at start
fullmatch(text) → Match               # Match entire text
find_all(text) → list                 # Find all matches
find_all_strings(text) → list         # Get matched strings only

replace(text, replacement, count) → str    # Replace matches
replace_func(text, func, count) → str      # Replace with function
split(text, maxsplit) → list          # Split by pattern
count(text) → int                     # Count matches

is_valid() → bool                     # Check if pattern valid
get_error() → str                     # Get compile error
```

### Match Class

**Properties**:
| Property | Type | Description |
|----------|------|-------------|
| `value` | str | Full matched text |
| `position` | int | Start position |
| `end_position` | int | End position |
| `length` | int | Match length |

**Methods**:
```python
group(index) → str                    # Get capture group
groups() → tuple                      # Get all groups
group_dict() → dict                   # Get named groups
is_valid() → bool                     # Check if valid match
```

**Convenience Functions**:
```python
regex_search(pattern, text, flags) → Match
regex_match(pattern, text, flags) → Match
regex_replace(pattern, text, replacement, flags, count) → str
regex_split(pattern, text, flags, maxsplit) → list
is_valid_pattern(pattern) → bool
escape_regex(text) → str              # Escape special chars
```

**Example**:
```python
# Search for emails
pattern = Regex(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
match = pattern.search("Contact: john@example.com")
if match:
    print(f"Found: {match.value}")

# Find all
text = "Prices: $10, $20, $30"
prices = Regex(r"\$\d+").find_all_strings(text)
# Returns: ['$10', '$20', '$30']

# Replace
result = regex_replace(r"\d+", "X", "Room 101, Floor 2")
# Returns: "Room X, Floor X"

# Split
parts = regex_split(r"\s*,\s*", "a, b, c")
# Returns: ['a', 'b', 'c']
```

---

## Custom Dialog Module

User-defined modal dialogs.

**Key Classes**:
- `CustomDialog` - Dialog container
- `DialogButton` - Dialog button
- `DialogResult` - Result enum

### DialogResult Values

| Value | Description |
|-------|-------------|
| `NONE` | No result |
| `OK` | OK button clicked |
| `CANCEL` | Cancel button clicked |
| `YES` | Yes button clicked |
| `NO` | No button clicked |
| `ABORT` | Abort button clicked |
| `RETRY` | Retry button clicked |
| `IGNORE` | Ignore button clicked |

### CustomDialog Methods

```python
CustomDialog(name_id, title, width, height)    # Create dialog

add_control(control)                            # Add UI control
remove_control(control)                         # Remove control

add_button(text, result, default, cancel)       # Add button
clear_buttons()                                 # Remove all buttons

show_dialog(modal, parent_x, parent_y, 
            parent_w, parent_h) → DialogResult   # Show dialog
close_dialog(result)                              # Close with result

get_values() → dict                             # Get control values
get_value(name) → any                           # Get specific value
set_value(name, value)                            # Set control value
```

**Events**:
- `on_dialog_open()` - Dialog opened
- `on_dialog_close()` - Dialog closed
- `on_dialog_result(result, values)` - Result available

### Convenience Functions

```python
create_input_dialog(title, prompt, default) → CustomDialog
create_confirm_dialog(title, message, yes_no) → CustomDialog
create_list_dialog(title, items, multi_select) → CustomDialog
create_progress_dialog(title, message) → CustomDialog
```

**Example**:
```python
# Simple input dialog
dialog = create_input_dialog("Enter Name", "Your name:", "John")
result = dialog.show_dialog(modal=True)

if result == DialogResult.OK:
    name = dialog.get_value("input")
    print(f"Hello, {name}!")

# Custom settings dialog
dialog = CustomDialog("settings", "Preferences", 50, 15)
dialog.add_control(TextBox(name_id="txtName", caption="John"))
dialog.add_control(CheckBox(name_id="chkActive", checked=True))

dialog.clear_buttons()
dialog.add_button("Save", DialogResult.OK, default=True)
dialog.add_button("Cancel", DialogResult.CANCEL, cancel=True)

result = dialog.show_dialog(modal=True, 
                            parent_x=frmMain.x, parent_y=frmMain.y,
                            parent_width=frmMain.w, parent_height=frmMain.h)

if result == DialogResult.OK:
    values = dialog.get_values()
    save_settings(values)
```

---

## Version Information

- **API Version**: 2.2.0
- **Release Date**: Q2 2025
- **Previous Version**: 2.1.0
- **Compatibility**: Backward compatible with v2.1.0 projects
