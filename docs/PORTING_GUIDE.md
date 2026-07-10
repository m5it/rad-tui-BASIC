# Porting Guide: VB1 DOS to RAD-TUI

## Overview

This guide helps developers migrate applications from the original VB1 DOS (Visual Basic 1.0 for DOS) to the RAD-TUI environment.

## Key Differences

| Aspect | VB1 DOS | RAD-TUI |
|--------|---------|---------|
| Language | Basic | Python / FreeBASIC |
| Platform | DOS | Linux/Windows |
| UI Style | Text-mode GUI | Terminal-based TUI |
| File Format | .FRM, .MAK | .JSON |
| Event Model | Similar | Similar |

## Control Mapping

### Basic Controls

| VB1 DOS | RAD-TUI | Notes |
|---------|---------|-------|
| `CommandButton` | `Command Btn` (Type 3) | Same functionality |
| `TextBox` | `Text Box` (Type 13) | Single-line only |
| `CheckBox` | `Check Box` (Type 1) | Visual style differs |
| `OptionButton` | `Option Btn` (Type 11) | Use `group` property |
| `Frame` | `Frame` (Type 7) | Container behavior same |
| `Label` | `Label` (Type 9) | Similar |
| `ListBox` | `List Box` (Type 10) | No multi-select |
| `ComboBox` | `Combo Box` (Type 2) | Dropdown only |
| `Timer` | `Timer` (Type 14) | Simulated |

### Not Available in RAD-TUI

| VB1 DOS Control | Workaround |
|-----------------|------------|
| `PictureBox` | Use Frame with custom characters |
| `DriveListBox` | Use Combo Box with drive list |
| `DirListBox` | Use List Box with directory items |
| `FileListBox` | Use List Box with file items |
| `HScrollBar/VScrollBar` | Built into List Box |
| `Shape` | Use text characters |
| `Image` | Not supported |

## Property Mapping

### Common Properties

| VB1 DOS | RAD-TUI | Conversion |
|---------|---------|------------|
| `Name` | `name_id` | Same purpose |
| `Caption` | `caption` | Same |
| `Text` | `caption` | For text boxes |
| `Value` | `checked` | For check boxes |
| `List` | `items` | Array of strings |
| `ListIndex` | `selected_index` | 0-based index |
| `Visible` | N/A | Always visible |
| `Enabled` | N/A | Always enabled |
| `Left`, `Top` | `x`, `y` | Same concept |
| `Width`, `Height` | `w`, `h` | Character units |

### Event Mapping

| VB1 DOS | RAD-TUI |
|---------|---------|
| `Click` | `on_click` |
| `Change` | `on_change` |
| `GotFocus` | `on_focus` |
| `LostFocus` | `on_blur` |
| `Timer` | `on_timer` |
| `Load` | `on_load` |

## Code Conversion

### Event Handlers

**VB1 DOS:**
```basic
SUB btnCalculate_Click ()
    DIM num1 AS SINGLE
    DIM num2 AS SINGLE
    
    num1 = VAL(txtNum1.Text)
    num2 = VAL(txtNum2.Text)
    
    txtResult.Text = STR$(num1 + num2)
END SUB
```

**RAD-TUI (Python):**
```python
def on_click_btnCalculate():
    num1 = float(txtNum1.caption)
    num2 = float(txtNum2.caption)
    
    txtResult.caption = str(num1 + num2)
```

**RAD-TUI (FreeBASIC):**
```freebasic
Sub on_click_btnCalculate()
    Dim num1 As Single
    Dim num2 As Single
    
    num1 = Val(txtNum1.caption)
    num2 = Val(txtNum2.caption)
    
    txtResult.caption = Str(num1 + num2)
End Sub
```

### Control Access

| VB1 DOS | RAD-TUI |
|---------|---------|
| `ControlName.Property` | `controlname.property` |
| `ControlName.Text` | `controlname.caption` |
| `ControlName.Value` | `controlname.checked` |

### String Operations

| VB1 DOS | Python | FreeBASIC |
|---------|--------|-----------|
| `STR$(num)` | `str(num)` | `Str(num)` |
| `VAL(str)` | `float(str)` or `int(str)` | `Val(str)` |
| `LEN(str)` | `len(str)` | `Len(str)` |
| `LEFT$(str, n)` | `str[:n]` | `Left(str, n)` |
| `RIGHT$(str, n)` | `str[-n:]` | `Right(str, n)` |
| `MID$(str, s, l)` | `str[s:s+l]` | `Mid(str, s, l)` |
| `INSTR(str, find)` | `str.find(find)` | `InStr(str, find)` |

### Message Boxes

**VB1 DOS:**
```basic
MsgBox "Hello, World!", "Title", "OK"
```

**RAD-TUI:**
```python
msgbox("Hello, World!", "Title")
```

### Conditional Logic

**VB1 DOS:**
```basic
IF chkOption.Value = 1 THEN
    txtResult.Text = "Enabled"
ELSE
    txtResult.Text = "Disabled"
END IF
```

**RAD-TUI (Python):**
```python
if chkOption.checked:
    txtResult.caption = "Enabled"
else:
    txtResult.caption = "Disabled"
```

### Loops

**VB1 DOS:**
```basic
FOR i = 1 TO 10
    PRINT i
NEXT i
```

**RAD-TUI (Python):**
```python
for i in range(1, 11):
    print(i)
```

**RAD-TUI (FreeBASIC):**
```freebasic
For i As Integer = 1 To 10
    Print i
Next i
```

## Step-by-Step Porting Process

### 1. Export Control Definitions

From VB1 DOS, document:
- Control types and positions
- Property values
- Event handlers

### 2. Create RAD-TUI Project

1. Start RAD-TUI IDE
2. Add corresponding controls from Toolbox
3. Set properties to match original layout
4. Adjust positions for character-based grid

### 3. Convert Event Code

1. Copy event handler logic
2. Convert syntax (see tables above)
3. Update control access patterns
4. Test each event handler

### 4. Handle Differences

| Issue | Solution |
|-------|----------|
| Graphics not supported | Use text characters or ASCII art |
| File I/O paths | Use relative paths or full paths |
| Color differences | Adapt to available color pairs |
| Font differences | Use standard terminal fonts |

## Example: Porting a Calculator

### Original VB1 DOS

```basic
' Calculator.frm
SUB btnAdd_Click()
    DIM a, b AS SINGLE
    a = VAL(txtNum1.Text)
    b = VAL(txtNum2.Text)
    txtResult.Text = STR$(a + b)
END SUB

SUB btnClear_Click()
    txtNum1.Text = ""
    txtNum2.Text = ""
    txtResult.Text = "0"
END SUB
```

### RAD-TUI Version

1. Create form with:
   - 2 Text Boxes (txtNum1, txtNum2)
   - 1 Label (txtResult)
   - 2 Buttons (btnAdd, btnClear)

2. Add code:
```python
def on_click_btnAdd():
    try:
        a = float(txtNum1.caption)
        b = float(txtNum2.caption)
        txtResult.caption = str(a + b)
    except:
        msgbox("Please enter valid numbers")

def on_click_btnClear():
    txtNum1.caption = ""
    txtNum2.caption = ""
    txtResult.caption = "0"
```

## Common Pitfalls

### 1. Variable Declaration

**VB1 DOS:**
```basic
DIM x AS INTEGER
```

**RAD-TUI (Python):**
```python
# No declaration needed
x = 0  # Just assign
```

### 2. String Concatenation

**VB1 DOS:**
```basic
result = "Hello" + " " + name$
```

**RAD-TUI (Python):**
```python
result = "Hello" + " " + name
# or
result = f"Hello {name}"
```

### 3. Arrays

**VB1 DOS:**
```basic
DIM items(1 TO 10) AS STRING
items(1) = "First"
```

**RAD-TUI (Python):**
```python
items = [""] * 10
items[0] = "First"  # 0-based indexing
```

## Testing After Porting

1. **Layout verification**: Check control positions
2. **Event testing**: Click all interactive controls
3. **Data validation**: Test with various inputs
4. **Edge cases**: Empty inputs, maximum values
5. **Menu testing**: If menus were ported

## Quick Reference Card

```
VB1 DOS → RAD-TUI

ControlName.Text → controlname.caption
ControlName.Value → controlname.checked
ControlName.List(x) → controlname.items[x]
ControlName.ListIndex → controlname.selected_index

STR$(x) → str(x)
VAL(x) → float(x) or int(x)
MSGBox → msgbox()
```

## Resources

- Example projects in `/examples` directory
- API Reference: `API_REFERENCE.md`
- Event Handling Guide: `EVENT_HANDLING.md`
- Project Format: `PROJECT_FORMAT.md`
