# Project File Format Specification

## Overview

VB1-DOS Clone projects are stored as JSON files with a `.json` extension. The format is compatible between Python and FreeBASIC implementations.

## File Structure

```json
{
  "x": 21,
  "y": 4,
  "w": 36,
  "h": 17,
  "title": "Form Title",
  "menu_count": 2,
  "menu_items": [...],
  "controls": [...]
}
```

## Root Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `x` | Integer | Yes | Form X position (screen coordinates) |
| `y` | Integer | Yes | Form Y position (screen coordinates) |
| `w` | Integer | Yes | Form width in characters |
| `h` | Integer | Yes | Form height in characters |
| `title` | String | Yes | Window title bar text |
| `menu_count` | Integer | Yes | Number of menu items (0 if none) |
| `menu_items` | Array | Yes | Array of menu item objects |
| `controls` | Array | Yes | Array of control objects |

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
| 13 | Text Box | 15x1 |
| 14 | Timer | 10x1 |

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

## Version History

| Version | Changes |
|---------|---------|
| 1.0 | Initial format |
| 1.1 | Added menu support |
| 1.2 | Added `code` field for event handlers |
| 1.3 | Added `parent` for frame containment |
| 1.4 | Added `items`, `selected_index`, `scroll_offset` for list controls |

## Compatibility Notes

- FreeBASIC and Python versions use the same JSON structure
- Code syntax differs (FreeBASIC uses `Sub/End Sub`, Python uses `def`)
- Both versions can load each other's project files
- Code may need adjustment when porting between versions
