"""
Data processing utilities for network analytics
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict
import h3

def calculate_failure_severity(failure_rate: float, ticket_count: int) -> str:
    """
    Calculate combined severity based on failure rate and support tickets
    
    Args:
        failure_rate: Cell tower failure rate (0-1)
        ticket_count: Number of support tickets
    
    Returns:
        str: Severity level (Critical, High, Medium, Low)
    """
    severity_score = (failure_rate * 100) + (ticket_count / 10)
    
    if severity_score > 15:
        return "Critical"
    elif severity_score > 10:
        return "High"
    elif severity_score > 5:
        return "Medium"
    else:
        return "Low"

def get_h3_hexagons(lat: float, lon: float, resolution: int = 7) -> List[str]:
    """
    Get H3 hexagon for given coordinates
    
    Args:
        lat: Latitude
        lon: Longitude
        resolution: H3 resolution level (default 7)
    
    Returns:
        List of H3 hexagon IDs
    """
    try:
        hex_id = h3.geo_to_h3(lat, lon, resolution)
        return [hex_id]
    except Exception:
        return []

def aggregate_metrics_by_region(df: pd.DataFrame, lat_col: str = 'LATITUDE', 
                                lon_col: str = 'LONGITUDE') -> pd.DataFrame:
    """
    Aggregate metrics by H3 hexagon regions
    
    Args:
        df: DataFrame with location and metric data
        lat_col: Name of latitude column
        lon_col: Name of longitude column
    
    Returns:
        pd.DataFrame: Aggregated metrics by region
    """
    try:
        # Add H3 hexagon IDs
        df['h3_hex'] = df.apply(
            lambda row: h3.geo_to_h3(row[lat_col], row[lon_col], 7), 
            axis=1
        )
        
        # Aggregate by hexagon
        aggregated = df.groupby('h3_hex').agg({
            'FAILURE_RATE': 'mean',
            'CELL_TOWER_ID': 'count',
            lat_col: 'mean',
            lon_col: 'mean'
        }).reset_index()
        
        aggregated.columns = ['h3_hex', 'avg_failure_rate', 'tower_count', 'latitude', 'longitude']
        
        return aggregated
    except Exception as e:
        print(f"Error in region aggregation: {str(e)}")
        return pd.DataFrame()

def calculate_correlation(df: pd.DataFrame, col1: str, col2: str) -> Tuple[float, float]:
    """
    Calculate Pearson correlation and p-value between two columns
    
    Args:
        df: DataFrame containing the data
        col1: First column name
        col2: Second column name
    
    Returns:
        Tuple of (correlation coefficient, p-value)
    """
    from scipy.stats import pearsonr
    
    try:
        clean_df = df[[col1, col2]].dropna()
        if len(clean_df) < 2:
            return (0.0, 1.0)
        
        corr, pval = pearsonr(clean_df[col1], clean_df[col2])
        return (corr, pval)
    except Exception:
        return (0.0, 1.0)

def get_top_performing_towers(df: pd.DataFrame, metric: str = 'FAILURE_RATE', 
                             top_n: int = 10, ascending: bool = True) -> pd.DataFrame:
    """
    Get top performing (or worst performing) cell towers
    
    Args:
        df: DataFrame with tower metrics
        metric: Metric to sort by
        top_n: Number of towers to return
        ascending: True for best performing, False for worst
    
    Returns:
        pd.DataFrame: Top N towers
    """
    return df.nsmallest(top_n, metric) if ascending else df.nlargest(top_n, metric)

def calculate_moving_average(series: pd.Series, window: int = 7) -> pd.Series:
    """
    Calculate moving average for time series data
    
    Args:
        series: Time series data
        window: Window size for moving average
    
    Returns:
        pd.Series: Smoothed series
    """
    return series.rolling(window=window, min_periods=1).mean()

def detect_anomalies(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    """
    Detect anomalies using z-score method
    
    Args:
        series: Data series
        threshold: Z-score threshold for anomaly detection
    
    Returns:
        pd.Series: Boolean series indicating anomalies
    """
    z_scores = np.abs((series - series.mean()) / series.std())
    return z_scores > threshold

def prepare_heatmap_data(df: pd.DataFrame, metric: str, 
                        lat_col: str = 'LATITUDE', 
                        lon_col: str = 'LONGITUDE') -> pd.DataFrame:
    """
    Prepare data for heatmap visualization
    
    Args:
        df: Source DataFrame
        metric: Metric to visualize
        lat_col: Latitude column name
        lon_col: Longitude column name
    
    Returns:
        pd.DataFrame: Prepared heatmap data
    """
    heatmap_df = df[[lat_col, lon_col, metric]].copy()
    heatmap_df.columns = ['lat', 'lon', 'value']
    heatmap_df = heatmap_df.dropna()
    
    return heatmap_df

def get_severity_color(severity: str) -> str:
    """
    Get color code for severity level
    
    Args:
        severity: Severity level string
    
    Returns:
        str: Hex color code
    """
    color_map = {
        'Critical': '#DC2626',  # Red
        'High': '#F59E0B',      # Orange
        'Medium': '#FCD34D',    # Yellow
        'Low': '#10B981'        # Green
    }
    return color_map.get(severity, '#6B7280')

