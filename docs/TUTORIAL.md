# Tutorial: Building Your First Application

## Overview

In this tutorial, you'll build a simple "Contact Manager" application that demonstrates:
- Creating a form with controls
- Adding event handlers
- Working with list boxes
- Input validation
- Status updates

## Prerequisites

- RAD-TUI IDE installed (Python or FreeBASIC version)
- Basic understanding of programming concepts

## Step 1: Create a New Project

1. Start the RAD-TUI IDE
2. You'll see a blank "Form 1" window
3. The Properties window shows "No selection"

## Step 2: Design the Form

### Add a Title Label

1. Click on "Label" in the Toolbox (item 9)
2. Click on the form at position (5, 2)
3. A label appears with default text "Label"
4. In the Properties window, click "Cap:" row
5. Type "Contact Manager" and press Enter

### Add Input Fields

1. Add another Label at (5, 5)
   - Set Caption to "Name:"
   
2. Add a Text Box at (15, 5)
   - This will be "txtName"

3. Add another Label at (5, 7)
   - Set Caption to "Phone:"

4. Add a Text Box at (15, 7)
   - This will be "txtPhone"

### Add Action Buttons

1. Add a Command Button at (5, 10)
   - Set Caption to "Add Contact"
   - This becomes "btnAdd"

2. Add a Command Button at (20, 10)
   - Set Caption to "Clear"
   - This becomes "btnClear"

### Add a List Box

1. Add a List Box at (5, 14)
   - Default size is fine
   - This becomes "lstContacts"

### Add a Status Label

1. Add a Label at (5, 21)
   - Set Caption to "Ready"
   - This becomes "lblStatus"

Your form should now look like:
```
┌──────────────────────────────────┐
│         Contact Manager          │
├──────────────────────────────────┤
│                                  │
│  Name:     [                  ]  │
│                                  │
│  Phone:    [                  ]  │
│                                  │
│  [Add Contact]  [Clear]         │
│                                  │
│  ┌──────────────────────────┬┐  │
│  │                          ││  │
│  │                          ││  │
│  │                          ││  │
│  │                          ││  │
│  └──────────────────────────┴┘  │
│                                  │
│  Ready                           │
└──────────────────────────────────┘
```

## Step 3: Add Event Handlers

### Add Contact Button

1. Double-click the "Add Contact" button
2. The Code Editor opens with a template
3. Replace with this code:

**Python:**
```python
def on_click_btnAdd():
    # Get input values
    name = txtName.caption.strip()
    phone = txtPhone.caption.strip()
    
    # Validate input
    if len(name) == 0:
        msgbox("Please enter a name")
        return
    
    if len(phone) == 0:
        msgbox("Please enter a phone number")
        return
    
    # Add to list
    contact = name + " - " + phone
    lstContacts.items.append(contact)
    
    # Clear inputs
    txtName.caption = ""
    txtPhone.caption = ""
    
    # Update status
    lblStatus.caption = "Added: " + name
    msgbox("Contact added successfully!")
```

**FreeBASIC:**
```freebasic
Sub on_click_btnAdd()
    ' Get input values
    Dim name As String = Trim(txtName.caption)
    Dim phone As String = Trim(txtPhone.caption)
    
    ' Validate input
    If Len(name) = 0 Then
        msgbox("Please enter a name")
        Exit Sub
    End If
    
    If Len(phone) = 0 Then
        msgbox("Please enter a phone number")
        Exit Sub
    End If
    
    ' Add to list (simulated)
    Dim contact As String = name + " - " + phone
    
    ' Clear inputs
    txtName.caption = ""
    txtPhone.caption = ""
    
    ' Update status
    lblStatus.caption = "Added: " + name
    msgbox("Contact added successfully!")
End Sub
```

4. Press Enter to save

### Clear Button

1. Double-click the "Clear" button
2. Add this code:

**Python:**
```python
def on_click_btnClear():
    txtName.caption = ""
    txtPhone.caption = ""
    lblStatus.caption = "Fields cleared"
```

**FreeBASIC:**
```freebasic
Sub on_click_btnClear()
    txtName.caption = ""
    txtPhone.caption = ""
    lblStatus.caption = "Fields cleared"
End Sub
```

### List Box Selection

1. Double-click the List Box
2. Add this code:

**Python:**
```python
def on_change_lstContacts():
    idx = lstContacts.selected_index
    if idx >= 0:
        selected = lstContacts.items[idx]
        lblStatus.caption = "Selected: " + selected
```

**FreeBASIC:**
```freebasic
Sub on_change_lstContacts()
    Dim idx As Integer = lstContacts.selected_index
    If idx >= 0 Then
        Dim selected As String = lstContacts.items(idx)
        lblStatus.caption = "Selected: " + selected
    End If
End Sub
```

## Step 4: Test the Application

1. Click `[RUN ]` in the menu bar
2. The application switches to Run mode
3. Try these tests:

### Test Case 1: Add a Contact
1. Type "John Smith" in Name field
2. Type "555-1234" in Phone field
3. Click "Add Contact"
4. You should see a success message
5. The contact appears in the list

### Test Case 2: Validation
1. Clear the Name field
2. Click "Add Contact"
3. You should see an error message

### Test Case 3: Selection
1. Add multiple contacts
2. Click on different items in the list
3. Status bar updates with selection

### Test Case 4: Clear
1. Enter text in both fields
2. Click "Clear"
3. Fields should be empty

## Step 5: Enhance the Application

### Add Delete Functionality

1. Add a "Delete" button at (35, 10)
2. Set Caption to "Delete"
3. Double-click and add code:

**Python:**
```python
def on_click_btnDelete():
    idx = lstContacts.selected_index
    if idx >= 0:
        deleted = lstContacts.items[idx]
        lstContacts.items.pop(idx)
        lstContacts.selected_index = -1
        lblStatus.caption = "Deleted: " + deleted
    else:
        msgbox("Please select a contact to delete")
```

### Add Search

1. Add a Text Box at (5, 12) - "txtSearch"
2. Add a "Search" button at (25, 12)
3. Add code:

**Python:**
```python
def on_click_btnSearch():
    search_term = txtSearch.caption.lower()
    found = False
    
    for i, item in enumerate(lstContacts.items):
        if search_term in item.lower():
            lstContacts.selected_index = i
            lblStatus.caption = "Found at position " + str(i + 1)
            found = True
            break
    
    if not found:
        msgbox("Contact not found")
```

## Step 6: Save Your Project

1. Click "File" in the menu bar
2. Select "Save Project As..."
3. Type "ContactManager"
4. Click OK

Your project is saved as `ContactManager.json`

## Step 7: Add a Menu (Optional)

1. In the Properties window, click "Click here to edit menu"
2. Press 'A' to add a menu
3. Caption: "File", Name ID: "mnuFile"
4. Press 'A' again
5. Caption: "Exit", Name ID: "mnuExit"
6. Press ESC to close editor
7. Double-click the menu bar
8. Add code for Exit:

**Python:**
```python
def on_menu_mnuExit():
    msgbox("Thank you for using Contact Manager!")
```

## Complete Code Reference

### Python Version

```python
# Contact Manager - Complete Code

def on_click_btnAdd():
    name = txtName.caption.strip()
    phone = txtPhone.caption.strip()
    
    if len(name) == 0:
        msgbox("Please enter a name")
        return
    
    if len(phone) == 0:
        msgbox("Please enter a phone number")
        return
    
    contact = name + " - " + phone
    lstContacts.items.append(contact)
    
    txtName.caption = ""
    txtPhone.caption = ""
    lblStatus.caption = "Added: " + name

def on_click_btnClear():
    txtName.caption = ""
    txtPhone.caption = ""
    lblStatus.caption = "Fields cleared"

def on_change_lstContacts():
    idx = lstContacts.selected_index
    if idx >= 0:
        lblStatus.caption = "Selected: " + lstContacts.items[idx]

def on_click_btnDelete():
    idx = lstContacts.selected_index
    if idx >= 0:
        lstContacts.items.pop(idx)
        lstContacts.selected_index = -1
        lblStatus.caption = "Contact deleted"
    else:
        msgbox("Please select a contact")

def on_menu_mnuExit():
    msgbox("Goodbye!")
```

## Troubleshooting

### Problem: Controls not appearing
- Check that controls are within form boundaries
- Verify minimum sizes (width >= 4, height >= 1)

### Problem: Code not executing
- Check function name matches pattern: `on_event_controlname`
- Verify indentation (Python)
- Check for syntax errors

### Problem: List not updating
- Remember to set `selected_index` after modifying items
- Call `on_change` manually if needed

## Next Steps

1. Add more fields (Email, Address)
2. Implement Save/Load to file
3. Add sorting functionality
4. Create a search filter
5. Add edit capability for existing contacts

## Resources

- `examples/` - Sample projects
- `API_REFERENCE.md` - Complete API documentation
- `EVENT_HANDLING.md` - Event handling patterns

Congratulations! You've built your first RAD-TUI application!
