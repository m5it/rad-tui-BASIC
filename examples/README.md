# VB1-DOS Clone Example Projects

This directory contains example projects demonstrating the capabilities of the VB1-DOS Clone IDE.

## Projects

### 1. Hello World (`hello_world.json`)
A simple introduction to the IDE featuring:
- Label controls for displaying text
- Command buttons with click handlers
- Message box integration
- Event-driven programming basics

**Usage**: Click "Click Me!" to see a greeting, then "Exit" to close.

### 2. Calculator (`calculator.json`)
A functional calculator demonstrating:
- Grid layout of buttons
- Text box for display
- Mathematical operations
- Event handlers for each button
- Basic expression evaluation

**Usage**: Click number and operator buttons to build expressions, then "=" to calculate.

### 3. Text Editor (`text_editor.json`)
A simple text editor showing:
- Multi-line list box for text lines
- Menu bar with File menu
- Text input for filename
- Line manipulation (add, clear)
- Status bar updates

**Usage**: Use "Add Line" to add text, "Clear" to reset, select lines to view details.

### 4. Database Browser (`database_browser.json`)
A customer database browser featuring:
- List box for record selection
- Frame container for grouping
- Data binding simulation
- Navigation buttons (First, Previous, Next, Last)
- Detail display fields

**Usage**: Select a customer from the list to see their details. Use navigation buttons to move through records.

### 5. Timer Demo (`timer_demo.json`)
A demonstration of timer-like functionality:
- Counter with increment/decrement
- Check box for auto mode toggle
- Start/Stop/Reset controls
- Status updates
- Animation simulation

**Usage**: Click "Start" to enable auto mode, "Stop" to pause, "Reset" to clear counter. Use +/- buttons for manual control.

## Loading Examples

1. Start the VB1-DOS Clone IDE
2. Click "File" in the menu bar
3. Select "Load Project..."
4. Navigate to the examples directory
5. Choose the desired `.json` file

## Creating Your Own Projects

To create your own projects:

1. Use the Toolbox to add controls to the form
2. Double-click controls to add event handlers
3. Use the Properties window to customize appearance
4. Save your project with File > Save Project As...

## Event Types Supported

- `on_click` - Button clicks, menu selections
- `on_change` - Text changes, check box toggles, list selections
- `on_focus` - Control receives focus
- `on_blur` - Control loses focus
- `on_timer` - Timer intervals
- `on_load` - Form initialization
- `on_menu` - Menu item clicks

## Tips

- Use `msgbox("text")` to display messages
- Access control properties: `controlname.caption`
- Access list items: `listname.items[index]`
- Use Python syntax in code editors
- Test your code in Run mode before saving
