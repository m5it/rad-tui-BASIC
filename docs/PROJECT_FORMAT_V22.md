# RAD-TUI Project Format Specification v2.2.0

## Overview

This document specifies the JSON project file format for RAD-TUI v2.2.0, including new features and backward compatibility with v2.1.0.

## Version Information

- **Format Version**: 2.2.0
- **Release Date**: 2025
- **Backward Compatible**: Yes (v2.1.0 projects load without modification)
- **File Extension**: `.json`

## JSON Structure

```json
{
  "version": "2.2.0",
  "x": 0,
  "y": 0,
  "w": 80,
  "h": 24,
  "title": "Application Title",
  "menu_count": 0,
  "menu_items": [],
  "controls": [],
  "code": ""
}
```

## Top-Level Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `version` | string | Yes | Format version ("2.2.0") |
| `x` | integer | Yes | Form X position |
| `y` | integer | Yes | Form Y position |
| `w` | integer | Yes | Form width |
| `h` | integer | Yes | Form height |
| `title` | string | Yes | Form title |
| `menu_count` | integer | Yes | Number of menu items |
| `menu_items` | array | Yes | Menu definitions |
| `controls` | array | Yes | Control definitions |
| `code` | string | Yes | Form-level code |

## Control Types

### v2.1.0 Controls (1-16)

| Type | Control | Description |
|------|---------|-------------|
| 1 | Label | Static text display |
| 2 | Button | Clickable button |
| 3 | Button (alt) | Alternative button style |
| 4 | TextBox | Single-line text input |
| 5 | CheckBox | Boolean checkbox |
| 6 | RadioButton | Single selection |
| 7 | ListBox | Selection list |
| 8 | ComboBox | Dropdown selection |
| 9 | GroupBox | Container with border |
| 10 | Panel | Simple container |
| 11 | Image | Image display |
| 12 | Menu | Menu bar |
| 13 | PopupMenu | Context menu |
| 14 | Edit | Multi-line text |
| 15 | Memo | Text area |
| 16 | Grid | Data grid |

### v2.2.0 New Controls (17-25)

| Type | Control | Description |
|------|---------|-------------|
| 17 | TreeView | Hierarchical tree |
| 18 | TabControl | Tabbed interface |
| 19 | ProgressBar | Progress indicator |
| 20 | Slider | Value slider |
| 21 | Toolbar | Button toolbar |
| 22 | StatusBar | Status panels |
| 23 | Splitter | Panel divider |
| 24 | ColorPicker | Color selection |
| 25 | Chart | Data visualization |

## Control Object Structure

### Common Properties (All Controls)

```json
{
  "x": 0,
  "y": 0,
  "w": 10,
  "h": 1,
  "tool_type": 1,
  "name_id": "controlName",
  "caption": "Control Text",
  "code": "def on_event():\\n    pass\\n",
  "visible": true,
  "enabled": true,
  "tag": null,
  "parent": "",
  "tab_order": 0
}
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `x` | integer | 0 | X position |
| `y` | integer | 0 | Y position |
| `w` | integer | 10 | Width |
| `h` | integer | 1 | Height |
| `tool_type` | integer | 1 | Control type (1-25) |
| `name_id` | string | "" | Unique identifier |
| `caption` | string | "" | Display text |
| `code` | string | "" | Event handlers |
| `visible` | boolean | true | Visibility |
| `enabled` | boolean | true | Enabled state |
| `tag` | any | null | User data |
| `parent` | string | "" | Parent control |
| `tab_order` | integer | 0 | Tab navigation order |

### TreeView (Type 17)

Additional properties:
```json
{
  "tool_type": 17,
  "indent_size": 2,
  "show_icons": true,
  "show_lines": true,
  "tree_nodes": [
    {
      "text": "Root",
      "icon": "R",
      "expanded": false,
      "selected": false,
      "children": []
    }
  ]
}
```

| Property | Type | Description |
|----------|------|-------------|
| `indent_size` | integer | Indentation per level |
| `show_icons` | boolean | Show node icons |
| `show_lines` | boolean | Show tree lines |
| `tree_nodes` | array | Root nodes |

### TabControl (Type 18)

Additional properties:
```json
{
  "tool_type": 18,
  "orientation": 0,
  "tab_height": 3,
  "show_close_button": false,
  "closable_tabs": false,
  "tabs": [
    {
      "caption": "Tab 1",
      "name_id": "tab1",
      "visible": true
    }
  ],
  "active_tab": 0
}
```

| Property | Type | Description |
|----------|------|-------------|
| `orientation` | integer | 0=horizontal, 1=vertical |
| `tab_height` | integer | Height of tab header |
| `show_close_button` | boolean | Show close buttons |
| `closable_tabs` | boolean | Allow closing tabs |
| `tabs` | array | Tab definitions |
| `active_tab` | integer | Active tab index |

### ProgressBar (Type 19)

Additional properties:
```json
{
  "tool_type": 19,
  "min_value": 0,
  "max_value": 100,
  "current_value": 0,
  "orientation": 0,
  "show_percentage": true,
  "bar_char": "\u2588",
  "fill_char": "\u2591"
}
```

| Property | Type | Description |
|----------|------|-------------|
| `min_value` | number | Minimum value |
| `max_value` | number | Maximum value |
| `current_value` | number | Current progress |
| `orientation` | integer | 0=horizontal, 1=vertical |
| `show_percentage` | boolean | Show percentage text |
| `bar_char` | string | Filled portion character |
| `fill_char` | string | Empty portion character |

### Slider (Type 20)

Additional properties:
```json
{
  "tool_type": 20,
  "min_value": 0,
  "max_value": 100,
  "current_value": 50,
  "step_increment": 1,
  "orientation": 0,
  "show_ticks": false,
  "tick_frequency": 10
}
```

| Property | Type | Description |
|----------|------|-------------|
| `min_value` | number | Minimum value |
| `max_value` | number | Maximum value |
| `current_value` | number | Current position |
| `step_increment` | number | Step size |
| `orientation` | integer | 0=horizontal, 1=vertical |
| `show_ticks` | boolean | Show tick marks |
| `tick_frequency` | integer | Tick spacing |

### Toolbar (Type 21)

Additional properties:
```json
{
  "tool_type": 21,
  "orientation": 0,
  "button_spacing": 1,
  "show_captions": false,
  "flat_style": true,
  "buttons": [
    {
      "caption": "New",
      "icon": "N",
      "tooltip": "New File",
      "button_type": 0,
      "enabled": true,
      "checked": false
    }
  ]
}
```

| Property | Type | Description |
|----------|------|-------------|
| `orientation` | integer | 0=horizontal, 1=vertical |
| `button_spacing` | integer | Space between buttons |
| `show_captions` | boolean | Show text labels |
| `flat_style` | boolean | Flat or 3D style |
| `buttons` | array | Toolbar buttons |

### StatusBar (Type 22)

Additional properties:
```json
{
  "tool_type": 22,
  "simple_mode": false,
  "simple_text": "",
  "show_size_grip": true,
  "panels": [
    {
      "text": "Ready",
      "width": 10,
      "auto_size": 0,
      "alignment": "left",
      "border": true
    }
  ]
}
```

| Property | Type | Description |
|----------|------|-------------|
| `simple_mode` | boolean | Single panel mode |
| `simple_text` | string | Simple mode text |
| `show_size_grip` | boolean | Show resize grip |
| `panels` | array | Status panels |

### Splitter (Type 23)

Additional properties:
```json
{
  "tool_type": 23,
  "orientation": 0,
  "position": 0.5,
  "use_percentage": true,
  "min_position": 0.1,
  "max_position": 0.9,
  "min_pixels": 5,
  "panel1_name": "",
  "panel2_name": ""
}
```

| Property | Type | Description |
|----------|------|-------------|
| `orientation` | integer | 0=horizontal, 1=vertical |
| `position` | float | Split position |
| `use_percentage` | boolean | Use percentage or pixels |
| `min_position` | float | Minimum position |
| `max_position` | float | Maximum position |
| `min_pixels` | integer | Minimum panel size |
| `panel1_name` | string | Associated panel 1 |
| `panel2_name` | string | Associated panel 2 |

### ColorPicker (Type 24)

Additional properties:
```json
{
  "tool_type": 24,
  "current_color": "#808080",
  "show_preview": true,
  "display_mode": 0,
  "color_palette": ["#FF0000", "#00FF00", "#0000FF"],
  "custom_colors": []
}
```

| Property | Type | Description |
|----------|------|-------------|
| `current_color` | string | Selected color (hex) |
| `show_preview` | boolean | Show color preview |
| `display_mode` | integer | 0=palette, 1=RGB, 2=hex |
| `color_palette` | array | Preset colors |
| `custom_colors` | array | User-defined colors |

### Chart (Type 25)

Additional properties:
```json
{
  "tool_type": 25,
  "chart_type": 0,
  "title": "",
  "x_label": "",
  "y_label": "",
  "show_legend": true,
  "show_grid": true,
  "show_values": false,
  "auto_scale": true,
  "min_y": 0,
  "max_y": 100,
  "series_list": [
    {
      "name": "Series 1",
      "data": [[0, 10], [1, 20], [2, 15]],
      "color": "blue",
      "visible": true
    }
  ]
}
```

| Property | Type | Description |
|----------|------|-------------|
| `chart_type` | integer | 0=bar, 1=line, 2=pie |
| `title` | string | Chart title |
| `x_label` | string | X-axis label |
| `y_label` | string | Y-axis label |
| `show_legend` | boolean | Show legend |
| `show_grid` | boolean | Show grid |
| `show_values` | boolean | Show values |
| `auto_scale` | boolean | Auto-scale axes |
| `min_y` | number | Y-axis minimum |
| `max_y` | number | Y-axis maximum |
| `series_list` | array | Data series |

## Menu Structure

```json
{
  "menu_count": 3,
  "menu_items": [
    {
      "caption": "File",
      "name_id": "mnuFile",
      "parent": 0,
      "has_submenu": true,
      "shortcut": "",
      "enabled": true,
      "visible": true
    },
    {
      "caption": "Open",
      "name_id": "mnuOpen",
      "parent": 1,
      "has_submenu": false,
      "shortcut": "Ctrl+O",
      "enabled": true,
      "visible": true
    }
  ]
}
```

| Property | Type | Description |
|----------|------|-------------|
| `caption` | string | Menu text |
| `name_id` | string | Unique identifier |
| `parent` | integer | Parent menu index (0=root) |
| `has_submenu` | boolean | Has child items |
| `shortcut` | string | Keyboard shortcut |
| `enabled` | boolean | Enabled state |
| `visible` | boolean | Visibility |

## Code Section

Event handlers are stored as strings with escaped newlines:

```json
{
  "code": "def on_load_frmMain():\\n    initialize()\\n\\ndef on_click_btnSubmit():\\n    submit_form()\\n"
}
```

### Event Handler Naming Convention

```
on_load_{form_name}           # Form load
on_click_{control_name}       # Button click
on_change_{control_name}      # Value change
on_select_{control_name}      # Selection change
on_close_{form_name}          # Form close
on_menu_{menu_name}           # Menu click
```

### Built-in Functions

v2.2.0 adds new built-in functions:

```python
# Database
database_connect(path) → Database
execute_query(sql, params) → QueryResult
get_tables() → list

# Network
http_get(url, headers) → HttpResponse
http_post(url, data, headers) → HttpResponse
http_download(url, path, callback) → bool

# Regex
regex_search(pattern, text) → Match
regex_replace(pattern, text, replacement) → str

# Dialogs
create_input_dialog(title, prompt, default) → CustomDialog
create_confirm_dialog(title, message) → CustomDialog
show_dialog(dialog) → DialogResult
```

## Database Connection Settings

Optional database configuration:

```json
{
  "database": {
    "enabled": false,
    "type": "sqlite",
    "path": "app.db",
    "connection_string": "",
    "auto_connect": false,
    "on_connect": "",
    "on_disconnect": ""
  }
}
```

## Network Configuration

Optional network settings:

```json
{
  "network": {
    "default_timeout": 30,
    "default_headers": {
      "User-Agent": "RAD-TUI/2.2.0"
    },
    "follow_redirects": true,
    "verify_ssl": true
  }
}
```

## Migration from v2.1.0

### Automatic Migration

v2.2.0 automatically handles v2.1.0 projects:

1. Loads v2.1.0 format without modification
2. Sets default values for new properties
3. Enables new features only when explicitly used

### Manual Upgrade

To upgrade a v2.1.0 project to v2.2.0:

1. Change version: `"version": "2.2.0"`
2. Add new control types as needed
3. Update documentation references

### Breaking Changes

None. v2.2.0 maintains full backward compatibility.

## Validation

### Schema Validation

Projects can be validated against JSON Schema:

```json
{
  "$schema": "https://rad-tui.io/schema/v2.2.0.json",
  "version": "2.2.0"
}
```

### Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Unknown control type | tool_type > 25 | Use valid type 1-25 |
| Missing required field | Required property absent | Add required property |
| Invalid JSON | Syntax error | Fix JSON syntax |
| Duplicate name_id | Control IDs not unique | Make name_id unique |

## Example Projects

### Minimal v2.2.0 Project

```json
{
  "version": "2.2.0",
  "x": 5,
  "y": 5,
  "w": 40,
  "h": 10,
  "title": "Hello v2.2",
  "menu_count": 0,
  "menu_items": [],
  "controls": [
    {
      "x": 10,
      "y": 4,
      "w": 20,
      "h": 1,
      "tool_type": 19,
      "name_id": "progressBar",
      "caption": "",
      "code": ""
    }
  ],
  "code": "def on_load_frmMain():\\n    progressBar.set_value(50)\\n"
}
```

### Complete v2.2.0 Project

See example projects in `/examples/` directory:
- `database_browser_v22.json`
- `chart_viewer.json`
- `web_api_client.json`
- `file_explorer_v22.json`
- `tabbed_interface.json`
- `color_picker_demo.json`
- `custom_dialog_demo.json`

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1.0 | 2024 | Initial release |
| 2.2.0 | 2025 | Added 9 controls, database, network, regex, dialogs |

## References

- [API Reference](API_REFERENCE_V22.md)
- [Database Tutorial](DATABASE_TUTORIAL.md)
- [Chart Control Guide](CHART_CONTROL_GUIDE.md)
- [Network Guide](NETWORK_GUIDE.md)

---

*Last Updated: 2025*
