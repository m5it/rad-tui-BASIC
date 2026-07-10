# Event Handling Guide

## Overview

VB1-DOS Clone uses an event-driven programming model. Your code runs in response to user actions like clicks, text entry, or timer ticks.

## Event Naming Convention

Events follow the pattern: `on_<event>_<control_name>`

Examples:
- `on_click_btnSubmit` - Button click event
- `on_change_txtName` - Text change event
- `on_focus_txtInput` - Focus gained event

## Event Types

### 1. Click Events (`on_click`)

Triggered when user clicks a control.

**Controls:** Command Buttons, Timers (when clicked)

**Example:**
```python
def on_click_btnCalculate():
    # Get input values
    num1 = int(txtNumber1.caption)
    num2 = int(txtNumber2.caption)
    
    # Calculate and display result
    result = num1 + num2
    txtResult.caption = str(result)
    
    # Update status
    lblStatus.caption = "Calculation complete"
```

---

### 2. Change Events (`on_change`)

Triggered when a control's value changes.

**Controls:** Check Boxes, Combo Boxes, List Boxes, Option Buttons, Text Boxes

**Check Box Example:**
```python
def on_change_chkAdvanced():
    if chkAdvanced.checked:
        # Show advanced options
        fraAdvanced.visible = True
        lblStatus.caption = "Advanced mode enabled"
    else:
        # Hide advanced options
        fraAdvanced.visible = False
        lblStatus.caption = "Basic mode"
```

**Text Box Example:**
```python
def on_change_txtPassword():
    password = txtPassword.caption
    
    # Validate password length
    if len(password) < 8:
        lblStrength.caption = "Weak: Too short"
    elif len(password) < 12:
        lblStrength.caption = "Medium"
    else:
        lblStrength.caption = "Strong"
```

**List Box Example:**
```python
def on_change_lstCountries():
    index = lstCountries.selected_index
    
    if index >= 0:
        selected_country = lstCountries.items[index]
        
        # Update related fields
        if selected_country == "USA":
            txtCurrency.caption = "USD"
        elif selected_country == "UK":
            txtCurrency.caption = "GBP"
        else:
            txtCurrency.caption = "EUR"
        
        lblStatus.caption = "Selected: " + selected_country
```

---

### 3. Focus Events (`on_focus`, `on_blur`)

Track when controls gain or lose focus.

**Controls:** Text Boxes, interactive controls

**Example - Form Validation:**
```python
def on_focus_txtEmail():
    lblHint.caption = "Enter a valid email address"

def on_blur_txtEmail():
    email = txtEmail.caption
    
    # Simple validation
    if "@" not in email:
        msgbox("Please enter a valid email address")
        lblStatus.caption = "Invalid email"
    else:
        lblStatus.caption = "Email validated"

def on_focus_txtPhone():
    lblHint.caption = "Format: 555-1234"

def on_blur_txtPhone():
    phone = txtPhone.caption
    if len(phone) == 0:
        msgbox("Phone number is required")
```

---

### 4. Timer Events (`on_timer`)

Triggered periodically for Timer controls.

**Controls:** Timer

**Example - Animation:**
```python
def on_timer_tmrAnimation():
    # Get current frame
    try:
        frame = int(lblFrame.caption)
    except:
        frame = 0
    
    # Increment frame
    frame = (frame + 1) % 10
    lblFrame.caption = str(frame)
    
    # Update animation
    if frame < 5:
        lblAnimation.caption = "◐"
    else:
        lblAnimation.caption = "◑"

def on_click_btnStart():
    # Enable timer (simulated by setting a flag)
    chkRunning.checked = True
    lblStatus.caption = "Animation started"

def on_click_btnStop():
    # Disable timer
    chkRunning.checked = False
    lblStatus.caption = "Animation stopped"
```

---

### 5. Load Events (`on_load`)

Triggered when form loads (run mode starts).

**Controls:** Form

**Example - Initialization:**
```python
def on_load_form():
    # Set default values
    txtDate.caption = get_current_date()
    txtUser.caption = get_username()
    
    # Populate list
    lstCategories.items = ["Electronics", "Clothing", "Food", "Books"]
    lstCategories.selected_index = 0
    
    # Set status
    lblStatus.caption = "Application ready"
    
    msgbox("Welcome to My Application!")
```

---

### 6. Menu Events (`on_menu`)

Triggered when menu items are clicked.

**Controls:** Menu items

**Example:**
```python
def on_menu_mnuFileNew():
    # Clear all fields
    txtContent.caption = ""
    txtFilename.caption = "untitled.txt"
    lblStatus.caption = "New document created"

def on_menu_mnuFileOpen():
    filename = txtFilename.caption
    if len(filename) > 0:
        lblStatus.caption = "Opening: " + filename
        # Load file logic here
    else:
        msgbox("Please enter a filename")

def on_menu_mnuFileExit():
    msgbox("Goodbye!")
    # Exit application
```

---

## Event Chaining

Events can trigger other events:

```python
def on_click_btnLoadData():
    # This might trigger on_change for lstData
    populate_list()
    lstData.selected_index = 0
    # Manually trigger change event
    on_change_lstData()

def on_change_lstData():
    # Update display based on selection
    update_detail_view()
    # Update status
    lblStatus.caption = "Data loaded"
```

---

## Error Handling

Always validate data in event handlers:

```python
def on_click_btnDivide():
    try:
        numerator = float(txtNum.caption)
        denominator = float(txtDenom.caption)
        
        if denominator == 0:
            msgbox("Cannot divide by zero!")
            txtResult.caption = "Error"
            return
        
        result = numerator / denominator
        txtResult.caption = str(result)
        lblStatus.caption = "Division successful"
        
    except ValueError:
        msgbox("Please enter valid numbers")
        txtNum.caption = ""
        txtDenom.caption = ""
        txtNum.focus()
```

---

## Best Practices

### 1. Keep Event Handlers Focused
```python
# Good - single responsibility
def on_click_btnSave():
    if validate_form():
        save_data()
        clear_form()
        msgbox("Saved successfully")

# Avoid - doing too much
def on_click_btnSave():
    # validation + saving + UI updates + logging + email sending...
```

### 2. Update Status After Operations
```python
def on_click_btnProcess():
    lblStatus.caption = "Processing..."
    
    # Do work
    result = process_data()
    
    lblStatus.caption = "Complete: " + str(result) + " items processed"
```

### 3. Provide Visual Feedback
```python
def on_change_chkEnable():
    if chkEnable.checked:
        btnAction.caption = "Enabled ✓"
        btnAction.enabled = True
    else:
        btnAction.caption = "Disabled ✗"
        btnAction.enabled = False
```

### 4. Validate Before Acting
```python
def on_click_btnDelete():
    # Confirm before destructive action
    if lstItems.selected_index >= 0:
        item = lstItems.items[lstItems.selected_index]
        
        # In real app, would show confirmation dialog
        msgbox("Deleting: " + item)
        
        # Perform deletion
        lstItems.items.pop(lstItems.selected_index)
        lstItems.selected_index = -1
        on_change_lstItems()
```

---

## Debugging Events

Use `msgbox()` to trace event flow:

```python
def on_click_btnTest():
    msgbox("Event triggered!")
    
    value = txtInput.caption
    msgbox("Value: " + value)  # Check the value
    
    result = process(value)
    msgbox("Result: " + str(result))  # Check the result
    
    txtOutput.caption = result
```

---

## Common Patterns

### Master-Detail View
```python
def on_change_lstMaster():
    index = lstMaster.selected_index
    if index >= 0:
        key = lstMaster.items[index]
        details = get_details(key)
        
        txtDetail1.caption = details[0]
        txtDetail2.caption = details[1]
        lblStatus.caption = "Showing details for " + key
```

### Wizard Navigation
```python
current_step = 0

def on_click_btnNext():
    global current_step
    if validate_step(current_step):
        current_step += 1
        show_step(current_step)
    else:
        msgbox("Please complete all fields")

def on_click_btnBack():
    global current_step
    if current_step > 0:
        current_step -= 1
        show_step(current_step)
```

### Auto-Save
```python
def on_change_txtDocument():
    # Auto-save after text changes
    content = txtDocument.caption
    save_to_temp(content)
    lblStatus.caption = "Auto-saved at " + get_time()
```
