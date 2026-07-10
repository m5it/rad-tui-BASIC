# Tutorial: Building a Text Editor Application

This tutorial guides you through building a complete text editor using VB1-DOS Clone v2.1.0.

## What You'll Build

A Notepad-like text editor with:
- Multi-line text editing with word wrap
- File menu with New, Open, Save, Save As, Exit
- Status bar showing line/column position
- Find and Replace dialog
- Go To Line feature

## Prerequisites

- VB1-DOS Clone v2.1.0 installed
- Basic understanding of Python
- Terminal with mouse support

---

## Step 1: Create a New Project

1. Start VB1-DOS Clone:
   ```bash
   python3 rad-tui-py.py
   ```

2. From the File menu, select **New Project** (or press Ctrl+N)

3. You'll see a blank form. Let's configure it:
   - Click on the form border to select it
   - In the Properties panel:
     - Set `title` to "Text Editor"
     - Set `w` to 80 (full width)
     - Set `h` to 24 (full height)
     - Set `x` to 1, `y` to 1

---

## Step 2: Add the Menu Bar

1. From the toolbox, select **Menu** tool (or press M)

2. Click on the form to add a menu bar

3. Double-click the menu to edit it. Add these menu items:

   **File Menu:**
   ```
   File (mnuFile)
     ├── New (mnuNew)
     ├── Open (mnuOpen)
     ├── Save (mnuSave)
     ├── Save As (mnuSaveAs)
     ├── ──────── (separator)
     └── Exit (mnuExit)
   ```

   **Edit Menu:**
   ```
   Edit (mnuEdit)
     ├── Cut (mnuCut)
     ├── Copy (mnuCopy)
     ├── Paste (mnuPaste)
     ├── ────────
     ├── Find (mnuFind)
     └── Replace (mnuReplace)
   ```

4. Click OK to save the menu structure

---

## Step 3: Add the TextArea Control

1. From the toolbox, select **TextArea** (tool type 15)

2. Draw a large text area on the form:
   - Position: x=2, y=3
   - Size: w=76, h=18

3. Set properties:
   - `name_id`: "txtEditor"
   - `word_wrap`: True
   - `caption`: "" (empty)

4. Double-click the TextArea to add code:

```python
def on_change_txtEditor():
    # Update status bar
    update_status()

def on_key_press_txtEditor():
    # Handle special keys
    if key == "Ctrl+S":
        on_menu_mnuSave()
    elif key == "Ctrl+O":
        on_menu_mnuOpen()
    elif key == "Ctrl+N":
        on_menu_mnuNew()
    elif key == "Ctrl+F":
        on_menu_mnuFind()
```

---

## Step 4: Add the Status Bar

1. Add a Label at the bottom:
   - Position: x=2, y=22
   - Size: w=76, h=1
   - `name_id`: "lblStatus"
   - `caption`: "Line 1, Col 1 | 0 chars"

2. Add helper function:

```python
def update_status():
    lines = txtEditor.caption.split('\n')
    current_line = txtEditor.cursor_y + 1
    current_col = txtEditor.cursor_x + 1
    total_chars = len(txtEditor.caption)
    
    lblStatus.caption = f"Line {current_line}, Col {current_col} | {total_chars} chars | {len(lines)} lines"
```

---

## Step 5: Implement File Operations

### New File

Double-click the menu to edit code, then add:

```python
def on_menu_mnuNew():
    # Check if unsaved changes
    if len(txtEditor.caption) > 0:
        result = msgbox("Save changes?", "Confirm", "yesnocancel")
        if result == "yes":
            on_menu_mnuSave()
        elif result == "cancel":
            return
    
    # Clear editor
    txtEditor.caption = ""
    txtEditor.cursor_x = 0
    txtEditor.cursor_y = 0
    frmMain.title = "Text Editor - Untitled"
    update_status()
```

### Open File

```python
current_file = ""

def on_menu_mnuOpen():
    global current_file
    
    # Check for unsaved changes
    if len(txtEditor.caption) > 0:
        result = msgbox("Save changes?", "Confirm", "yesnocancel")
        if result == "yes":
            on_menu_mnuSave()
        elif result == "cancel":
            return
    
    # Open file dialog
    filename = file_dialog('open', ['.txt', '.py', '.bas', '*'])
    if not filename:
        return
    
    # Read file
    handle = open_file(filename, 'r')
    if handle:
        lines = []
        line = read_line(handle)
        while line is not None:
            lines.append(line)
            line = read_line(handle)
        close_file(handle)
        
        # Load into editor
        txtEditor.caption = '\n'.join(lines)
        current_file = filename
        frmMain.title = f"Text Editor - {filename}"
        update_status()
        msgbox(f"Loaded {len(lines)} lines", "Open")
```

### Save File

```python
def on_menu_mnuSave():
    global current_file
    
    if current_file == "":
        on_menu_mnuSaveAs()
    else:
        save_to_file(current_file)

def save_to_file(filename):
    handle = open_file(filename, 'w')
    if handle:
        lines = txtEditor.caption.split('\n')
        for line in lines:
            write_line(handle, line)
        close_file(handle)
        msgbox(f"Saved {len(lines)} lines", "Save")

def on_menu_mnuSaveAs():
    global current_file
    
    filename = file_dialog('save', ['.txt', '.py', '.bas'])
    if filename:
        # Add extension if missing
        if '.' not in filename:
            filename = filename + '.txt'
        
        # Check if file exists
        if file_exists(filename):
            result = msgbox(f"Overwrite {filename}?", "Confirm", "yesno")
            if result != "yes":
                return
        
        save_to_file(filename)
        current_file = filename
        frmMain.title = f"Text Editor - {filename}"
```

### Exit

```python
def on_menu_mnuExit():
    # Check for unsaved changes
    if len(txtEditor.caption) > 0:
        result = msgbox("Save changes before exit?", "Confirm", "yesnocancel")
        if result == "yes":
            on_menu_mnuSave()
        elif result == "cancel":
            return
    
    # Exit application
    exit()
```

---

## Step 6: Implement Edit Operations

### Cut, Copy, Paste

```python
selected_text = ""

def on_menu_mnuCut():
    global selected_text
    selected_text = txtEditor.get_selected_text()
    txtEditor.delete_text(txtEditor.selection_start, txtEditor.selection_end)
    update_status()

def on_menu_mnuCopy():
    global selected_text
    selected_text = txtEditor.get_selected_text()
    clipboard_set(selected_text)
    update_status()

def on_menu_mnuPaste():
    text = clipboard_get()
    txtEditor.insert_text(txtEditor.cursor_pos, text)
    update_status()
```

---

## Step 7: Find and Replace

### Find Dialog

```python
def on_menu_mnuFind():
    search_term = inputbox("Find:", "Find", "")
    if search_term:
        pos = txtEditor.caption.find(search_term)
        if pos >= 0:
            # Calculate line and column
            text_before = txtEditor.caption[:pos]
            lines_before = text_before.split('\n')
            line_num = len(lines_before) - 1
            col_num = len(lines_before[-1]) if lines_before else 0
            
            # Move cursor
            txtEditor.cursor_y = line_num
            txtEditor.cursor_x = col_num
            
            # Select found text
            txtEditor.selection_start = pos
            txtEditor.selection_end = pos + len(search_term)
            
            update_status()
        else:
            msgbox(f"'{search_term}' not found", "Find")
```

### Replace Dialog

```python
def on_menu_mnuReplace():
    # Create simple replace dialog using inputbox
    search_term = inputbox("Find:", "Replace", "")
    if not search_term:
        return
    
    replace_term = inputbox("Replace with:", "Replace", "")
    
    # Count occurrences
    count = txtEditor.caption.count(search_term)
    if count == 0:
        msgbox(f"'{search_term}' not found", "Replace")
        return
    
    # Confirm replace all
    result = msgbox(f"Replace {count} occurrences?", "Confirm", "yesno")
    if result == "yes":
        new_text = txtEditor.caption.replace(search_term, replace_term)
        txtEditor.caption = new_text
        msgbox(f"Replaced {count} occurrences", "Replace")
```

---

## Step 8: Add Keyboard Shortcuts

Add this to the form's `on_load` event:

```python
def on_load_frmMain():
    # Initialize
    current_file = ""
    update_status()
```

---

## Step 9: Test Your Application

1. Press **F5** to switch to Runtime mode

2. Test all features:
   - Create a new file (Ctrl+N)
   - Type some text
   - Save the file (Ctrl+S)
   - Open the file (Ctrl+O)
   - Try Find and Replace
   - Check the status bar updates

3. Press **F5** again to return to Design mode

---

## Step 10: Save Your Project

1. From the File menu, select **Save Project As**

2. Name it "text_editor.json"

3. Your text editor is now complete!

---

## Bonus Features

### Add Line Numbers

1. Add a ListBox to the left of the TextArea:
   - Position: x=1, y=3
   - Size: w=4, h=18
   - `name_id`: "lstLineNumbers"

2. Update the `update_status()` function:

```python
def update_line_numbers():
    lines = txtEditor.caption.split('\n')
    line_nums = [str(i+1) for i in range(len(lines))]
    lstLineNumbers.items = line_nums
```

### Add Word Count

Add to the status bar:

```python
def update_status():
    lines = txtEditor.caption.split('\n')
    words = len(txtEditor.caption.split())
    chars = len(txtEditor.caption)
    
    lblStatus.caption = f"Lines: {len(lines)} | Words: {words} | Chars: {chars}"
```

---

## Complete Code Listing

Here's the complete code for the text editor:

```python
# Text Editor Application
# VB1-DOS Clone v2.1.0

current_file = ""
selected_text = ""

def on_load_frmMain():
    global current_file
    current_file = ""
    frmMain.title = "Text Editor - Untitled"
    update_status()

def update_status():
    lines = txtEditor.caption.split('\n')
    words = len(txtEditor.caption.split())
    chars = len(txtEditor.caption)
    current_line = txtEditor.cursor_y + 1
    current_col = txtEditor.cursor_x + 1
    
    lblStatus.caption = f"Ln {current_line}, Col {current_col} | {len(lines)} lines | {words} words | {chars} chars"

def on_change_txtEditor():
    update_status()

def on_menu_mnuNew():
    global current_file
    if len(txtEditor.caption) > 0:
        result = msgbox("Save changes?", "Confirm", "yesnocancel")
        if result == "yes":
            on_menu_mnuSave()
        elif result == "cancel":
            return
    
    txtEditor.caption = ""
    current_file = ""
    frmMain.title = "Text Editor - Untitled"
    update_status()

def on_menu_mnuOpen():
    global current_file
    
    if len(txtEditor.caption) > 0:
        result = msgbox("Save changes?", "Confirm", "yesnocancel")
        if result == "yes":
            on_menu_mnuSave()
        elif result == "cancel":
            return
    
    filename = file_dialog('open', ['.txt', '.py', '.bas', '*'])
    if filename:
        handle = open_file(filename, 'r')
        if handle:
            lines = []
            line = read_line(handle)
            while line is not None:
                lines.append(line)
                line = read_line(handle)
            close_file(handle)
            
            txtEditor.caption = '\n'.join(lines)
            current_file = filename
            frmMain.title = f"Text Editor - {filename}"
            update_status()

def save_to_file(filename):
    handle = open_file(filename, 'w')
    if handle:
        lines = txtEditor.caption.split('\n')
        for line in lines:
            write_line(handle, line)
        close_file(handle)

def on_menu_mnuSave():
    global current_file
    if current_file == "":
        on_menu_mnuSaveAs()
    else:
        save_to_file(current_file)
        msgbox("File saved", "Save")

def on_menu_mnuSaveAs():
    global current_file
    filename = file_dialog('save', ['.txt', '.py', '.bas'])
    if filename:
        if '.' not in filename:
            filename = filename + '.txt'
        if file_exists(filename):
            result = msgbox(f"Overwrite {filename}?", "Confirm", "yesno")
            if result != "yes":
                return
        save_to_file(filename)
        current_file = filename
        frmMain.title = f"Text Editor - {filename}"

def on_menu_mnuExit():
    if len(txtEditor.caption) > 0:
        result = msgbox("Save changes before exit?", "Confirm", "yesnocancel")
        if result == "yes":
            on_menu_mnuSave()
        elif result == "cancel":
            return
    exit()

def on_menu_mnuCut():
    global selected_text
    selected_text = txtEditor.get_selected_text()
    txtEditor.delete_text(txtEditor.selection_start, txtEditor.selection_end)
    clipboard_set(selected_text)
    update_status()

def on_menu_mnuCopy():
    global selected_text
    selected_text = txtEditor.get_selected_text()
    clipboard_set(selected_text)

def on_menu_mnuPaste():
    text = clipboard_get()
    txtEditor.insert_text(txtEditor.cursor_pos, text)
    update_status()

def on_menu_mnuFind():
    search_term = inputbox("Find:", "Find", "")
    if search_term:
        pos = txtEditor.caption.find(search_term)
        if pos >= 0:
            text_before = txtEditor.caption[:pos]
            lines_before = text_before.split('\n')
            line_num = len(lines_before) - 1
            col_num = len(lines_before[-1]) if lines_before else 0
            txtEditor.cursor_y = line_num
            txtEditor.cursor_x = col_num
            msgbox(f"Found at line {line_num + 1}", "Find")
        else:
            msgbox(f"'{search_term}' not found", "Find")

def on_menu_mnuReplace():
    search_term = inputbox("Find:", "Replace", "")
    if not search_term:
        return
    replace_term = inputbox("Replace with:", "Replace", "")
    count = txtEditor.caption.count(search_term)
    if count == 0:
        msgbox(f"'{search_term}' not found", "Replace")
        return
    result = msgbox(f"Replace {count} occurrences?", "Confirm", "yesno")
    if result == "yes":
        new_text = txtEditor.caption.replace(search_term, replace_term)
        txtEditor.caption = new_text
        msgbox(f"Replaced {count} occurrences", "Replace")
        update_status()
```

---

## Next Steps

Congratulations! You've built a fully functional text editor. Here are some ideas to extend it:

1. **Add syntax highlighting** - Colorize Python keywords
2. **Add print support** - Print the document
3. **Add recent files** - Remember last 5 opened files
4. **Add search/replace with regex** - Pattern matching
5. **Add split view** - Edit two files side by side

Happy coding!
