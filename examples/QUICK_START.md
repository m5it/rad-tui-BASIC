# VB1-DOS Clone Quick Start Guide

## Getting Started

### Running the IDE

**Python Version:**
```bash
python rad-tui-py.py
```

**FreeBASIC Version:**
```bash
fbc rad-tui-BASIC.bas
./rad-tui-BASIC
```

### Basic Workflow

1. **Design Mode** (default):
   - Add controls from the Toolbox
   - Position and resize controls
   - Edit properties in the Properties window
   - Double-click controls to add code

2. **Run Mode**:
   - Click `[RUN ]` to test your application
   - Click `[STOP]` to return to design mode

## Controls Reference

| Tool # | Control | Typical Use |
|--------|---------|-------------|
| 1 | Check Box | Boolean options |
| 2 | Combo Box | Dropdown selection |
| 3 | Command Button | Actions, triggers |
| 7 | Frame | Grouping controls |
| 9 | Label | Display text |
| 10 | List Box | Select from list |
| 11 | Option Button | Mutually exclusive choice |
| 13 | Text Box | Text input |
| 14 | Timer | Periodic events |

## Event Handlers

Add code by double-clicking controls. Common patterns:

```python
# Button click
def on_click_btnName():
    msgbox("Hello!")
    txtDisplay.caption = "Updated"

# Text change
def on_change_txtName():
    lblStatus.caption = "Text changed"

# List selection
def on_change_lstItems():
    selected = lstItems.selected_index
    txtDisplay.caption = lstItems.items[selected]
```

## Property Access

Access control properties at runtime:

```python
# Read property
current_text = txtInput.caption

# Set property
txtInput.caption = "New text"
lblStatus.caption = "Updated"

# Check box
if chkOption.checked:
    msgbox("Checked!")
else:
    msgbox("Not checked")

# List box
lstItems.items.append("New item")
lstItems.selected_index = 0
```

## Menu System

1. In Properties window, click "Click here to edit menu"
2. Press 'A' to add menu items
3. Set caption and name ID
4. For submenus, answer 'Y' when prompted
5. ESC to close editor

Menu event handlers:
```python
def on_menu_mnuFile():
    msgbox("File menu clicked")

def on_menu_mnuNew():
    msgbox("New document")
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| ESC | Cancel / Exit dialog |
| ENTER | Confirm / Save |
| Arrow keys | Navigate / Move controls |
| TAB | Indent in code editor |

## Troubleshooting

**Controls not appearing in Run mode:**
- Check that controls are within form boundaries
- Verify control size (minimum 1 height, 4 width)

**Code not executing:**
- Check function name matches `on_event_controlname`
- Verify Python syntax (indentation matters!)
- Use `msgbox()` to debug

**Menu not showing:**
- Add at least one top-level menu item (parent=0)
- Menu bar appears below title bar

## Sample Code Snippets

### Counter Application
```python
def on_click_btnIncrement():
    value = int(txtCounter.caption)
    txtCounter.caption = str(value + 1)
```

### Toggle Switch
```python
def on_change_chkEnable():
    if chkEnable.checked:
        btnAction.caption = "Enabled"
    else:
        btnAction.caption = "Disabled"
```

### List Navigation
```python
def on_click_btnNext():
    current = lstData.selected_index
    if current < len(lstData.items) - 1:
        lstData.selected_index = current + 1
        on_change_lstData()  # Refresh display
```

## Next Steps

1. Load the example projects to see working code
2. Modify the examples to understand how they work
3. Create your own project from scratch
4. Experiment with different control combinations

Happy coding!
