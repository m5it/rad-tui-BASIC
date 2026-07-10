# Chart Control Guide for RAD-TUI v2.2.0

## Table of Contents

1. [Introduction](#introduction)
2. [Chart Types](#chart-types)
3. [Creating Charts](#creating-charts)
4. [Data Series](#data-series)
5. [Chart Appearance](#chart-appearance)
6. [Events and Interactivity](#events-and-interactivity)
7. [Updating Data Dynamically](#updating-data-dynamically)
8. [Practical Examples](#practical-examples)
9. [Best Practices](#best-practices)

---

## Introduction

The Chart control (Control Type 25) in RAD-TUI v2.2.0 provides data visualization capabilities directly in your terminal applications. It supports three chart types: Bar, Line, and Pie charts.

### Features

- **Multiple chart types**: Bar, Line, Pie
- **Multiple series**: Display multiple data sets
- **Auto-scaling**: Automatic axis range calculation
- **Customizable appearance**: Colors, labels, grid
- **Interactive**: Click events on data points
- **Terminal-optimized**: ASCII/Unicode rendering

---

## Chart Types

### Bar Chart (Type 0)

Best for comparing discrete categories.

```python
chart = Chart(name_id="barChart", x=2, y=2, width=40, height=15)
chart.set_chart_type(Chart.BAR)
chart.title = "Sales by Month"
```

**When to use**:
- Comparing values across categories
- Showing changes over time (discrete)
- Ranking items

### Line Chart (Type 1)

Best for showing trends over time.

```python
chart = Chart(name_id="lineChart", x=2, y=2, width=40, height=15)
chart.set_chart_type(Chart.LINE)
chart.title = "Stock Price Trend"
```

**When to use**:
- Continuous data over time
- Showing trends and patterns
- Multiple series comparison

### Pie Chart (Type 2)

Best for showing parts of a whole.

```python
chart = Chart(name_id="pieChart", x=2, y=2, width=30, height=15)
chart.set_chart_type(Chart.PIE)
chart.title = "Market Share"
```

**When to use**:
- Percentage distribution
- Proportional data
- Limited categories (2-7 items)

---

## Creating Charts

### Basic Chart Setup

```python
# Create chart control
chart = Chart(
    name_id="myChart",
    x=5,
    y=3,
    width=50,
    height=20
)

# Set chart type
chart.set_chart_type(Chart.BAR)  # or Chart.LINE, Chart.PIE

# Add title and labels
chart.title = "Quarterly Revenue"
chart.x_label = "Quarter"
chart.y_label = "Revenue ($K)"
```

### Factory Functions

```python
# Quick creation with presets
bar_chart = create_bar_chart("salesChart")
line_chart = create_line_chart("trendChart")
pie_chart = create_pie_chart("shareChart")

# Sample data for testing
sample = sample_data_chart()
```

---

## Data Series

### Creating Series

```python
# Add a series
sales_series = chart.add_series(
    name="Sales",
    data=[(0, 100), (1, 150), (2, 120), (3, 180)],
    color="green"
)

# Add points individually
revenue = chart.add_series("Revenue", color="blue")
revenue.add_point(0, 50000)
revenue.add_point(1, 65000)
revenue.add_point(2, 58000)
revenue.add_point(3, 72000)
```

### Data Formats

```python
# Format 1: List of (x, y) tuples
series1 = chart.add_series("Series 1")
series1.data = [(0, 10), (1, 20), (2, 15), (3, 25)]

# Format 2: Just Y values (X auto-generated)
series2 = chart.add_series("Series 2")
series2.data = [10, 20, 15, 25]  # X will be 0, 1, 2, 3

# Format 3: Mixed
series3 = chart.add_series("Series 3")
series3.data = [5, (2, 8), 12, (5, 20)]
```

### Multiple Series

```python
# Bar chart with multiple series
chart = create_bar_chart("comparisonChart")

# Add multiple data sets
chart.add_series("2023", color="blue")
chart.add_series("2024", color="green")

# Populate data
for i, series in enumerate(chart.series_list):
    for month in range(12):
        value = random.randint(50, 100)
        series.add_point(month, value)
```

---

## Chart Appearance

### Colors

```python
# Named colors
chart.add_series("Sales", color="red")
chart.add_series("Profit", color="green")
chart.add_series("Expenses", color="blue")

# Hex colors (terminal-approximated)
chart.add_series("Custom", color="#FF5733")

# No color (uses default)
chart.add_series("Default")
```

### Labels and Titles

```python
chart.title = "Annual Performance"
chart.x_label = "Month"
chart.y_label = "Amount ($)"

# For pie charts, labels come from data names
pie.add_series("Market Share")
for name, value in [("A", 30), ("B", 45), ("C", 25)]:
    series.add_point(name, value)
```

### Grid and Legend

```python
# Show/hide elements
chart.show_grid = True      # Background grid
chart.show_legend = True     # Series legend
chart.show_values = False    # Value labels on bars/points

# Legend position (when implemented)
chart.legend_position = "right"  # or "bottom", "top"
```

### Axis Configuration

```python
# Manual Y-axis range
chart.set_range(0, 1000)  # min_y, max_y
chart.auto_scale = False

# Auto-scaling (default)
chart.auto_scale = True

# X-axis range (for line charts)
chart.min_x = 0
chart.max_x = 12
```

---

## Events and Interactivity

### Click Events

```python
# Point click
def on_point_click_chart():
    point = chart.selected_point
    if point:
        print(f"Clicked: {point}")

chart.on_point_click = on_point_click_chart

# Series click
def on_series_click_chart():
    series = chart.selected_series
    if series:
        print(f"Series: {series.name}")
```

### Hover Events (when implemented)

```python
def on_point_hover_chart():
    point = chart.hovered_point
    # Update tooltip or status bar
    statusBar.set_panel_text(0, f"Value: {point.value}")
```

### Selection

```python
# Programmatic selection
chart.select_point(series_index, point_index)

# Get selection
selected = chart.get_selected_point()
if selected:
    print(f"Selected: {selected.series.name}, {selected.value}")
```

---

## Updating Data Dynamically

### Real-time Updates

```python
import time

# Create chart
chart = create_line_chart("liveChart")
series = chart.add_series("Live Data", color="green")

# Simulate real-time data
def update_chart():
    while True:
        # Add new point
        x = len(series.data)
        y = random.randint(50, 100)
        series.add_point(x, y)
        
        # Keep only last 20 points
        if len(series.data) > 20:
            series.data.pop(0)
        
        # Auto-scale Y-axis
        chart.auto_scale_range()
        
        # Refresh display
        chart.render(screen)
        
        time.sleep(1)
```

### Loading from Data Source

```python
def load_sales_data(chart, start_date, end_date):
    """Load data from database"""
    db = Database()
    db.connect("sales.db")
    
    result = db.execute_query(
        "SELECT date, amount FROM sales WHERE date BETWEEN ? AND ?",
        (start_date, end_date)
    )
    
    series = chart.add_series("Sales")
    for row in result.rows:
        date_str = row[0]
        amount = row[1]
        series.add_point(date_str, amount)
        
    db.disconnect()

# Usage
chart = create_bar_chart("salesChart")
load_sales_data(chart, "2024-01-01", "2024-12-31")
```

### Updating Existing Data

```python
# Modify existing series
series = chart.series_list[0]
series.data[5] = (5, 150)  # Update point at index 5

# Clear and reload
series.clear()
for new_point in updated_data:
    series.add_point(new_point[0], new_point[1])

# Remove series
chart.remove_series(1)

# Refresh
chart.render(screen)
```

---

## Practical Examples

### Sales Dashboard

```python
def create_sales_dashboard():
    dashboard = Form("Sales Dashboard", width=80, height=24)
    
    # Monthly sales bar chart
    monthly = create_bar_chart("monthlySales")
    monthly.title = "Monthly Sales"
    monthly.x_label = "Month"
    monthly.y_label = "Revenue ($K)"
    monthly.set_range(0, 200)
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    sales = [120, 135, 155, 140, 175, 190]
    
    series = monthly.add_series("2024", color="green")
    for i, (month, sale) in enumerate(zip(months, sales)):
        series.add_point(i, sale)
    
    dashboard.add_control(monthly)
    
    # Category pie chart
    category = create_pie_chart("categoryShare")
    category.title = "Sales by Category"
    
    cat_series = category.add_series("Categories")
    cat_series.add_point("Electronics", 45)
    cat_series.add_point("Clothing", 30)
    cat_series.add_point("Food", 25)
    
    dashboard.add_control(category)
    
    return dashboard
```

### Stock Price Tracker

```python
class StockTracker:
    def __init__(self):
        self.chart = create_line_chart("stockChart")
        self.chart.title = "Stock Price"
        self.chart.show_grid = True
        
        self.price_series = self.chart.add_series("Price", color="blue")
        self.volume_series = self.chart.add_series("Volume", color="gray")
        
    def add_tick(self, price, volume):
        """Add new stock tick"""
        x = len(self.price_series.data)
        
        self.price_series.add_point(x, price)
        self.volume_series.add_point(x, volume / 100)  # Scale volume
        
        # Keep last 50 ticks
        if len(self.price_series.data) > 50:
            self.price_series.data.pop(0)
            self.volume_series.data.pop(0)
            
        # Update range
        self.chart.auto_scale_range()
        
    def get_chart(self):
        return self.chart
```

### Survey Results

```python
def display_survey_results(responses):
    """
    responses: dict with question -> {option: count}
    """
    form = Form("Survey Results", width=60, height=20)
    
    y_position = 2
    for question, answers in responses.items():
        # Create pie chart for each question
        chart = create_pie_chart(f"chart_{question}")
        chart.title = question[:30]  # Truncate long questions
        
        series = chart.add_series("Responses")
        for option, count in answers.items():
            series.add_point(option, count)
            
        chart.x = 2
        chart.y = y_position
        chart.width = 25
        chart.height = 10
        
        form.add_control(chart)
        
        # Add data table next to chart
        table = Grid(x=30, y=y_position, width=25, height=10)
        table.grid_headers = ["Option", "Count", "%"]
        
        total = sum(answers.values())
        for option, count in answers.items():
            percent = (count / total) * 100
            table.grid_data.append([option, str(count), f"{percent:.1f}%"])
            
        form.add_control(table)
        y_position += 12
        
    return form
```

### Performance Monitor

```python
class PerformanceMonitor:
    def __init__(self):
        self.cpu_chart = create_line_chart("cpuChart")
        self.cpu_chart.title = "CPU Usage %"
        self.cpu_chart.set_range(0, 100)
        
        self.mem_chart = create_line_chart("memChart")
        self.mem_chart.title = "Memory Usage MB"
        
        self.cpu_series = self.cpu_chart.add_series("CPU", color="red")
        self.mem_series = self.mem_chart.add_series("Memory", color="blue")
        
    def update(self, cpu_percent, memory_mb):
        """Update with new metrics"""
        # Add points
        self.cpu_series.add_point(len(self.cpu_series.data), cpu_percent)
        self.mem_series.add_point(len(self.mem_series.data), memory_mb)
        
        # Keep last 60 points (1 minute at 1 sample/sec)
        if len(self.cpu_series.data) > 60:
            self.cpu_series.data.pop(0)
            self.mem_series.data.pop(0)
            
        # Auto-scale memory chart
        self.mem_chart.auto_scale_range()
```

---

## Best Practices

### Performance

1. **Limit data points**: Keep under 100 for smooth rendering
2. **Use auto-scale sparingly**: Set fixed ranges when possible
3. **Batch updates**: Update data, then render once
4. **Remove unused series**: Free memory when done

### Design

1. **Choose right chart type**:
   - Bar: Comparisons
   - Line: Trends
   - Pie: Proportions

2. **Limit series**: Max 3-4 series for clarity
3. **Use contrasting colors**: Ensure visibility
4. **Add labels**: Always label axes
5. **Keep titles short**: Under 40 characters

### Data

1. **Normalize data**: Scale values appropriately
2. **Handle missing values**: Use None or interpolate
3. **Sort data**: For bar charts, sort by value
4. **Round numbers**: Avoid excessive decimal places

### Terminal Considerations

1. **Use Unicode**: Box-drawing characters look better
2. **Mind the aspect**: Characters are taller than wide
3. **Test colors**: Not all terminals support 256 colors
4. **Keep it simple**: Complex charts don't render well

---

## Common Patterns

### Responsive Chart

```python
def create_responsive_chart(parent_width, parent_height):
    """Create chart that fills available space"""
    margin = 2
    chart = Chart(
        name_id="responsiveChart",
        x=margin,
        y=margin,
        width=parent_width - margin * 2,
        height=parent_height - margin * 2 - 2  # Leave room for status
    )
    return chart
```

### Chart with Legend

```python
def create_chart_with_legend():
    """Create chart with external legend"""
    form = Form("Chart", width=60, height=20)
    
    # Main chart
    chart = create_bar_chart("mainChart")
    chart.x = 2
    chart.y = 2
    chart.width = 40
    chart.height = 15
    chart.show_legend = False  # Hide built-in legend
    
    # External legend as list
    legend = ListBox(x=45, y=2, width=12, height=10)
    legend.items = []
    
    for series in chart.series_list:
        legend.items.append(f"■ {series.name}")
        
    form.add_control(chart)
    form.add_control(legend)
    
    return form
```

### Export Chart Data

```python
def export_chart_data(chart, filename):
    """Export chart data to CSV"""
    handle = open_file(filename, 'w')
    if handle:
        # Header
        headers = ["X"]
        for series in chart.series_list:
            headers.append(series.name)
        write_line(handle, ','.join(headers))
        
        # Data (assuming same X for all series)
        max_points = max(len(s.data) for s in chart.series_list)
        for i in range(max_points):
            row = [str(i)]
            for series in chart.series_list:
                if i < len(series.data):
                    point = series.data[i]
                    y_val = point[1] if isinstance(point, tuple) else point
                    row.append(str(y_val))
                else:
                    row.append("")
            write_line(handle, ','.join(row))
            
        close_file(handle)
```

---

## Troubleshooting

### Chart Not Displaying

- Check `visible` property is True
- Verify chart dimensions (width > 10, height > 5)
- Ensure chart is added to form

### Data Not Showing

- Verify data format: list of tuples or values
- Check series has `visible = True`
- Ensure data is within axis range

### Colors Not Working

- Terminal may not support colors
- Use named colors instead of hex
- Check terminal color settings

### Performance Issues

- Too many data points (>100)
- Too many series (>5)
- Frequent re-rendering

---

## Resources

- [Chart.js Documentation](https://www.chartjs.org/docs/) (concepts)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html) (inspiration)
- [RAD-TUI API Reference](API_REFERENCE_V22.md)

---

*Last Updated: 2025*
