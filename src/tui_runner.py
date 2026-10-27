"""Curses form runner for RAD-TUI v2.2 projects.

This module is used by ``rad-tui-py-v22.py`` when a project is launched with
``run`` or ``--run``.  It draws the form and its controls in the terminal and
dispatches mouse/keyboard events to the handlers defined by the project.
"""

import curses
import time

PAIR_BG = 1
PAIR_BORDER = 2
PAIR_BUTTON = 3
PAIR_TEXTBOX = 4
PAIR_MENU = 5
PAIR_STATUS = 6
PAIR_ERROR = 7
PAIR_SELECT = 8
PAIR_DIM = 9
PAIR_SWATCH = 10  # 10..17


def decode_text(value):
    """Turn legacy escaped newlines in captions into real newlines."""
    if value is None:
        return ""
    text = str(value)
    if "\\n" in text or "\\r" in text or "\\t" in text or '\\"' in text:
        text = (
            text.replace("\\r\\n", "\n")
            .replace("\\n", "\n")
            .replace("\\r", "\n")
            .replace("\\t", "\t")
            .replace('\\"', '"')
        )
    return text


def wrap_text(text, width):
    """Wrap text to *width* columns, preserving explicit newlines."""
    text = decode_text(text)
    if width <= 0:
        return [""]
    result = []
    for paragraph in text.split("\n"):
        if paragraph == "":
            result.append("")
            continue
        while len(paragraph) > width:
            cut = paragraph.rfind(" ", 0, width + 1)
            if cut <= 0:
                cut = width
            result.append(paragraph[:cut])
            paragraph = paragraph[cut:].lstrip(" ")
        result.append(paragraph)
    return result or [""]


def put(screen, y, x, text, attr=0):
    """Write text without ever raising from a curses bounds error."""
    if not text:
        return
    try:
        height, width = screen.getmaxyx()
        if y < 0 or y >= height or x >= width:
            return
        if x < 0:
            text = text[-x:]
            x = 0
        if x + len(text) > width:
            text = text[: max(0, width - x)]
        if text:
            screen.addstr(y, x, text, attr)
    except (curses.error, UnicodeEncodeError):
        pass


def draw_box(screen, y, x, height, width, attr=0, title=None, title_attr=None):
    """Draw a single-line box at (x, y)."""
    if width <= 0 or height <= 0:
        return
    if height == 1:
        put(screen, y, x, "\u2500" * width, attr)
        return
    if width == 1:
        put(screen, y, x, "\u2502", attr)
        return
    put(screen, y, x, "\u250c" + "\u2500" * (width - 2) + "\u2510", attr)
    for row in range(1, height - 1):
        put(screen, y + row, x, "\u2502", attr)
        put(screen, y + row, x + width - 1, "\u2502", attr)
    put(screen, y + height - 1, x, "\u2514" + "\u2500" * (width - 2) + "\u2518", attr)
    if title:
        label = (" " + decode_text(title) + " ")[: max(0, width - 4)]
        put(screen, y, x + 2, label, title_attr if title_attr is not None else attr)


class ProjectRunner:
    """Draw and run one project form."""

    def __init__(self, project, runtime):
        self.project = project
        self.runtime = runtime
        self.screen = None
        self.running = True
        self.error = None
        self.focused = None
        self.editing = None
        self.edit_buffer = ""
        self.edit_pos = 0
        self.form_x = 0
        self.form_y = 0
        self.form_w = 80
        self.form_h = 24
        self.last_click = (0.0, -1, -1)

    # ------------------------------------------------------------------ setup

    def set_error(self, message):
        self.error = str(message)

    def _init_colors(self):
        try:
            curses.start_color()
        except curses.error:
            return
        try:
            curses.use_default_colors()
        except curses.error:
            pass
        pairs = [
            (PAIR_BG, curses.COLOR_WHITE, curses.COLOR_BLUE),
            (PAIR_BORDER, curses.COLOR_CYAN, curses.COLOR_BLUE),
            (PAIR_BUTTON, curses.COLOR_BLACK, curses.COLOR_CYAN),
            (PAIR_TEXTBOX, curses.COLOR_BLACK, curses.COLOR_WHITE),
            (PAIR_MENU, curses.COLOR_YELLOW, curses.COLOR_BLUE),
            (PAIR_STATUS, curses.COLOR_BLACK, curses.COLOR_CYAN),
            (PAIR_ERROR, curses.COLOR_WHITE, curses.COLOR_RED),
            (PAIR_SELECT, curses.COLOR_WHITE, curses.COLOR_CYAN),
            (PAIR_DIM, curses.COLOR_WHITE, curses.COLOR_BLACK),
        ]
        for pair, fg, bg in pairs:
            try:
                curses.init_pair(pair, fg, bg)
            except curses.error:
                pass
        swatches = [
            curses.COLOR_BLACK,
            curses.COLOR_RED,
            curses.COLOR_GREEN,
            curses.COLOR_YELLOW,
            curses.COLOR_BLUE,
            curses.COLOR_MAGENTA,
            curses.COLOR_CYAN,
            curses.COLOR_WHITE,
        ]
        for index, color in enumerate(swatches):
            try:
                curses.init_pair(PAIR_SWATCH + index, color, color)
            except curses.error:
                pass

    def _setup(self, screen):
        self.screen = screen
        try:
            curses.set_escdelay(25)
        except (AttributeError, curses.error):
            pass
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        screen.keypad(True)
        screen.timeout(120)
        self._init_colors()
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
            curses.mouseinterval(0)
        except curses.error:
            pass

    def _teardown(self):
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        try:
            curses.mousemask(0)
        except curses.error:
            pass

    def _geometry(self):
        height, width = self.screen.getmaxyx()
        fw = int(self.project.get("w", 70) or 70)
        fh = int(self.project.get("h", 20) or 20)
        fw = max(20, min(fw, width - 2))
        fh = max(6, min(fh, height - 2))
        fx = int(self.project.get("x", 1) or 0)
        fy = int(self.project.get("y", 1) or 0)
        fx = max(0, min(fx, width - fw))
        fy = max(0, min(fy, height - fh))
        self.form_x, self.form_y = fx, fy
        self.form_w, self.form_h = fw, fh

    def _controls(self):
        return list(self.runtime.controls.values())

    def _tool_type(self, control):
        """Return the effective type, accepting legacy type-number quirks.

        Older RAD-TUI projects reused a handful of type numbers (for example
        10 for a ListBox, 13 for a TextBox, and 1 for a CheckBox).  The
        ``name_id`` prefix is the most reliable discriminator, with the JSON
        shape (items/checked) as a fallback.
        """
        tool_type = int(getattr(control, "tool_type", 0))
        data = getattr(control, "_json", {}) or {}
        name = str(getattr(control, "name_id", "")).lower()
        height = int(getattr(control, "height", 1))
        has_items = bool(data.get("items"))
        has_checked = "checked" in data

        # v2.2 controls have unambiguous numbers; do not override them by name
        # (for example a StatusBar is often named lblStatus).
        if name.startswith("tmr"):
            return 10
        if tool_type in (14, 15, 16) or tool_type >= 17:
            return tool_type
        if name.startswith("lbl"):
            return 1
        if name.startswith("btn"):
            return 2
        if name.startswith(("txt", "edt")):
            return 4
        if name.startswith(("chk", "checkbox")):
            return 5
        if name.startswith(("rad", "opt")):
            return 6
        if name.startswith("lst"):
            return 7
        if name.startswith(("cmb", "cbo")):
            return 8
        if name.startswith(("fra", "frm")):
            return 9
        if name.startswith("tmr"):
            return 10
        if name.startswith("img"):
            return 11
        if name.startswith("pic"):
            return 12
        if name.startswith(("grd", "grid")):
            return 16
        if name.startswith("tree"):
            return 17
        if name.startswith("tab"):
            return 18
        if name.startswith("prg"):
            return 19
        if name.startswith("sld"):
            return 20
        if name.startswith("tbr"):
            return 21
        if name.startswith(("sts", "status")):
            return 22
        if name.startswith("spl"):
            return 23
        if name.startswith("clr"):
            return 24
        if name.startswith(("cht", "chart")):
            return 25

        if tool_type == 1:
            return 5 if has_checked else 1
        if tool_type == 2:
            return 8 if has_items else 2
        if tool_type == 7:
            return 7 if has_items else 9
        if tool_type == 9:
            return 1 if height <= 2 else 9
        if tool_type == 10:
            return 7 if (has_items or data.get("items") is not None) else 10
        if tool_type == 11:
            return 6 if has_checked else 11
        if tool_type in (12, 13):
            if has_items:
                return 7
            if has_checked and height <= 2:
                return 5
            if height <= 2:
                return 4
            return 12
        return tool_type

    def _ensure_focus(self):
        if self.focused is not None:
            return
        for control in self._controls():
            if getattr(control, "visible", True) and self._tool_type(control) != 10:
                self.focused = control
                return

    # --------------------------------------------------------------- main loop

    def run(self, screen, prepare=None):
        self._setup(screen)
        self._geometry()
        if prepare is not None:
            try:
                prepare()
            except Exception as exc:  # pragma: no cover - defensive
                self.error = str(exc)
        if getattr(self.runtime, "last_error", None):
            self.error = self.runtime.last_error
        self._ensure_focus()
        try:
            while self.running:
                self.redraw()
                ch = screen.getch()
                if ch == curses.KEY_RESIZE:
                    self._geometry()
                elif ch == curses.KEY_MOUSE:
                    self.handle_mouse()
                elif ch != -1:
                    self.handle_key(ch)
                if getattr(self.runtime, "exit_requested", False):
                    self.running = False
        finally:
            self._teardown()

    # ------------------------------------------------------------------ drawing

    def redraw(self):
        self.screen.erase()
        self._draw_form()
        controls = self._controls()
        for control in controls:
            if self._tool_type(control) == 9:
                self._draw_control(control)
        for control in controls:
            if self._tool_type(control) != 9:
                self._draw_control(control)
        if self.editing is not None:
            self._place_cursor()
        else:
            try:
                curses.curs_set(0)
            except curses.error:
                pass
        if self.error:
            self._draw_error()
        self.screen.refresh()

    def _draw_form(self):
        bg = curses.color_pair(PAIR_BG)
        border = curses.color_pair(PAIR_BORDER)
        for row in range(1, self.form_h - 1):
            put(self.screen, self.form_y + row, self.form_x + 1, " " * (self.form_w - 2), bg)
        draw_box(
            self.screen,
            self.form_y,
            self.form_x,
            self.form_h,
            self.form_w,
            border,
            self.project.get("title", ""),
            border,
        )
        self._draw_menu_bar()

    def _draw_menu_bar(self):
        menus = [m for m in self.project.get("menu_items", []) if int(m.get("parent", 0)) == 0]
        if not menus:
            return
        x = self.form_x + 1
        for menu in menus:
            caption = decode_text(menu.get("caption", ""))
            label = " " + caption + " "
            if x + len(label) > self.form_x + self.form_w - 1:
                break
            put(self.screen, self.form_y + 1, x, label, curses.color_pair(PAIR_MENU) | curses.A_BOLD)
            x += len(label) + 1

    def _draw_error(self):
        width = min(self.form_w - 4, max(30, len(self.error) + 4))
        x = self.form_x + (self.form_w - width) // 2
        y = self.form_y + 2
        draw_box(self.screen, y, x, 3, width, curses.color_pair(PAIR_ERROR))
        put(self.screen, y + 1, x + 2, self.error[: width - 4], curses.color_pair(PAIR_ERROR) | curses.A_BOLD)

    def _geom(self, control):
        x = self.form_x + int(getattr(control, "x", 0))
        y = self.form_y + int(getattr(control, "y", 0))
        width = max(1, int(getattr(control, "width", getattr(control, "w", 10))))
        height = max(1, int(getattr(control, "height", getattr(control, "h", 1))))
        max_width = self.form_x + self.form_w - 1 - x
        max_height = self.form_y + self.form_h - 1 - y
        if max_width <= 0 or max_height <= 0:
            return None
        return x, y, min(width, max_width), min(height, max_height)

    def _text_of(self, control):
        if self.editing is control:
            return self.edit_buffer
        value = getattr(control, "text", "")
        if value:
            return decode_text(value)
        value = getattr(control, "caption", "")
        if value:
            return decode_text(value)
        lines = getattr(control, "lines", None)
        if lines:
            return decode_text("\n".join(str(line) for line in lines))
        return ""

    def _draw_control(self, control):
        if not getattr(control, "visible", True):
            return
        geom = self._geom(control)
        if not geom:
            return
        x, y, width, height = geom
        tool_type = self._tool_type(control)
        data = getattr(control, "_json", {}) or {}

        # The older main IDE uses type 12/13 for picture/menu controls too.
        if tool_type in (12, 13):
            if getattr(control, "image", None) or getattr(control, "image_list", None):
                self._draw_picture(control, x, y, width, height)
                return
            if data.get("items"):
                tool_type = 7
            else:
                return

        if tool_type == 1:
            self._draw_label(control, x, y, width)
        elif tool_type in (2, 3):
            self._draw_button(control, x, y, width, height)
        elif tool_type == 4:
            self._draw_text(control, x, y, width, height)
        elif tool_type == 5:
            self._draw_check(control, x, y, width)
        elif tool_type == 6:
            self._draw_radio(control, x, y, width)
        elif tool_type == 7:
            self._draw_list(control, x, y, width, height)
        elif tool_type == 8:
            self._draw_combo(control, x, y, width)
        elif tool_type == 9:
            self._draw_frame(control, x, y, width, height)
        elif tool_type == 11:
            self._draw_image(control, x, y, width, height)
        elif tool_type == 14:
            self._draw_text(control, x, y, width, height)
        elif tool_type == 15:
            self._draw_text(control, x, y, width, height)
        elif tool_type == 16:
            self._draw_grid(control, x, y, width, height)
        elif tool_type == 17:
            self._draw_tree(control, x, y, width, height)
        elif tool_type == 18:
            self._draw_tabs(control, x, y, width, height)
        elif tool_type == 19:
            self._draw_progress(control, x, y, width, height)
        elif tool_type == 20:
            self._draw_slider(control, x, y, width, height)
        elif tool_type == 21:
            self._draw_toolbar(control, x, y, width, height)
        elif tool_type == 22:
            self._draw_status(control, x, y, width)
        elif tool_type == 23:
            self._draw_splitter(control, x, y, width, height)
        elif tool_type == 24:
            self._draw_color_picker(control, x, y, width, height)
        elif tool_type == 25:
            self._draw_chart(control, x, y, width, height)

    # ------------------------------------------------------------ simple draws

    def _draw_label(self, control, x, y, width):
        text = self._text_of(control)
        alignment = getattr(control, "alignment", "left")
        if alignment == "center":
            text = text.center(width)
        elif alignment == "right":
            text = text.rjust(width)
        put(self.screen, y, x, text[:width], self._control_attr(control))

    def _control_attr(self, control):
        if control is self.focused:
            return curses.color_pair(PAIR_SELECT)
        return curses.color_pair(PAIR_BG)

    def _draw_button(self, control, x, y, width, height):
        caption = decode_text(getattr(control, "caption", ""))
        attr = curses.color_pair(PAIR_BUTTON)
        if not getattr(control, "enabled", True):
            attr = curses.color_pair(PAIR_DIM)
        if height <= 1:
            label = (" " + caption + " ")[:width]
            label = label.center(width)
            put(self.screen, y, x, label, attr)
            return
        draw_box(self.screen, y, x, height, width, attr)
        row = y + height // 2
        text = caption[: max(0, width - 2)].center(max(0, width - 2))
        put(self.screen, row, x + 1, text, attr)

    def _draw_text(self, control, x, y, width, height):
        text = self._text_of(control)
        if height <= 1:
            attr = curses.color_pair(PAIR_TEXTBOX)
            if control is self.focused or self.editing is control:
                attr |= curses.A_BOLD
            put(self.screen, y, x, (" " + text)[:width].ljust(width), attr)
            return
        draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER))
        lines = wrap_text(text, width - 2)
        for row in range(height - 2):
            line = lines[row] if row < len(lines) else ""
            put(self.screen, y + 1 + row, x + 1, line[: width - 2].ljust(width - 2), curses.color_pair(PAIR_TEXTBOX))

    def _draw_check(self, control, x, y, width):
        checked = bool(getattr(control, "checked", (getattr(control, "_json", {}) or {}).get("checked", False)))
        mark = "X" if checked else " "
        caption = decode_text(getattr(control, "caption", ""))
        if caption.startswith(("[ ]", "[X]")):
            caption = caption[3:].lstrip()
        put(self.screen, y, x, f"[{mark}] {caption}"[:width], self._control_attr(control))

    def _draw_radio(self, control, x, y, width):
        checked = bool(getattr(control, "checked", (getattr(control, "_json", {}) or {}).get("checked", False)))
        mark = "*" if checked else " "
        caption = decode_text(getattr(control, "caption", ""))
        if caption.startswith(("( )", "(*)")):
            caption = caption[3:].lstrip()
        put(self.screen, y, x, f"({mark}) {caption}"[:width], self._control_attr(control))

    def _items(self, control):
        items = getattr(control, "items", None)
        if items is None:
            items = (getattr(control, "_json", {}) or {}).get("items", [])
        return items or []

    def _draw_list(self, control, x, y, width, height):
        draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER))
        items = self._items(control)
        selected = int(getattr(control, "selected_index", -1))
        offset = int(getattr(control, "scroll_offset", 0))
        for row in range(max(0, height - 2)):
            index = offset + row
            if index >= len(items):
                break
            attr = curses.color_pair(PAIR_SELECT) if index == selected else curses.color_pair(PAIR_BG)
            text = decode_text(items[index])[: width - 2].ljust(width - 2)
            put(self.screen, y + 1 + row, x + 1, text, attr)

    def _draw_combo(self, control, x, y, width):
        items = self._items(control)
        index = int(getattr(control, "selected_index", -1))
        if 0 <= index < len(items):
            text = decode_text(items[index])
        else:
            text = decode_text(getattr(control, "caption", ""))
        put(self.screen, y, x, (" " + text)[: max(0, width - 2)].ljust(max(0, width - 1)) + "\u25bc", curses.color_pair(PAIR_TEXTBOX))

    def _draw_frame(self, control, x, y, width, height):
        draw_box(
            self.screen,
            y,
            x,
            height,
            width,
            curses.color_pair(PAIR_BORDER),
            getattr(control, "caption", ""),
        )

    def _draw_picture(self, control, x, y, width, height):
        draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER),
                 getattr(control, "caption", ""))
        image = getattr(control, "image", None)
        if image is None:
            image_list = getattr(control, "image_list", None)
            image = getattr(image_list, "get_current", lambda: None)() if image_list else None
        if image is None:
            put(self.screen, y + 1, x + 1, "[no image]"[: width - 2], curses.color_pair(PAIR_DIM))
            return
        pixels = getattr(image, "pixels", None) or []
        lines = ["".join(str(ch) for ch in row) for row in pixels]
        top = max(0, (height - 2 - len(lines)) // 2)
        for index, line in enumerate(lines[: max(0, height - 2)]):
            left = max(0, (width - 2 - len(line)) // 2)
            put(self.screen, y + 1 + top + index, x + 1 + left,
                line[: max(0, width - 2 - left)], curses.color_pair(PAIR_BG))

    def _draw_image(self, control, x, y, width, height):
        draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER))
        text = decode_text(getattr(control, "caption", "") or getattr(control, "image_path", "") or "[image]")
        for row in range(max(0, height - 2)):
            put(self.screen, y + 1 + row, x + 1, text[: width - 2].ljust(width - 2), curses.color_pair(PAIR_BG))
            text = ""

    # --------------------------------------------------------------- data views

    def _draw_grid(self, control, x, y, width, height):
        headers = [decode_text(h) for h in (getattr(control, "grid_headers", None) or [])]
        rows = getattr(control, "grid_data", None)
        if rows is None:
            rows = (getattr(control, "_json", {}) or {}).get("grid_data", [])
        rows = rows or []
        ncols = max(1, len(headers), max((len(row) for row in rows), default=0))
        draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER))
        if height < 3 or width < 3:
            return
        content_width = max(1, width - 2 - (ncols - 1))
        col_widths = [max(1, content_width // ncols)] * ncols
        col_widths[-1] += content_width - sum(col_widths)
        selected = int(getattr(control, "selected_row", -1))
        row_y = y + 1
        if headers:
            cells = []
            for index in range(ncols):
                text = headers[index] if index < len(headers) else ""
                cells.append(text[: col_widths[index]].ljust(col_widths[index]))
            put(self.screen, row_y, x + 1, "\u2502".join(cells), curses.color_pair(PAIR_MENU) | curses.A_BOLD)
            row_y += 1
            if row_y < y + height - 1:
                sep = "\u251c" + "\u253c".join("\u2500" * w for w in col_widths) + "\u2524"
                put(self.screen, row_y, x, sep[:width], curses.color_pair(PAIR_BORDER))
                row_y += 1
        data_row = 0
        while row_y < y + height - 1:
            if data_row >= len(rows):
                break
            row = rows[data_row]
            cells = []
            for index in range(ncols):
                value = row[index] if index < len(row) else ""
                cells.append(decode_text(value)[: col_widths[index]].ljust(col_widths[index]))
            attr = curses.color_pair(PAIR_SELECT) if data_row == selected else curses.color_pair(PAIR_BG)
            put(self.screen, row_y, x + 1, "\u2502".join(cells), attr)
            row_y += 1
            data_row += 1

    def _visible_nodes(self, control):
        nodes = getattr(control, "visible_nodes", None)
        if not nodes:
            updater = getattr(control, "_update_visible_nodes", None)
            if callable(updater):
                try:
                    updater()
                except Exception:
                    pass
            nodes = getattr(control, "visible_nodes", [])
        return nodes or []

    def _draw_tree(self, control, x, y, width, height):
        draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER), getattr(control, "caption", ""))
        nodes = self._visible_nodes(control)
        selected = getattr(control, "selected_node", None)
        offset = int(getattr(control, "scroll_offset", 0))
        indent_size = int(getattr(control, "indent_size", 2))
        show_icons = bool(getattr(control, "show_icons", True))
        if not nodes:
            put(self.screen, y + 1, x + 1, "(empty)"[: width - 2], curses.color_pair(PAIR_DIM))
            return
        for row in range(max(0, height - 2)):
            index = offset + row
            if index >= len(nodes):
                break
            node = nodes[index]
            level = int(getattr(node, "visible_level", 0))
            has_children = bool(getattr(node, "has_children", lambda: False)())
            marker = ("-" if getattr(node, "expanded", False) else "+") if has_children else " "
            icon = ""
            if show_icons and getattr(node, "icon", ""):
                icon = str(getattr(node, "icon")) + " "
            text = " " * (level * indent_size) + marker + " " + icon + decode_text(getattr(node, "text", ""))
            attr = curses.color_pair(PAIR_SELECT) if node is selected else curses.color_pair(PAIR_BG)
            put(self.screen, y + 1 + row, x + 1, text[: width - 2].ljust(width - 2), attr)

    def _draw_tabs(self, control, x, y, width, height):
        tabs = getattr(control, "tabs", None) or []
        active = int(getattr(control, "active_tab_index", 0))
        cursor = x
        for index, tab in enumerate(tabs):
            caption = decode_text(getattr(tab, "caption", f"Tab {index + 1}"))
            label = " " + caption + " "
            if cursor + len(label) > x + width:
                break
            attr = curses.color_pair(PAIR_SELECT) if index == active else curses.color_pair(PAIR_MENU)
            put(self.screen, y, cursor, label, attr)
            cursor += len(label) + 1
        if height > 1:
            draw_box(self.screen, y + 1, x, height - 1, width, curses.color_pair(PAIR_BORDER))

    # -------------------------------------------------------------- indicators

    def _draw_progress(self, control, x, y, width, height):
        value = float(getattr(control, "current_value", getattr(control, "value", 0)) or 0)
        minimum = float(getattr(control, "min_value", 0) or 0)
        maximum = float(getattr(control, "max_value", 100) or 100)
        percent = 0.0 if maximum <= minimum else max(0.0, min(1.0, (value - minimum) / (maximum - minimum)))
        if height <= 1:
            bar_width = max(1, width - 6)
            filled = int(bar_width * percent)
            text = "\u2588" * filled + "\u2591" * (bar_width - filled) + f" {percent * 100:3.0f}%"
            put(self.screen, y, x, text[:width], curses.color_pair(PAIR_STATUS))
            return
        draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER))
        bar_width = max(1, width - 8)
        filled = int(bar_width * percent)
        text = "\u2588" * filled + "\u2591" * (bar_width - filled) + f" {percent * 100:3.0f}%"
        put(self.screen, y + height // 2, x + 1, text[: width - 2], curses.color_pair(PAIR_SELECT))

    def _draw_slider(self, control, x, y, width, height):
        value = float(getattr(control, "value", getattr(control, "current_value", 0)) or 0)
        minimum = float(getattr(control, "min_value", 0) or 0)
        maximum = float(getattr(control, "max_value", 100) or 100)
        percent = 0.0 if maximum <= minimum else max(0.0, min(1.0, (value - minimum) / (maximum - minimum)))
        track = max(1, width - 2)
        position = min(track - 1, int(percent * (track - 1)))
        line = ["\u2500"] * track
        line[position] = "\u25cf"
        put(self.screen, y, x, "[" + "".join(line) + "]", curses.color_pair(PAIR_TEXTBOX))

    def _draw_toolbar(self, control, x, y, width, height):
        buttons = getattr(control, "buttons", None) or []
        if not buttons:
            put(self.screen, y, x, self._text_of(control)[:width], curses.color_pair(PAIR_MENU))
            return
        cursor = x
        for button in buttons:
            text = decode_text(getattr(button, "text", getattr(button, "caption", "")))
            label = " " + text + " "
            if cursor + len(label) > x + width:
                break
            put(self.screen, y, cursor, label[: width - (cursor - x)], curses.color_pair(PAIR_BUTTON))
            cursor += len(label) + 1

    def _draw_status(self, control, x, y, width):
        panels = getattr(control, "panels", None) or []
        attr = curses.color_pair(PAIR_STATUS)
        if not panels:
            text = decode_text(getattr(control, "caption", "") or getattr(control, "simple_text", ""))
            put(self.screen, y, x, text[:width].ljust(width), attr)
            return
        total_width = width
        fixed = sum(int(getattr(panel, "width", 10)) for panel in panels if int(getattr(panel, "auto_size", 0)) != 1)
        springs = [panel for panel in panels if int(getattr(panel, "auto_size", 0)) == 1]
        borders = max(0, len(panels) - 1)
        remaining = max(0, total_width - fixed - borders)
        share = max(3, remaining // len(springs)) if springs else 0
        cursor = x
        for index, panel in enumerate(panels):
            panel_width = share if int(getattr(panel, "auto_size", 0)) == 1 else int(getattr(panel, "width", 10))
            panel_width = max(1, min(panel_width, x + width - cursor))
            text = decode_text(getattr(panel, "text", ""))
            alignment = getattr(panel, "alignment", "left")
            if alignment == "center":
                text = text.center(panel_width)
            elif alignment == "right":
                text = text.rjust(panel_width)
            else:
                text = text.ljust(panel_width)
            put(self.screen, y, cursor, text[:panel_width], attr)
            cursor += panel_width
            if index < len(panels) - 1 and cursor < x + width:
                put(self.screen, y, cursor, "\u2502", attr)
                cursor += 1

    def _draw_splitter(self, control, x, y, width, height):
        orientation = getattr(control, "orientation", 0)
        if orientation in (1, "horizontal"):
            put(self.screen, y, x, "\u2500" * width, curses.color_pair(PAIR_BORDER))
        else:
            for row in range(height):
                put(self.screen, y + row, x, "\u2502", curses.color_pair(PAIR_BORDER))

    def _color_attr(self, color):
        try:
            red, green, blue = color.r, color.g, color.b
        except Exception:
            return curses.color_pair(PAIR_BG)
        choices = [
            (0, 0, 0),
            (255, 0, 0),
            (0, 255, 0),
            (255, 255, 0),
            (0, 0, 255),
            (255, 0, 255),
            (0, 255, 255),
            (255, 255, 255),
        ]
        best = min(range(len(choices)), key=lambda i: sum((choices[i][j] - (red, green, blue)[j]) ** 2 for j in range(3)))
        return curses.color_pair(PAIR_SWATCH + best)

    def _draw_color_picker(self, control, x, y, width, height):
        draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER))
        palette = getattr(control, "color_palette", []) or []
        columns = max(1, (width - 2) // 4)
        cell_width = max(1, (width - 2) // max(1, min(4, len(palette) or 1)))
        for index, color in enumerate(palette):
            row = index // 4
            column = index % 4
            if row >= max(0, height - 2):
                break
            cx = x + 1 + column * cell_width
            put(self.screen, y + 1 + row, cx, " " * min(2, max(1, cell_width - 1)), self._color_attr(color))
        current = getattr(control, "current_color", None)
        if current is not None and height > 2:
            info = f" {current.to_hex()}  RGB({current.r},{current.g},{current.b}) "
            put(self.screen, y + height - 1, x, info[:width], curses.color_pair(PAIR_STATUS))

    def _draw_chart(self, control, x, y, width, height):
        draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER), getattr(control, "title", ""))
        series = getattr(control, "series_list", None) or []
        points = []
        for item in series:
            data = getattr(item, "data", None) or []
            for point in data:
                if isinstance(point, (tuple, list)) and len(point) >= 2:
                    points.append((point[0], point[1]))
                else:
                    points.append((len(points), point))
        if not points:
            put(self.screen, y + 1, x + 1, "No data"[: width - 2], curses.color_pair(PAIR_DIM))
            return
        maximum = max((float(point[1]) for point in points), default=1.0) or 1.0
        available = max(1, height - 2)
        bar_width = max(1, width - 16)
        for row, (label, value) in enumerate(points[:available]):
            try:
                ratio = max(0.0, min(1.0, float(value) / maximum))
            except (TypeError, ValueError):
                ratio = 0.0
            filled = int(bar_width * ratio)
            text = f"{str(label)[:8]:>8} " + "\u2588" * filled
            put(self.screen, y + 1 + row, x + 1, text[: width - 2], curses.color_pair(PAIR_SELECT))

    # -------------------------------------------------------------- interaction

    def _fire(self, names):
        if isinstance(names, str):
            names = [names]
        for name in names:
            handler = self.runtime.variables.get(name)
            if callable(handler):
                try:
                    handler()
                except Exception as exc:
                    self.error = f"{name}: {exc}"
                return True
        return False

    def handle_key(self, ch):
        if self.error and ch in (27, 10, 13, 32):
            self.error = None
            return
        if self.editing is not None:
            self._edit_key(ch)
            return
        if ch == 27:
            self.running = False
        elif ch == 9:
            self._move_focus(1)
        elif ch == curses.KEY_BTAB:
            self._move_focus(-1)
        elif ch in (10, 13, 32):
            self._activate(self.focused)
        elif ch in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):
            self._nav_key(ch)
        elif 32 <= ch < 127:
            control = self.focused
            if control is not None and self._tool_type(control) in (4, 14, 15):
                self._start_edit(control, chr(ch))

    def _move_focus(self, direction):
        controls = [
            control
            for control in self._controls()
            if getattr(control, "visible", True) and self._tool_type(control) != 10
        ]
        if not controls:
            self.focused = None
            return
        try:
            index = controls.index(self.focused)
        except ValueError:
            index = 0
        self.focused = controls[(index + direction) % len(controls)]

    def _activate(self, control):
        if control is None:
            return
        tool_type = self._tool_type(control)
        if tool_type in (2, 3):
            self._fire([f"on_click_{control.name_id}", f"on_click_{control.name_id.lower()}"])
        elif tool_type == 5:
            control.checked = not bool(getattr(control, "checked", False))
            self._fire([f"on_change_{control.name_id}", f"on_click_{control.name_id}"])
        elif tool_type == 6:
            control.checked = True
            self._fire([f"on_change_{control.name_id}", f"on_click_{control.name_id}"])
        elif tool_type in (4, 14, 15):
            self._start_edit(control)

    def _nav_key(self, ch):
        control = self.focused
        if control is None:
            return
        tool_type = self._tool_type(control)
        if tool_type == 17:
            nodes = self._visible_nodes(control)
            current = getattr(control, "selected_node", None)
            try:
                index = nodes.index(current)
            except ValueError:
                index = 0
            if ch == curses.KEY_UP:
                index = max(0, index - 1)
            elif ch == curses.KEY_DOWN:
                index = min(len(nodes) - 1, index + 1)
            elif ch in (curses.KEY_RIGHT, curses.KEY_LEFT):
                if current is not None and hasattr(control, "toggle_node"):
                    control.toggle_node(current)
                    name = "expand" if getattr(current, "expanded", False) else "collapse"
                    self._fire([f"on_node_{name}_{control.name_id}", f"on_node_{name}"])
                return
            if nodes:
                control.select_node(nodes[index])
                self._fire([f"on_node_click_{control.name_id}"])
        elif tool_type == 7:
            items = self._items(control)
            selected = int(getattr(control, "selected_index", -1))
            selected = max(0, min(len(items) - 1, selected + (1 if ch == curses.KEY_DOWN else -1)))
            control.selected_index = selected
            self._fire([f"on_change_{control.name_id}", f"on_click_{control.name_id}"])
        elif tool_type == 16:
            rows = getattr(control, "grid_data", None) or []
            selected = int(getattr(control, "selected_row", -1))
            selected = max(0, min(len(rows) - 1, selected + (1 if ch == curses.KEY_DOWN else -1)))
            control.selected_row = selected
            self._fire([f"on_cell_click_{control.name_id}"])
        elif tool_type == 20:
            step = 1 if ch == curses.KEY_RIGHT else -1
            value = float(getattr(control, "value", 0) or 0) + step
            control.value = value
            self._fire([f"on_change_{control.name_id}"])

    # --------------------------------------------------------------- text edit

    def _start_edit(self, control, initial=None):
        self.editing = control
        base = self._text_of(control) if initial is None else ""
        if initial:
            base += initial
        self.edit_buffer = base
        self.edit_pos = len(base)
        try:
            curses.curs_set(1)
        except curses.error:
            pass

    def _edit_key(self, ch):
        if ch == 27:
            self.editing = None
            return
        if ch in (10, 13):
            self._commit_edit()
            return
        if ch in (8, 127, curses.KEY_BACKSPACE):
            if self.edit_pos > 0:
                self.edit_buffer = self.edit_buffer[: self.edit_pos - 1] + self.edit_buffer[self.edit_pos :]
                self.edit_pos -= 1
            return
        if ch == curses.KEY_DC:
            self.edit_buffer = self.edit_buffer[: self.edit_pos] + self.edit_buffer[self.edit_pos + 1 :]
            return
        if ch == curses.KEY_LEFT:
            self.edit_pos = max(0, self.edit_pos - 1)
            return
        if ch == curses.KEY_RIGHT:
            self.edit_pos = min(len(self.edit_buffer), self.edit_pos + 1)
            return
        if ch == curses.KEY_HOME:
            self.edit_pos = 0
            return
        if ch == curses.KEY_END:
            self.edit_pos = len(self.edit_buffer)
            return
        if 32 <= ch < 127:
            self.edit_buffer = self.edit_buffer[: self.edit_pos] + chr(ch) + self.edit_buffer[self.edit_pos :]
            self.edit_pos += 1

    def _commit_edit(self):
        control = self.editing
        if control is None:
            return
        text = self.edit_buffer
        control.caption = text
        if hasattr(control, "text"):
            control.text = text
        if hasattr(control, "lines"):
            control.lines = text.split("\n")
        self.editing = None
        self._fire([f"on_change_{control.name_id}", f"on_click_{control.name_id}"])

    def _place_cursor(self):
        control = self.editing
        if control is None:
            return
        geom = self._geom(control)
        if not geom:
            return
        x, y, width, height = geom
        if height <= 1:
            row, column = y, x + 1 + min(self.edit_pos, max(0, width - 2))
        else:
            before = self.edit_buffer[: self.edit_pos]
            lines = before.split("\n")
            row = y + 1 + min(len(lines) - 1, max(0, height - 2))
            column = x + 1 + min(len(lines[-1]), max(0, width - 2))
        try:
            self.screen.move(row, column)
            curses.curs_set(1)
        except curses.error:
            pass

    # ------------------------------------------------------------------- mouse

    def _control_at(self, mx, my):
        for control in reversed(self._controls()):
            if not getattr(control, "visible", True):
                continue
            geom = self._geom(control)
            if not geom:
                continue
            x, y, width, height = geom
            if x <= mx < x + width and y <= my < y + height:
                return control
        return None

    def handle_mouse(self):
        try:
            _, mx, my, _, state = curses.getmouse()
        except curses.error:
            return
        if not (state & (curses.BUTTON1_CLICKED | curses.BUTTON1_PRESSED)):
            return
        now = time.time()
        if now - self.last_click[0] < 0.08 and (mx, my) == self.last_click[1:]:
            return
        double = now - self.last_click[0] < 0.45 and (mx, my) == self.last_click[1:]
        self.last_click = (now, mx, my)
        if self.error:
            self.error = None
            return
        if self.editing is not None:
            control = self._control_at(mx, my)
            if control is not self.editing:
                self._commit_edit()
        menu = self._menu_at(mx, my)
        if menu is not None:
            if menu.get("has_submenu"):
                choice = self._menu_popup(menu)
                if choice is not None:
                    self._fire([f"on_menu_{choice.get('name_id')}"])
            else:
                self._fire([f"on_menu_{menu.get('name_id')}"])
            return
        control = self._control_at(mx, my)
        if control is not None:
            self._click_control(control, mx, my, double)
        else:
            self.focused = None

    def _menu_at(self, mx, my):
        if my != self.form_y + 1:
            return None
        x = self.form_x + 1
        menus = [m for m in self.project.get("menu_items", []) if int(m.get("parent", 0)) == 0]
        for menu in menus:
            label = " " + decode_text(menu.get("caption", "")) + " "
            if x <= mx < x + len(label):
                return menu
            x += len(label) + 1
        return None

    def _menu_popup(self, menu):
        items = self.project.get("menu_items", [])
        try:
            root_index = items.index(menu) + 1
        except ValueError:
            return None
        children = [item for item in items if int(item.get("parent", 0)) == root_index]
        if not children:
            return None
        width = max(len(decode_text(item.get("caption", ""))) for item in children) + 4
        x = self.form_x + 1
        menus = [m for m in items if int(m.get("parent", 0)) == 0]
        for item in menus:
            if item is menu:
                break
            x += len(decode_text(item.get("caption", ""))) + 3
        height = len(children) + 2
        x = min(x, self.form_x + self.form_w - width - 1)
        y = self.form_y + 2
        self.redraw()
        for row in range(height):
            put(self.screen, y + row, x, " " * width, curses.color_pair(PAIR_MENU))
        draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_MENU))
        for index, item in enumerate(children):
            caption = decode_text(item.get("caption", ""))
            put(self.screen, y + 1 + index, x + 1, (" " + caption)[: width - 2].ljust(width - 2),
                curses.color_pair(PAIR_MENU))
        self.screen.refresh()
        while True:
            ch = self.screen.getch()
            if ch in (27, ord("q")):
                return None
            if ch in (10, 13):
                return children[0]
            if ch == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, state = curses.getmouse()
                except curses.error:
                    continue
                if not (state & (curses.BUTTON1_CLICKED | curses.BUTTON1_PRESSED)):
                    continue
                for index, item in enumerate(children):
                    if x <= mx < x + width and y + 1 + index == my:
                        return item
                return None

    def _click_control(self, control, mx, my, double):
        self.focused = control
        tool_type = self._tool_type(control)
        geom = self._geom(control)
        if not geom:
            return
        x, y, width, height = geom
        if tool_type in (2, 3):
            self._fire([f"on_click_{control.name_id}"])
        elif tool_type == 5:
            control.checked = not bool(getattr(control, "checked", False))
            self._fire([f"on_change_{control.name_id}", f"on_click_{control.name_id}"])
        elif tool_type == 6:
            control.checked = True
            self._fire([f"on_change_{control.name_id}", f"on_click_{control.name_id}"])
        elif tool_type == 7:
            row = my - (y + 1)
            index = int(getattr(control, "scroll_offset", 0)) + row
            if 0 <= index < len(self._items(control)):
                control.selected_index = index
                self._fire([f"on_change_{control.name_id}", f"on_click_{control.name_id}"])
        elif tool_type == 8:
            items = self._items(control)
            if items:
                control.selected_index = (int(getattr(control, "selected_index", -1)) + 1) % len(items)
                self._fire([f"on_change_{control.name_id}", f"on_click_{control.name_id}"])
        elif tool_type in (12, 13):
            if getattr(control, "image", None) or getattr(control, "image_list", None):
                self._fire([f"on_image_click_{control.name_id}", f"on_click_{control.name_id}"])
            elif self._items(control):
                items = self._items(control)
                control.selected_index = (int(getattr(control, "selected_index", -1)) + 1) % len(items)
                self._fire([f"on_change_{control.name_id}", f"on_click_{control.name_id}"])
            elif "checked" in (getattr(control, "_json", {}) or {}):
                control.checked = not bool(getattr(control, "checked", False))
                self._fire([f"on_change_{control.name_id}", f"on_click_{control.name_id}"])
        elif tool_type in (4, 14, 15):
            self._start_edit(control)
        elif tool_type == 16:
            row = my - (y + 1)
            if getattr(control, "grid_headers", None):
                row -= 2
            if row >= 0:
                control.selected_row = row
                self._fire([f"on_cell_click_{control.name_id}", f"on_cell_edit_{control.name_id}"])
        elif tool_type == 17:
            node = self._tree_node_at(control, mx, my)
            if node is not None:
                if hasattr(control, "select_node"):
                    control.select_node(node)
                level = int(getattr(node, "visible_level", 0))
                indent_size = int(getattr(control, "indent_size", 2))
                indicator_x = x + 1 + level * indent_size
                on_indicator = indicator_x <= mx <= indicator_x + 1
                if (double or on_indicator) and getattr(node, "has_children", lambda: False)():
                    if hasattr(control, "toggle_node"):
                        control.toggle_node(node)
                        name = "expand" if getattr(node, "expanded", False) else "collapse"
                        self._fire([f"on_node_{name}_{control.name_id}", f"on_node_{name}"])
                self._fire([f"on_node_click_{control.name_id}"])
        elif tool_type == 18:
            tabs = getattr(control, "tabs", None) or []
            cursor = x
            for index, tab in enumerate(tabs):
                label = " " + decode_text(getattr(tab, "caption", "")) + " "
                if cursor <= mx < cursor + len(label):
                    control.active_tab_index = index
                    self._fire([f"on_tab_change_{control.name_id}", f"on_tab_click_{control.name_id}"])
                    break
                cursor += len(label) + 1
        elif tool_type == 20:
            track = max(1, width - 2)
            ratio = max(0.0, min(1.0, (mx - x - 1) / track))
            minimum = float(getattr(control, "min_value", 0) or 0)
            maximum = float(getattr(control, "max_value", 100) or 100)
            control.value = minimum + ratio * (maximum - minimum)
            self._fire([f"on_change_{control.name_id}"])
        elif tool_type == 24:
            palette = getattr(control, "color_palette", None) or []
            cell_width = max(1, (width - 2) // max(1, min(4, len(palette) or 1)))
            column = max(0, min(3, (mx - x - 1) // cell_width))
            row = my - (y + 1)
            index = row * 4 + column
            if 0 <= index < len(palette):
                control.set_color(palette[index])
                self._fire([f"on_color_change_{control.name_id}", f"on_color_select_{control.name_id}"])
        elif tool_type == 25:
            self._fire([f"on_point_click_{control.name_id}"])

    def _tree_node_at(self, control, mx, my):
        geom = self._geom(control)
        if not geom:
            return None
        x, y, width, height = geom
        row = my - (y + 1)
        if row < 0 or row >= height - 2:
            return None
        nodes = self._visible_nodes(control)
        index = int(getattr(control, "scroll_offset", 0)) + row
        if 0 <= index < len(nodes):
            return nodes[index]
        return None

    # ------------------------------------------------------------------ dialogs

    def _dialog_rect(self, width, height):
        screen_h, screen_w = self.screen.getmaxyx()
        width = max(20, min(width, screen_w - 2))
        height = max(3, min(height, screen_h - 2))
        return (screen_w - width) // 2, (screen_h - height) // 2, width, height

    def _fill_rect(self, x, y, width, height, attr):
        for row in range(height):
            put(self.screen, y + row, x, " " * width, attr)

    def msgbox(self, text, title="Message"):
        if self.screen is None:
            return None
        screen_h, screen_w = self.screen.getmaxyx()
        lines = []
        for line in decode_text(text).split("\n"):
            lines.extend(wrap_text(line, max(10, min(60, screen_w - 10))))
        width = max(len(decode_text(title)) + 6, max((len(line) for line in lines), default=0) + 6, 30)
        x, y, width, height = self._dialog_rect(width, len(lines) + 4)
        self.redraw()
        self._fill_rect(x, y, width, height, curses.color_pair(PAIR_BG))
        draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER), title, curses.color_pair(PAIR_MENU))
        for index, line in enumerate(lines[: height - 3]):
            put(self.screen, y + 1 + index, x + 2, line[: width - 4], curses.color_pair(PAIR_BG))
        put(self.screen, y + height - 2, x + 2, " Press Enter or Esc "[: width - 4], curses.color_pair(PAIR_MENU))
        self.screen.refresh()
        while True:
            ch = self.screen.getch()
            if ch in (10, 13, 27, 32):
                break
        return None

    def input_box(self, prompt, title="Input", default=""):
        if self.screen is None:
            return default
        screen_h, screen_w = self.screen.getmaxyx()
        prompt_lines = wrap_text(prompt, max(10, min(60, screen_w - 10)))
        width = max(len(decode_text(title)) + 6, max((len(line) for line in prompt_lines), default=0) + 6, 34)
        x, y, width, height = self._dialog_rect(width, len(prompt_lines) + 5)
        value = str(default or "")
        while True:
            self.redraw()
            self._fill_rect(x, y, width, height, curses.color_pair(PAIR_BG))
            draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER), title, curses.color_pair(PAIR_MENU))
            for index, line in enumerate(prompt_lines[: height - 4]):
                put(self.screen, y + 1 + index, x + 2, line[: width - 4], curses.color_pair(PAIR_BG))
            put(self.screen, y + height - 3, x + 2, " " * (width - 4), curses.color_pair(PAIR_TEXTBOX))
            shown = value[-(width - 5):] if len(value) >= width - 4 else value
            put(self.screen, y + height - 3, x + 2, (" " + shown)[: width - 4].ljust(width - 4), curses.color_pair(PAIR_TEXTBOX))
            try:
                self.screen.move(y + height - 3, x + 3 + min(len(shown), width - 5))
                curses.curs_set(1)
            except curses.error:
                pass
            self.screen.refresh()
            ch = self.screen.getch()
            if ch in (10, 13):
                try:
                    curses.curs_set(0)
                except curses.error:
                    pass
                return value if value else default
            if ch == 27:
                try:
                    curses.curs_set(0)
                except curses.error:
                    pass
                return None
            if ch in (8, 127, curses.KEY_BACKSPACE):
                value = value[:-1]
            elif 32 <= ch < 127:
                value += chr(ch)

    def confirm_dialog(self, text, title="Confirm"):
        if self.screen is None:
            return False
        screen_h, screen_w = self.screen.getmaxyx()
        lines = wrap_text(text, max(10, min(60, screen_w - 10)))
        width = max(len(decode_text(title)) + 6, max((len(line) for line in lines), default=0) + 6, 30)
        x, y, width, height = self._dialog_rect(width, len(lines) + 4)
        self.redraw()
        self._fill_rect(x, y, width, height, curses.color_pair(PAIR_BG))
        draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER), title, curses.color_pair(PAIR_MENU))
        for index, line in enumerate(lines[: height - 3]):
            put(self.screen, y + 1 + index, x + 2, line[: width - 4], curses.color_pair(PAIR_BG))
        put(self.screen, y + height - 2, x + 2, " Yes (y)   No (n) "[: width - 4], curses.color_pair(PAIR_MENU))
        self.screen.refresh()
        while True:
            ch = self.screen.getch()
            if ch in (ord("y"), ord("Y"), 10, 13):
                return True
            if ch in (ord("n"), ord("N"), 27):
                return False

    def option_dialog(self, text, title, options):
        """Show a small dialog with up to a few labeled choices."""
        if self.screen is None:
            return options[0][1] if options else None
        screen_h, screen_w = self.screen.getmaxyx()
        lines = wrap_text(text, max(10, min(60, screen_w - 10)))
        buttons = "   ".join(f"{label} ({label[0].lower()})" for label, _ in options)
        width = max(
            len(decode_text(title)) + 6,
            max((len(line) for line in lines), default=0) + 6,
            len(buttons) + 6,
            30,
        )
        x, y, width, height = self._dialog_rect(width, len(lines) + 4)
        self.redraw()
        self._fill_rect(x, y, width, height, curses.color_pair(PAIR_BG))
        draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER),
                 title, curses.color_pair(PAIR_MENU))
        for index, line in enumerate(lines[: height - 3]):
            put(self.screen, y + 1 + index, x + 2, line[: width - 4], curses.color_pair(PAIR_BG))
        put(self.screen, y + height - 2, x + 2, buttons[: width - 4], curses.color_pair(PAIR_MENU))
        self.screen.refresh()
        while True:
            ch = self.screen.getch()
            if ch in (10, 13):
                return options[0][1] if options else None
            if ch == 27:
                return options[-1][1] if options else None
            if 32 <= ch < 127:
                key = chr(ch).lower()
                for label, value in options:
                    if label and label[0].lower() == key:
                        return value

    def list_dialog(self, items, title="Select"):
        """Show a modal list and return the selected item (or None)."""
        items = [decode_text(item) for item in items]
        if self.screen is None:
            return items[0] if items else None
        width = max(30, min(60, max((len(item) for item in items), default=0) + 8))
        height = max(5, min(len(items) + 4, self.screen.getmaxyx()[0] - 2))
        x, y, width, height = self._dialog_rect(width, height)
        selected = 0
        while True:
            self.redraw()
            self._fill_rect(x, y, width, height, curses.color_pair(PAIR_BG))
            draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER),
                     title, curses.color_pair(PAIR_MENU))
            visible = max(1, height - 3)
            start = max(0, min(selected - visible + 1, len(items) - visible))
            for row in range(visible):
                index = start + row
                if index >= len(items):
                    break
                attr = curses.color_pair(PAIR_SELECT) if index == selected else curses.color_pair(PAIR_BG)
                put(self.screen, y + 1 + row, x + 2,
                    (" " + items[index])[: width - 4].ljust(width - 4), attr)
            self.screen.refresh()
            ch = self.screen.getch()
            if ch in (10, 13):
                return items[selected] if items else None
            if ch == 27:
                return None
            if ch in (curses.KEY_UP, ord("k")) and items:
                selected = (selected - 1) % len(items)
            elif ch in (curses.KEY_DOWN, ord("j")) and items:
                selected = (selected + 1) % len(items)

    def custom_dialog(self, dialog):
        """Render a v2.2 CustomDialog with its controls and buttons."""
        if self.screen is None:
            return dialog.result
        screen_h, screen_w = self.screen.getmaxyx()
        width = max(20, min(int(getattr(dialog, "width", 40) or 40), screen_w - 2))
        height = max(5, min(int(getattr(dialog, "height", 12) or 12), screen_h - 2))
        x = max(0, min(int(getattr(dialog, "x", 0) or 0), screen_w - width))
        y = max(0, min(int(getattr(dialog, "y", 0) or 0), screen_h - height))
        buttons = [button for button in getattr(dialog, "buttons", []) if getattr(button, "visible", True)]
        default_button = next((b for b in buttons if getattr(b, "default", False)), buttons[0] if buttons else None)
        cancel_button = next((b for b in buttons if getattr(b, "cancel", False)), None)
        from custom_dialog import DialogResult as _DialogResult
        cancel_result = getattr(cancel_button, "result", _DialogResult.CANCEL)

        old_geometry = (self.form_x, self.form_y, self.form_w, self.form_h)
        self.form_x, self.form_y, self.form_w, self.form_h = x, y, width, height
        try:
            while True:
                self.redraw()
                self._fill_rect(x, y, width, height, curses.color_pair(PAIR_BG))
                draw_box(self.screen, y, x, height, width, curses.color_pair(PAIR_BORDER),
                         getattr(dialog, "title", "Dialog"), curses.color_pair(PAIR_MENU))
                for control in getattr(dialog, "controls", []):
                    if getattr(control, "width", 0) <= 0:
                        control.width = 20
                    if getattr(control, "height", 0) <= 0:
                        control.height = 1
                    self._draw_control(control)

                button_rects = []
                if buttons:
                    labels = [f" {getattr(b, 'text', 'OK')} " for b in buttons]
                    total = sum(len(label) + 2 for label in labels) - 2
                    cursor = x + max(1, (width - total) // 2)
                    button_y = y + height - 2
                    for button, label in zip(buttons, labels):
                        attr = curses.color_pair(PAIR_BUTTON)
                        if button is default_button:
                            attr |= curses.A_BOLD
                        put(self.screen, button_y, cursor, label, attr)
                        button_rects.append((cursor, button_y, len(label), button))
                        cursor += len(label) + 2
                self.screen.refresh()

                ch = self.screen.getch()
                if ch == 27:
                    dialog.close_dialog(cancel_result)
                    return cancel_result
                if ch in (10, 13) and default_button is not None:
                    dialog.close_dialog(default_button.result)
                    return default_button.result
                if ch == curses.KEY_MOUSE:
                    try:
                        _, mx, my, _, state = curses.getmouse()
                    except curses.error:
                        continue
                    for bx, by, bw, button in button_rects:
                        if by == my and bx <= mx < bx + bw:
                            dialog.close_dialog(button.result)
                            return button.result
                    for control in getattr(dialog, "controls", []):
                        geom = self._geom(control)
                        if not geom:
                            continue
                        cx, cy, cw, chh = geom
                        if cx <= mx < cx + cw and cy <= my < cy + chh:
                            tool_type = self._tool_type(control)
                            if tool_type == 5:
                                control.checked = not bool(getattr(control, "checked", False))
                            elif tool_type == 8:
                                items = self._items(control)
                                if items:
                                    control.selected_index = (int(getattr(control, "selected_index", -1)) + 1) % len(items)
                            break
        finally:
            self.form_x, self.form_y, self.form_w, self.form_h = old_geometry

    def file_dialog(self, mode="open", filters=None):
        label = "File path" if mode == "open" else "Save as"
        return self.input_box(label, "Open File" if mode == "open" else "Save File", "")
