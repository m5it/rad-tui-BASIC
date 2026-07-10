# RAD-TUI v2.2.0 Quick Reference Card

## New Controls (v2.2.0)

### TreeView (Type 17)
```python
tree = TreeView(name_id="tree", x=2, y=2, width=30, height=10)
root = tree.add_root_node("Root", icon="R")
child = root.add_child("Child", icon="C")
tree.expand_node(root)
```

### TabControl (Type 18)
```python
tabs = TabControl(name_id="tabs", x=2, y=2, width=50, height=15)
tab1 = tabs.add_tab("General", "tabGeneral")
tabs.set_active_tab(0)
```

### ProgressBar (Type 19)
```python
pb = ProgressBar(name_id="progress", x=2, y=10, width=40)
pb.set_range(0, 100)
pb.set_value(50)
```

### Slider (Type 20)
```python
slider = Slider(name_id="slider", x=10, y=5, width=30)
slider.set_range(0, 100)
slider.set_value(50)
```

### Toolbar (Type 21)
```python
toolbar = Toolbar(name_id="toolbar", x=2, y=1, width=50)
toolbar.add_button("New", icon="N", tooltip="New File")
toolbar.add_separator()
```

### StatusBar (Type 22)
```python
status = StatusBar(name_id="status", x=2, y=22, width=76)
status.add_panel("Ready", width=30, auto_size=1)
status.add_panel("Ln 1", width=10)
```

### Splitter (Type 23)
```python
splitter = Splitter(name_id="splitter", x=25, y=2, height=15)
splitter.set_orientation(Splitter.VERTICAL)
splitter.set_position(0.3)
```

### ColorPicker (Type 24)
```python
picker = ColorPicker(name_id="picker", x=2, y=2, width=20, height=8)
picker.set_color("#FF5733")
color = picker.get_color()
```

### Chart (Type 25)
```python
chart = Chart(name_id="chart", x=2, y=2, width=40, height=15)
chart.set_chart_type(Chart.BAR)
series = chart.add_series("Sales", color="green")
series.add_point(0, 100)
```

## Database Module

```python
from database import Database

db = Database()
db.connect("app.db")

# Query
result = db.execute_query("SELECT * FROM users WHERE id = ?", (1,))
for row in result.rows:
    print(row[1])

# Insert
row_id = db.insert("users", {"name": "John", "email": "john@example.com"})

# Transaction
db.begin_transaction()
db.execute_non_query("UPDATE users SET active = 1")
db.commit()

db.disconnect()
```

## Network Module

```python
from network import NetworkManager, http_get

nm = NetworkManager()

# GET
response = nm.get("https://api.example.com/data")
if response.is_success():
    data = response.json()

# POST
response = nm.post("https://api.example.com/users", {"name": "John"})

# Download
nm.download_file("https://example.com/file.zip", "local.zip", on_progress)
```

## Regex Module

```python
from regex import Regex, regex_search, regex_replace

# Search
pattern = Regex(r"\d{3}-\d{4}")
match = pattern.search("Phone: 123-4567")
if match:
    print(match.value)  # "123-4567"

# Replace
result = regex_replace(r"\d+", "X", "Room 101")
# "Room X"

# Split
parts = regex_split(r"\s+", "a b c")
# ['a', 'b', 'c']
```

## Custom Dialogs

```python
from custom_dialog import create_input_dialog, DialogResult

dialog = create_input_dialog("Enter Name", "Your name:", "John")
result = dialog.show_dialog(modal=True)

if result == DialogResult.OK:
    name = dialog.get_value("input")
```

## Event Handlers

```python
# TreeView
def on_node_click_tree():
    node = tree.get_selected()
    if node:
        print(node.text)

# TabControl
def on_tab_change_tabs():
    idx = tabs.get_active_index()
    print(f"Switched to tab {idx}")

# Slider/ProgressBar
def on_value_change_slider():
    print(slider.get_value())

# ColorPicker
def on_color_select_picker():
    print(picker.get_color().to_hex())
```

## Built-in Functions

```python
# v2.2.0 New Functions
database_connect(path) → Database
execute_query(sql, params) → QueryResult
http_get(url) → HttpResponse
http_post(url, data) → HttpResponse
http_download(url, path, callback) → bool
regex_search(pattern, text) → Match
regex_replace(pattern, text, replacement) → str
create_input_dialog(title, prompt, default) → CustomDialog
create_confirm_dialog(title, message) → CustomDialog

# Existing Functions
msgbox(text, title)
input_box(prompt, title, default)
confirm_dialog(text, title) → bool
file_dialog(mode, filters) → path
open_file(path, mode) → handle
read_line(handle) → line
write_line(handle, text)
close_file(handle)
len(obj)
str(obj)
int(obj)
float(obj)
```

## Control Properties

### Common
- `x`, `y`, `w`, `h` - Position and size
- `name_id` - Unique identifier
- `caption` - Display text
- `visible` - Boolean visibility
- `enabled` - Boolean enabled state
- `tag` - User data
- `code` - Event handlers

### TreeView
- `indent_size` - Indentation per level
- `show_icons` - Show node icons
- `show_lines` - Show tree lines

### TabControl
- `orientation` - 0=horizontal, 1=vertical
- `show_close_button` - Show close buttons

### ProgressBar/Slider
- `min_value`, `max_value` - Range
- `current_value` - Current position
- `orientation` - 0=horizontal, 1=vertical

### Chart
- `chart_type` - 0=bar, 1=line, 2=pie
- `title` - Chart title
- `x_label`, `y_label` - Axis labels
- `show_legend` - Show legend
- `show_grid` - Show grid

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| F5 | Run application |
| F9 | Toggle breakpoint |
| Ctrl+S | Save project |
| Ctrl+O | Open project |
| Ctrl+N | New project |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Delete | Delete selected control |
| Tab | Next control |
| Shift+Tab | Previous control |
| Arrow Keys | Move selected control |

## Project Format

```json
{
  "version": "2.2.0",
  "x": 5, "y": 5, "w": 70, "h": 20,
  "title": "My Application",
  "menu_count": 0,
  "menu_items": [],
  "controls": [],
  "code": ""
}
```

## Control Types

| Type | Control |
|------|---------|
| 1 | Label |
| 2-3 | Button |
| 4 | TextBox |
| 5 | CheckBox |
| 6 | RadioButton |
| 7 | ListBox |
| 8 | ComboBox |
| 9 | Frame |
| 10 | Timer |
| 11 | Image |
| 12 | Menu |
| 13 | PopupMenu |
| 14 | Edit |
| 15 | Memo |
| 16 | Grid |
| **17** | **TreeView** |
| **18** | **TabControl** |
| **19** | **ProgressBar** |
| **20** | **Slider** |
| **21** | **Toolbar** |
| **22** | **StatusBar** |
| **23** | **Splitter** |
| **24** | **ColorPicker** |
| **25** | **Chart** |

## Common Patterns

### File Browser
```python
tree = TreeView(name_id="treeFiles")
root = tree.add_root_node("Computer")
docs = root.add_child("Documents")
docs.add_child("file.txt")
tree.expand_node(root)
```

### Settings Dialog
```python
tabs = TabControl(name_id="tabSettings")
tabs.add_tab("General")
tabs.add_tab("Advanced")
tabs.set_active_tab(0)
```

### Progress Dialog
```python
dialog = create_progress_dialog("Processing", "Please wait...")
for i in range(101):
    progress = dialog.get_value("progress")
    if progress:
        progress.set_value(i)
dialog.close_dialog(DialogResult.OK)
```

### Database Grid
```python
db = Database()
result = db.execute_query("SELECT * FROM users")
grid.grid_headers = result.columns
grid.grid_data = [list(row) for row in result.rows]
```

### API to Chart
```python
response = http_get("https://api.example.com/data")
if response.is_success():
    data = response.json()
    series = chart.add_series("API Data")
    for i, item in enumerate(data):
        series.add_point(i, item["value"])
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Control not showing | Check `visible` property |
| Events not firing | Verify `name_id` is unique |
| Database locked | Call `disconnect()` when done |
| Network timeout | Increase timeout value |
| Chart empty | Verify data format |
| Dialog not modal | Pass `modal=True` to `show_dialog()` |

## Resources

- Full API: [API_REFERENCE_V22.md](API_REFERENCE_V22.md)
- Database: [DATABASE_TUTORIAL.md](DATABASE_TUTORIAL.md)
- Charts: [CHART_CONTROL_GUIDE.md](CHART_CONTROL_GUIDE.md)
- Network: [NETWORK_GUIDE.md](NETWORK_GUIDE.md)
- Examples: `/examples/` directory

---

*Quick Reference for RAD-TUI v2.2.0*
