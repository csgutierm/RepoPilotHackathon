"""
RepoPilot Dashboard - Interactive visualization using Streamlit and Plotly
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import pandas as pd
from typing import Dict, Any, List

from src.repopilot.analyzers import ASTAnalyzer, DependencyAnalyzer, CoverageAnalyzer
from src.repopilot.generators import DocGenerator, OnboardingGenerator


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
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 2rem;
    }
</style>
""", unsafe_allow_html=True)


def create_architecture_visualizations(architecture: Dict[str, Any]) -> None:
    """Create visualizations for architecture analysis"""
    
    st.subheader("📊 Architecture Overview")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Files", architecture.get('total_files', 0))
    with col2:
        st.metric("Total Classes", architecture.get('total_classes', 0))
    with col3:
        st.metric("Total Functions", architecture.get('total_functions', 0))
    with col4:
        st.metric("Lines of Code", f"{architecture.get('total_lines_of_code', 0):,}")
    
    # Complexity metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Average Complexity", f"{architecture.get('average_complexity', 0):.2f}")
    with col2:
        st.metric("Max Complexity", architecture.get('max_complexity', 0))
    
    st.divider()
    
    # Module breakdown
    if architecture.get('modules'):
        st.subheader("📦 Module Breakdown")
        
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
            
            # Bar chart for classes and functions
            col1, col2 = st.columns(2)
            
            with col1:
                fig_classes = px.bar(
                    df_modules.head(10),
                    x='Module',
                    y='Classes',
                    title='Top 10 Modules by Classes',
                    color='Classes',
                    color_continuous_scale='Blues'
                )
                fig_classes.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_classes, width='stretch')
            
            with col2:
                fig_functions = px.bar(
                    df_modules.head(10),
                    x='Module',
                    y='Functions',
                    title='Top 10 Modules by Functions',
                    color='Functions',
                    color_continuous_scale='Greens'
                )
                fig_functions.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_functions, width='stretch')
            
            # Complexity scatter plot
            fig_complexity = px.scatter(
                df_modules,
                x='Lines',
                y='Complexity',
                size='Functions',
                hover_data=['Module'],
                title='Module Complexity vs Lines of Code',
                labels={'Lines': 'Lines of Code', 'Complexity': 'Cyclomatic Complexity'}
            )
            st.plotly_chart(fig_complexity, width='stretch')
            
            # Data table
            st.subheader("📋 Detailed Module Data")
            st.dataframe(df_modules, width='stretch')


def create_dependency_visualizations(dependencies: Dict[str, Any]) -> None:
    """Create visualizations for dependency analysis"""
    
    st.subheader("🔗 Dependency Overview")
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Dependencies", dependencies.get('total_dependencies', 0))
    with col2:
        st.metric("External Packages", dependencies.get('external_packages', 0))
    with col3:
        st.metric("Standard Library", dependencies.get('standard_library', 0))
    
    st.divider()
    
    # Pie chart for dependency types
    col1, col2 = st.columns(2)
    
    with col1:
        dep_types = {
            'External Packages': dependencies.get('external_packages', 0),
            'Standard Library': dependencies.get('standard_library', 0)
        }
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=list(dep_types.keys()),
            values=list(dep_types.values()),
            hole=0.3,
            marker_colors=['#1f77b4', '#ff7f0e']
        )])
        fig_pie.update_layout(title='Dependency Distribution')
        st.plotly_chart(fig_pie, width='stretch')
    
    with col2:
        # External packages list
        if dependencies.get('external_packages_list'):
            st.subheader("📦 External Packages")
            packages_data = []
            for pkg in dependencies['external_packages_list'][:15]:
                packages_data.append({
                    'Package': pkg['name'],
                    'Version': pkg.get('version', 'N/A')
                })
            
            df_packages = pd.DataFrame(packages_data)
            st.dataframe(df_packages, width='stretch', hide_index=True)
    
    # Module dependencies
    if dependencies.get('module_dependencies'):
        st.subheader("🔀 Module Dependencies")
        
        module_deps_list = dependencies['module_dependencies']
        
        # Count dependencies per source module
        dep_counts_dict = {}
        for dep in module_deps_list:
            source = dep['source']
            if source in dep_counts_dict:
                dep_counts_dict[source] += 1
            else:
                dep_counts_dict[source] = 1
        
        dep_counts = [(module, count) for module, count in dep_counts_dict.items()]
        dep_counts.sort(key=lambda x: x[1], reverse=True)
        
        if dep_counts:
            df_deps = pd.DataFrame(dep_counts[:15], columns=['Module', 'Dependencies'])
            
            fig_deps = px.bar(
                df_deps,
                x='Module',
                y='Dependencies',
                title='Top 15 Modules by Dependency Count',
                color='Dependencies',
                color_continuous_scale='Reds'
            )
            fig_deps.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_deps, width='stretch')
            
            # Show dependency details table
            st.subheader("📋 Dependency Details")
            deps_data = []
            for dep in module_deps_list[:20]:
                deps_data.append({
                    'Source Module': dep['source'],
                    'Target Module': dep['target'],
                    'Import Type': dep['type']
                })
            
            if deps_data:
                df_deps_detail = pd.DataFrame(deps_data)
                st.dataframe(df_deps_detail, width='stretch', hide_index=True)


def create_coverage_visualizations(coverage: Dict[str, Any]) -> None:
    """Create visualizations for coverage analysis"""
    
    st.subheader("🎯 Coverage Overview")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        coverage_pct = coverage.get('overall_coverage', 0)
        st.metric("Overall Coverage", f"{coverage_pct}%")
    with col2:
        st.metric("Total Tests", coverage.get('total_tests', 0))
    with col3:
        st.metric("Total Modules", coverage.get('total_modules', 0))
    with col4:
        tested = coverage.get('tested_modules', 0)
        st.metric("Tested Modules", tested)
    
    st.divider()
    
    # Coverage gauge
    col1, col2 = st.columns(2)
    
    with col1:
        coverage_pct = coverage.get('overall_coverage', 0)
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=coverage_pct,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Test Coverage"},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        st.plotly_chart(fig_gauge, width='stretch')
    
    with col2:
        # Test breakdown
        test_breakdown = coverage.get('test_breakdown', {})
        if test_breakdown:
            fig_tests = go.Figure(data=[go.Pie(
                labels=list(test_breakdown.keys()),
                values=list(test_breakdown.values()),
                hole=0.3
            )])
            fig_tests.update_layout(title='Test Type Distribution')
            st.plotly_chart(fig_tests, width='stretch')
    
    # Module coverage
    if coverage.get('module_coverage'):
        st.subheader("📊 Module Coverage Details")
        
        module_cov = coverage['module_coverage']
        cov_data = []
        for module, cov_info in module_cov.items():
            cov_data.append({
                'Module': module,
                'Coverage': cov_info.get('coverage', 0),
                'Tested': 'Yes' if cov_info.get('has_tests', False) else 'No'
            })
        
        if cov_data:
            df_cov = pd.DataFrame(cov_data)
            df_cov = df_cov.sort_values('Coverage', ascending=False)
            
            # Bar chart
            fig_cov = px.bar(
                df_cov.head(15),
                x='Module',
                y='Coverage',
                title='Top 15 Modules by Coverage',
                color='Coverage',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100]
            )
            fig_cov.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_cov, width='stretch')
            
            # Data table
            st.dataframe(df_cov, width='stretch', hide_index=True)
    
    # Recommendations
    if coverage.get('recommendations'):
        st.subheader("💡 Recommendations")
        for rec in coverage['recommendations']:
            st.info(rec)


def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<h1 class="main-header">🚀 RepoPilot Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Interactive Repository Analysis & Visualization")
    
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
        analyze_button = st.button("🔍 Analyze Repository", type="primary", width='stretch')
        
        st.divider()
        
        # Info
        st.info("""
        **How to use:**
        1. Enter repository path
        2. Click 'Analyze Repository'
        3. Explore results in tabs
        """)
        
        st.divider()
        
        # About
        st.markdown("### About RepoPilot")
        st.markdown("""
        A powerful Python repository analysis platform with:
        - 🏗️ Architecture Analysis
        - 🔗 Dependency Mapping
        - 🎯 Coverage Analysis
        - 📚 Documentation Generation
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
        with st.spinner("🔄 Analyzing repository..."):
            try:
                # Perform analyses
                ast_analyzer = ASTAnalyzer()
                ast_analyzer.analyze_directory(repo_path)
                architecture = ast_analyzer.get_architecture_summary()
                
                dep_analyzer = DependencyAnalyzer(repo_path)
                dependencies = dep_analyzer.analyze_project()
                
                coverage_analyzer = CoverageAnalyzer(repo_path)
                coverage = coverage_analyzer.analyze_coverage()
                
                # Store in session state
                st.session_state['architecture'] = architecture
                st.session_state['dependencies'] = dependencies
                st.session_state['coverage'] = coverage
                st.session_state['ast_analyses'] = ast_analyzer.analyses
                st.session_state['repo_path'] = repo_path
                st.session_state['analyzed'] = True
                
                st.success("✅ Analysis completed successfully!")
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                return
    
    # Display results if available
    if st.session_state.get('analyzed'):
        st.divider()
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏗️ Architecture",
            "🔗 Dependencies",
            "🎯 Coverage",
            "📊 Summary"
        ])
        
        with tab1:
            create_architecture_visualizations(st.session_state['architecture'])
        
        with tab2:
            create_dependency_visualizations(st.session_state['dependencies'])
        
        with tab3:
            create_coverage_visualizations(st.session_state['coverage'])
        
        with tab4:
            st.subheader("📊 Analysis Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🏗️ Architecture")
                arch = st.session_state['architecture']
                st.metric("Files", arch.get('total_files', 0))
                st.metric("Classes", arch.get('total_classes', 0))
                st.metric("Functions", arch.get('total_functions', 0))
                st.metric("Lines of Code", f"{arch.get('total_lines_of_code', 0):,}")
            
            with col2:
                st.markdown("### 🔗 Dependencies")
                deps = st.session_state['dependencies']
                st.metric("Total Dependencies", deps.get('total_dependencies', 0))
                st.metric("External Packages", deps.get('external_packages', 0))
                st.metric("Standard Library", deps.get('standard_library', 0))
            
            with col3:
                st.markdown("### 🎯 Coverage")
                cov = st.session_state['coverage']
                st.metric("Overall Coverage", f"{cov.get('overall_coverage', 0)}%")
                st.metric("Total Tests", cov.get('total_tests', 0))
                st.metric("Tested Modules", cov.get('tested_modules', 0))
            
            st.divider()
            
            # Export options
            st.subheader("📥 Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Generate Documentation", width='stretch'):
                    with st.spinner("Generating documentation..."):
                        try:
                            doc_gen = DocGenerator(repo_path)
                            arch_doc = doc_gen.generate_architecture_docs(st.session_state['architecture'])
                            arch_path = doc_gen.save_documentation("ARCHITECTURE.md", arch_doc)
                            st.success(f"✅ Documentation saved to: {arch_path}")
                        except Exception as e:
                            st.error(f"❌ Failed to generate documentation: {str(e)}")
            
            with col2:
                if st.button("📋 Generate Onboarding Report", width='stretch'):
                    with st.spinner("Generating onboarding report..."):
                        try:
                            repo_path = st.session_state.get('repo_path', Path('.'))
                            onboarding_gen = OnboardingGenerator(repo_path)
                            report = onboarding_gen.generate_onboarding_report(
                                st.session_state['architecture'],
                                st.session_state['dependencies'],
                                st.session_state['coverage'],
                                st.session_state.get('ast_analyses', {})
                            )
                            report_path = onboarding_gen.save_onboarding_report(report)
                            st.success(f"✅ Onboarding report saved to: {report_path}")
                        except Exception as e:
                            st.error(f"❌ Failed to generate report: {str(e)}")
    
    else:
        # Welcome message
        st.info("👈 Enter a repository path in the sidebar and click 'Analyze Repository' to get started!")
        
        # Feature showcase
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🏗️ Architecture Analysis")
            st.markdown("""
            - Deep code analysis using AST
            - Class and function extraction
            - Complexity metrics
            - Module breakdown
            """)
        
        with col2:
            st.markdown("### 🔗 Dependency Mapping")
            st.markdown("""
            - External package detection
            - Version tracking
            - Module dependencies
            - Dependency graphs
            """)
        
        with col3:
            st.markdown("### 🎯 Coverage Analysis")
            st.markdown("""
            - Test coverage metrics
            - Module-level coverage
            - Test recommendations
            - Coverage visualization
            """)


if __name__ == "__main__":
    main()

# Made with Bob