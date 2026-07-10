#!/usr/bin/env python3
"""
Debugger Module for VB1-DOS Clone v2.1.0
Runtime debugging with breakpoints, step-through, and watch expressions
"""

import sys
import traceback
import linecache
from enum import Enum

class DebugState(Enum):
    RUNNING = "running"
    PAUSED = "paused"
    STEPPING = "stepping"
    BREAKPOINT = "breakpoint"

class Debugger:
    """
    Runtime debugger for Python code execution
    """
    
    def __init__(self):
        self.state = DebugState.RUNNING
        self.breakpoints = {}  # file -> set of line numbers
        self.call_stack = []
        self.variables = {}  # Current scope variables
        self.watch_expressions = []
        self.output_buffer = []
        self.current_frame = None
        self.step_into = False
        self.step_over = False
        self.step_out = False
        self.last_exception = None
        self.debug_window_active = False
        
        # Statistics
        self.lines_executed = 0
        self.functions_called = 0
    
    def trace_calls(self, frame, event, arg):
        """
        Trace function for sys.settrace
        """
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        func_name = frame.f_code.co_name
        
        # Skip debugger and system files
        if self._should_skip(filename):
            return None
        
        # Update current frame
        self.current_frame = frame
        self.variables = dict(frame.f_locals)
        
        # Track call stack
        if event == 'call':
            self.call_stack.append({
                'func': func_name,
                'file': filename,
                'line': lineno,
                'locals': dict(frame.f_locals)
            })
            self.functions_called += 1
            
            # Check for step out
            if self.step_out:
                self.step_out = False
                self.state = DebugState.PAUSED
                return self.trace_calls
            
        elif event == 'return':
            if self.call_stack:
                self.call_stack.pop()
            
            # Check for step out completion
            if self.step_out and len(self.call_stack) <= self._target_stack_depth:
                self.step_out = False
                self.state = DebugState.PAUSED
        
        elif event == 'line':
            self.lines_executed += 1
            
            # Check breakpoints
            if self._is_breakpoint(filename, lineno):
                self.state = DebugState.BREAKPOINT
                self._pause_at_line(frame, "Breakpoint hit")
                return self.trace_calls
            
            # Check stepping
            if self.state == DebugState.STEPPING:
                if self.step_into:
                    self.state = DebugState.PAUSED
                    self._pause_at_line(frame, "Step")
                    return self.trace_calls
                elif self.step_over:
                    if len(self.call_stack) <= self._target_stack_depth:
                        self.state = DebugState.PAUSED
                        self._pause_at_line(frame, "Step over")
                        return self.trace_calls
            
            # Continue tracing
            if self.state in [DebugState.RUNNING, DebugState.STEPPING]:
                return self.trace_calls
        
        elif event == 'exception':
            exc_type, exc_value, exc_traceback = arg
            self.last_exception = {
                'type': exc_type.__name__ if exc_type else None,
                'value': str(exc_value) if exc_value else None,
                'traceback': traceback.format_exception(exc_type, exc_value, exc_traceback),
                'line': lineno,
                'file': filename
            }
            self._handle_exception(frame, exc_type, exc_value, lineno)
        
        return self.trace_calls
    
    def _should_skip(self, filename):
        """Check if file should be skipped in tracing"""
        skip_patterns = [
            '<frozen',
            '<built-in',
            'debugger.py',
            'curses',
            'encodings',
            'importlib',
            'threading'
        ]
        return any(pattern in filename for pattern in skip_patterns)
    
    def _is_breakpoint(self, filename, lineno):
        """Check if line is a breakpoint"""
        if filename in self.breakpoints:
            return lineno in self.breakpoints[filename]
        return False
    
    def set_breakpoint(self, filename, lineno):
        """Set a breakpoint"""
        if filename not in self.breakpoints:
            self.breakpoints[filename] = set()
        self.breakpoints[filename].add(lineno)
    
    def clear_breakpoint(self, filename, lineno):
        """Clear a breakpoint"""
        if filename in self.breakpoints and lineno in self.breakpoints[filename]:
            self.breakpoints[filename].remove(lineno)
    
    def clear_all_breakpoints(self):
        """Clear all breakpoints"""
        self.breakpoints = {}
    
    def step_into_func(self):
        """Step into function call"""
        self.state = DebugState.STEPPING
        self.step_into = True
        self.step_over = False
        self.step_out = False
    
    def step_over_func(self):
        """Step over function call"""
        self.state = DebugState.STEPPING
        self.step_into = False
        self.step_over = True
        self.step_out = False
        self._target_stack_depth = len(self.call_stack)
    
    def step_out_func(self):
        """Step out of current function"""
        self.state = DebugState.STEPPING
        self.step_into = False
        self.step_over = False
        self.step_out = True
        self._target_stack_depth = len(self.call_stack) - 1 if self.call_stack else 0
    
    def continue_execution(self):
        """Continue execution"""
        self.state = DebugState.RUNNING
        self.step_into = False
        self.step_over = False
        self.step_out = False
    
    def pause_execution(self):
        """Pause execution"""
        self.state = DebugState.PAUSED
    
    def _pause_at_line(self, frame, reason):
        """Handle pause at a line"""
        self.debug_window_active = True
        self.output_buffer.append(f"[DEBUG] {reason} at {frame.f_code.co_filename}:{frame.f_lineno}")
    
    def _handle_exception(self, frame, exc_type, exc_value, lineno):
        """Handle runtime exception"""
        error_msg = f"Exception: {exc_type.__name__}: {exc_value} at line {lineno}"
        self.output_buffer.append(f"[ERROR] {error_msg}")
        self.state = DebugState.PAUSED
    
    def get_call_stack(self):
        """Get current call stack"""
        return self.call_stack.copy()
    
    def get_variables(self):
        """Get current scope variables"""
        return self.variables.copy()
    
    def evaluate_watch(self, expression):
        """
        Evaluate a watch expression in current context
        """
        try:
            result = eval(expression, self.current_frame.f_globals if self.current_frame else {}, self.variables)
            return str(result)
        except Exception as e:
            return f"<Error: {e}>"
    
    def add_watch(self, expression):
        """Add a watch expression"""
        if expression not in self.watch_expressions:
            self.watch_expressions.append(expression)
    
    def remove_watch(self, expression):
        """Remove a watch expression"""
        if expression in self.watch_expressions:
            self.watch_expressions.remove(expression)
    
    def get_watches(self):
        """Get all watch expressions with current values"""
        return [(expr, self.evaluate_watch(expr)) for expr in self.watch_expressions]
    
    def print_debug(self, *args):
        """Print to debug console"""
        message = ' '.join(str(arg) for arg in args)
        self.output_buffer.append(f"[PRINT] {message}")
    
    def get_output(self, clear=False):
        """Get debug output"""
        output = self.output_buffer.copy()
        if clear:
            self.output_buffer = []
        return output
    
    def get_line_source(self, filename, lineno, context=3):
        """
        Get source code around a line
        """
        try:
            lines = []
            for i in range(lineno - context, lineno + context + 1):
                if i > 0:
                    line = linecache.getline(filename, i)
                    if line:
                        marker = ">>> " if i == lineno else "    "
                        lines.append(f"{marker}{i:4d}: {line.rstrip()}")
            return '\n'.join(lines)
        except:
            return f"<Could not load source for {filename}:{lineno}>"
    
    def format_exception(self):
        """Format last exception for display"""
        if not self.last_exception:
            return "No exception"
        
        exc_info = self.last_exception
        lines = [
            f"Exception Type: {exc_info['type']}",
            f"Message: {exc_info['value']}",
            f"Location: {exc_info['file']}:{exc_info['line']}",
            "",
            "Traceback:"
        ]
        lines.extend(exc_info['traceback'])
        return '\n'.join(lines)


class DebugWindow:
    """
    Debug window UI for displaying debugger information
    """
    
    def __init__(self, debugger, x=1, y=1, w=78, h=20):
        self.debugger = debugger
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.visible = False
        self.active_tab = 0  # 0=Variables, 1=Call Stack, 2=Watches, 3=Output
        self.tabs = ["Variables", "Call Stack", "Watches", "Output"]
    
    def show(self):
        """Show debug window"""
        self.visible = True
    
    def hide(self):
        """Hide debug window"""
        self.visible = False
    
    def toggle(self):
        """Toggle visibility"""
        self.visible = not self.visible
    
    def next_tab(self):
        """Switch to next tab"""
        self.active_tab = (self.active_tab + 1) % len(self.tabs)
    
    def prev_tab(self):
        """Switch to previous tab"""
        self.active_tab = (self.active_tab - 1) % len(self.tabs)
    
    def draw(self, stdscr, colors, box_chars):
        """Draw debug window"""
        if not self.visible:
            return
        
        C_BORDER = colors.get('border', 0)
        C_BG = colors.get('bg', 0)
        C_ACTIVE = colors.get('active_tool', 0)
        C_HIGHLIGHT = colors.get('textbox', 0)
        
        # Draw border
        top = box_chars['tl'] + box_chars['h'] * (self.w - 2) + box_chars['tr']
        stdscr.addstr(self.y, self.x, top, C_BORDER)
        
        for i in range(1, self.h - 1):
            stdscr.addstr(self.y + i, self.x, box_chars['v'], C_BORDER)
            stdscr.addstr(self.y + i, self.x + self.w - 1, box_chars['v'], C_BORDER)
        
        bottom = box_chars['bl'] + box_chars['h'] * (self.w - 2) + box_chars['br']
        stdscr.addstr(self.y + self.h - 1, self.x, bottom, C_BORDER)
        
        # Title
        title = " DEBUG WINDOW "
        stdscr.addstr(self.y, self.x + (self.w - len(title)) // 2, title, C_BORDER)
        
        # Tabs
        tab_y = self.y + 1
        tab_x = self.x + 2
        for i, tab in enumerate(self.tabs):
            attr = C_ACTIVE if i == self.active_tab else C_BG
            tab_text = f"[{tab}]" if i == self.active_tab else f" {tab} "
            stdscr.addstr(tab_y, tab_x, tab_text, attr)
            tab_x += len(tab_text) + 1
        
        # Separator
        sep_y = self.y + 2
        sep = box_chars['tee_r'] + box_chars['h'] * (self.w - 2) + box_chars['tee_l']
        stdscr.addstr(sep_y, self.x, sep, C_BORDER)
        
        # Content area
        content_y = sep_y + 1
        content_h = self.h - 4
        
        if self.active_tab == 0:  # Variables
            self._draw_variables(stdscr, C_BG, content_y, content_h)
        elif self.active_tab == 1:  # Call Stack
            self._draw_call_stack(stdscr, C_BG, content_y, content_h)
        elif self.active_tab == 2:  # Watches
            self._draw_watches(stdscr, C_BG, content_y, content_h)
        elif self.active_tab == 3:  # Output
            self._draw_output(stdscr, C_BG, content_y, content_h)
        
        # Status bar
        status_y = self.y + self.h - 2
        status = f" State: {self.debugger.state.value} | Lines: {self.debugger.lines_executed} | Functions: {self.debugger.functions_called} "
        stdscr.addstr(status_y, self.x + 2, status[:self.w-4], C_BG)
    
    def _draw_variables(self, stdscr, attr, start_y, height):
        """Draw variables tab"""
        variables = self.debugger.get_variables()
        
        # Sort and filter
        var_list = [(k, str(v)[:40]) for k, v in sorted(variables.items()) 
                   if not k.startswith('__')]
        
        for i in range(height - 1):
            idx = i
            if idx < len(var_list):
                name, value = var_list[idx]
                line = f"{name[:15]} = {value[:40]}"
                stdscr.addstr(start_y + i, self.x + 2, line[:self.w-4], attr)
            else:
                stdscr.addstr(start_y + i, self.x + 2, " " * (self.w-4), attr)
    
    def _draw_call_stack(self, stdscr, attr, start_y, height):
        """Draw call stack tab"""
        stack = self.debugger.get_call_stack()
        
        for i in range(height - 1):
            idx = len(stack) - 1 - i  # Show most recent first
            if 0 <= idx < len(stack):
                frame = stack[idx]
                line = f"{frame['func']}() at {frame['file']}:{frame['line']}"
                # Highlight current frame
                frame_attr = attr | curses.A_BOLD if idx == len(stack) - 1 else attr
                stdscr.addstr(start_y + i, self.x + 2, line[:self.w-4], frame_attr)
            else:
                stdscr.addstr(start_y + i, self.x + 2, " " * (self.w-4), attr)
    
    def _draw_watches(self, stdscr, attr, start_y, height):
        """Draw watches tab"""
        watches = self.debugger.get_watches()
        
        for i in range(height - 1):
            if i < len(watches):
                expr, value = watches[i]
                line = f"{expr[:20]} = {value[:40]}"
                stdscr.addstr(start_y + i, self.x + 2, line[:self.w-4], attr)
            else:
                stdscr.addstr(start_y + i, self.x + 2, " " * (self.w-4), attr)
    
    def _draw_output(self, stdscr, attr, start_y, height):
        """Draw output tab"""
        output = self.debugger.get_output()
        
        # Show last N lines
        visible_lines = output[-(height-1):]
        
        for i, line in enumerate(visible_lines):
            # Truncate line
            display = line[:self.w-4]
            stdscr.addstr(start_y + i, self.x + 2, display, attr)
        
        # Clear remaining space
        for i in range(len(visible_lines), height - 1):
            stdscr.addstr(start_y + i, self.x + 2, " " * (self.w-4), attr)


# Global debugger instance
_debugger = None

def get_debugger():
    global _debugger
    if _debugger is None:
        _debugger = Debugger()
    return _debugger

def debug_print(*args):
    """Print to debug console"""
    get_debugger().print_debug(*args)

def set_trace():
    """Set debugger trace"""
    debugger = get_debugger()
    sys.settrace(debugger.trace_calls)


# Test
if __name__ == "__main__":
    import curses
    
    def main(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        
        colors = {
            'border': curses.A_BOLD,
            'bg': 0,
            'active_tool': curses.A_BOLD | curses.A_REVERSE,
            'textbox': curses.A_REVERSE
        }
        
        box_chars = {
            'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
            'h': '─', 'v': '│', 'tee_r': '├', 'tee_l': '┤'
        }
        
        debugger = get_debugger()
        debug_window = DebugWindow(debugger, 1, 1, 78, 20)
        debug_window.show()
        
        # Add some test data
        debugger.variables = {
            'x': 42,
            'y': "hello",
            'items': [1, 2, 3],
            'flag': True
        }
        
        debugger.call_stack = [
            {'func': 'main', 'file': 'test.py', 'line': 10, 'locals': {}},
            {'func': 'helper', 'file': 'test.py', 'line': 20, 'locals': {}},
            {'func': 'process', 'file': 'test.py', 'line': 30, 'locals': {}}
        ]
        
        debugger.add_watch('x * 2')
        debugger.add_watch('len(items)')
        
        debugger.print_debug("Test message 1")
        debugger.print_debug("Test message 2")
        debugger.print_debug("Variable x =", 42)
        
        debugger.state = DebugState.PAUSED
        
        active_tab = 0
        
        while True:
            stdscr.clear()
            
            # Draw debug window
            debug_window.draw(stdscr, colors, box_chars)
            
            # Instructions
            stdscr.addstr(22, 2, "Tab=Next Tab, Arrows=Scroll, Q=Quit", colors['border'])
            stdscr.refresh()
            
            ch = stdscr.getch()
            if ch == ord('q') or ch == ord('Q'):
                break
            elif ch == 9:  # Tab
                debug_window.next_tab()
            elif ch == curses.KEY_BTAB:  # Shift-Tab
                debug_window.prev_tab()
            
            time.sleep(0.05)
    
    import time
    curses.wrapper(main)
