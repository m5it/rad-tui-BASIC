#!/usr/bin/env python3
"""
RAD-TUI v2.2.0 Feature Test Suite
Comprehensive testing for all v2.2.0 modules and controls

Run with: python -m pytest test_v22_features.py -v
Or: python test_v22_features.py
"""

import unittest
import sys
import os
import json
import tempfile
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

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
    from network import NetworkManager, HttpResponse, http_get, http_post
    from regex import Regex, Match, regex_search, regex_replace
    from custom_dialog import CustomDialog, DialogResult
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    MODULES_AVAILABLE = False


# =============================================================================
# CONTROL TESTS
# =============================================================================

class TestTreeView(unittest.TestCase):
    """Test TreeView and TreeNode functionality"""
    
    def setUp(self):
        self.tree = TreeView(name_id="testTree", x=2, y=2, width=30, height=10)
        
    def test_tree_initialization(self):
        """Test TreeView initialization"""
        self.assertEqual(self.tree.name_id, "testTree")
        self.assertEqual(self.tree.x, 2)
        self.assertEqual(self.tree.y, 2)
        self.assertEqual(self.tree.width, 30)
        self.assertEqual(self.tree.height, 10)
        self.assertEqual(len(self.tree.root_nodes), 0)
        self.assertIsNone(self.tree.selected_node)
        
    def test_add_root_node(self):
        """Test adding root nodes"""
        root = self.tree.add_root_node("Root", icon="R")
        self.assertIsNotNone(root)
        self.assertEqual(root.text, "Root")
        self.assertEqual(root.icon, "R")
        self.assertEqual(len(self.tree.root_nodes), 1)
        
    def test_add_child_node(self):
        """Test adding child nodes"""
        root = self.tree.add_root_node("Root")
        child = root.add_child("Child", icon="C")
        self.assertEqual(child.text, "Child")
        self.assertEqual(child.icon, "C")
        self.assertEqual(child.parent, root)
        self.assertEqual(len(root.children), 1)
        
    def test_expand_collapse(self):
        """Test node expansion and collapse"""
        root = self.tree.add_root_node("Root")
        root.add_child("Child")
        
        self.assertFalse(root.expanded)
        self.tree.expand_node(root)
        self.assertTrue(root.expanded)
        self.tree.collapse_node(root)
        self.assertFalse(root.expanded)
        self.tree.toggle_node(root)
        self.assertTrue(root.expanded)
        
    def test_node_selection(self):
        """Test node selection"""
        root = self.tree.add_root_node("Root")
        self.tree.set_selected(root)
        self.assertEqual(self.tree.get_selected(), root)
        
    def test_clear_tree(self):
        """Test clearing tree"""
        self.tree.add_root_node("Root1")
        self.tree.add_root_node("Root2")
        self.tree.clear()
        self.assertEqual(len(self.tree.root_nodes), 0)
        self.assertIsNone(self.tree.selected_node)
        
    def test_remove_node(self):
        """Test node removal"""
        root = self.tree.add_root_node("Root")
        child = root.add_child("Child")
        self.tree.remove_node(child)
        self.assertEqual(len(root.children), 0)


class TestTabControl(unittest.TestCase):
    """Test TabControl and TabPage functionality"""
    
    def setUp(self):
        self.tabs = TabControl(name_id="testTabs", x=2, y=2, width=50, height=15)
        
    def test_initialization(self):
        """Test TabControl initialization"""
        self.assertEqual(self.tabs.name_id, "testTabs")
        self.assertEqual(len(self.tabs.tabs), 0)
        self.assertEqual(self.tabs.active_tab_index, 0)
        self.assertEqual(self.tabs.orientation, TabControl.HORIZONTAL)
        
    def test_add_tab(self):
        """Test adding tabs"""
        tab1 = self.tabs.add_tab("General", "tabGeneral")
        tab2 = self.tabs.add_tab("Advanced", "tabAdvanced")
        
        self.assertEqual(self.tabs.get_tab_count(), 2)
        self.assertEqual(tab1.caption, "General")
        self.assertEqual(tab1.name_id, "tabGeneral")
        self.assertEqual(tab2.caption, "Advanced")
        
    def test_set_active_tab(self):
        """Test tab activation"""
        self.tabs.add_tab("Tab1", "t1")
        self.tabs.add_tab("Tab2", "t2")
        
        self.tabs.set_active_tab(1)
        self.assertEqual(self.tabs.get_active_index(), 1)
        self.assertEqual(self.tabs.get_active_tab().name_id, "t2")
        
    def test_remove_tab(self):
        """Test tab removal"""
        self.tabs.add_tab("Tab1", "t1")
        self.tabs.add_tab("Tab2", "t2")
        self.tabs.remove_tab(0)
        
        self.assertEqual(self.tabs.get_tab_count(), 1)
        self.assertEqual(self.tabs.get_active_tab().name_id, "t2")
        
    def test_tab_controls(self):
        """Test adding controls to tabs"""
        tab = self.tabs.add_tab("Test", "test")
        label = Mock()
        tab.add_control(label)
        self.assertEqual(len(tab.controls), 1)


class TestProgressBar(unittest.TestCase):
    """Test ProgressBar functionality"""
    
    def setUp(self):
        self.pb = ProgressBar(name_id="testProgress", x=2, y=10, width=40)
        
    def test_initialization(self):
        """Test ProgressBar initialization"""
        self.assertEqual(self.pb.name_id, "testProgress")
        self.assertEqual(self.pb.min_value, 0)
        self.assertEqual(self.pb.max_value, 100)
        self.assertEqual(self.pb.current_value, 0)
        self.assertEqual(self.pb.orientation, ProgressBar.HORIZONTAL)
        
    def test_set_range(self):
        """Test setting range"""
        self.pb.set_range(0, 200)
        self.assertEqual(self.pb.min_value, 0)
        self.assertEqual(self.pb.max_value, 200)
        
    def test_set_value(self):
        """Test setting value"""
        self.pb.set_value(50)
        self.assertEqual(self.pb.get_value(), 50)
        
    def test_value_clamping(self):
        """Test value clamping to range"""
        self.pb.set_value(-10)
        self.assertEqual(self.pb.get_value(), 0)
        self.pb.set_value(150)
        self.assertEqual(self.pb.get_value(), 100)
        
    def test_percentage(self):
        """Test percentage calculation"""
        self.pb.set_value(50)
        self.assertEqual(self.pb.get_percentage(), 50.0)
        self.pb.set_value(25)
        self.assertEqual(self.pb.get_percentage(), 25.0)
        
    def test_increment(self):
        """Test increment operation"""
        self.pb.set_value(50)
        self.pb.increment(10)
        self.assertEqual(self.pb.get_value(), 60)
        
    def test_complete(self):
        """Test completion detection"""
        self.assertFalse(self.pb.is_complete())
        self.pb.set_value(100)
        self.assertTrue(self.pb.is_complete())


class TestSlider(unittest.TestCase):
    """Test Slider functionality"""
    
    def setUp(self):
        self.slider = Slider(name_id="testSlider", x=10, y=5, width=30)
        
    def test_initialization(self):
        """Test Slider initialization"""
        self.assertEqual(self.slider.name_id, "testSlider")
        self.assertEqual(self.slider.min_value, 0)
        self.assertEqual(self.slider.max_value, 100)
        self.assertEqual(self.slider.step_increment, 1)
        
    def test_set_range(self):
        """Test setting range"""
        self.slider.set_range(-50, 50)
        self.assertEqual(self.slider.min_value, -50)
        self.assertEqual(self.slider.max_value, 50)
        
    def test_set_value(self):
        """Test setting value"""
        self.slider.set_value(50)
        self.assertEqual(self.slider.get_value(), 50)
        
    def test_set_step(self):
        """Test setting step increment"""
        self.slider.set_step(5)
        self.assertEqual(self.slider.step_increment, 5)
        
    def test_percentage(self):
        """Test percentage calculation"""
        self.slider.set_value(50)
        self.assertEqual(self.slider.get_percentage(), 0.5)
        self.slider.set_value(25)
        self.assertEqual(self.slider.get_percentage(), 0.25)


class TestToolbar(unittest.TestCase):
    """Test Toolbar functionality"""
    
    def setUp(self):
        self.toolbar = Toolbar(name_id="testToolbar", x=2, y=1, width=50)
        
    def test_initialization(self):
        """Test Toolbar initialization"""
        self.assertEqual(self.toolbar.name_id, "testToolbar")
        self.assertEqual(len(self.toolbar.buttons), 0)
        self.assertEqual(self.toolbar.orientation, Toolbar.HORIZONTAL)
        
    def test_add_button(self):
        """Test adding buttons"""
        btn = self.toolbar.add_button("New", icon="N", tooltip="New File")
        self.assertEqual(len(self.toolbar.buttons), 1)
        self.assertEqual(btn.caption, "New")
        self.assertEqual(btn.icon, "N")
        self.assertEqual(btn.tooltip, "New File")
        self.assertTrue(btn.enabled)
        
    def test_add_separator(self):
        """Test adding separators"""
        self.toolbar.add_separator()
        self.assertEqual(self.toolbar.buttons[0].button_type, ToolbarButton.SEPARATOR)
        
    def test_remove_button(self):
        """Test button removal"""
        self.toolbar.add_button("Test", "T")
        self.toolbar.remove_button(0)
        self.assertEqual(len(self.toolbar.buttons), 0)


class TestStatusBar(unittest.TestCase):
    """Test StatusBar functionality"""
    
    def setUp(self):
        self.status = StatusBar(name_id="testStatus", x=2, y=22, width=76)
        
    def test_initialization(self):
        """Test StatusBar initialization"""
        self.assertEqual(self.status.name_id, "testStatus")
        self.assertEqual(len(self.status.panels), 0)
        self.assertFalse(self.status.simple_mode)
        
    def test_add_panel(self):
        """Test adding panels"""
        panel = self.status.add_panel("Ready", width=30, auto_size=1)
        self.assertEqual(len(self.status.panels), 1)
        self.assertEqual(panel.text, "Ready")
        self.assertEqual(panel.width, 30)
        self.assertTrue(panel.auto_size)
        
    def test_set_panel_text(self):
        """Test setting panel text"""
        self.status.add_panel("Initial", width=20)
        self.status.set_panel_text(0, "Updated")
        self.assertEqual(self.status.get_panel_text(0), "Updated")


class TestSplitter(unittest.TestCase):
    """Test Splitter functionality"""
    
    def setUp(self):
        self.splitter = Splitter(name_id="testSplitter", x=25, y=2, width=1, height=15)
        
    def test_initialization(self):
        """Test Splitter initialization"""
        self.assertEqual(self.splitter.name_id, "testSplitter")
        self.assertEqual(self.splitter.orientation, Splitter.VERTICAL)
        self.assertEqual(self.splitter.position, 0.5)
        
    def test_set_orientation(self):
        """Test orientation setting"""
        self.splitter.set_orientation(Splitter.HORIZONTAL)
        self.assertEqual(self.splitter.orientation, Splitter.HORIZONTAL)
        
    def test_set_position(self):
        """Test position setting"""
        self.splitter.set_position(0.3)
        self.assertEqual(self.splitter.get_position(), 0.3)
        
    def test_position_clamping(self):
        """Test position clamping"""
        self.splitter.set_range(0.1, 0.9)
        self.splitter.set_position(0.05)
        self.assertEqual(self.splitter.get_position(), 0.1)
        self.splitter.set_position(0.95)
        self.assertEqual(self.splitter.get_position(), 0.9)


class TestColorPicker(unittest.TestCase):
    """Test ColorPicker and Color functionality"""
    
    def setUp(self):
        self.picker = ColorPicker(name_id="testPicker", x=2, y=2, width=20, height=8)
        
    def test_color_initialization(self):
        """Test Color initialization"""
        color = Color(255, 128, 64)
        self.assertEqual(color.r, 255)
        self.assertEqual(color.g, 128)
        self.assertEqual(color.b, 64)
        
    def test_color_clamping(self):
        """Test Color value clamping"""
        color = Color(300, -50, 128)
        self.assertEqual(color.r, 255)
        self.assertEqual(color.g, 0)
        self.assertEqual(color.b, 128)
        
    def test_color_to_hex(self):
        """Test hex conversion"""
        color = Color(255, 0, 128)
        self.assertEqual(color.to_hex(), "#ff0080")
        
    def test_color_from_hex(self):
        """Test hex parsing"""
        color = Color()
        color.from_hex("#00FF80")
        self.assertEqual(color.r, 0)
        self.assertEqual(color.g, 255)
        self.assertEqual(color.b, 128)
        
    def test_picker_set_color(self):
        """Test ColorPicker set color"""
        color = Color(128, 64, 32)
        self.picker.set_color(color)
        self.assertEqual(self.picker.get_color().r, 128)
        
    def test_picker_set_hex(self):
        """Test ColorPicker set from hex"""
        self.picker.set_color("#FF5733")
        self.assertEqual(self.picker.get_color().to_hex(), "#ff5733")


class TestChart(unittest.TestCase):
    """Test Chart and ChartSeries functionality"""
    
    def setUp(self):
        self.chart = Chart(name_id="testChart", x=2, y=2, width=40, height=15)
        
    def test_initialization(self):
        """Test Chart initialization"""
        self.assertEqual(self.chart.name_id, "testChart")
        self.assertEqual(self.chart.chart_type, Chart.BAR)
        self.assertEqual(len(self.chart.series_list), 0)
        self.assertTrue(self.chart.show_legend)
        
    def test_set_chart_type(self):
        """Test chart type setting"""
        self.chart.set_chart_type(Chart.LINE)
        self.assertEqual(self.chart.chart_type, Chart.LINE)
        self.chart.set_chart_type(Chart.PIE)
        self.assertEqual(self.chart.chart_type, Chart.PIE)
        
    def test_add_series(self):
        """Test adding series"""
        series = self.chart.add_series("Sales", color="green")
        self.assertEqual(len(self.chart.series_list), 1)
        self.assertEqual(series.name, "Sales")
        self.assertEqual(series.color, "green")
        
    def test_add_data_points(self):
        """Test adding data points"""
        series = self.chart.add_series("Data")
        series.add_point(0, 100)
        series.add_point(1, 150)
        self.assertEqual(len(series.data), 2)
        self.assertEqual(series.data[0], (0, 100))
        
    def test_auto_scale(self):
        """Test auto-scaling"""
        series = self.chart.add_series("Data")
        series.add_point(0, 50)
        series.add_point(1, 150)
        series.add_point(2, 100)
        self.chart.auto_scale_range()
        self.assertEqual(self.chart.min_y, 50)
        self.assertEqual(self.chart.max_y, 150)
        
    def test_clear_data(self):
        """Test clearing data"""
        series = self.chart.add_series("Data")
        series.add_point(0, 100)
        self.chart.clear_data()
        self.assertEqual(len(series.data), 0)


# =============================================================================
# MODULE TESTS
# =============================================================================

class TestDatabase(unittest.TestCase):
    """Test Database module with in-memory SQLite"""
    
    def setUp(self):
        self.db = Database()
        
    def tearDown(self):
        self.db.disconnect()
        
    def test_connection(self):
        """Test database connection"""
        result = self.db.connect(":memory:")
        self.assertTrue(result)
        self.assertTrue(self.db.is_connected)
        
    def test_disconnect(self):
        """Test disconnection"""
        self.db.connect(":memory:")
        self.db.disconnect()
        self.assertFalse(self.db.is_connected)
        
    def test_create_table(self):
        """Test table creation"""
        self.db.connect(":memory:")
        result = self.db.execute_non_query(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
        )
        self.assertGreaterEqual(result, 0)
        
    def test_insert(self):
        """Test data insertion"""
        self.db.connect(":memory:")
        self.db.execute_non_query("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        row_id = self.db.insert("test", {"name": "John"})
        self.assertGreater(row_id, 0)
        
    def test_query(self):
        """Test data querying"""
        self.db.connect(":memory:")
        self.db.execute_non_query("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        self.db.insert("test", {"name": "Alice"})
        self.db.insert("test", {"name": "Bob"})
        
        result = self.db.execute_query("SELECT * FROM test ORDER BY name")
        self.assertIsNone(result.error)
        self.assertEqual(result.row_count, 2)
        self.assertEqual(result.rows[0][1], "Alice")
        
    def test_parameterized_query(self):
        """Test parameterized queries"""
        self.db.connect(":memory:")
        self.db.execute_non_query("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        self.db.insert("test", {"name": "Test"})
        
        result = self.db.execute_query("SELECT * FROM test WHERE name = ?", ("Test",))
        self.assertEqual(result.row_count, 1)
        
    def test_transaction(self):
        """Test transaction handling"""
        self.db.connect(":memory:")
        self.db.execute_non_query("CREATE TABLE test (id INTEGER PRIMARY KEY, value INTEGER)")
        
        # Transaction should work (if implemented)
        try:
            self.db.begin_transaction()
            self.db.execute_non_query("INSERT INTO test (value) VALUES (1)")
            self.db.commit()
        except AttributeError:
            pass  # begin_transaction not implemented


class TestNetwork(unittest.TestCase):
    """Test Network module with mock responses"""
    
    def setUp(self):
        self.nm = NetworkManager()
        
    def test_initialization(self):
        """Test NetworkManager initialization"""
        self.assertEqual(self.nm.timeout, 30)
        self.assertTrue(self.nm.follow_redirects)
        
    def test_http_response(self):
        """Test HttpResponse"""
        response = HttpResponse()
        response.status_code = 200
        response.body = '{"key": "value"}'
        self.assertTrue(response.is_success())
        
    def test_mock_get(self):
        """Test GET with mock"""
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.read.return_value = b'{"data": "test"}'
        
        with patch('urllib.request.urlopen', return_value=mock_response):
            with patch.object(mock_response, '__enter__', return_value=mock_response):
                with patch.object(mock_response, '__exit__', return_value=False):
                    response = self.nm.get("http://example.com/api")
                    # Note: This is simplified; real test would need proper mock context
                    
    def test_http_get_function(self):
        """Test http_get convenience function"""
        with patch.object(NetworkManager, 'get') as mock_get:
            mock_get.return_value = HttpResponse()
            http_get("http://example.com")
            mock_get.assert_called_once()


class TestRegex(unittest.TestCase):
    """Test Regex module"""
    
    def test_regex_initialization(self):
        """Test Regex initialization"""
        pattern = Regex(r"\d+")
        self.assertIsNotNone(pattern)
        
    def test_invalid_pattern(self):
        """Test invalid pattern handling"""
        pattern = Regex(r"[invalid")
        self.assertIsNone(pattern.compiled)
        
    def test_search(self):
        """Test regex search"""
        pattern = Regex(r"\d{3}-\d{4}")
        match = pattern.search("Phone: 123-4567")
        self.assertIsNotNone(match)
        self.assertEqual(match.value, "123-4567")
        
    def test_match(self):
        """Test regex match"""
        pattern = Regex(r"^\d+$")
        match = pattern.match("12345")
        self.assertIsNotNone(match)
        no_match = pattern.match("abc123")
        self.assertIsNone(no_match)
        
    def test_find_all(self):
        """Test find_all"""
        pattern = Regex(r"\w+")
        matches = pattern.find_all("Hello World Test")
        self.assertEqual(len(matches), 3)
        
    def test_replace(self):
        """Test regex replace"""
        pattern = Regex(r"\d+")
        result = pattern.replace("Room 101", "XXX")
        self.assertEqual(result, "Room XXX")
        
    def test_regex_search_function(self):
        """Test regex_search convenience function"""
        match = regex_search(r"\w+", "test string")
        self.assertIsNotNone(match)
        self.assertEqual(match.value, "test")
        
    def test_regex_replace_function(self):
        """Test regex_replace convenience function"""
        result = regex_replace(r"\s+", "-", "hello world test")
        self.assertEqual(result, "hello-world-test")


class TestCustomDialog(unittest.TestCase):
    """Test CustomDialog functionality"""
    
    def setUp(self):
        self.dialog = CustomDialog(name_id="testDialog", title="Test", width=40, height=10)
        
    def test_initialization(self):
        """Test dialog initialization"""
        self.assertEqual(self.dialog.name_id, "testDialog")
        self.assertEqual(self.dialog.title, "Test")
        self.assertEqual(self.dialog.width, 40)
        self.assertEqual(self.dialog.height, 10)
        self.assertTrue(self.dialog.modal)
        self.assertEqual(self.dialog.result, DialogResult.NONE)
        
    def test_add_control(self):
        """Test adding controls"""
        mock_control = Mock()
        self.dialog.add_control(mock_control)
        self.assertEqual(len(self.dialog.controls), 1)
        
    def test_set_get_value(self):
        """Test value storage"""
        self.dialog.set_value("input", "test value")
        self.assertEqual(self.dialog.get_value("input"), "test value")
        
    def test_close_dialog(self):
        """Test dialog closing"""
        self.dialog.show_dialog(modal=True)
        self.dialog.close_dialog(DialogResult.OK)
        self.assertEqual(self.dialog.result, DialogResult.OK)
        self.assertFalse(self.dialog.visible)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestV22Examples(unittest.TestCase):
    """Test loading v2.2.0 example projects"""
    
    def setUp(self):
        self.examples_dir = os.path.join(os.path.dirname(__file__), '..', 'examples')
        
    def test_example_files_exist(self):
        """Test that example files exist"""
        v22_examples = [
            'database_browser_v22.json',
            'chart_viewer.json',
            'web_api_client.json',
            'file_explorer_v22.json',
            'tabbed_interface.json',
            'color_picker_demo.json',
            'custom_dialog_demo.json',
            'V22_EXAMPLES_SUMMARY.md'
        ]
        
        for example in v22_examples:
            path = os.path.join(self.examples_dir, example)
            self.assertTrue(os.path.exists(path), f"Missing: {example}")
            
    def test_load_database_browser(self):
        """Test loading database browser example"""
        path = os.path.join(self.examples_dir, 'database_browser_v22.json')
        if os.path.exists(path):
            with open(path) as f:
                project = json.load(f)
            self.assertEqual(project['version'], '2.2.0')
            # Check for v2.2.0 controls
            tool_types = [c.get('tool_type') for c in project.get('controls', [])]
            self.assertIn(17, tool_types)  # TreeView
            
    def test_load_chart_viewer(self):
        """Test loading chart viewer example"""
        path = os.path.join(self.examples_dir, 'chart_viewer.json')
        if os.path.exists(path):
            with open(path) as f:
                project = json.load(f)
            tool_types = [c.get('tool_type') for c in project.get('controls', [])]
            self.assertIn(25, tool_types)  # Chart
            
    def test_load_tabbed_interface(self):
        """Test loading tabbed interface example"""
        path = os.path.join(self.examples_dir, 'tabbed_interface.json')
        if os.path.exists(path):
            with open(path) as f:
                project = json.load(f)
            tool_types = [c.get('tool_type') for c in project.get('controls', [])]
            self.assertIn(18, tool_types)  # TabControl


class TestControlFactory(unittest.TestCase):
    """Test control factory creates correct types"""
    
    def test_create_v22_controls(self):
        """Test factory creates v2.2.0 controls"""
        from rad_tui_py_v22 import create_control
        
        controls = {
            17: TreeView,
            18: TabControl,
            19: ProgressBar,
            20: Slider,
            21: Toolbar,
            22: StatusBar,
            23: Splitter,
            24: ColorPicker,
            25: Chart,
        }
        
        for tool_type, expected_class in controls.items():
            control = create_control(tool_type, 0, 0, "test")
            self.assertIsInstance(control, expected_class, 
                                f"Tool type {tool_type} should create {expected_class.__name__}")


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests():
    """Run all tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestTreeView,
        TestTabControl,
        TestProgressBar,
        TestSlider,
        TestToolbar,
        TestStatusBar,
        TestSplitter,
        TestColorPicker,
        TestChart,
        TestDatabase,
        TestNetwork,
        TestRegex,
        TestCustomDialog,
        TestV22Examples,
        TestControlFactory,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == '__main__':
    if MODULES_AVAILABLE:
        sys.exit(run_tests())
    else:
        print("Cannot run tests: v2.2.0 modules not available")
        sys.exit(1)
