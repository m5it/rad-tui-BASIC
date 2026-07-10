# RAD-TUI Project Format v2 Specification

## Overview

This document defines the enhanced JSON project format for RAD-TUI (Rapid Application Development - Terminal User Interface). Version 2 adds support for multiple forms, menus, extended event handlers, and control-specific properties while maintaining backward compatibility with v1.

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | Initial | Single form, basic controls, on_click only |
| 2.0 | Current | Multiple forms, menus, extended events, control properties |

## File Structure

```json
{
  "version": "2.0",
  "project_name": "MyApplication",
  "main_form": "frmMain",
  "forms": [
    {
      "name_id": "frmMain",
      "title": "Main Form",
      "x": 16,
      "y": 2,
      "w": 36,
      "h": 17,
      "controls": [...],
      "menus": [...],
      "code": "..."
    }
  ],
  "global_code": "...",
  "resources": {...}
}
```

## Root Object Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | Yes | Format version ("2.0") |
| `project_name` | string | No | Human-readable project name |
| `main_form` | string | Yes | Name of form to show at startup |
| `forms` | array | Yes | Array of form objects |
| `global_code` | string | No | Code shared across all forms |
| `resources` | object | No | Strings, images, data files |

## Form Object

```json
{
  "name_id": "frmMain",
  "title": "Main Form",
  "x": 16,
  "y": 2,
  "w": 36,
  "h": 17,
  "visible": true,
  "border_style": 2,
  "controls": [...],
  "menus": [...],
  "code": "...",
  "events": {...}
}
```

### Form Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name_id` | string | required | Unique identifier for the form |
| `title` | string | "Form" | Window title bar text |
| `x`, `y` | integer | 0 | Position in terminal coordinates |
| `w`, `h` | integer | 20, 10 | Width and height |
| `visible` | boolean | true | Show at startup |
| `border_style` | integer | 2 | 0=None, 1=Single, 2=Double, 3=Dialog |
| `controls` | array | [] | Child controls |
| `menus` | array | [] | Menu bar definition |
| `code` | string | "" | Form-level code |
| `events` | object | {} | Form event handlers |

## Control Object

```json
{
  "name_id": "btnOK",
  "tool_type": 3,
  "x": 11,
  "y": 11,
  "w": 12,
  "h": 3,
  "caption": "OK",
  "enabled": true,
  "visible": true,
  "tab_index": 0,
  "events": {
    "on_click": "def on_click_btnOK():\n    msgbox('Clicked!')\n",
    "on_focus": "def on_focus_btnOK():\n    pass\n"
  },
  "properties": {...}
}
```

### Common Control Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name_id` | string | Yes | Unique identifier |
| `tool_type` | integer | Yes | Control type ID (see table) |
| `x`, `y` | integer | Yes | Position relative to form |
| `w`, `h` | integer | Yes | Size in characters |
| `caption` | string | No | Display text |
| `enabled` | boolean | No | Can receive input |
| `visible` | boolean | No | Rendered on screen |
| `tab_index` | integer | No | Tab order (-1 = skip) |
| `events` | object | No | Event handler map |
| `properties` | object | No | Type-specific properties |

### Tool Type IDs

| ID | Control | Description |
|----|---------|-------------|
| 0 | Move/Size | Selector tool (not a control) |
| 1 | Check Box | Boolean checkbox [X] or [ ] |
| 2 | Combo Box | Dropdown with editable text |
| 3 | Command Button | Push button |
| 4 | Dir List | Directory listing |
| 5 | Drive List | Drive selection dropdown |
| 6 | File List | File browser |
| 7 | Frame | Container with border |
| 8 | HScrollBar | Horizontal scrollbar |
| 9 | Label | Static text |
| 10 | List Box | Scrollable selection list |
| 11 | Option Button | Radio button (o) or ( ) |
| 12 | Picture Box | Image/ASCII art display |
| 13 | Text Box | Single-line text input |
| 14 | Timer | Background timer (invisible) |
| 15 | VScrollBar | Vertical scrollbar |
| 16 | TextArea | Multi-line text (v2.1+) |

## Control-Specific Properties

### Check Box (type 1)
```json
"properties": {
  "checked": false,
  "check_style": "x"  // "x" or "checkmark"
}
```

### Option Button (type 11)
```json
"properties": {
  "selected": false,
  "group": "group1"  // Mutual exclusion group
}
```

### Combo Box (type 2)
```json
"properties": {
  "items": ["Item 1", "Item 2", "Item 3"],
  "selected_index": 0,
  "sorted": false,
  "dropdown_count": 5
}
```

### List Box (type 10)
```json
"properties": {
  "items": ["Item 1", "Item 2", "Item 3"],
  "selected_index": -1,
  "multi_select": false,
  "sorted": false
}
```

### Frame (type 7)
```json
"properties": {
  "border_style": 2,  // 1=Single, 2=Double
  "clip_children": true
}
```

### Scroll Bars (types 8, 15)
```json
"properties": {
  "min": 0,
  "max": 100,
  "value": 0,
  "small_change": 1,
  "large_change": 10
}
```

### Timer (type 14)
```json
"properties": {
  "interval": 1000,  // Milliseconds
  "enabled": false
}
```

### Text Box / TextArea (types 13, 16)
```json
"properties": {
  "max_length": 255,
  "password_char": "",
  "read_only": false,
  "multi_line": false,
  "scroll_bars": 0  // 0=None, 1=Horizontal, 2=Vertical, 3=Both
}
```

## Event Handlers

Events are stored as strings containing Python function definitions.

### Supported Events

| Event | Trigger | Available On |
|-------|---------|--------------|
| `on_load` | Form shown first time | Forms |
| `on_unload` | Form closing | Forms |
| `on_activate` | Form gains focus | Forms |
| `on_deactivate` | Form loses focus | Forms |
| `on_click` | Mouse click | Buttons, Check, Option |
| `on_dbl_click` | Double click | Most controls |
| `on_change` | Value changed | Text, Combo, List, Check, Scroll |
| `on_focus` | Receives focus | Interactive controls |
| `on_blur` | Loses focus | Interactive controls |
| `on_key_press` | Key pressed | Focused control |
| `on_key_down` | Key down event | Forms, controls |
| `on_key_up` | Key up event | Forms, controls |
| `on_mouse_down` | Mouse button down | Controls |
| `on_mouse_up` | Mouse button up | Controls |
| `on_mouse_move` | Mouse moved | Forms |
| `on_timer` | Timer interval elapsed | Timer control |
| `on_scroll` | Scrollbar moved | Scroll bars |
| `on_select` | Item selected | List, Combo |

### Event Handler Format

```json
"events": {
  "on_click": "def on_click_btnOK():\n    msgbox('Hello!')\n    frmMain.caption = 'Clicked'\n",
  "on_focus": "def on_focus_btnOK():\n    btnOK.caption = 'Ready'\n"
}
```

Function naming convention: `{event}_{control_name_id}`

## Menu System

Menus are defined per-form in a hierarchical structure.

```json
"menus": [
  {
    "caption": "&File",
    "name_id": "mnuFile",
    "items": [
      {
        "caption": "&New",
        "name_id": "mnuFileNew",
        "shortcut": "Ctrl+N",
        "enabled": true,
        "visible": true,
        "event": "def on_click_mnuFileNew():\n    msgbox('New file')\n"
      },
      {
        "caption": "&Open...",
        "name_id": "mnuFileOpen",
        "shortcut": "Ctrl+O",
        "event": "..."
      },
      { "type": "separator" },
      {
        "caption": "E&xit",
        "name_id": "mnuFileExit",
        "event": "def on_click_mnuFileExit():\n    frmMain.close()\n"
      }
    ]
  },
  {
    "caption": "&Help",
    "name_id": "mnuHelp",
    "items": [
      {
        "caption": "&About",
        "name_id": "mnuHelpAbout",
        "event": "def on_click_mnuHelpAbout():\n    msgbox('RAD-TUI v2.0')\n"
      }
    ]
  }
]
```

### Menu Item Fields

| Field | Type | Description |
|-------|------|-------------|
| `caption` | string | Display text (& for accelerator) |
| `name_id` | string | Unique identifier |
| `shortcut` | string | Keyboard shortcut text |
| `enabled` | boolean | Can be selected |
| `visible` | boolean | Show in menu |
| `checked` | boolean | Show checkmark |
| `event` | string | Python handler code |
| `items` | array | Submenu items |
| `type` | string | "separator" for divider lines |

## Global Code

Shared code available to all forms and controls.

```json
"global_code": "
import json\n
def format_date(d):\n
    return d.strftime('%Y-%m-%d')\n
"
```

## Resources

External assets and data.

```json
"resources": {
  "strings": {
    "app_title": "My Application",
    "welcome_msg": "Welcome to RAD-TUI!"
  },
  "data": {
    "config": {"theme": "classic", "autosave": true}
  }
}
```

## Complete Example

```json
{
  "version": "2.0",
  "project_name": "HelloWorld",
  "main_form": "frmMain",
  "forms": [
    {
      "name_id": "frmMain",
      "title": "Hello World Application",
      "x": 10,
      "y": 3,
      "w": 50,
      "h": 20,
      "border_style": 2,
      "controls": [
        {
          "name_id": "lblPrompt",
          "tool_type": 9,
          "x": 2,
          "y": 2,
          "w": 20,
          "h": 1,
          "caption": "Enter your name:",
          "enabled": true,
          "visible": true
        },
        {
          "name_id": "txtName",
          "tool_type": 13,
          "x": 24,
          "y": 2,
          "w": 20,
          "h": 1,
          "caption": "",
          "tab_index": 0,
          "events": {
            "on_change": "def on_change_txtName():\n    btnOK.enabled = len(txtName.caption) > 0\n"
          },
          "properties": {
            "max_length": 50
          }
        },
        {
          "name_id": "btnOK",
          "tool_type": 3,
          "x": 20,
          "y": 5,
          "w": 10,
          "h": 3,
          "caption": "OK",
          "enabled": false,
          "tab_index": 1,
          "events": {
            "on_click": "def on_click_btnOK():\n    msgbox(f'Hello, {txtName.caption}!')\n    lblResult.caption = f'Welcome, {txtName.caption}'\n",
            "on_focus": "def on_focus_btnOK():\n    btnOK.caption = '[ OK ]'\n",
            "on_blur": "def on_blur_btnOK():\n    btnOK.caption = 'OK'\n"
          }
        },
        {
          "name_id": "lblResult",
          "tool_type": 9,
          "x": 2,
          "y": 9,
          "w": 46,
          "h": 1,
          "caption": "Click OK to see greeting",
          "enabled": true,
          "visible": true
        },
        {
          "name_id": "chkRemember",
          "tool_type": 1,
          "x": 2,
          "y": 12,
          "w": 25,
          "h": 1,
          "caption": "Remember my name",
          "tab_index": 2,
          "properties": {
            "checked": false
          }
        }
      ],
      "menus": [
        {
          "caption": "&File",
          "name_id": "mnuFile",
          "items": [
            {
              "caption": "E&xit",
              "name_id": "mnuFileExit",
              "event": "def on_click_mnuFileExit():\n    frmMain.close()\n"
            }
          ]
        }
      ],
      "events": {
        "on_load": "def on_load_frmMain():\n    txtName.set_focus()\n"
      }
    }
  ],
  "global_code": "\ndef center_message(text):\n    width = 40\n    pad = (width - len(text)) // 2\n    return ' ' * pad + text\n"
}
```

## Backward Compatibility

### Loading v1 Projects

When loading a v1 project (no `version` field):
1. Treat entire JSON as a single form
2. Generate `name_id`: "frmMain"
3. Set `version` to "2.0" after import
4. Convert `code` field to `events.on_click`

### Migration Path

```python
def migrate_v1_to_v2(v1_data):
    return {
        "version": "2.0",
        "project_name": "Migrated Project",
        "main_form": "frmMain",
        "forms": [{
            "name_id": "frmMain",
            "title": v1_data.get("title", "Form 1"),
            "x": v1_data.get("x", 0),
            "y": v1_data.get("y", 0),
            "w": v1_data.get("w", 20),
            "h": v1_data.get("h", 10),
            "controls": [
                migrate_control(c) for c in v1_data.get("controls", [])
            ]
        }],
        "global_code": ""
    }

def migrate_control(c):
    # Move code to events dict
    events = {}
    if c.get("code"):
        events["on_click"] = c["code"]
    return {
        "name_id": c.get("name_id", "ctrl"),
        "tool_type": c.get("tool_type", 0),
        "x": c.get("x", 0),
        "y": c.get("y", 0),
        "w": c.get("w", 10),
        "h": c.get("h", 1),
        "caption": c.get("caption", ""),
        "enabled": True,
        "visible": True,
        "events": events,
        "properties": {}
    }
```

## Validation Schema (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "forms"],
  "properties": {
    "version": { "const": "2.0" },
    "project_name": { "type": "string" },
    "main_form": { "type": "string" },
    "forms": {
      "type": "array",
      "items": { "$ref": "#/definitions/form" }
    },
    "global_code": { "type": "string" },
    "resources": { "type": "object" }
  },
  "definitions": {
    "form": {
      "type": "object",
      "required": ["name_id"],
      "properties": {
        "name_id": { "type": "string", "pattern": "^[a-zA-Z_][a-zA-Z0-9_]*$" },
        "title": { "type": "string" },
        "x": { "type": "integer" },
        "y": { "type": "integer" },
        "w": { "type": "integer", "minimum": 1 },
        "h": { "type": "integer", "minimum": 1 },
        "visible": { "type": "boolean" },
        "border_style": { "type": "integer", "enum": [0, 1, 2, 3] },
        "controls": { "type": "array" },
        "menus": { "type": "array" },
        "code": { "type": "string" },
        "events": { "type": "object" }
      }
    }
  }
}
```

## Implementation Notes

### Python Implementation
- Use `json` module for serialization
- Store event handlers as strings, compile with `compile()` at runtime
- Control access via `getattr/setattr` on form/control objects

### FreeBASIC Implementation
- Use external JSON library or custom parser
- Store event code strings
- For runtime: either interpret simple commands or compile to temp .bas file

## Future Extensions (v2.1+)

- **Data binding**: Link controls to data sources
- **Custom controls**: User-defined control types
- **Layout managers**: Flow, grid, table layouts
- **Themes**: Color scheme definitions
- **Localization**: Multi-language string tables
- **Binary resources**: Embed small files as base64

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-10  
**Status:** Draft for Implementation
