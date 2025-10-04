"""
Visualization utilities for network analytics
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import pydeck as pdk
from typing import Optional, List

def create_scatter_map(df: pd.DataFrame, lat_col: str = 'LATITUDE', 
                      lon_col: str = 'LONGITUDE', color_col: str = 'FAILURE_RATE',
                      size_col: Optional[str] = None, hover_data: Optional[List[str]] = None,
                      title: str = "Cell Tower Map") -> go.Figure:
    """
    Create interactive scatter map using Plotly
    
    Args:
        df: DataFrame with location data
        lat_col: Latitude column name
        lon_col: Longitude column name
        color_col: Column to color by
        size_col: Column to size markers by
        hover_data: Additional columns to show on hover
        title: Map title
    
    Returns:
        go.Figure: Plotly figure object
    """
    fig = px.scatter_mapbox(
        df,
        lat=lat_col,
        lon=lon_col,
        color=color_col,
        size=size_col if size_col else None,
        hover_data=hover_data,
        title=title,
        zoom=10,
        height=600,
        color_continuous_scale="RdYlGn_r"
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )
    
    return fig

def create_heatmap_layer(df: pd.DataFrame, lat_col: str = 'LATITUDE',
                        lon_col: str = 'LONGITUDE', weight_col: str = 'FAILURE_RATE',
                        zoom: int = 10) -> pdk.Deck:
    """
    Create heatmap layer using PyDeck
    
    Args:
        df: DataFrame with location and weight data
        lat_col: Latitude column name
        lon_col: Longitude column name
        weight_col: Column to use as heatmap weight
        zoom: Initial zoom level
    
    Returns:
        pdk.Deck: PyDeck deck object
    """
    # Normalize weights to 0-1 range
    df_copy = df.copy()
    if weight_col in df_copy.columns:
        max_weight = df_copy[weight_col].max()
        if max_weight > 0:
            df_copy['weight'] = df_copy[weight_col] / max_weight
        else:
            df_copy['weight'] = 0
    else:
        df_copy['weight'] = 1
    
    # Calculate center point
    center_lat = df_copy[lat_col].mean()
    center_lon = df_copy[lon_col].mean()
    
    # Create heatmap layer
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data=df_copy,
        get_position=f"[{lon_col}, {lat_col}]",
        get_weight="weight",
        radiusPixels=60,
        intensity=1,
        threshold=0.05,
        pickable=True
    )
    
    # Create deck
    deck = pdk.Deck(
        layers=[heatmap_layer],
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=zoom,
            pitch=0
        ),
        tooltip={"text": f"{weight_col}: {{weight}}"}
    )
    
    return deck

def create_scatter_plot(df: pd.DataFrame, x_col: str, y_col: str,
                       color_col: Optional[str] = None,
                       title: str = "Scatter Plot",
                       trendline: bool = True) -> go.Figure:
    """
    Create scatter plot with optional trendline
    
    Args:
        df: DataFrame with data
        x_col: X-axis column
        y_col: Y-axis column
        color_col: Optional color grouping column
        title: Plot title
        trendline: Whether to add trendline
    
    Returns:
        go.Figure: Plotly figure object
    """
    if trendline:
        fig = px.scatter(
            df, x=x_col, y=y_col, color=color_col,
            title=title, trendline="ols",
            labels={x_col: x_col.replace('_', ' ').title(),
                   y_col: y_col.replace('_', ' ').title()}
        )
    else:
        fig = px.scatter(
            df, x=x_col, y=y_col, color=color_col,
            title=title,
            labels={x_col: x_col.replace('_', ' ').title(),
                   y_col: y_col.replace('_', ' ').title()}
        )
    
    fig.update_layout(
        height=500,
        hovermode='closest'
    )
    
    return fig

def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str,
                    title: str = "Bar Chart", orientation: str = 'v',
                    color_col: Optional[str] = None) -> go.Figure:
    """
    Create bar chart
    
    Args:
        df: DataFrame with data
        x_col: X-axis column
        y_col: Y-axis column
        title: Chart title
        orientation: 'v' for vertical, 'h' for horizontal
        color_col: Optional color column
    
    Returns:
        go.Figure: Plotly figure object
    """
    fig = px.bar(
        df, x=x_col, y=y_col, color=color_col,
        title=title, orientation=orientation,
        labels={x_col: x_col.replace('_', ' ').title(),
               y_col: y_col.replace('_', ' ').title()}
    )
    
    fig.update_layout(
        height=400,
        xaxis_tickangle=-45 if orientation == 'v' else 0
    )
    
    return fig

def create_line_chart(df: pd.DataFrame, x_col: str, y_cols: List[str],
                     title: str = "Time Series", smooth: bool = False) -> go.Figure:
    """
    Create line chart for time series data
    
    Args:
        df: DataFrame with time series data
        x_col: X-axis (time) column
        y_cols: List of Y-axis columns
        title: Chart title
        smooth: Whether to apply smoothing
    
    Returns:
        go.Figure: Plotly figure object
    """
    fig = go.Figure()
    
    for col in y_cols:
        if smooth:
            y_data = df[col].rolling(window=7, min_periods=1).mean()
        else:
            y_data = df[col]
        
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=y_data,
            mode='lines+markers',
            name=col.replace('_', ' ').title()
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title="Value",
        height=500,
        hovermode='x unified'
    )
    
    return fig

def create_gauge_chart(value: float, title: str, max_value: float = 100,
                      threshold_colors: Optional[List[dict]] = None) -> go.Figure:
    """
    Create gauge chart for single metric
    
    Args:
        value: Current value
        title: Chart title
        max_value: Maximum value for gauge
        threshold_colors: List of threshold color definitions
    
    Returns:
        go.Figure: Plotly figure object
    """
    if threshold_colors is None:
        threshold_colors = [
            {'range': [0, 33], 'color': "lightgreen"},
            {'range': [33, 66], 'color': "yellow"},
            {'range': [66, 100], 'color': "red"}
        ]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title},
        delta={'reference': max_value * 0.7},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': "darkblue"},
            'steps': threshold_colors,
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    return fig

