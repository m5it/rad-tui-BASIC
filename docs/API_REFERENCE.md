# VB1-DOS Clone API Reference

## Controls

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

**Example:**
```python
def on_change_cmbColors():
    idx = cmbColors.selected_index
    if idx >= 0:
        lblResult.caption = "Selected: " + cmbColors.items[idx]
```

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

**Example:**
```python
def on_click_btnSave():
    msgbox("Data saved!")
    txtStatus.caption = "Saved at " + get_time()
```

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

**Events:**
- None

**Example:**
```python
# Frame is a container, access child controls directly
def on_click_btnInFrame():
    txtInFrame.caption = "Updated"
```

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

**Events:**
- None

**Example:**
```python
# Update label from code
lblStatus.caption = "Processing complete"
```

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

**Example:**
```python
def on_change_lstCustomers():
    idx = lstCustomers.selected_index
    if idx >= 0:
        txtDetail.caption = lstCustomers.items[idx]
```

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

**Example:**
```python
def on_change_optSize():
    if optSmall.checked:
        txtPrice.caption = "$10"
    elif optMedium.checked:
        txtPrice.caption = "$20"
    elif optLarge.checked:
        txtPrice.caption = "$30"
```

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

**Example:**
```python
def on_change_txtName():
    if len(txtName.caption) > 0:
        lblGreeting.caption = "Hello, " + txtName.caption
    else:
        lblGreeting.caption = "Please enter your name"

def on_focus_txtName():
    lblStatus.caption = "Enter your full name"

def on_blur_txtName():
    if len(txtName.caption) == 0:
        msgbox("Name is required!")
```

---

### Timer (Type 14)
Triggers periodic events (simulated).

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `name_id` | String | Unique identifier |
| `caption` | String | Timer label |
| `x`, `y` | Integer | Position coordinates |
| `w`, `h` | Integer | Size |

**Events:**
- `on_timer` - Fired on each timer tick
- `on_click` - Fired when timer control clicked

**Example:**
```python
def on_timer_tmrAnimation():
    # Increment animation frame
    current = int(lblFrame.caption)
    lblFrame.caption = str(current + 1)
```

---

## Global Functions

### `msgbox(text, title="Message")`
Displays a modal message dialog.

**Parameters:**
- `text` (String) - Message to display
- `title` (String) - Dialog title (optional)

**Example:**
```python
msgbox("Operation completed successfully", "Success")
```

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
    
    # Get list selection
    idx = lstOptions.selected_index
    if idx >= 0:
        selected = lstOptions.items[idx]
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
| `x`, `y`, `w`, `h` | All | Read-only at runtime |

---

## Event Summary Table

| Event | Triggered By | Applicable Controls |
|-------|--------------|---------------------|
| `on_click` | Mouse click | Button, Timer |
| `on_change` | Value change | Check Box, Combo Box, List Box, Option Button, Text Box |
| `on_focus` | Receiving focus | Text Box, all interactive |
| `on_blur` | Losing focus | Text Box, all interactive |
| `on_timer` | Timer interval | Timer |
| `on_load` | Form initialization | Form |
| `on_menu` | Menu click | Menu items |

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
13 = Text Box
14 = Timer
```
