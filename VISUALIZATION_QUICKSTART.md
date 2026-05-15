# 🚀 RepoPilot Visualization - Quick Start Guide

Get started with RepoPilot's powerful visualization dashboard in 5 minutes!

## 📦 Installation

```bash
# Clone the repository (if you haven't already)
git clone <your-repo-url>
cd RepoPilotHackathon

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Quick Start

### Option 1: Enhanced Dashboard (Recommended)

```bash
# Run the enhanced dashboard with 6 comprehensive tabs
streamlit run dashboard_enhanced.py
```

The dashboard will open at `http://localhost:8501`

### Option 2: Original Dashboard

```bash
# Run the original dashboard
streamlit run dashboard.py
```

### Option 3: API + Dashboard

```bash
# Terminal 1: Start the API server
uvicorn src.repopilot.api.main:app --reload

# Terminal 2: Run the dashboard
streamlit run dashboard_enhanced.py

# Access API docs at http://localhost:8000/docs
# Access dashboard at http://localhost:8501
```

## 🎨 Dashboard Features

### 📊 Tab 1: Overview
- Repository KPIs (Files, Classes, Functions, Lines, Coverage)
- Health Score with breakdown
- Quick summary charts

### 🏗️ Tab 2: Architecture
- Code structure analysis
- Complexity metrics
- Module treemap
- Complexity vs. size scatter plot

### 🔗 Tab 3: Dependencies
- **Circular dependency detection** ⚠️
- Interactive network graph
- External package list
- Dependency metrics

### 📚 Tab 4: Documentation
- Documentation coverage analysis
- Missing docs identification
- Generate architecture docs
- Recommendations

### 🧪 Tab 5: Testing
- Test coverage metrics
- Module-level breakdown
- Coverage gauges
- Testing recommendations

### 🎓 Tab 6: Onboarding
- 4-step learning path
- Key modules to explore
- Generate onboarding report
- Getting started guide

## 🔥 Quick Examples

### Analyze Your Repository

1. Open the dashboard: `streamlit run dashboard_enhanced.py`
2. Enter repository path: `.` (current directory)
3. Click "🔍 Analyze Repository"
4. Explore the 6 tabs!

### Using the API

```bash
# Analyze a repository
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "."}'

# View visualization (opens beautiful redirect page)
curl "http://localhost:8000/api/v1/visualize"

# List all analyses
curl "http://localhost:8000/api/v1/visualize/list"
```

### Generate Documentation

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

## 🎯 Key Features

### ✨ Interactive Visualizations
- **Zoom, pan, and hover** on all charts
- **Network graphs** for dependencies
- **Treemaps** for module size
- **Gauges** for metrics
- **Scatter plots** for complexity analysis

### 🔍 Circular Dependency Detection
The dashboard automatically detects and highlights circular dependencies:
```
⚠️ 3 Circular Dependencies Detected!
1. module_a → module_b → module_c → module_a
2. utils → helpers → utils
```

### 📊 Health Score
Comprehensive repository health score based on:
- **Coverage** (40% weight)
- **Complexity** (30% weight)
- **Test Ratio** (30% weight)

### 🎨 Beautiful UI
- Modern gradient themes
- Responsive layout
- Color-coded metrics
- Professional design

## 📚 Documentation

For detailed documentation, see:
- [Full Visualization Guide](docs/VISUALIZATION.md)
- [Architecture Documentation](docs/ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs) (when API is running)

## 🛠️ Troubleshooting

### Dashboard won't start
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check Streamlit version
streamlit --version
```

### Analysis fails
- Verify repository path is correct
- Check Python file syntax
- Ensure you have read permissions

### Visualizations not showing
- Refresh the browser
- Clear Streamlit cache: `streamlit cache clear`
- Check browser console for errors

## 🎓 Next Steps

1. **Explore the Dashboard**: Try all 6 tabs
2. **Generate Reports**: Use the export buttons
3. **Fix Issues**: Address circular dependencies and low coverage
4. **Improve Health**: Aim for 70+ health score
5. **Read Full Docs**: Check out [VISUALIZATION.md](docs/VISUALIZATION.md)

## 💡 Pro Tips

- **Regular Analysis**: Run after major changes
- **Monitor Trends**: Track health score over time
- **Address Warnings**: Fix circular dependencies immediately
- **Improve Coverage**: Aim for 80%+ test coverage
- **Document Code**: Maintain 70%+ documentation coverage

## 🚀 Advanced Usage

### Custom Visualizations

```python
from src.repopilot.visualization.components import (
    create_pie_chart,
    create_network_graph,
    create_gauge_chart
)

# Create custom charts
fig = create_pie_chart(
    labels=['A', 'B', 'C'],
    values=[30, 45, 25],
    title="My Chart",
    hole=0.4
)
```

### API Integration

```python
import requests

# Analyze via API
response = requests.post(
    "http://localhost:8000/analyze",
    json={"repository_path": "."}
)

# Get results
data = response.json()
print(f"Coverage: {data['coverage_report']['overall_coverage']}%")
```

## 🎉 You're Ready!

Start exploring your repository with RepoPilot's powerful visualization dashboard!

```bash
streamlit run dashboard_enhanced.py
```

---

**Questions?** Check the [full documentation](docs/VISUALIZATION.md) or open an issue.

**Made with ❤️ by the RepoPilot Team**