# Grid Control Usage Guide

The Grid control (Type 16) provides powerful tabular data display with sorting, selection, and editing capabilities.

---

## Overview

The Grid control is perfect for:
- Displaying database records
- Spreadsheet-like data editing
- CSV file viewing
- Data analysis and reporting

---

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `grid_data` | 2D Array | Cell data[row][col] |
| `grid_headers` | Array | Column header strings |
| `grid_col_widths` | Array | Column width in characters |
| `grid_row_count` | Integer | Number of rows |
| `grid_col_count` | Integer | Number of columns |
| `grid_selected_cell` | Tuple | (row, col) of selected cell |
| `grid_sort_col` | Integer | Currently sorted column (-1 = none) |
| `grid_sort_asc` | Boolean | Sort ascending flag |

---

## Basic Usage

### Creating a Grid

1. Select Grid tool from toolbox
2. Draw on form
3. Set properties in Property Editor:
   - `name_id`: "gridData"
   - `grid_headers`: ["Name", "Age", "City"]
   - `grid_col_widths`: [15, 8, 15]
   - `grid_col_count`: 3

### Loading Data

```python
# Set data directly
gridData.grid_data = [
    ["John Smith", "30", "New York"],
    ["Jane Doe", "25", "Boston"],
    ["Bob Wilson", "35", "Chicago"]
]
gridData.grid_row_count = 3

# Or load from CSV
gridData.load_csv("data.csv")
```

### Reading Selected Cell

```python
def on_cell_click_gridData():
    row, col = gridData.grid_selected_cell
    if row >= 0:
        value = gridData.get_cell(row, col)
        lblStatus.caption = f"Selected: {value} at row {row}, col {col}"
```

---

## Data Manipulation

### Adding Rows

```python
def on_click_btnAdd():
    new_row = ["New Name", "0", "Unknown"]
    gridData.add_row(new_row)
    msgbox("Row added", "Add")
```

### Deleting Rows

```python
def on_click_btnDelete():
    row, col = gridData.grid_selected_cell
    if row >= 0:
        result = msgbox(f"Delete row {row}?", "Confirm", "yesno")
        if result == "yes":
            gridData.delete_row(row)
```

### Updating Cells

```python
def on_click_btnUpdate():
    row, col = gridData.grid_selected_cell
    if row >= 0:
        new_value = inputbox("New value:", "Edit", gridData.get_cell(row, col))
        if new_value:
            gridData.set_cell(row, col, new_value)
```

---

## Sorting

### Sort by Column

```python
def on_header_click_gridData():
    # Toggle sort on clicked column
    col = gridData.grid_sort_col
    
    if col < 0:
        # No sort - start with ascending
        gridData.sort(0, True)
    else:
        # Toggle direction
        gridData.sort(col, not gridData.grid_sort_asc)
```

### Custom Sort

```python
def sort_by_age():
    # Sort by column 1 (Age) ascending
    gridData.sort(1, True)
    
    # Update status
    lblStatus.caption = "Sorted by Age"
```

---

## Import/Export

### Loading CSV

```python
def on_click_btnLoad():
    filename = file_dialog('open', ['.csv'])
    if filename:
        if gridData.load_csv(filename):
            msgbox(f"Loaded {gridData.grid_row_count} rows", "Load")
        else:
            msgbox("Failed to load file", "Error")
```

### Saving CSV

```python
def on_click_btnSave():
    filename = file_dialog('save', ['.csv'])
    if filename:
        if '.' not in filename:
            filename = filename + '.csv'
        if gridData.save_csv(filename):
            msgbox("File saved", "Save")
```

---

## Complete Examples

### Example 1: Simple Database Browser

```python
# Initialize with sample data
def on_load_frmMain():
    gridCustomers.grid_headers = ["ID", "Name", "Email", "Phone"]
    gridCustomers.grid_col_widths = [6, 20, 25, 15]
    gridCustomers.grid_col_count = 4
    
    gridCustomers.grid_data = [
        ["001", "John Smith", "john@email.com", "555-0101"],
        ["002", "Jane Doe", "jane@email.com", "555-0102"],
        ["003", "Bob Wilson", "bob@email.com", "555-0103"]
    ]
    gridCustomers.grid_row_count = 3

def on_cell_click_gridCustomers():
    row, col = gridCustomers.grid_selected_cell
    if row >= 0:
        # Display record details
        txtID.caption = gridCustomers.get_cell(row, 0)
        txtName.caption = gridCustomers.get_cell(row, 1)
        txtEmail.caption = gridCustomers.get_cell(row, 2)
        txtPhone.caption = gridCustomers.get_cell(row, 3)

def on_click_btnFirst():
    if gridCustomers.grid_row_count > 0:
        gridCustomers.grid_selected_cell = (0, 0)
        on_cell_click_gridCustomers()

def on_click_btnPrev():
    row, col = gridCustomers.grid_selected_cell
    if row > 0:
        gridCustomers.grid_selected_cell = (row - 1, col)
        on_cell_click_gridCustomers()

def on_click_btnNext():
    row, col = gridCustomers.grid_selected_cell
    if row < gridCustomers.grid_row_count - 1:
        gridCustomers.grid_selected_cell = (row + 1, col)
        on_cell_click_gridCustomers()

def on_click_btnLast():
    if gridCustomers.grid_row_count > 0:
        gridCustomers.grid_selected_cell = (gridCustomers.grid_row_count - 1, 0)
        on_cell_click_gridCustomers()
```

### Example 2: Spreadsheet Calculator

```python
def on_cell_edit_gridSheet():
    row, col = gridSheet.grid_selected_cell
    
    # Auto-calculate if editing column 2 or 3
    if col == 1 or col == 2:  # Price or Quantity
        price = float(gridSheet.get_cell(row, 1) or "0")
        qty = int(gridSheet.get_cell(row, 2) or "0")
        total = price * qty
        gridSheet.set_cell(row, 3, format_number(total, 2))
        
        # Update grand total
        update_total()

def update_total():
    total = 0.0
    for row in range(gridSheet.grid_row_count):
        try:
            total = total + float(gridSheet.get_cell(row, 3) or "0")
        except:
            pass
    lblTotal.caption = f"Total: ${format_number(total, 2)}"

def on_click_btnAddRow():
    new_row = ["", "0.00", "0", "0.00"]
    gridSheet.add_row(new_row)
```

### Example 3: File Browser

```python
def on_load_frmMain():
    load_directory(".")

def load_directory(path):
    files = list_files(path, "*")
    
    gridFiles.grid_headers = ["Name", "Size", "Type"]
    gridFiles.grid_col_widths = [30, 12, 10]
    gridFiles.grid_col_count = 3
    
    gridFiles.grid_data = []
    for filename in files:
        size = file_size(filename)
        type_str = "File" if "." in filename else "Folder"
        
        # Format size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size // 1024} KB"
        else:
            size_str = f"{size // (1024 * 1024)} MB"
        
        gridFiles.grid_data.append([filename, size_str, type_str])
    
    gridFiles.grid_row_count = len(gridFiles.grid_data)
    lblPath.caption = f"Path: {path}"

def on_cell_click_gridFiles():
    row, col = gridFiles.grid_selected_cell
    if row >= 0:
        filename = gridFiles.get_cell(row, 0)
        lblSelected.caption = f"Selected: {filename}"
```

### Example 4: Sortable Data Table

```python
def on_header_click_gridData():
    col = gridData.grid_sort_col
    
    # Determine sort column from click position
    # (simplified - in real app, calculate from mouse position)
    clicked_col = 0  # Determine from click
    
    if gridData.grid_sort_col == clicked_col:
        # Same column - toggle direction
        gridData.sort(clicked_col, not gridData.grid_sort_asc)
    else:
        # New column - sort ascending
        gridData.sort(clicked_col, True)
    
    update_sort_indicator()

def update_sort_indicator():
    col = gridData.grid_sort_col
    direction = "▲" if gridData.grid_sort_asc else "▼"
    
    headers = gridData.grid_headers[:]
    if col >= 0:
        headers[col] = headers[col] + " " + direction
    gridData.grid_headers = headers
```

### Example 5: Editable Grid with Validation

```python
def on_cell_edit_gridData():
    row, col = gridData.grid_selected_cell
    
    if col == 1:  # Email column
        email = gridData.get_cell(row, col)
        if "@" not in email:
            msgbox("Invalid email address!", "Validation")
            gridData.set_cell(row, col, "")  # Clear invalid
    
    elif col == 2:  # Age column
        try:
            age = int(gridData.get_cell(row, col))
            if age < 0 or age > 150:
                raise ValueError
        except:
            msgbox("Age must be 0-150", "Validation")
            gridData.set_cell(row, col, "0")

def on_click_btnSearch():
    search_term = inputbox("Search for:", "Search", "")
    if not search_term:
        return
    
    # Search all cells
    for row in range(gridData.grid_row_count):
        for col in range(gridData.grid_col_count):
            if search_term in gridData.get_cell(row, col):
                gridData.grid_selected_cell = (row, col)
                msgbox(f"Found at row {row}, col {col}", "Search")
                return
    
    msgbox("Not found", "Search")
```

---

## Styling Tips

### Column Widths

Adjust `grid_col_widths` for optimal display:

```python
# Auto-size based on content (simplified)
def auto_size_columns():
    widths = []
    for col in range(gridData.grid_col_count):
        max_width = len(gridData.grid_headers[col])
        for row in range(gridData.grid_row_count):
            cell_len = len(str(gridData.get_cell(row, col)))
            if cell_len > max_width:
                max_width = cell_len
        widths.append(max_width + 2)  # Add padding
    
    gridData.grid_col_widths = widths
```

### Alternating Row Colors

While the Grid control doesn't support colors directly, you can add visual indicators:

```python
def format_with_indicators():
    # Add row numbers or status indicators
    for row in range(gridData.grid_row_count):
        status = gridData.get_cell(row, 3)
        if status == "Complete":
            gridData.set_cell(row, 0, "✓ " + gridData.get_cell(row, 0))
        elif status == "Error":
            gridData.set_cell(row, 0, "✗ " + gridData.get_cell(row, 0))
```

---

## Best Practices

1. **Set headers first**: Define `grid_headers` before loading data
2. **Update row_count**: Always set `grid_row_count` after modifying data
3. **Validate indices**: Check bounds before accessing cells
4. **Use transactions**: Batch updates for better performance
5. **Handle empty data**: Show placeholder when no data
6. **Confirm deletes**: Ask before removing rows
7. **Auto-save**: Save changes periodically

---

## Event Reference

| Event | Description |
|-------|-------------|
| `on_cell_click` | User clicked a cell |
| `on_cell_edit` | User edited a cell |
| `on_header_click` | User clicked column header |
| `on_selection_change` | Selection changed |

---

## Method Reference

| Method | Description |
|--------|-------------|
| `get_cell(row, col)` | Get cell value |
| `set_cell(row, col, value)` | Set cell value |
| `add_row(data)` | Append row |
| `delete_row(index)` | Remove row |
| `sort(col, ascending)` | Sort by column |
| `load_csv(filename)` | Load from CSV |
| `save_csv(filename)` | Save to CSV |
