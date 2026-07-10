# File I/O Operations Guide

VB1-DOS Clone v2.1.0 provides comprehensive file I/O capabilities for building applications that read, write, and manipulate files.

---

## Basic File Operations

### Opening a File

Use `open_file()` to open a file for reading or writing:

```python
# Open for reading
handle = open_file("data.txt", "r")

# Open for writing (creates or truncates)
handle = open_file("output.txt", "w")

# Open for appending
handle = open_file("log.txt", "a")

# Always check if successful
if handle:
    # File operations...
    close_file(handle)
else:
    msgbox("Failed to open file!", "Error")
```

### Reading Files

#### Read Line by Line
```python
handle = open_file("data.txt", "r")
if handle:
    lines = []
    line = read_line(handle)
    while line is not None:
        lines.append(line)
        line = read_line(handle)
    close_file(handle)
    
    # Load into ListBox
    lstData.items = lines
```

#### Read Entire File
```python
def read_entire_file(filename):
    handle = open_file(filename, "r")
    if not handle:
        return None
    
    content = ""
    line = read_line(handle)
    while line is not None:
        content = content + line + "\n"
        line = read_line(handle)
    close_file(handle)
    return content

# Usage
text = read_entire_file("document.txt")
txtEditor.caption = text
```

### Writing Files

#### Write Line by Line
```python
handle = open_file("output.txt", "w")
if handle:
    for item in lstItems.items:
        write_line(handle, item)
    close_file(handle)
    msgbox("File saved successfully!", "Save")
```

#### Write Multiple Lines
```python
def write_entire_file(filename, content):
    handle = open_file(filename, "w")
    if not handle:
        return False
    
    lines = content.split('\n')
    for line in lines:
        write_line(handle, line)
    close_file(handle)
    return True

# Usage
write_entire_file("document.txt", txtEditor.caption)
```

---

## File Management

### Check File Existence
```python
if file_exists("config.txt"):
    load_config()
else:
    create_default_config()
```

### Delete a File
```python
if file_exists("temp.txt"):
    if delete_file("temp.txt"):
        msgbox("Temporary file deleted", "Cleanup")
```

### Rename a File
```python
if rename_file("oldname.txt", "newname.txt"):
    msgbox("File renamed successfully", "Rename")
```

### Get File Size
```python
size = file_size("data.txt")
if size >= 0:
    lblSize.caption = f"Size: {size} bytes"
else:
    lblSize.caption = "File not found"
```

### List Directory Contents
```python
files = list_files(".", "*.txt")
for filename in files:
    lstFiles.items.append(filename)
```

---

## Common Dialogs

### Open File Dialog
```python
filename = file_dialog('open', ['.txt', '.csv', '.json'])
if filename:
    handle = open_file(filename, 'r')
    # ... process file
```

### Save File Dialog
```python
filename = file_dialog('save', ['.txt'])
if filename:
    # Add extension if missing
    if '.' not in filename:
        filename = filename + '.txt'
    
    # Check for overwrite
    if file_exists(filename):
        result = msgbox("File exists. Overwrite?", "Confirm", "yesno")
        if result != "yes":
            return
    
    handle = open_file(filename, 'w')
    # ... write file
```

---

## Practical Examples

### Example 1: Simple Notepad
```python
def on_click_btnOpen():
    filename = file_dialog('open', ['.txt', '*'])
    if not filename:
        return
    
    handle = open_file(filename, 'r')
    if handle:
        content = ""
        line = read_line(handle)
        while line is not None:
            content = content + line + "\n"
            line = read_line(handle)
        close_file(handle)
        
        txtEditor.caption = content
        lblFilename.caption = filename

def on_click_btnSave():
    filename = file_dialog('save', ['.txt'])
    if not filename:
        return
    
    if '.' not in filename:
        filename = filename + '.txt'
    
    handle = open_file(filename, 'w')
    if handle:
        lines = txtEditor.caption.split('\n')
        for line in lines:
            write_line(handle, line)
        close_file(handle)
        msgbox("File saved!", "Success")
```

### Example 2: CSV Data Viewer
```python
def load_csv(filename):
    handle = open_file(filename, 'r')
    if not handle:
        return False
    
    gridData.grid_data = []
    line = read_line(handle)
    
    # Read header
    if line:
        headers = split(line, ',')
        gridData.grid_headers = headers
        gridData.grid_col_count = len(headers)
    
    # Read data rows
    row_count = 0
    line = read_line(handle)
    while line is not None:
        cells = split(line, ',')
        gridData.grid_data.append(cells)
        row_count = row_count + 1
        line = read_line(handle)
    
    close_file(handle)
    gridData.grid_row_count = row_count
    return True

def save_csv(filename):
    handle = open_file(filename, 'w')
    if not handle:
        return False
    
    # Write header
    header_line = join(gridData.grid_headers, ',')
    write_line(handle, header_line)
    
    # Write data rows
    for row in gridData.grid_data:
        line = join(row, ',')
        write_line(handle, line)
    
    close_file(handle)
    return True
```

### Example 3: Configuration File
```python
def load_config():
    if not file_exists("app.config"):
        return False
    
    handle = open_file("app.config", "r")
    if not handle:
        return False
    
    line = read_line(handle)
    while line is not None:
        if line.startswith("username="):
            txtUsername.caption = line[9:]
        elif line.startswith("theme="):
            cmbTheme.selected_index = int(line[6:])
        elif line.startswith("autosave="):
            chkAutosave.checked = (line[9:] == "true")
        line = read_line(handle)
    
    close_file(handle)
    return True

def save_config():
    handle = open_file("app.config", "w")
    if not handle:
        return False
    
    write_line(handle, "username=" + txtUsername.caption)
    write_line(handle, "theme=" + str(cmbTheme.selected_index))
    write_line(handle, "autosave=" + ("true" if chkAutosave.checked else "false"))
    
    close_file(handle)
    return True
```

### Example 4: Log File
```python
def log_message(message):
    handle = open_file("app.log", "a")
    if handle:
        timestamp = get_datetime()
        write_line(handle, timestamp + " - " + message)
        close_file(handle)

def on_click_btnProcess():
    log_message("Processing started")
    # ... processing code ...
    log_message("Processing completed")
```

### Example 5: Import/Export
```python
def export_data():
    filename = file_dialog('save', ['.txt', '.csv'])
    if not filename:
        return
    
    handle = open_file(filename, 'w')
    if handle:
        # Export grid data
        for row in gridData.grid_data:
            line = join(row, "\t")
            write_line(handle, line)
        close_file(handle)
        msgbox("Data exported!", "Export")

def import_data():
    filename = file_dialog('open', ['.txt', '.csv', '.tsv'])
    if not filename:
        return
    
    handle = open_file(filename, 'r')
    if handle:
        gridData.grid_data = []
        line = read_line(handle)
        while line is not None:
            cells = split(line, '\t')
            gridData.grid_data.append(cells)
            line = read_line(handle)
        close_file(handle)
        gridData.grid_row_count = len(gridData.grid_data)
        msgbox("Data imported!", "Import")
```

---

## Error Handling

Always handle file errors gracefully:

```python
def safe_file_operation():
    # Check if file exists before reading
    if not file_exists("data.txt"):
        msgbox("File not found!", "Error")
        return
    
    # Try to open with error handling
    handle = open_file("data.txt", "r")
    if not handle:
        msgbox("Cannot open file!", "Error")
        return
    
    # Process with error checking
    try:
        content = ""
        line = read_line(handle)
        while line is not None:
            content = content + line + "\n"
            line = read_line(handle)
    except:
        msgbox("Error reading file!", "Error")
    finally:
        close_file(handle)
    
    return content
```

---

## Best Practices

1. **Always close files**: Use `close_file()` when done
2. **Check return values**: Verify file operations succeeded
3. **Use dialogs for user files**: Let users choose files with `file_dialog()`
4. **Handle extensions**: Check/add file extensions automatically
5. **Confirm overwrites**: Ask before replacing existing files
6. **Use try/except**: Wrap file operations in error handling
7. **Log operations**: Keep audit trails for important operations

---

## File I/O Function Reference

| Function | Description |
|----------|-------------|
| `open_file(filename, mode)` | Open file for reading/writing |
| `read_line(handle)` | Read next line from file |
| `write_line(handle, text)` | Write line to file |
| `close_file(handle)` | Close open file |
| `file_exists(filename)` | Check if file exists |
| `delete_file(filename)` | Delete a file |
| `rename_file(old, new)` | Rename a file |
| `file_size(filename)` | Get file size in bytes |
| `list_files(dir, pattern)` | List files matching pattern |
| `file_dialog(mode, filters)` | Show file open/save dialog |
