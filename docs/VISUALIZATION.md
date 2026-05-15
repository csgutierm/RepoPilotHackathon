# RepoPilot Visualization Guide

## Overview

RepoPilot now features a comprehensive interactive visualization dashboard built with Streamlit and Plotly, providing deep insights into your Python repositories through 6 specialized tabs.

## Features

### 🎨 Interactive Dashboard

The enhanced dashboard (`dashboard_enhanced.py`) provides:

- **6 Comprehensive Tabs**: Overview, Architecture, Dependencies, Documentation, Testing, and Onboarding
- **Real-time Analysis**: Analyze any Python repository on-demand
- **Interactive Charts**: Zoom, pan, and hover for detailed information
- **Professional Design**: Modern UI with gradient themes and responsive layout
- **Export Capabilities**: Generate documentation and reports directly from the dashboard

### 📊 Visualization Components

Located in `src/repopilot/visualization/components.py`, this module provides 10+ reusable Plotly chart functions:

1. **create_pie_chart** - Interactive pie/donut charts
2. **create_bar_chart** - Vertical/horizontal bar charts
3. **create_horizontal_bar_chart** - Specialized horizontal bars
4. **create_scatter_plot** - Scatter plots with size and color encoding
5. **create_gauge_chart** - Gauge charts for metrics
6. **create_network_graph** - Interactive network/dependency graphs
7. **create_sunburst_chart** - Hierarchical sunburst charts
8. **create_treemap_chart** - Treemap visualizations
9. **create_heatmap** - Heatmap visualizations
10. **create_line_chart** - Line charts for trends
11. **detect_circular_dependencies** - Circular dependency detection

### 🌐 API Endpoints

New visualization API routes (`src/repopilot/api/routes/visualization.py`):

- `GET /api/v1/visualize` - Redirect to latest analysis
- `GET /api/v1/visualize/{analysis_id}` - Redirect to specific analysis
- `GET /api/v1/visualize/{analysis_id}/data` - Get raw analysis data
- `GET /api/v1/visualize/list` - List all analyses
- `DELETE /api/v1/visualize/{analysis_id}` - Delete an analysis

Each redirect endpoint includes a beautiful HTML loading page with animations.

## Dashboard Tabs

### 📊 Tab 1: Overview

**Purpose**: High-level repository metrics and health score

**Features**:
- 5 key metrics cards (Files, Classes, Functions, Lines, Coverage)
- Code structure pie chart
- Dependency type distribution
- Test coverage gauge
- Repository health score with breakdown
- Color-coded status indicators

**Health Score Calculation**:
```
Health Score = (Coverage × 0.4) + (Complexity × 0.3) + (Test Ratio × 0.3)
```

### 🏗️ Tab 2: Architecture

**Purpose**: Deep dive into code structure and complexity

**Features**:
- Complexity metrics (average, max, status)
- Module size treemap
- Complexity vs. size scatter plot
- Top modules by complexity bar chart
- Detailed module data table with gradient coloring
- Module breakdown analysis

**Key Insights**:
- Identify overly complex modules
- Visualize code distribution
- Find refactoring candidates

### 🔗 Tab 3: Dependencies

**Purpose**: Dependency analysis and circular dependency detection

**Features**:
- Dependency metrics (total, external, standard library)
- **Circular dependency detection** with warnings
- Interactive network graph visualization
- External package list with versions
- Module dependency relationships
- Network graph with up to 100 nodes for performance

**Circular Dependency Detection**:
Uses NetworkX to detect cycles in the dependency graph and highlights them in the visualization.

### 📚 Tab 4: Documentation

**Purpose**: Documentation coverage analysis

**Features**:
- Documentation metrics (total items, documented, missing)
- Documentation coverage pie chart
- Coverage gauge
- Actionable recommendations
- Generate architecture documentation button
- API documentation generation (coming soon)

**Recommendations Include**:
- Increase coverage targets
- Add docstrings to classes
- Document function parameters
- Create comprehensive README
- Set up Sphinx documentation

### 🧪 Tab 5: Testing

**Purpose**: Test coverage analysis and recommendations

**Features**:
- Overall coverage metrics
- Coverage gauge with threshold indicators
- Test type distribution (unit, integration, functional)
- Module-level coverage breakdown
- Top 15 modules by coverage bar chart
- Color-coded coverage table
- Testing recommendations

**Coverage Thresholds**:
- 🟢 Green: ≥80%
- 🟡 Yellow: 50-79%
- 🔴 Red: <50%

### 🎓 Tab 6: Onboarding

**Purpose**: Developer onboarding and learning path

**Features**:
- Project overview with key metrics
- 4-step learning path with expandable sections
- Key modules to explore (top 10 by size)
- Generate comprehensive onboarding report
- Getting started guide
- Module exploration recommendations

**Learning Path Steps**:
1. Setup Development Environment
2. Understand Core Architecture
3. Explore Key Components
4. Make Your First Contribution

## Usage

### Running the Enhanced Dashboard

```bash
# Install dependencies
pip install -r requirements.txt

# Run the enhanced dashboard
streamlit run dashboard_enhanced.py

# The dashboard will open at http://localhost:8501
```

### Using the Dashboard

1. **Enter Repository Path**: In the sidebar, enter the path to your repository (default: ".")
2. **Click Analyze**: Press the "🔍 Analyze Repository" button
3. **Wait for Analysis**: Progress bar shows analysis status
4. **Explore Tabs**: Navigate through the 6 tabs to explore different aspects
5. **Generate Reports**: Use buttons in Documentation and Onboarding tabs to generate reports

### Using Visualization Components

```python
from src.repopilot.visualization.components import (
    create_pie_chart,
    create_network_graph,
    detect_circular_dependencies
)

# Create a pie chart
fig = create_pie_chart(
    labels=['Category A', 'Category B', 'Category C'],
    values=[30, 45, 25],
    title="Distribution",
    hole=0.4  # Donut chart
)

# Detect circular dependencies
dependencies = [
    {'source': 'module_a', 'target': 'module_b'},
    {'source': 'module_b', 'target': 'module_c'},
    {'source': 'module_c', 'target': 'module_a'}  # Circular!
]
circular_deps = detect_circular_dependencies(dependencies)
print(f"Found {len(circular_deps)} circular dependencies")

# Create network graph
nodes = [
    {'id': 'module_a', 'label': 'Module A'},
    {'id': 'module_b', 'label': 'Module B'}
]
edges = [
    {'source': 'module_a', 'target': 'module_b'}
]
fig = create_network_graph(nodes, edges, "Dependency Graph", circular_deps)
```

### Using API Endpoints

```bash
# Analyze a repository (stores result for visualization)
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "."}'

# Response includes visualization URL:
# "message": "Analysis completed successfully. View at /api/v1/visualize/{analysis_id}"

# Access visualization (redirects to dashboard)
curl "http://localhost:8000/api/v1/visualize"

# Get raw analysis data
curl "http://localhost:8000/api/v1/visualize/{analysis_id}/data"

# List all analyses
curl "http://localhost:8000/api/v1/visualize/list"
```

## Architecture

### Component Structure

```
src/repopilot/
├── visualization/
│   ├── __init__.py
│   └── components.py          # Reusable Plotly components
├── api/
│   ├── routes/
│   │   ├── __init__.py
│   │   └── visualization.py   # Visualization API routes
│   └── main.py                # Main API with router
dashboard_enhanced.py          # Enhanced Streamlit dashboard
```

### Data Flow

```
1. User triggers analysis via Dashboard or API
2. Analyzers process repository (AST, Dependencies, Coverage)
3. Results stored in session state (Dashboard) or memory (API)
4. Visualization components render interactive charts
5. User explores data through 6 specialized tabs
6. Optional: Generate documentation/reports
```

### Technology Stack

- **Streamlit**: Dashboard framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation
- **NetworkX**: Graph analysis and circular dependency detection
- **FastAPI**: API endpoints
- **Pydantic**: Data validation

## Customization

### Adding New Visualizations

1. Create a new function in `components.py`:

```python
def create_custom_chart(data: List[Any], title: str) -> go.Figure:
    """Create a custom chart"""
    fig = go.Figure(...)
    fig.update_layout(title=title, height=400)
    return fig
```

2. Export it in `__init__.py`
3. Use it in the dashboard tabs

### Adding New Dashboard Tabs

1. Create a new tab function:

```python
def create_custom_tab(data: Dict[str, Any]) -> None:
    """Create a custom tab"""
    st.markdown("## Custom Analysis")
    # Add your visualizations
```

2. Add the tab in `main()`:

```python
tab7 = st.tabs(["...", "🎨 Custom"])
with tab7:
    create_custom_tab(st.session_state['data'])
```

### Customizing Colors

Modify the `COLORS` dictionary in `components.py`:

```python
COLORS = {
    'primary': '#your_color',
    'secondary': '#your_color',
    # ...
}
```

## Performance Considerations

### Large Repositories

- Network graphs limited to 100 nodes for performance
- Module tables show top 15 by default
- Use pagination for large datasets
- Consider caching analysis results

### Optimization Tips

1. **Cache Analysis Results**: Use `@st.cache_data` for expensive operations
2. **Limit Graph Size**: Reduce nodes/edges in network visualizations
3. **Lazy Loading**: Load data only when tabs are accessed
4. **Batch Processing**: Process files in batches for large repos

## Troubleshooting

### Common Issues

**Dashboard won't start**:
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Check Streamlit version
streamlit --version
```

**Analysis fails**:
- Verify repository path is correct
- Check file permissions
- Ensure Python files are valid syntax

**Visualizations not showing**:
- Check browser console for errors
- Try refreshing the page
- Clear Streamlit cache: `streamlit cache clear`

**API endpoints not working**:
- Ensure FastAPI server is running: `uvicorn src.repopilot.api.main:app --reload`
- Check port 8000 is not in use
- Verify router is included in main app

## Examples

### Example 1: Analyze Current Project

```bash
streamlit run dashboard_enhanced.py
# Enter "." as repository path
# Click "Analyze Repository"
```

### Example 2: Generate Reports

```python
from pathlib import Path
from src.repopilot.analyzers import ASTAnalyzer
from src.repopilot.generators import DocGenerator

# Analyze
analyzer = ASTAnalyzer()
analyzer.analyze_directory(Path("."))
architecture = analyzer.get_architecture_summary()

# Generate docs
doc_gen = DocGenerator(Path("."))
arch_doc = doc_gen.generate_architecture_docs(architecture)
doc_gen.save_documentation("ARCHITECTURE.md", arch_doc)
```

### Example 3: API Integration

```python
import requests

# Analyze repository
response = requests.post(
    "http://localhost:8000/analyze",
    json={"repository_path": "."}
)

# Get visualization URL
data = response.json()
print(data["message"])  # Contains visualization URL

# Access visualization
viz_response = requests.get("http://localhost:8000/api/v1/visualize")
```

## Best Practices

1. **Regular Analysis**: Run analysis after major changes
2. **Monitor Health Score**: Keep it above 70
3. **Address Circular Dependencies**: Refactor to remove cycles
4. **Improve Coverage**: Aim for 80%+ test coverage
5. **Document Code**: Maintain 70%+ documentation coverage
6. **Review Complexity**: Refactor modules with high complexity
7. **Update Dependencies**: Keep external packages current

## Future Enhancements

- [ ] Real-time analysis updates
- [ ] Historical trend tracking
- [ ] Comparison between branches
- [ ] Custom metric definitions
- [ ] Export to PDF/HTML
- [ ] Integration with CI/CD
- [ ] Team collaboration features
- [ ] AI-powered recommendations

## Contributing

To contribute new visualizations:

1. Add component function to `components.py`
2. Write tests for the component
3. Update this documentation
4. Submit a pull request

## Support

For issues or questions:
- Check the troubleshooting section
- Review example usage
- Open an issue on GitHub

---

**Made with ❤️ by the RepoPilot Team**