"""
Geospatial Analysis Page
========================
Advanced heatmap overlays and correlation analysis for network performance
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
from datetime import datetime, timedelta
from utils.snowflake_connection import execute_query
from utils.data_processing import calculate_correlation, aggregate_metrics_by_region
from utils.visualizations import create_scatter_plot, create_bar_chart

# Page configuration
st.set_page_config(
    page_title="Geospatial Analysis",
    page_icon="🔥",
    layout="wide"
)

@st.cache_data(ttl=300)
def load_geospatial_data():
    """Load combined cell tower and support ticket data"""
    query = """
    SELECT 
        ct.CELL_TOWER_ID,
        ct.LATITUDE,
        ct.LONGITUDE,
        ct.FAILURE_RATE,
        ct.REGION,
        ct.STATUS,
        COUNT(st.TICKET_ID) as TICKET_COUNT,
        AVG(st.SENTIMENT_SCORE) as AVG_SENTIMENT
    FROM CELL_TOWERS ct
    LEFT JOIN SUPPORT_TICKETS st ON ct.CELL_TOWER_ID = st.CELL_TOWER_ID
    WHERE st.TICKET_DATE >= DATEADD(day, -30, CURRENT_DATE())
    GROUP BY ct.CELL_TOWER_ID, ct.LATITUDE, ct.LONGITUDE, ct.FAILURE_RATE, ct.REGION, ct.STATUS
    """
    
    try:
        df = execute_query(query)
        if df is not None and not df.empty:
            return df
        else:
            return generate_sample_geospatial_data()
    except Exception:
        return generate_sample_geospatial_data()

def generate_sample_geospatial_data():
    """Generate sample geospatial data"""
    np.random.seed(42)
    n_towers = 200
    
    center_lat, center_lon = 37.7749, -122.4194
    
    data = {
        'CELL_TOWER_ID': [f'CT-{i:04d}' for i in range(1, n_towers + 1)],
        'LATITUDE': np.random.normal(center_lat, 0.15, n_towers),
        'LONGITUDE': np.random.normal(center_lon, 0.15, n_towers),
        'FAILURE_RATE': np.random.beta(2, 50, n_towers),
        'REGION': np.random.choice(['North', 'South', 'East', 'West', 'Central'], n_towers),
        'STATUS': np.random.choice(['Operational', 'Warning', 'Critical'], n_towers, p=[0.7, 0.2, 0.1]),
        'TICKET_COUNT': np.random.poisson(15, n_towers),
        'AVG_SENTIMENT': np.random.beta(2, 2, n_towers) * 3 + 1  # 1-4 scale
    }
    
    df = pd.DataFrame(data)
    
    # Create correlation between failure rate and tickets
    df['TICKET_COUNT'] = (df['TICKET_COUNT'] + df['FAILURE_RATE'] * 100).astype(int)
    
    return df

def create_heatmap(df, metric='FAILURE_RATE', title='Heatmap'):
    """Create heatmap visualization"""
    center_lat = df['LATITUDE'].mean()
    center_lon = df['LONGITUDE'].mean()
    
    # Normalize metric for heatmap intensity
    df_copy = df.copy()
    max_val = df[metric].max()
    if max_val > 0:
        df_copy['weight'] = df[metric] / max_val
    else:
        df_copy['weight'] = 0
    
    # Create heatmap layer
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data=df_copy,
        get_position="[LONGITUDE, LATITUDE]",
        get_weight="weight",
        radiusPixels=50,
        intensity=2,
        threshold=0.03,
    )
    
    # Create scatter layer for reference
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_copy,
        get_position="[LONGITUDE, LATITUDE]",
        get_radius=200,
        get_fill_color=[255, 255, 255, 100],
        pickable=True,
    )
    
    # Create deck
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=0
    )
    
    deck = pdk.Deck(
        layers=[heatmap_layer, scatter_layer],
        initial_view_state=view_state,
        tooltip={
            "html": f"<b>Tower:</b> {{CELL_TOWER_ID}}<br/><b>{metric}:</b> {{{metric}}}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }
    )
    
    return deck

def display_correlation_analysis(df):
    """Display correlation analysis between metrics"""
    st.markdown("### 📈 Correlation Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Failure Rate vs Ticket Count
        corr1, pval1 = calculate_correlation(df, 'FAILURE_RATE', 'TICKET_COUNT')
        
        fig1 = create_scatter_plot(
            df,
            x_col='FAILURE_RATE',
            y_col='TICKET_COUNT',
            title=f'Failure Rate vs Support Tickets (r={corr1:.3f}, p={pval1:.3f})',
            trendline=True
        )
        
        fig1.update_xaxes(title="Failure Rate")
        fig1.update_yaxes(title="Support Ticket Count")
        
        st.plotly_chart(fig1, use_container_width=True)
        
        if pval1 < 0.05:
            st.success(f"✅ **Significant correlation** found (r={corr1:.3f})")
        else:
            st.info(f"ℹ️ No significant correlation (r={corr1:.3f})")
    
    with col2:
        # Failure Rate vs Sentiment
        corr2, pval2 = calculate_correlation(df, 'FAILURE_RATE', 'AVG_SENTIMENT')
        
        fig2 = create_scatter_plot(
            df,
            x_col='FAILURE_RATE',
            y_col='AVG_SENTIMENT',
            title=f'Failure Rate vs Customer Sentiment (r={corr2:.3f}, p={pval2:.3f})',
            trendline=True
        )
        
        fig2.update_xaxes(title="Failure Rate")
        fig2.update_yaxes(title="Average Sentiment Score")
        
        st.plotly_chart(fig2, use_container_width=True)
        
        if pval2 < 0.05:
            st.success(f"✅ **Significant correlation** found (r={corr2:.3f})")
        else:
            st.info(f"ℹ️ No significant correlation (r={corr2:.3f})")

def display_top_problematic_areas(df):
    """Display top problematic areas"""
    st.markdown("### ⚠️ Priority Areas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Worst Performing Towers")
        
        # Calculate combined severity score
        df['severity_score'] = (
            df['FAILURE_RATE'] * 100 +
            df['TICKET_COUNT'] / 10 +
            (5 - df['AVG_SENTIMENT'])
        )
        
        top_worst = df.nlargest(10, 'severity_score')[[
            'CELL_TOWER_ID', 'REGION', 'FAILURE_RATE', 'TICKET_COUNT', 'AVG_SENTIMENT'
        ]].copy()
        
        top_worst['FAILURE_RATE'] = top_worst['FAILURE_RATE'].apply(lambda x: f"{x:.2%}")
        top_worst['AVG_SENTIMENT'] = top_worst['AVG_SENTIMENT'].apply(lambda x: f"{x:.2f}")
        
        st.dataframe(top_worst, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### Highest Ticket Volume by Region")
        
        region_tickets = df.groupby('REGION').agg({
            'TICKET_COUNT': 'sum',
            'FAILURE_RATE': 'mean',
            'CELL_TOWER_ID': 'count'
        }).reset_index()
        
        region_tickets.columns = ['REGION', 'TOTAL_TICKETS', 'AVG_FAILURE_RATE', 'TOWER_COUNT']
        region_tickets = region_tickets.sort_values('TOTAL_TICKETS', ascending=False)
        
        region_tickets['AVG_FAILURE_RATE'] = region_tickets['AVG_FAILURE_RATE'].apply(lambda x: f"{x:.2%}")
        
        st.dataframe(region_tickets, use_container_width=True, hide_index=True)
        
        # Bar chart
        fig = create_bar_chart(
            region_tickets,
            x_col='REGION',
            y_col='TOTAL_TICKETS',
            title='Total Support Tickets by Region'
        )
        st.plotly_chart(fig, use_container_width=True)

def display_regional_comparison(df):
    """Display regional comparison metrics"""
    st.markdown("### 🌍 Regional Performance Comparison")
    
    regional_stats = df.groupby('REGION').agg({
        'FAILURE_RATE': ['mean', 'std'],
        'TICKET_COUNT': ['sum', 'mean'],
        'AVG_SENTIMENT': 'mean',
        'CELL_TOWER_ID': 'count'
    }).reset_index()
    
    regional_stats.columns = [
        'REGION', 'AVG_FAILURE_RATE', 'STD_FAILURE_RATE',
        'TOTAL_TICKETS', 'AVG_TICKETS', 'AVG_SENTIMENT', 'TOWER_COUNT'
    ]
    
    # Create grouped bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Avg Failure Rate (%)',
        x=regional_stats['REGION'],
        y=regional_stats['AVG_FAILURE_RATE'] * 100,
        marker_color='indianred'
    ))
    
    fig.add_trace(go.Bar(
        name='Avg Tickets per Tower',
        x=regional_stats['REGION'],
        y=regional_stats['AVG_TICKETS'],
        marker_color='lightsalmon'
    ))
    
    fig.update_layout(
        title='Regional Performance Metrics',
        barmode='group',
        height=400,
        xaxis_title='Region',
        yaxis_title='Value'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display table
    display_regional = regional_stats.copy()
    display_regional['AVG_FAILURE_RATE'] = display_regional['AVG_FAILURE_RATE'].apply(lambda x: f"{x:.2%}")
    display_regional['STD_FAILURE_RATE'] = display_regional['STD_FAILURE_RATE'].apply(lambda x: f"{x:.2%}")
    display_regional['AVG_TICKETS'] = display_regional['AVG_TICKETS'].apply(lambda x: f"{x:.1f}")
    display_regional['AVG_SENTIMENT'] = display_regional['AVG_SENTIMENT'].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(display_regional, use_container_width=True, hide_index=True)

def main():
    st.title("🔥 Geospatial Analysis & Heatmaps")
    st.markdown("Visualize network performance patterns and customer impact across regions")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading geospatial data..."):
        df = load_geospatial_data()
    
    if df is None or df.empty:
        st.error("No geospatial data available.")
        return
    
    # Sidebar controls
    st.sidebar.header("🎛️ Heatmap Controls")
    
    heatmap_metric = st.sidebar.selectbox(
        "Select Metric to Visualize",
        options=[
            ('FAILURE_RATE', 'Cell Tower Failure Rate'),
            ('TICKET_COUNT', 'Support Ticket Density'),
            ('AVG_SENTIMENT', 'Customer Sentiment')
        ],
        format_func=lambda x: x[1]
    )[0]
    
    # Display heatmap
    st.markdown(f"### 🗺️ Heatmap: {heatmap_metric.replace('_', ' ').title()}")
    
    deck = create_heatmap(df, metric=heatmap_metric, title=heatmap_metric)
    st.pydeck_chart(deck)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Towers Analyzed", len(df))
    
    with col2:
        st.metric("Total Support Tickets", int(df['TICKET_COUNT'].sum()))
    
    with col3:
        st.metric("Avg Failure Rate", f"{df['FAILURE_RATE'].mean():.2%}")
    
    with col4:
        st.metric("Avg Sentiment Score", f"{df['AVG_SENTIMENT'].mean():.2f}/5.0")
    
    st.markdown("---")
    
    # Correlation analysis
    display_correlation_analysis(df)
    
    st.markdown("---")
    
    # Top problematic areas
    display_top_problematic_areas(df)
    
    st.markdown("---")
    
    # Regional comparison
    display_regional_comparison(df)

if __name__ == "__main__":
    main()

