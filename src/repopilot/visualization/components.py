"""
Reusable Plotly Visualization Components for RepoPilot
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import networkx as nx


# Color schemes
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff9800',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
}

COLOR_SCALES = {
    'blues': 'Blues',
    'greens': 'Greens',
    'reds': 'Reds',
    'viridis': 'Viridis',
    'plasma': 'Plasma',
    'rdylgn': 'RdYlGn',
}


def create_metric_cards(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Create metric card data for display
    
    Args:
        metrics: Dictionary of metric names and values
        
    Returns:
        List of metric card dictionaries
    """
    cards = []
    for name, value in metrics.items():
        cards.append({
            'name': name,
            'value': value,
            'delta': None  # Can be extended to show changes
        })
    return cards


def create_pie_chart(
    labels: List[str],
    values: List[float],
    title: str = "",
    hole: float = 0.0,
    colors: Optional[List[str]] = None
) -> go.Figure:
    """
    Create an interactive pie chart
    
    Args:
        labels: Category labels
        values: Values for each category
        title: Chart title
        hole: Size of hole for donut chart (0-1)
        colors: Custom color list
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=hole,
        marker_colors=colors,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percent: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=title,
        showlegend=True,
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig


def create_bar_chart(
    x: List[str],
    y: List[float],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    color_scale: str = 'Blues',
    orientation: str = 'v'
) -> go.Figure:
    """
    Create an interactive bar chart
    
    Args:
        x: X-axis values
        y: Y-axis values
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color_scale: Color scale name
        orientation: 'v' for vertical, 'h' for horizontal
        
    Returns:
        Plotly Figure object
    """
    df = pd.DataFrame({'x': x, 'y': y})
    
    if orientation == 'v':
        fig = px.bar(
            df, x='x', y='y',
            title=title,
            labels={'x': x_label, 'y': y_label},
            color='y',
            color_continuous_scale=color_scale
        )
        fig.update_layout(xaxis_tickangle=-45)
    else:
        fig = px.bar(
            df, x='y', y='x',
            title=title,
            labels={'x': y_label, 'y': x_label},
            color='y',
            color_continuous_scale=color_scale,
            orientation='h'
        )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        hovermode='closest'
    )
    
    return fig


def create_horizontal_bar_chart(
    categories: List[str],
    values: List[float],
    title: str = "",
    color: str = COLORS['primary']
) -> go.Figure:
    """
    Create a horizontal bar chart
    
    Args:
        categories: Category names
        values: Values for each category
        title: Chart title
        color: Bar color
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation='h',
        marker_color=color,
        hovertemplate='<b>%{y}</b><br>Value: %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Value",
        yaxis_title="",
        height=max(400, len(categories) * 30),
        margin=dict(l=150)
    )
    
    return fig


def create_scatter_plot(
    x: List[float],
    y: List[float],
    labels: List[str],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    size: Optional[List[float]] = None,
    color: Optional[List[float]] = None
) -> go.Figure:
    """
    Create an interactive scatter plot
    
    Args:
        x: X-axis values
        y: Y-axis values
        labels: Point labels
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        size: Point sizes
        color: Point colors
        
    Returns:
        Plotly Figure object
    """
    df = pd.DataFrame({
        'x': x,
        'y': y,
        'label': labels,
        'size': size if size else [10] * len(x),
        'color': color if color else y
    })
    
    fig = px.scatter(
        df, x='x', y='y',
        size='size',
        color='color',
        hover_data=['label'],
        title=title,
        labels={'x': x_label, 'y': y_label}
    )
    
    fig.update_layout(
        height=500,
        hovermode='closest'
    )
    
    return fig


def create_gauge_chart(
    value: float,
    title: str = "",
    max_value: float = 100,
    threshold: float = 80,
    reference: float = 80
) -> go.Figure:
    """
    Create a gauge chart
    
    Args:
        value: Current value
        title: Chart title
        max_value: Maximum value on gauge
        threshold: Threshold line value
        reference: Reference value for delta
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        delta={'reference': reference, 'increasing': {'color': COLORS['success']}},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1},
            'bar': {'color': COLORS['primary']},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_value * 0.5], 'color': '#ffebee'},
                {'range': [max_value * 0.5, max_value * 0.8], 'color': '#fff9c4'}
            ],
            'threshold': {
                'line': {'color': COLORS['danger'], 'width': 4},
                'thickness': 0.75,
                'value': threshold
            }
        }
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig


def create_network_graph(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    title: str = "",
    circular_deps: Optional[List[List[str]]] = None
) -> go.Figure:
    """
    Create an interactive network graph
    
    Args:
        nodes: List of node dictionaries with 'id' and 'label'
        edges: List of edge dictionaries with 'source' and 'target'
        title: Chart title
        circular_deps: List of circular dependency paths
        
    Returns:
        Plotly Figure object
    """
    # Create NetworkX graph
    G = nx.DiGraph()
    
    # Add nodes
    for node in nodes:
        G.add_node(node['id'], label=node.get('label', node['id']))
    
    # Add edges
    for edge in edges:
        G.add_edge(edge['source'], edge['target'])
    
    # Calculate layout
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Create edge traces
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    
    # Create node traces
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=20,
            color=[],
            colorbar=dict(
                thickness=15,
                title=dict(text='Node Connections', side='right'),
                xanchor='left'
            ),
            line=dict(width=2, color='white')
        ),
        textposition="top center"
    )
    
    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([G.nodes[node].get('label', node)])
        node_trace['marker']['color'] += tuple([len(list(G.neighbors(node)))])
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title=title,
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20, l=5, r=5, t=40),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=600
                   ))
    
    # Add annotation for circular dependencies
    if circular_deps:
        fig.add_annotation(
            text=f"⚠️ {len(circular_deps)} circular dependencies detected",
            xref="paper", yref="paper",
            x=0.5, y=1.05,
            showarrow=False,
            font=dict(size=14, color=COLORS['danger']),
            bgcolor="rgba(255, 0, 0, 0.1)",
            bordercolor=COLORS['danger'],
            borderwidth=2
        )
    
    return fig


def create_sunburst_chart(
    labels: List[str],
    parents: List[str],
    values: List[float],
    title: str = ""
) -> go.Figure:
    """
    Create a sunburst chart for hierarchical data
    
    Args:
        labels: Node labels
        parents: Parent node for each label
        values: Values for each node
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percent: %{percentParent}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        height=600,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig


def create_treemap_chart(
    labels: List[str],
    parents: List[str],
    values: List[float],
    title: str = ""
) -> go.Figure:
    """
    Create a treemap chart for hierarchical data
    
    Args:
        labels: Node labels
        parents: Parent node for each label
        values: Values for each node
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        textinfo="label+value+percent parent",
        hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percent: %{percentParent}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        height=600,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig


def create_heatmap(
    z: List[List[float]],
    x: List[str],
    y: List[str],
    title: str = "",
    color_scale: str = 'RdYlGn'
) -> go.Figure:
    """
    Create a heatmap
    
    Args:
        z: 2D array of values
        x: X-axis labels
        y: Y-axis labels
        title: Chart title
        color_scale: Color scale name
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=x,
        y=y,
        colorscale=color_scale,
        hovertemplate='X: %{x}<br>Y: %{y}<br>Value: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        height=500,
        xaxis_title="",
        yaxis_title=""
    )
    
    return fig


def create_line_chart(
    x: List[Any],
    y: List[float],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    line_color: str = COLORS['primary']
) -> go.Figure:
    """
    Create a line chart
    
    Args:
        x: X-axis values
        y: Y-axis values
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        line_color: Line color
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure(go.Scatter(
        x=x,
        y=y,
        mode='lines+markers',
        line=dict(color=line_color, width=3),
        marker=dict(size=8),
        hovertemplate='%{x}<br>Value: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=400,
        hovermode='x unified'
    )
    
    return fig


def detect_circular_dependencies(dependencies: List[Dict[str, str]]) -> List[List[str]]:
    """
    Detect circular dependencies in a dependency graph
    
    Args:
        dependencies: List of dependency dictionaries with 'source' and 'target'
        
    Returns:
        List of circular dependency paths
    """
    # Build graph
    G = nx.DiGraph()
    for dep in dependencies:
        G.add_edge(dep['source'], dep['target'])
    
    # Find cycles
    try:
        cycles = list(nx.simple_cycles(G))
        return cycles
    except:
        return []

# Made with Bob
