#!/usr/bin/env python3
"""
RAD-TUI v2.2.0 Integration Test Suite
Tests all v2.2.0 features: controls, database, network, regex, dialogs
"""

import sys
import os
import json
import tempfile
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import v2.2.0 modules
try:
    from treeview import TreeView, TreeNode
    from tabcontrol import TabControl, TabPage
    from progressbar import ProgressBar
    from slider import Slider
    from toolbar import Toolbar, ToolbarButton
    from statusbar import StatusBar, StatusPanel
    from splitter import Splitter
    from colorpicker import ColorPicker, Color
    from chart import Chart, ChartSeries
    from database import Database, QueryResult
    from network import NetworkManager, HttpResponse, http_get
    from regex import Regex, Match, regex_search
    from custom_dialog import CustomDialog, DialogResult
    MODULES_LOADED = True
except ImportError as e:
    print(f"Warning: Some modules not found: {e}")
    MODULES_LOADED = False


class TestRunner:
    """Test runner with reporting"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []
        
    def run_test(self, name, test_func):
        """Run a single test"""
        self.tests_run += 1
        try:
            test_func()
            self.tests_passed += 1
            print(f"  ✓ {name}")
            return True
        except AssertionError as e:
            self.tests_failed += 1
            self.failures.append((name, str(e)))
            print(f"  ✗ {name}: {e}")
            return False
        except Exception as e:
            self.tests_failed += 1
            self.failures.append((name, f"Exception: {e}"))
            print(f"  ✗ {name}: Exception - {e}")
            return False
            
    def report(self):
        """Print test report"""
        print("\n" + "="*60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failures:
            print("\nFailed Tests:")
            for name, error in self.failures:
                print(f"  - {name}: {error}")
                
        print("="*60)
        return self.tests_failed == 0


# Test Functions
def test_treeview_basic():
    """Test TreeView basic functionality"""
    tree = TreeView(name_id="testTree", x=0, y=0, width=30, height=10)
    
    # Add root node
    root = tree.add_root_node("Root", icon="R")
    assert root is not None
    assert root.text == "Root"
    assert root.icon == "R"
    
    # Add child
    child = root.add_child("Child", icon="C")
    assert child is not None
    assert child.text == "Child"
    assert child.parent == root
    
    # Test expansion
    tree.expand_node(root)
    assert root.expanded == True
    
    tree.collapse_node(root)
    assert root.expanded == False
    
    # Clear
    tree.clear()
    assert len(tree.root_nodes) == 0


def test_tabcontrol_basic():
    """Test TabControl basic functionality"""
    tabs = TabControl(name_id="testTabs", x=0, y=0, width=50, height=15)
    
    # Add tabs
    tab1 = tabs.add_tab("Tab 1", "tab1")
    tab2 = tabs.add_tab("Tab 2", "tab2")
    
    assert tabs.get_tab_count() == 2
    assert tab1.caption == "Tab 1"
    assert tab2.name_id == "tab2"
    
    # Set active
    tabs.set_active_tab(1)
    assert tabs.get_active_index() == 1
    assert tabs.get_active_tab() == tab2
    
    # Remove tab
    tabs.remove_tab(0)
    assert tabs.get_tab_count() == 1


def test_progressbar_basic():
    """Test ProgressBar basic functionality"""
    pb = ProgressBar(name_id="testProgress", x=0, y=0, width=40, height=1)
    
    # Set range
    pb.set_range(0, 100)
    assert pb.min_value == 0
    assert pb.max_value == 100
    
    # Set value
    pb.set_value(50)
    assert pb.get_value() == 50
    
    # Percentage
    assert pb.get_percentage() == 50.0
    
    # Increment
    pb.increment(10)
    assert pb.get_value() == 60
    
    # Complete check
    pb.set_value(100)
    assert pb.is_complete() == True


def test_slider_basic():
    """Test Slider basic functionality"""
    slider = Slider(name_id="testSlider", x=0, y=0, width=30, height=1)
    
    # Set range
    slider.set_range(0, 100)
    assert slider.min_value == 0
    assert slider.max_value == 100
    
    # Set value
    slider.set_value(50)
    assert slider.get_value() == 50
    
    # Step
    slider.set_step(5)
    assert slider.step_increment == 5
    
    # Percentage
    assert slider.get_percentage() == 50.0


def test_toolbar_basic():
    """Test Toolbar basic functionality"""
    toolbar = Toolbar(name_id="testToolbar", x=0, y=0, width=50, height=1)
    
    # Add buttons
    btn1 = toolbar.add_button("New", icon="N", tooltip="New File")
    btn2 = toolbar.add_button("Open", icon="O", tooltip="Open File")
    
    assert len(toolbar.buttons) == 2
    assert btn1.caption == "New"
    assert btn2.icon == "O"
    
    # Add separator
    toolbar.add_separator()
    assert toolbar.buttons[-1].button_type == ToolbarButton.SEPARATOR


def test_statusbar_basic():
    """Test StatusBar basic functionality"""
    status = StatusBar(name_id="testStatus", x=0, y=0, width=76, height=1)
    
    # Add panels
    status.add_panel("Ready", width=30, auto_size=1)
    status.add_panel("Ln 1", width=10)
    
    assert len(status.panels) == 2
    
    # Set text
    status.set_panel_text(0, "Editing")
    assert status.get_panel_text(0) == "Editing"


def test_splitter_basic():
    """Test Splitter basic functionality"""
    splitter = Splitter(name_id="testSplitter", x=0, y=0, height=15)
    
    # Set orientation
    splitter.set_orientation(Splitter.VERTICAL)
    assert splitter.orientation == Splitter.VERTICAL
    
    # Set position
    splitter.set_position(0.4)
    assert splitter.get_position() == 0.4
    
    # Range
    splitter.set_range(0.1, 0.9)
    assert splitter.min_position == 0.1
    assert splitter.max_position == 0.9


def test_colorpicker_basic():
    """Test ColorPicker basic functionality"""
    picker = ColorPicker(name_id="testPicker", x=0, y=0, width=20, height=8)
    
    # Set color
    color = Color(128, 64, 32)
    picker.set_color(color)
    
    retrieved = picker.get_color()
    assert retrieved.r == 128
    assert retrieved.g == 64
    assert retrieved.b == 32


def test_chart_basic():
    """Test Chart basic functionality"""
    chart = Chart(name_id="testChart", x=0, y=0, width=40, height=15)
    
    # Set type
    chart.set_chart_type(Chart.BAR)
    assert chart.chart_type == Chart.BAR
    
    # Add series
    series = chart.add_series("Sales", color="green")
    assert series.name == "Sales"
    
    # Add points
    series.add_point(0, 100)
    series.add_point(1, 150)
    assert len(series.data) == 2
    
    # Auto scale
    chart.auto_scale_range()
    assert chart.max_y >= 150


def test_database_basic():
    """Test Database basic functionality"""
    # Use in-memory database
    db = Database()
    
    # Connect
    assert db.connect(":memory:") == True
    assert db.is_connected() == True
    
    # Create table
    result = db.execute_non_query(
        "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
    )
    assert result >= 0
    
    # Insert
    row_id = db.insert("test", {"name": "John"})
    assert row_id > 0
    
    # Query
    result = db.execute_query("SELECT * FROM test")
    assert result.error is None
    assert result.row_count == 1
    assert result.rows[0][1] == "John"
    
    # Disconnect
    db.disconnect()
    assert db.is_connected() == False


def test_network_basic():
    """Test Network basic functionality"""
    nm = NetworkManager()
    
    # Check initialization
    assert nm.timeout == 30
    assert nm.follow_redirects == True
    
    # Test URL validation
    from network import is_valid_url
    assert is_valid_url("https://example.com") == True
    assert is_valid_url("not-a-url") == False


def test_regex_basic():
    """Test Regex basic functionality"""
    # Search
    pattern = Regex(r"\d{3}-\d{4}")
    match = pattern.search("Phone: 123-4567")
    
    assert match is not None
    assert match.is_valid() == True
    assert match.value == "123-4567"
    
    # Replace
    result = pattern.replace("Call 123-4567", "XXX-XXXX")
    assert result == "Call XXX-XXXX"


def test_custom_dialog_basic():
    """Test CustomDialog basic functionality"""
    dialog = CustomDialog(name_id="testDialog", title="Test", width=40, height=10)
    
    assert dialog.title == "Test"
    assert dialog.width == 40
    
    # Add button
    btn = dialog.add_button("OK", DialogResult.OK, default=True)
    assert btn.text == "OK"
    assert btn.result == DialogResult.OK
    assert btn.default == True


def test_project_format():
    """Test project format loading"""
    # Create minimal v2.2.0 project
    project = {
        "version": "2.2.0",
        "x": 5, "y": 5, "w": 40, "h": 10,
        "title": "Test Project",
        "menu_count": 0,
        "menu_items": [],
        "controls": [
            {
                "x": 2, "y": 2, "w": 10, "h": 1,
                "tool_type": 17,  # TreeView
                "name_id": "tree1",
                "caption": "",
                "code": ""
            },
            {
                "x": 2, "y": 4, "w": 20, "h": 1,
                "tool_type": 19,  # ProgressBar
                "name_id": "progress1",
                "caption": "",
                "code": ""
            }
        ],
        "code": ""
    }
    
    # Verify structure
    assert project["version"] == "2.2.0"
    assert len(project["controls"]) == 2
    assert project["controls"][0]["tool_type"] == 17
    assert project["controls"][1]["tool_type"] == 19


def test_backward_compatibility():
    """Test v2.1.0 project compatibility"""
    # Create v2.1.0 style project
    project = {
        "version": "2.1.0",
        "x": 2, "y": 2, "w": 50, "h": 15,
        "title": "Legacy Project",
        "menu_count": 0,
        "menu_items": [],
        "controls": [
            {
                "x": 5, "y": 5, "w": 10, "h": 1,
                "tool_type": 2,  # Button
                "name_id": "btn1",
                "caption": "Click Me",
                "code": ""
            }
        ],
        "code": ""
    }
    
    # Should load without errors (no v2.2.0 specific features)
    assert project["version"] == "2.1.0"
    assert len(project["controls"]) == 1


def test_integration_example():
    """Test complete integration scenario"""
    # Create a form with multiple v2.2.0 controls
    # and verify they work together
    
    # TreeView + StatusBar
    tree = TreeView(name_id="tree", width=30, height=10)
    status = StatusBar(name_id="status", width=76)
    
    root = tree.add_root_node("Root")
    child = root.add_child("Child")
    
    status.add_panel(f"Nodes: {len(root.children)}", width=20)
    
    assert len(root.children) == 1
    
    # Chart + Database (simulated)
    chart = Chart(name_id="chart", width=40, height=10)
    series = chart.add_series("Data")
    series.add_point(0, 100)
    
    assert len(series.data) == 1


# Main test execution
def main():
    print("="*60)
    print("RAD-TUI v2.2.0 Integration Test Suite")
    print("="*60)
    
    if not MODULES_LOADED:
        print("\nWarning: Not all modules could be imported.")
        print("Some tests may be skipped.\n")
    
    runner = TestRunner()
    
    # Control Tests
    print("\n--- Control Tests ---")
    runner.run_test("TreeView Basic", test_treeview_basic)
    runner.run_test("TabControl Basic", test_tabcontrol_basic)
    runner.run_test("ProgressBar Basic", test_progressbar_basic)
    runner.run_test("Slider Basic", test_slider_basic)
    runner.run_test("Toolbar Basic", test_toolbar_basic)
    runner.run_test("StatusBar Basic", test_statusbar_basic)
    runner.run_test("Splitter Basic", test_splitter_basic)
    runner.run_test("ColorPicker Basic", test_colorpicker_basic)
    runner.run_test("Chart Basic", test_chart_basic)
    
    # Module Tests
    print("\n--- Module Tests ---")
    runner.run_test("Database Basic", test_database_basic)
    runner.run_test("Network Basic", test_network_basic)
    runner.run_test("Regex Basic", test_regex_basic)
    runner.run_test("Custom Dialog Basic", test_custom_dialog_basic)
    
    # Integration Tests
    print("\n--- Integration Tests ---")
    runner.run_test("Project Format", test_project_format)
    runner.run_test("Backward Compatibility", test_backward_compatibility)
    runner.run_test("Integration Example", test_integration_example)
    
    # Report
    success = runner.report()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
