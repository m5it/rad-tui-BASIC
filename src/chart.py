"""
Chart/Graph Control Module for RAD-TUI v2.2.0
Provides data visualization with bar, line, and pie charts
"""

class ChartSeries:
    """Represents a data series in a chart"""
    
    def __init__(self, name="", data=None, color=None):
        self.name = name
        self.data = data or []  # List of (x, y) tuples or just y values
        self.color = color or "blue"
        self.visible = True
        self.line_style = "-"  # -, --, :, etc.
        
    def add_point(self, x, y):
        """Add a data point"""
        self.data.append((x, y))
        
    def clear(self):
        """Clear all data"""
        self.data = []
        
    def get_max_y(self):
        """Get maximum Y value"""
        if not self.data:
            return 0
        return max(p[1] if isinstance(p, tuple) else p for p in self.data)
        
    def get_min_y(self):
        """Get minimum Y value"""
        if not self.data:
            return 0
        return min(p[1] if isinstance(p, tuple) else p for p in self.data)
        
    def get_max_x(self):
        """Get maximum X value"""
        if not self.data:
            return 0
        return max(p[0] if isinstance(p, tuple) else i for i, p in enumerate(self.data))
        
    def get_min_x(self):
        """Get minimum X value"""
        if not self.data:
            return 0
        return min(p[0] if isinstance(p, tuple) else i for i, p in enumerate(self.data))


class Chart:
    """Chart control for data visualization"""
    
    TOOL_TYPE = 25
    
    # Chart types
    BAR = 0
    LINE = 1
    PIE = 2
    
    def __init__(self, name_id="chart1", x=0, y=0, width=40, height=20):
        self.name_id = name_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Chart data
        self.series_list = []
        self.chart_type = self.BAR
        
        # Appearance
        self.title = ""
        self.x_label = ""
        self.y_label = ""
        self.show_legend = True
        self.show_grid = True
        self.show_values = False
        
        # Axis settings
        self.auto_scale = True
        self.min_y = 0
        self.max_y = 100
        self.min_x = 0
        self.max_x = 10
        
        # Characters for drawing
        self.bar_char = "\u2588"  # Full block
        self.line_char = "*"      # Line marker
        self.grid_char = "."      # Grid dot
        self.axis_char = "+"      # Axis intersection
        
        # Events
        self.on_point_click = None
        self.on_series_click = None
        
        # State
        self.enabled = True
        self.visible = True
        
    def add_series(self, name, data=None, color=None):
        """Add a data series"""
        series = ChartSeries(name, data, color)
        self.series_list.append(series)
        return series
        
    def remove_series(self, index):
        """Remove series by index"""
        if 0 <= index < len(self.series_list):
            del self.series_list[index]
            
    def clear_series(self):
        """Remove all series"""
        self.series_list = []
        
    def set_chart_type(self, chart_type):
        """Set chart type (BAR, LINE, or PIE)"""
        self.chart_type = chart_type
        
    def set_range(self, min_y, max_y):
        """Set Y-axis range (disables auto-scale)"""
        self.min_y = min_y
        self.max_y = max_y
        self.auto_scale = False
        
    def auto_scale_range(self):
        """Automatically calculate Y-axis range from data"""
        if not self.series_list:
            self.min_y = 0
            self.max_y = 100
            return
            
        all_values = []
        for series in self.series_list:
            if series.data:
                values = [p[1] if isinstance(p, tuple) else p for p in series.data]
                all_values.extend(values)
                
        if all_values:
            self.min_y = min(0, min(all_values))
            self.max_y = max(all_values) * 1.1  # Add 10% padding
        else:
            self.min_y = 0
            self.max_y = 100
            
    def render(self, screen):
        """Render the chart"""
        if not self.visible:
            return
            
        if self.auto_scale:
            self.auto_scale_range()
            
        if self.chart_type == self.BAR:
            self._render_bar_chart(screen)
        elif self.chart_type == self.LINE:
            self._render_line_chart(screen)
        elif self.chart_type == self.PIE:
            self._render_pie_chart(screen)
            
        # Render title
        if self.title:
            self._render_title(screen)
            
        # Render legend
        if self.show_legend:
            self._render_legend(screen)
            
    def _render_bar_chart(self, screen):
        """Render bar chart"""
        if not self.series_list:
            return
            
        # Calculate plot area
        plot_height = self.height - 4  # Leave room for labels
        plot_width = self.width - 6     # Leave room for Y-axis
        
        # Get data to plot
        series = self.series_list[0]  # Use first series for now
        data = series.data[:plot_width]  # Limit to available width
        
        if not data:
            return
            
        # Calculate scale
        y_range = self.max_y - self.min_y
        if y_range == 0:
            y_range = 1
            
        # Draw bars
        for i, point in enumerate(data):
            if i >= plot_width:
                break
                
            y_val = point[1] if isinstance(point, tuple) else point
            bar_height = int((y_val - self.min_y) / y_range * plot_height)
            
            x = self.x + 4 + i
            
            # Draw bar from bottom up
            for h in range(bar_height):
                y = self.y + self.height - 2 - h
                # Draw bar character
                
    def _render_line_chart(self, screen):
        """Render line chart"""
        if not self.series_list:
            return
            
        plot_height = self.height - 4
        plot_width = self.width - 6
        
        # Draw grid
        if self.show_grid:
            for y in range(0, plot_height, 4):
                grid_y = self.y + self.height - 2 - y
                for x in range(plot_width):
                    # Draw grid dot
                    pass
                    
        # Draw each series
        for series in self.series_list:
            if not series.data or not series.visible:
                continue
                
            y_range = self.max_y - self.min_y
            if y_range == 0:
                y_range = 1
                
            prev_x = None
            prev_y = None
            
            for i, point in enumerate(series.data[:plot_width]):
                y_val = point[1] if isinstance(point, tuple) else point
                
                plot_x = self.x + 4 + i
                plot_y = self.y + self.height - 2 - int((y_val - self.min_y) / y_range * plot_height)
                
                # Draw point
                # Draw line from previous point
                if prev_x is not None:
                    self._draw_line(screen, prev_x, prev_y, plot_x, plot_y, series.color)
                    
                prev_x = plot_x
                prev_y = plot_y
                
    def _render_pie_chart(self, screen):
        """Render pie chart"""
        if not self.series_list:
            return
            
        series = self.series_list[0]
        data = series.data
        
        if not data:
            return
            
        # Calculate total
        values = [p[1] if isinstance(p, tuple) else p for p in data]
        total = sum(values)
        
        if total == 0:
            return
            
        # Simple pie chart using characters
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        radius = min(self.width, self.height) // 2 - 2
        
        # Draw segments
        current_angle = 0
        for i, (point, value) in enumerate(zip(data, values)):
            angle = (value / total) * 360
            # Draw segment (simplified)
            current_angle += angle
            
    def _render_title(self, screen):
        """Render chart title"""
        title_x = self.x + (self.width - len(self.title)) // 2
        title_y = self.y
        # Draw title at title_x, title_y
        
    def _render_legend(self, screen):
        """Render legend"""
        legend_x = self.x + self.width - 15
        legend_y = self.y + 2
        
        for i, series in enumerate(self.series_list):
            if not series.visible:
                continue
                
            y = legend_y + i
            # Draw color indicator
            # Draw series name
            name = series.name[:12]  # Truncate if needed
            # Draw at legend_x + 2, y
            
    def _draw_line(self, screen, x1, y1, x2, y2, color):
        """Draw line between two points (Bresenham's algorithm)"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            # Draw point at x, y
            
            if x == x2 and y == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy


# Utility functions

def create_bar_chart(name_id="barChart"):
    """Create a bar chart with default settings"""
    chart = Chart(name_id=name_id)
    chart.set_chart_type(Chart.BAR)
    chart.show_legend = True
    return chart


def create_line_chart(name_id="lineChart"):
    """Create a line chart with default settings"""
    chart = Chart(name_id=name_id)
    chart.set_chart_type(Chart.LINE)
    chart.show_grid = True
    return chart


def create_pie_chart(name_id="pieChart"):
    """Create a pie chart with default settings"""
    chart = Chart(name_id=name_id)
    chart.set_chart_type(Chart.PIE)
    return chart


def sample_data_chart():
    """Create a sample chart with demo data"""
    chart = create_bar_chart("sampleChart")
    chart.title = "Sample Data"
    
    series = chart.add_series("Sales", color="green")
    series.add_point(0, 10)
    series.add_point(1, 25)
    series.add_point(2, 15)
    series.add_point(3, 30)
    series.add_point(4, 20)
    
    return chart
