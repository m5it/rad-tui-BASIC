# Project File Format Specification v2.1.0

## Overview

VB1-DOS Clone projects are stored as JSON files with a `.json` extension. The format is compatible between Python and FreeBASIC implementations.

**New in v2.1.0:**
- TextArea control (Type 15)
- Grid control (Type 16)
- Extended properties for drag-drop
- Template metadata support

## File Structure

```json
{
  "version": "2.1.0",
  "x": 21,
  "y": 4,
  "w": 36,
  "h": 17,
  "title": "Form Title",
  "menu_count": 2,
  "menu_items": [...],
  "controls": [...],
  "template": {...}
}
```

## Root Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `version` | String | Yes | Project format version ("2.1.0") |
| `x` | Integer | Yes | Form X position (screen coordinates) |
| `y` | Integer | Yes | Form Y position (screen coordinates) |
| `w` | Integer | Yes | Form width in characters |
| `h` | Integer | Yes | Form height in characters |
| `title` | String | Yes | Window title bar text |
| `menu_count` | Integer | Yes | Number of menu items (0 if none) |
| `menu_items` | Array | Yes | Array of menu item objects |
| `controls` | Array | Yes | Array of control objects |
| `template` | Object | No | Template metadata (if saved as template) |

## Menu Item Object

```json
{
  "caption": "File",
  "name_id": "mnuFile",
  "parent": 0,
  "has_submenu": true
}
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `caption` | String | Yes | Menu text displayed to user |
| `name_id` | String | Yes | Unique identifier for event handling |
| `parent` | Integer | Yes | Parent menu index (0 = top-level) |
| `has_submenu` | Boolean | Yes | True if this item has child items |

### Menu Hierarchy

Top-level items have `parent: 0`. Submenu items reference their parent's 1-based index.

Example:
```json
{
  "menu_items": [
    { "caption": "File", "name_id": "mnuFile", "parent": 0, "has_submenu": true },
    { "caption": "New", "name_id": "mnuNew", "parent": 1, "has_submenu": false },
    { "caption": "Open", "name_id": "mnuOpen", "parent": 1, "has_submenu": false }
  ]
}
```

## Control Object

```json
{
  "x": 5,
  "y": 3,
  "w": 12,
  "h": 3,
  "tool_type": 3,
  "name_id": "btnSubmit",
  "caption": "Submit",
  "code": "def on_click_btnSubmit():\\n    msgbox('Hello!')\\n",
  "checked": false,
  "group": "",
  "parent": 0,
  "items": [],
  "selected_index": -1,
  "scroll_offset": 0
}
```

### Common Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `x` | Integer | Yes | Control X position (relative to form) |
| `y` | Integer | Yes | Control Y position (relative to form) |
| `w` | Integer | Yes | Control width in characters |
| `h` | Integer | Yes | Control height in characters |
| `tool_type` | Integer | Yes | Control type (see table below) |
| `name_id` | String | Yes | Unique identifier for code and access |
| `caption` | String | Yes | Display text |
| `code` | String | Yes | Event handler code (may be empty) |
| `checked` | Boolean | Yes | Checked state (for applicable controls) |
| `group` | String | Yes | Group name (for option buttons) |
| `parent` | Integer | Yes | Parent frame index (0 = no parent) |

### Type-Specific Properties

#### List Box / Combo Box

| Property | Type | Description |
|----------|------|-------------|
| `items` | Array of Strings | List of options |
| `selected_index` | Integer | Currently selected index (-1 = none) |
| `scroll_offset` | Integer | Scroll position for List Box |

#### TextArea (NEW in v2.1.0)

| Property | Type | Description |
|----------|------|-------------|
| `word_wrap` | Boolean | Enable word wrapping |
| `cursor_x` | Integer | Cursor column position |
| `cursor_y` | Integer | Cursor row position |
| `scroll_x` | Integer | Horizontal scroll offset |
| `scroll_y` | Integer | Vertical scroll offset |

#### Grid (NEW in v2.1.0)

| Property | Type | Description |
|----------|------|-------------|
| `grid_data` | 2D Array | Cell data[row][col] |
| `grid_headers` | Array | Column header strings |
| `grid_col_widths` | Array | Column width in characters |
| `grid_row_count` | Integer | Number of rows |
| `grid_col_count` | Integer | Number of columns |
| `grid_selected_cell` | Array | [row, col] of selected cell |
| `grid_sort_col` | Integer | Currently sorted column |
| `grid_sort_asc` | Boolean | Sort ascending flag |

#### Picture Box

| Property | Type | Description |
|----------|------|-------------|
| `image_path` | String | Path to image file |
| `stretch` | Boolean | Resize image to fit |
| `center` | Boolean | Center image in box |
| `border` | Boolean | Show border |
| `auto_size` | Boolean | Adjust size to image |

## Tool Type Reference

| Value | Control | Default Size |
|-------|---------|--------------|
| 1 | Check Box | 20x1 |
| 2 | Combo Box | 20x1 |
| 3 | Command Button | 12x3 |
| 7 | Frame | 20x10 |
| 9 | Label | 12x1 |
| 10 | List Box | 20x6 |
| 11 | Option Button | 20x1 |
| 12 | Picture Box | 20x10 |
| 13 | Text Box | 15x1 |
| 14 | Timer | 10x1 |
| 15 | TextArea | 60x12 |
| 16 | Grid | 40x10 |

## Template Metadata (Optional)

When saved as a template:

```json
{
  "template": {
    "name": "Text Editor",
    "description": "Simple text editor with file operations",
    "category": "Productivity",
    "author": "User Name",
    "version": "1.0",
    "created": "2025-01-15T10:30:00"
  }
}
```

## Code Encoding

Event handler code is stored as a single string with escaped newlines (`\n`).

### Python Format
```json
{
  "code": "def on_click_btnName():\\n    msgbox('Hello')\\n    txtResult.caption = 'Done'\\n"
}
```

### FreeBASIC Format
```json
{
  "code": "Sub on_click_btnName()\\n    msgbox \\\"Hello\\\"\\n    txtResult.caption = \\\"Done\\\"\\nEnd Sub"
}
```

## Complete Example

```json
{
  "version": "2.1.0",
  "x": 21,
  "y": 4,
  "w": 36,
  "h": 17,
  "title": "My Application",
  "menu_count": 1,
  "menu_items": [
    {
      "caption": "File",
      "name_id": "mnuFile",
      "parent": 0,
      "has_submenu": false
    }
  ],
  "controls": [
    {
      "x": 8,
      "y": 3,
      "w": 20,
      "h": 1,
      "tool_type": 9,
      "name_id": "lblTitle",
      "caption": "Welcome!",
      "code": "",
      "checked": false,
      "group": "",
      "parent": 0,
      "items": [],
      "selected_index": -1,
      "scroll_offset": 0
    },
    {
      "x": 12,
      "y": 8,
      "w": 12,
      "h": 3,
      "tool_type": 3,
      "name_id": "btnOK",
      "caption": "OK",
      "code": "def on_click_btnOK():\\n    msgbox('Clicked!')\\n",
      "checked": false,
      "group": "",
      "parent": 0,
      "items": [],
      "selected_index": -1,
      "scroll_offset": 0
    }
  ]
}
```

## Validation Rules

1. **name_id uniqueness**: All `name_id` values must be unique within the project
2. **Menu parent references**: `parent` values must reference valid menu item indices
3. **Control parent references**: `parent` values must reference valid control indices
4. **Position bounds**: Controls should fit within form boundaries
5. **Minimum sizes**: Controls must meet minimum dimensions
6. **Version compatibility**: Use "2.1.0" for v2.1.0 features

## Version History

| Version | Changes |
|---------|---------|
| 1.0 | Initial format |
| 1.1 | Added menu support |
| 1.2 | Added `code` field for event handlers |
| 1.3 | Added `parent` for frame containment |
| 1.4 | Added `items`, `selected_index`, `scroll_offset` for list controls |
| 2.0 | Added version field, multiple forms support |
| 2.1.0 | Added TextArea (15), Grid (16), template metadata |

## Compatibility Notes

- FreeBASIC and Python versions use the same JSON structure
- Code syntax differs (FreeBASIC uses `Sub/End Sub`, Python uses `def`)
- Both versions can load each other's project files
- v2.1.0 features require v2.1.0+ runtime
- Unknown properties are ignored for backward compatibility
