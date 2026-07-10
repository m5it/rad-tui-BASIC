# Debugging Guide for Runtime Mode

VB1-DOS Clone v2.1.0 includes powerful debugging capabilities to help you find and fix issues in your applications.

---

## Debug Window

The Debug Window provides real-time visibility into your application's execution.

### Opening the Debug Window

- **Design Mode**: Tools → Debug Window (or Ctrl+D)
- **Runtime Mode**: Press F12 to toggle

### Debug Window Tabs

#### 1. Variables Tab
Shows all variables in the current scope:
- Local variables from event handlers
- Control properties
- Global variables

```
x              = 42
y              = "hello"
txtName.caption = "John"
lstItems.items  = ["Item 1", "Item 2"]
```

#### 2. Call Stack Tab
Displays the execution stack:
```
process()      at myapp.py:45
helper()       at myapp.py:32
on_click_btnGo at myapp.py:15
```

#### 3. Watches Tab
Monitor specific expressions:
```
Expression          Value
----------------    -----
x * y               420
len(lstItems.items) 2
txtName.caption     "John"
```

#### 4. Output Tab
Shows debug messages and print statements:
```
[PRINT] Starting calculation...
[DEBUG] Step 1 complete
[ERROR] Division by zero at line 42
```

---

## Breakpoints

Set breakpoints to pause execution at specific lines.

### Setting Breakpoints

1. Open the Code Editor (double-click a control)
2. Navigate to the line where you want to pause
3. Press F9 or click in the gutter
4. A red dot appears indicating the breakpoint

### Managing Breakpoints

| Action | Shortcut |
|--------|----------|
| Toggle breakpoint | F9 |
| Clear all breakpoints | Ctrl+Shift+F9 |
| Disable breakpoint | Click the red dot |

### Breakpoint Behavior

When execution hits a breakpoint:
- Application pauses
- Debug Window shows current state
- Variables show values at that moment
- Call stack is captured

---

## Step-Through Execution

Control execution flow when paused.

### Step Into (F11)
Execute the current line and step into any function call.
```python
def on_click_btnCalculate():
    result = calculate()  # <-- Step Into enters calculate()
    show_result(result)
```

### Step Over (F10)
Execute the current line without entering functions.
```python
def on_click_btnCalculate():
    result = calculate()  # <-- Step Over runs calculate(), pauses after
    show_result(result)   # <-- Pauses here
```

### Step Out (Shift+F11)
Execute until the current function returns.
```python
def calculate():
    x = 1
    y = 2
    return x + y  # <-- Step Out runs to here, returns to caller
```

### Continue (F5)
Resume normal execution until next breakpoint or error.

---

## Watch Expressions

Monitor variables and expressions as they change.

### Adding Watches

1. In the Debug Window, switch to Watches tab
2. Press Insert or right-click → Add Watch
3. Enter expression: `gridData.grid_row_count * 2`
4. Press Enter

### Watch Expression Examples

```python
# Simple variables
x
counter
txtName.caption

# Expressions
x + y
len(lstItems.items)
gridData.grid_row_count > 0

# Control properties
txtResult.caption.upper()
float(txtPrice.caption) * int(txtQty.caption)
```

### Watch Evaluation

- Watches update automatically when execution pauses
- Invalid expressions show `<Error: ...>`
- Complex expressions may impact performance

---

## Runtime Error Handling

### Error Display

When an error occurs:
1. Execution pauses
2. Error message appears in Output tab
3. Source line is highlighted
4. Call stack shows where error occurred

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| NameError | Variable not defined | Check variable name spelling |
| TypeError | Wrong operation on type | Verify data types |
| IndexError | List index out of range | Check bounds before accessing |
| KeyError | Dictionary key not found | Verify key exists |
| ZeroDivisionError | Division by zero | Check denominator |

### Error Recovery

```python
def on_click_btnCalculate():
    try:
        result = 100 / int(txtDivisor.caption)
        txtResult.caption = str(result)
    except ZeroDivisionError:
        msgbox("Cannot divide by zero!", "Error")
        txtResult.caption = "Error"
    except ValueError:
        msgbox("Please enter a valid number", "Error")
```

---

## Debug Output

Use `debug_print()` to trace execution.

### Basic Usage

```python
def on_click_btnProcess():
    debug_print("Starting process...")
    
    for i in range(len(lstItems.items)):
        debug_print(f"Processing item {i}: {lstItems.items[i]}")
        # ... process item ...
    
    debug_print(f"Completed. Total: {len(lstItems.items)}")
```

### Conditional Debugging

```python
def on_change_txtValue():
    debug_print(f"Value changed to: {txtValue.caption}")
    
    if debug_mode:  # Set in your app
        debug_print("Call stack:", get_call_stack())
        debug_print("Variables:", get_variables())
```

### Debug vs Print

```python
# Use debug_print for development messages
debug_print("Debug: Entering function")

# Use msgbox for user-facing messages
msgbox("Operation complete", "Done")
```

---

## Debugging Techniques

### Technique 1: Binary Search

When you don't know where the bug is:
1. Set breakpoint at halfway point
2. Check if error occurred before or after
3. Repeat with smaller section

### Technique 2: Variable Inspection

Track variable values through execution:
```python
def calculate_total():
    debug_print("Starting calculation")
    total = 0
    
    for price in prices:
        debug_print(f"Adding price: {price}")
        total = total + price
        debug_print(f"Running total: {total}")
    
    debug_print(f"Final total: {total}")
    return total
```

### Technique 3: Assertions

Verify assumptions:
```python
def process_data(data):
    # Ensure data is valid
    assert len(data) > 0, "Data cannot be empty"
    assert isinstance(data, list), "Data must be a list"
    
    # Process...
```

### Technique 4: Step Through New Code

When adding new functionality:
1. Set breakpoint at start
2. Step through line by line
3. Verify each step produces expected result

---

## Debugging Examples

### Example 1: Finding a Logic Error

```python
# Bug: Always shows "Even" for odd numbers
def on_click_btnCheck():
    num = int(txtNumber.caption)
    
    # Set breakpoint here
    debug_print(f"Input number: {num}")
    
    if num / 2 == 0:  # BUG: Should be num % 2
        lblResult.caption = "Even"
    else:
        lblResult.caption = "Odd"
    
    debug_print(f"Result: {lblResult.caption}")
```

### Example 2: Tracking Data Flow

```python
def on_click_btnLoad():
    filename = file_dialog('open', ['.csv'])
    debug_print(f"Selected file: {filename}")
    
    if filename:
        gridData.load_csv(filename)
        debug_print(f"Rows loaded: {gridData.grid_row_count}")
        debug_print(f"Columns: {gridData.grid_col_count}")
        
        update_display()
        debug_print("Display updated")

def update_display():
    debug_print("Entering update_display")
    for row in range(gridData.grid_row_count):
        debug_print(f"Processing row {row}")
        # ... processing ...
    debug_print("Exiting update_display")
```

### Example 3: Debugging Event Handlers

```python
def on_change_txtInput():
    debug_print("on_change_txtInput triggered")
    debug_print(f"New value: {txtInput.caption}")
    
    # Check if this causes unexpected recursion
    if len(txtInput.caption) > 10:
        txtInput.caption = txtInput.caption[:10]  # Truncate
        debug_print("Value truncated to 10 chars")

def on_focus_txtInput():
    debug_print("txtInput received focus")

def on_blur_txtInput():
    debug_print("txtInput lost focus")
    debug_print(f"Final value: {txtInput.caption}")
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| F5 | Continue execution |
| F9 | Toggle breakpoint |
| F10 | Step over |
| F11 | Step into |
| Shift+F11 | Step out |
| F12 | Toggle Debug Window |
| Ctrl+Shift+F9 | Clear all breakpoints |

---

## Best Practices

1. **Use descriptive debug messages**: `debug_print(f"User clicked row {row}")` not `debug_print("here")`
2. **Remove debug code before release**: Or use conditional debugging
3. **Set strategic breakpoints**: At function starts, after user input
4. **Watch key variables**: Those that affect program flow
5. **Check boundary conditions**: First/last items, empty lists
6. **Verify data types**: Ensure variables are expected type
7. **Test error paths**: Verify error handling works

---

## Troubleshooting

### Debug Window Not Showing
- Check if F12 is mapped to something else in your terminal
- Try Tools → Debug Window from menu

### Breakpoints Not Working
- Ensure code is saved before running
- Check that breakpoint is on executable line (not blank or comment)
- Verify you're in Runtime mode (F5)

### Variables Not Updating
- Execution must be paused for variables to refresh
- Some optimizations may prevent variable inspection
- Use `debug_print()` to force value display

### Performance Issues
- Too many watches can slow execution
- Remove breakpoints in loops that execute many times
- Use conditional breakpoints: `if i > 100: debug_break()`
