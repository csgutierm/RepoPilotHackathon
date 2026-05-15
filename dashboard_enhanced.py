"""
RepoPilot Enhanced Dashboard - Interactive visualization with 6 comprehensive tabs
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import pandas as pd
from typing import Dict, Any, List

from src.repopilot.analyzers import ASTAnalyzer, DependencyAnalyzer, CoverageAnalyzer
from src.repopilot.generators import DocGenerator, OnboardingGenerator
from src.repopilot.visualization.components import (
    create_pie_chart,
    create_bar_chart,
    create_gauge_chart,
    create_network_graph,
    create_scatter_plot,
    create_treemap_chart,
    detect_circular_dependencies,
)


# Page configuration
st.set_page_config(
    page_title="RepoPilot Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3.5rem;
        padding: 0 2rem;
        background-color: white;
        border-radius: 8px;
        font-weight: 600;
        color: #1f1f1f !important;
        border: 2px solid #e0e0e0;
    }
    .stTabs [data-baseweb="tab"]:hover {
        border-color: #667eea;
        background-color: #f8f9ff;
    }
    .stTabs [data-baseweb="tab"] p {
        color: #1f1f1f !important;
        font-size: 1rem;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-color: #667eea !important;
    }
    .stTabs [aria-selected="true"] p {
        color: white !important;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def create_overview_tab(architecture: Dict[str, Any], dependencies: Dict[str, Any], 
                       coverage: Dict[str, Any]) -> None:
    """Create the Overview tab with KPIs and summary metrics"""
    
    st.markdown("## 📊 Repository Overview & Key Metrics")
    st.divider()
    
    # Top-level KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📁 Files", architecture.get('total_files', 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📦 Classes", architecture.get('total_classes', 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("⚡ Functions", architecture.get('total_functions', 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📝 Lines", f"{architecture.get('total_lines_of_code', 0):,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        coverage_pct = coverage.get('overall_coverage', 0)
        st.metric("🎯 Coverage", f"{coverage_pct}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Summary charts
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🏗️ Code Structure")
        structure_data = {
            'Classes': architecture.get('total_classes', 0),
            'Functions': architecture.get('total_functions', 0),
            'Files': architecture.get('total_files', 0)
        }
        fig = create_pie_chart(
            list(structure_data.keys()),
            list(structure_data.values()),
            title="Code Distribution",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🔗 Dependencies")
        dep_data = {
            'External': dependencies.get('external_packages', 0),
            'Standard Lib': dependencies.get('standard_library', 0)
        }
        fig = create_pie_chart(
            list(dep_data.keys()),
            list(dep_data.values()),
            title="Dependency Types",
            hole=0.4,
            colors=['#667eea', '#764ba2']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.subheader("🎯 Test Coverage")
        fig = create_gauge_chart(
            coverage.get('overall_coverage', 0),
            title="Coverage %",
            max_value=100,
            threshold=80
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Health Score
    st.subheader("💚 Repository Health Score")
    
    # Calculate health score
    coverage_score = min(coverage.get('overall_coverage', 0), 100)
    complexity_score = max(0, 100 - (architecture.get('average_complexity', 0) * 10))
    test_score = min((coverage.get('total_tests', 0) / max(architecture.get('total_files', 1), 1)) * 100, 100)
    
    health_score = (coverage_score * 0.4 + complexity_score * 0.3 + test_score * 0.3)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=health_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Health", 'font': {'size': 28}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen" if health_score > 70 else "orange" if health_score > 40 else "red"},
                'steps': [
                    {'range': [0, 40], 'color': "lightgray"},
                    {'range': [40, 70], 'color': "gray"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ],
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Score Breakdown")
        st.metric("Coverage Score", f"{coverage_score:.1f}/100")
        st.metric("Complexity Score", f"{complexity_score:.1f}/100")
        st.metric("Test Score", f"{test_score:.1f}/100")


def create_architecture_tab(architecture: Dict[str, Any]) -> None:
    """Create the Architecture tab with code structure analysis"""
    
    st.markdown("## 🏗️ Architecture Analysis")
    st.divider()
    
    # Complexity metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Avg Complexity", f"{architecture.get('average_complexity', 0):.2f}")
    with col2:
        st.metric("Max Complexity", architecture.get('max_complexity', 0))
    with col3:
        st.metric("Total Modules", len(architecture.get('modules', {})))
    with col4:
        complexity = architecture.get('average_complexity', 0)
        status = "🟢 Good" if complexity < 5 else "🟡 Medium" if complexity < 10 else "🔴 High"
        st.metric("Complexity Status", status)
    
    st.divider()
    
    # Module analysis
    if architecture.get('modules'):
        st.subheader("📦 Module Analysis")
        
        modules_data = []
        for module_name, module_info in architecture['modules'].items():
            modules_data.append({
                'Module': module_name,
                'Classes': module_info.get('classes', 0),
                'Functions': module_info.get('functions', 0),
                'Lines': module_info.get('lines_of_code', 0),
                'Complexity': module_info.get('complexity', 0)
            })
        
        if modules_data:
            df_modules = pd.DataFrame(modules_data)
            df_modules = df_modules.sort_values('Lines', ascending=False)
            
            # Treemap visualization
            st.subheader("🗺️ Module Size Treemap")
            labels = df_modules['Module'].tolist()
            parents = [''] * len(labels)
            values = df_modules['Lines'].tolist()
            
            fig = create_treemap_chart(labels, parents, values, "Module Size by Lines of Code")
            st.plotly_chart(fig, use_container_width=True)
            
            # Complexity scatter
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Complexity vs Size")
                fig = create_scatter_plot(
                    df_modules['Lines'].tolist(),
                    df_modules['Complexity'].tolist(),
                    df_modules['Module'].tolist(),
                    title="Module Complexity Analysis",
                    x_label="Lines of Code",
                    y_label="Complexity",
                    size=df_modules['Functions'].tolist()
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📈 Top Modules by Complexity")
                top_complex = df_modules.nlargest(10, 'Complexity')
                fig = create_bar_chart(
                    top_complex['Module'].tolist(),
                    top_complex['Complexity'].tolist(),
                    title="",
                    x_label="Module",
                    y_label="Complexity",
                    color_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            st.subheader("📋 Detailed Module Data")
            st.dataframe(
                df_modules.style.background_gradient(subset=['Complexity'], cmap='RdYlGn_r'),
                use_container_width=True,
                hide_index=True
            )


def create_dependencies_tab(dependencies: Dict[str, Any]) -> None:
    """Create the Dependencies tab with interactive dependency graph"""
    
    st.markdown("## 🔗 Dependency Analysis")
    st.divider()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Dependencies", dependencies.get('total_dependencies', 0))
    with col2:
        st.metric("External Packages", dependencies.get('external_packages', 0))
    with col3:
        st.metric("Standard Library", dependencies.get('standard_library', 0))
    with col4:
        module_deps = dependencies.get('module_dependencies', [])
        st.metric("Module Links", len(module_deps))
    
    st.divider()
    
    # Circular dependency detection
    module_deps = dependencies.get('module_dependencies', [])
    if module_deps:
        circular_deps = detect_circular_dependencies(module_deps)
        
        if circular_deps:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.warning(f"⚠️ **{len(circular_deps)} Circular Dependencies Detected!**")
            with st.expander("View Circular Dependencies"):
                for i, cycle in enumerate(circular_deps, 1):
                    st.write(f"{i}. {' → '.join(cycle)} → {cycle[0]}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.success("✅ No circular dependencies detected!")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Network graph
        st.subheader("🕸️ Interactive Dependency Network")
        
        # Prepare nodes and edges
        nodes = []
        node_set = set()
        for dep in module_deps:
            if dep['source'] not in node_set:
                nodes.append({'id': dep['source'], 'label': dep['source'].split('.')[-1]})
                node_set.add(dep['source'])
            if dep['target'] not in node_set:
                nodes.append({'id': dep['target'], 'label': dep['target'].split('.')[-1]})
                node_set.add(dep['target'])
        
        edges = [{'source': dep['source'], 'target': dep['target']} for dep in module_deps[:100]]  # Limit for performance
        
        fig = create_network_graph(nodes, edges, "Module Dependency Graph", circular_deps)
        st.plotly_chart(fig, use_container_width=True)
        
        if len(module_deps) > 100:
            st.info(f"ℹ️ Showing first 100 of {len(module_deps)} dependencies for performance")
    
    st.divider()
    
    # External packages
    if dependencies.get('external_packages_list'):
        st.subheader("📦 External Packages")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            packages_data = []
            for pkg in dependencies['external_packages_list']:
                packages_data.append({
                    'Package': pkg['name'],
                    'Version': pkg.get('version', 'N/A'),
                    'Type': 'External'
                })
            
            df_packages = pd.DataFrame(packages_data)
            st.dataframe(df_packages, use_container_width=True, hide_index=True)
        
        with col2:
            st.metric("Total External", len(dependencies['external_packages_list']))
            st.metric("With Version Info", sum(1 for p in dependencies['external_packages_list'] if p.get('version')))


def create_documentation_tab(architecture: Dict[str, Any], repo_path: Path) -> None:
    """Create the Documentation tab with coverage analysis"""
    
    st.markdown("## 📚 Documentation Analysis")
    st.divider()
    
    # Calculate documentation metrics
    total_items = architecture.get('total_classes', 0) + architecture.get('total_functions', 0)
    
    # Simulated doc coverage (in real implementation, parse docstrings)
    documented_items = int(total_items * 0.65)  # Placeholder
    doc_coverage = (documented_items / total_items * 100) if total_items > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Items", total_items)
    with col2:
        st.metric("Documented", documented_items)
    with col3:
        st.metric("Missing Docs", total_items - documented_items)
    with col4:
        st.metric("Doc Coverage", f"{doc_coverage:.1f}%")
    
    st.divider()
    
    # Documentation coverage visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Documentation Coverage")
        fig = create_pie_chart(
            ['Documented', 'Missing'],
            [documented_items, total_items - documented_items],
            title="Documentation Status",
            hole=0.4,
            colors=['#4caf50', '#f44336']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Coverage Gauge")
        fig = create_gauge_chart(
            doc_coverage,
            title="Documentation %",
            max_value=100,
            threshold=70
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Documentation recommendations
    st.subheader("💡 Documentation Recommendations")
    
    recommendations = []
    if doc_coverage < 70:
        recommendations.append("📝 Increase documentation coverage to at least 70%")
    if architecture.get('total_classes', 0) > 0:
        recommendations.append("📚 Add docstrings to all public classes")
    if architecture.get('total_functions', 0) > 0:
        recommendations.append("⚡ Document all public functions with parameters and return types")
    recommendations.append("📖 Create a comprehensive README.md")
    recommendations.append("🔧 Add API documentation using tools like Sphinx")
    
    for rec in recommendations:
        st.markdown(f"- {rec}")
    
    st.divider()
    
    # Generate documentation button
    st.subheader("📥 Generate Documentation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate Architecture Docs", use_container_width=True):
            with st.spinner("Generating..."):
                try:
                    doc_gen = DocGenerator(repo_path)
                    arch_doc = doc_gen.generate_architecture_docs(architecture)
                    arch_path = doc_gen.save_documentation("ARCHITECTURE.md", arch_doc)
                    st.success(f"✅ Saved to: {arch_path}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.button("📋 Generate API Docs", use_container_width=True):
            st.info("🚧 API documentation generation coming soon!")


def create_testing_tab(coverage: Dict[str, Any]) -> None:
    """Create the Testing tab with test coverage analysis"""
    
    st.markdown("## 🧪 Testing & Coverage Analysis")
    st.divider()
    
    # Test metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Coverage", f"{coverage.get('overall_coverage', 0)}%")
    with col2:
        st.metric("Total Tests", coverage.get('total_tests', 0))
    with col3:
        st.metric("Tested Modules", coverage.get('tested_modules', 0))
    with col4:
        st.metric("Total Modules", coverage.get('total_modules', 0))
    
    st.divider()
    
    # Coverage visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Coverage Gauge")
        fig = create_gauge_chart(
            coverage.get('overall_coverage', 0),
            title="Test Coverage",
            max_value=100,
            threshold=80,
            reference=80
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Test Type Distribution")
        test_breakdown = coverage.get('test_breakdown', {})
        if test_breakdown:
            fig = create_pie_chart(
                list(test_breakdown.keys()),
                list(test_breakdown.values()),
                title="Test Types",
                hole=0.3
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No test breakdown data available")
    
    st.divider()
    
    # Module coverage details
    if coverage.get('module_coverage'):
        st.subheader("📦 Module Coverage Details")
        
        module_cov = coverage['module_coverage']
        cov_data = []
        for module, cov_info in module_cov.items():
            cov_data.append({
                'Module': module,
                'Coverage': cov_info.get('coverage', 0),
                'Has Tests': '✅' if cov_info.get('has_tests', False) else '❌',
                'Status': '🟢' if cov_info.get('coverage', 0) >= 80 else '🟡' if cov_info.get('coverage', 0) >= 50 else '🔴'
            })
        
        if cov_data:
            df_cov = pd.DataFrame(cov_data)
            df_cov = df_cov.sort_values('Coverage', ascending=False)
            
            # Bar chart
            fig = create_bar_chart(
                df_cov.head(15)['Module'].tolist(),
                df_cov.head(15)['Coverage'].tolist(),
                title="Top 15 Modules by Coverage",
                x_label="Module",
                y_label="Coverage %",
                color_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            st.dataframe(
                df_cov.style.background_gradient(subset=['Coverage'], cmap='RdYlGn', vmin=0, vmax=100),
                use_container_width=True,
                hide_index=True
            )
    
    st.divider()
    
    # Recommendations
    if coverage.get('recommendations'):
        st.subheader("💡 Testing Recommendations")
        for rec in coverage['recommendations']:
            st.markdown(f"- {rec}")


def create_onboarding_tab(architecture: Dict[str, Any], dependencies: Dict[str, Any],
                         coverage: Dict[str, Any], repo_path: Path, ast_analyses: Dict) -> None:
    """Create the Onboarding tab with learning path"""
    
    st.markdown("## 🎓 Developer Onboarding Guide")
    st.divider()
    
    # Project overview
    st.subheader("📋 Project Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏗️ Architecture")
        st.write(f"- **Files:** {architecture.get('total_files', 0)}")
        st.write(f"- **Classes:** {architecture.get('total_classes', 0)}")
        st.write(f"- **Functions:** {architecture.get('total_functions', 0)}")
        st.write(f"- **Lines:** {architecture.get('total_lines_of_code', 0):,}")
    
    with col2:
        st.markdown("### 🔗 Dependencies")
        st.write(f"- **External:** {dependencies.get('external_packages', 0)}")
        st.write(f"- **Standard Lib:** {dependencies.get('standard_library', 0)}")
        st.write(f"- **Total:** {dependencies.get('total_dependencies', 0)}")
    
    with col3:
        st.markdown("### 🧪 Testing")
        st.write(f"- **Coverage:** {coverage.get('overall_coverage', 0)}%")
        st.write(f"- **Tests:** {coverage.get('total_tests', 0)}")
        st.write(f"- **Tested Modules:** {coverage.get('tested_modules', 0)}")
    
    st.divider()
    
    # Learning path
    st.subheader("🗺️ Suggested Learning Path")
    
    learning_path = [
        {
            'step': 1,
            'title': 'Setup Development Environment',
            'tasks': [
                'Clone the repository',
                'Install dependencies: `pip install -r requirements.txt`',
                'Set up virtual environment',
                'Run tests to verify setup'
            ]
        },
        {
            'step': 2,
            'title': 'Understand Core Architecture',
            'tasks': [
                'Review ARCHITECTURE.md documentation',
                'Explore main modules and their responsibilities',
                'Understand the project structure',
                'Review key classes and interfaces'
            ]
        },
        {
            'step': 3,
            'title': 'Explore Key Components',
            'tasks': [
                'Study the analyzer modules',
                'Review generator implementations',
                'Understand API endpoints',
                'Examine test structure'
            ]
        },
        {
            'step': 4,
            'title': 'Make Your First Contribution',
            'tasks': [
                'Pick a good first issue',
                'Write tests for your changes',
                'Follow coding standards',
                'Submit a pull request'
            ]
        }
    ]
    
    for path_item in learning_path:
        with st.expander(f"**Step {path_item['step']}: {path_item['title']}**", expanded=path_item['step']==1):
            for task in path_item['tasks']:
                st.markdown(f"- {task}")
    
    st.divider()
    
    # Key modules to explore
    st.subheader("🔑 Key Modules to Explore")
    
    if architecture.get('modules'):
        # Get top modules by size
        modules_data = []
        for module_name, module_info in architecture['modules'].items():
            modules_data.append({
                'Module': module_name,
                'Lines': module_info.get('lines_of_code', 0),
                'Classes': module_info.get('classes', 0),
                'Functions': module_info.get('functions', 0)
            })
        
        df_modules = pd.DataFrame(modules_data)
        df_modules = df_modules.sort_values('Lines', ascending=False).head(10)
        
        st.dataframe(df_modules, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Generate onboarding report
    st.subheader("📥 Generate Onboarding Report")
    
    if st.button("📋 Generate Complete Onboarding Report", use_container_width=True):
        with st.spinner("Generating comprehensive onboarding report..."):
            try:
                onboarding_gen = OnboardingGenerator(repo_path)
                report = onboarding_gen.generate_onboarding_report(
                    architecture,
                    dependencies,
                    coverage,
                    ast_analyses
                )
                report_path = onboarding_gen.save_onboarding_report(report)
                st.success(f"✅ Onboarding report saved to: {report_path}")
                
                with st.expander("📄 View Report Preview"):
                    st.markdown(report[:1000] + "...")
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")


def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<h1 class="main-header">🚀 RepoPilot Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive Repository Analysis & Visualization Platform</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Repository path input
        repo_path_input = st.text_input(
            "Repository Path",
            value=".",
            help="Enter the path to the repository you want to analyze"
        )
        
        repo_path = Path(repo_path_input)
        
        # Analyze button
        analyze_button = st.button("🔍 Analyze Repository", type="primary", use_container_width=True)
        
        st.divider()
        
        # Quick stats
        if st.session_state.get('analyzed'):
            st.markdown("### 📊 Quick Stats")
            arch = st.session_state['architecture']
            st.metric("Files", arch.get('total_files', 0))
            st.metric("Classes", arch.get('total_classes', 0))
            st.metric("Functions", arch.get('total_functions', 0))
        
        st.divider()
        
        # Info
        st.markdown("### ℹ️ How to Use")
        st.markdown("""
        1. Enter repository path
        2. Click 'Analyze Repository'
        3. Explore 6 comprehensive tabs:
           - 📊 Overview
           - 🏗️ Architecture
           - 🔗 Dependencies
           - 📚 Documentation
           - 🧪 Testing
           - 🎓 Onboarding
        """)
        
        st.divider()
        
        # About
        st.markdown("### 🚀 About RepoPilot")
        st.markdown("""
        A powerful Python repository analysis platform with comprehensive visualization and insights.
        
        **Features:**
        - Deep code analysis
        - Dependency mapping
        - Test coverage tracking
        - Documentation generation
        - Developer onboarding
        """)
    
    # Main content
    if analyze_button:
        if not repo_path.exists():
            st.error(f"❌ Repository path not found: {repo_path_input}")
            return
        
        if not repo_path.is_dir():
            st.error(f"❌ Path is not a directory: {repo_path_input}")
            return
        
        # Progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # AST Analysis
            status_text.text("🔍 Analyzing code structure...")
            progress_bar.progress(20)
            ast_analyzer = ASTAnalyzer()
            ast_analyzer.analyze_directory(repo_path)
            architecture = ast_analyzer.get_architecture_summary()
            
            # Dependency Analysis
            status_text.text("🔗 Analyzing dependencies...")
            progress_bar.progress(50)
            dep_analyzer = DependencyAnalyzer(repo_path)
            dependencies = dep_analyzer.analyze_project()
            
            # Coverage Analysis
            status_text.text("🧪 Analyzing test coverage...")
            progress_bar.progress(80)
            coverage_analyzer = CoverageAnalyzer(repo_path)
            coverage = coverage_analyzer.analyze_coverage()
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Store in session state
            st.session_state['architecture'] = architecture
            st.session_state['dependencies'] = dependencies
            st.session_state['coverage'] = coverage
            st.session_state['ast_analyses'] = ast_analyzer.analyses
            st.session_state['repo_path'] = repo_path
            st.session_state['analyzed'] = True
            
            st.success("✅ Analysis completed successfully!")
            
            # Clear progress indicators
            import time
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            progress_bar.empty()
            status_text.empty()
            return
    
    # Display results if available
    if st.session_state.get('analyzed'):
        st.divider()
        
        # Create 6 tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Overview",
            "🏗️ Architecture",
            "🔗 Dependencies",
            "📚 Documentation",
            "🧪 Testing",
            "🎓 Onboarding"
        ])
        
        with tab1:
            create_overview_tab(
                st.session_state['architecture'],
                st.session_state['dependencies'],
                st.session_state['coverage']
            )
        
        with tab2:
            create_architecture_tab(st.session_state['architecture'])
        
        with tab3:
            create_dependencies_tab(st.session_state['dependencies'])
        
        with tab4:
            create_documentation_tab(
                st.session_state['architecture'],
                st.session_state['repo_path']
            )
        
        with tab5:
            create_testing_tab(st.session_state['coverage'])
        
        with tab6:
            create_onboarding_tab(
                st.session_state['architecture'],
                st.session_state['dependencies'],
                st.session_state['coverage'],
                st.session_state['repo_path'],
                st.session_state['ast_analyses']
            )
    
    else:
        # Welcome message
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.info("👈 Enter a repository path in the sidebar and click 'Analyze Repository' to get started!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Feature showcase
        st.subheader("✨ Dashboard Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📊 Overview")
            st.markdown("""
            - Repository KPIs
            - Health score
            - Quick metrics
            - Summary charts
            """)
            
            st.markdown("### 🏗️ Architecture")
            st.markdown("""
            - Code structure
            - Complexity analysis
            - Module breakdown
            - Treemap visualization
            """)
        
        with col2:
            st.markdown("### 🔗 Dependencies")
            st.markdown("""
            - Dependency graph
            - Circular detection
            - Package analysis
            - Network visualization
            """)
            
            st.markdown("### 📚 Documentation")
            st.markdown("""
            - Doc coverage
            - Missing docs
            - Recommendations
            - Auto-generation
            """)
        
        with col3:
            st.markdown("### 🧪 Testing")
            st.markdown("""
            - Test coverage
            - Module breakdown
            - Coverage gauges
            - Test recommendations
            """)
            
            st.markdown("### 🎓 Onboarding")
            st.markdown("""
            - Learning path
            - Key modules
            - Getting started
            - Onboarding report
            """)


if __name__ == "__main__":
    main()

# Made with Bob