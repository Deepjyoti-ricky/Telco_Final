"""
Cell Tower Lookup Page
======================
Interactive map interface for examining individual cell tower performance metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
from datetime import datetime, timedelta
from utils.snowflake_connection import get_snowflake_connection, execute_query
from utils.visualizations import create_scatter_map, create_gauge_chart
from utils.data_processing import calculate_failure_severity

# Page configuration
st.set_page_config(
    page_title="Cell Tower Lookup",
    page_icon="🗺️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .tower-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.875rem;
    }
    .status-operational {
        background: #DEF7EC;
        color: #03543F;
    }
    .status-warning {
        background: #FEF3C7;
        color: #92400E;
    }
    .status-critical {
        background: #FEE2E2;
        color: #991B1B;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_cell_tower_data():
    """Load cell tower data from Snowflake"""
    query = """
    SELECT 
        CELL_TOWER_ID,
        LATITUDE,
        LONGITUDE,
        FAILURE_RATE,
        LAST_MAINTENANCE_DATE,
        SIGNAL_STRENGTH,
        COVERAGE_RADIUS,
        STATUS,
        REGION
    FROM CELL_TOWERS
    ORDER BY FAILURE_RATE DESC
    """
    
    try:
        df = execute_query(query)
        if df is not None and not df.empty:
            # Add severity calculation
            df['SEVERITY'] = df.apply(
                lambda row: calculate_failure_severity(row['FAILURE_RATE'], 0),
                axis=1
            )
            return df
        else:
            # Return sample data if database is not available
            return generate_sample_data()
    except Exception as e:
        st.warning(f"Using sample data: {str(e)}")
        return generate_sample_data()

def generate_sample_data():
    """Generate sample cell tower data for demonstration"""
    import numpy as np
    
    n_towers = 150
    
    # Center around a sample location (e.g., San Francisco)
    center_lat, center_lon = 37.7749, -122.4194
    
    data = {
        'CELL_TOWER_ID': [f'CT-{i:04d}' for i in range(1, n_towers + 1)],
        'LATITUDE': np.random.normal(center_lat, 0.1, n_towers),
        'LONGITUDE': np.random.normal(center_lon, 0.1, n_towers),
        'FAILURE_RATE': np.random.beta(2, 50, n_towers),
        'LAST_MAINTENANCE_DATE': [
            datetime.now() - timedelta(days=int(x)) 
            for x in np.random.exponential(30, n_towers)
        ],
        'SIGNAL_STRENGTH': np.random.uniform(-100, -50, n_towers),
        'COVERAGE_RADIUS': np.random.uniform(0.5, 3.0, n_towers),
        'STATUS': np.random.choice(['Operational', 'Warning', 'Critical'], n_towers, p=[0.7, 0.2, 0.1]),
        'REGION': np.random.choice(['North', 'South', 'East', 'West'], n_towers)
    }
    
    df = pd.DataFrame(data)
    df['SEVERITY'] = df.apply(
        lambda row: calculate_failure_severity(row['FAILURE_RATE'], 0),
        axis=1
    )
    
    return df

def display_tower_details(tower_data):
    """Display detailed information for selected tower"""
    st.markdown("### 📡 Tower Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tower ID", tower_data['CELL_TOWER_ID'])
        st.metric("Region", tower_data['REGION'])
    
    with col2:
        status = tower_data['STATUS']
        status_class = {
            'Operational': 'operational',
            'Warning': 'warning',
            'Critical': 'critical'
        }.get(status, 'operational')
        
        st.markdown(f"""
        **Status**  
        <span class="status-badge status-{status_class}">{status}</span>
        """, unsafe_allow_html=True)
        
        st.metric("Failure Rate", f"{tower_data['FAILURE_RATE']:.2%}")
    
    with col3:
        st.metric("Signal Strength", f"{tower_data['SIGNAL_STRENGTH']:.1f} dBm")
        st.metric("Coverage Radius", f"{tower_data['COVERAGE_RADIUS']:.2f} km")
    
    st.markdown("---")
    
    # Performance metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Failure rate gauge
        failure_gauge = create_gauge_chart(
            value=tower_data['FAILURE_RATE'] * 100,
            title="Failure Rate (%)",
            max_value=10,
            threshold_colors=[
                {'range': [0, 3], 'color': "lightgreen"},
                {'range': [3, 5], 'color': "yellow"},
                {'range': [5, 10], 'color': "red"}
            ]
        )
        st.plotly_chart(failure_gauge, use_container_width=True)
    
    with col2:
        # Signal strength gauge
        signal_normalized = (tower_data['SIGNAL_STRENGTH'] + 100) * 2  # Normalize to 0-100
        signal_gauge = create_gauge_chart(
            value=signal_normalized,
            title="Signal Strength",
            max_value=100,
            threshold_colors=[
                {'range': [0, 33], 'color': "red"},
                {'range': [33, 66], 'color': "yellow"},
                {'range': [66, 100], 'color': "lightgreen"}
            ]
        )
        st.plotly_chart(signal_gauge, use_container_width=True)
    
    # Maintenance information
    st.markdown("### 🔧 Maintenance Information")
    days_since_maintenance = (datetime.now() - tower_data['LAST_MAINTENANCE_DATE']).days
    
    if days_since_maintenance > 60:
        st.warning(f"⚠️ Last maintenance was **{days_since_maintenance} days ago**. Maintenance recommended.")
    else:
        st.info(f"✅ Last maintenance was **{days_since_maintenance} days ago**.")
    
    st.caption(f"Last Maintenance Date: {tower_data['LAST_MAINTENANCE_DATE'].strftime('%B %d, %Y')}")

def display_tower_map(df, selected_tower_id=None):
    """Display interactive map of cell towers"""
    st.markdown("### 🗺️ Cell Tower Map")
    
    # Color mapping based on status
    color_map = {
        'Operational': [0, 255, 0, 160],
        'Warning': [255, 165, 0, 160],
        'Critical': [255, 0, 0, 160]
    }
    
    df['color'] = df['STATUS'].map(color_map)
    
    # Highlight selected tower
    if selected_tower_id:
        df['elevation'] = df['CELL_TOWER_ID'].apply(
            lambda x: 1000 if x == selected_tower_id else 0
        )
    else:
        df['elevation'] = 0
    
    # Calculate center
    center_lat = df['LATITUDE'].mean()
    center_lon = df['LONGITUDE'].mean()
    
    # Create PyDeck layers
    scatter_layer = pdk.Layer(
        'ScatterplotLayer',
        data=df,
        get_position='[LONGITUDE, LATITUDE]',
        get_color='color',
        get_radius='COVERAGE_RADIUS * 500',
        pickable=True,
        auto_highlight=True,
        elevation_scale=1,
        get_elevation='elevation'
    )
    
    # Create deck
    deck = pdk.Deck(
        layers=[scatter_layer],
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=40
        ),
        tooltip={
            "html": "<b>Tower:</b> {CELL_TOWER_ID}<br/>"
                   "<b>Status:</b> {STATUS}<br/>"
                   "<b>Failure Rate:</b> {FAILURE_RATE:.2%}<br/>"
                   "<b>Signal:</b> {SIGNAL_STRENGTH:.1f} dBm",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }
    )
    
    st.pydeck_chart(deck)

def display_statistics(df):
    """Display overall statistics"""
    st.markdown("### 📊 Network Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Towers", len(df))
    
    with col2:
        avg_failure = df['FAILURE_RATE'].mean()
        st.metric("Avg Failure Rate", f"{avg_failure:.2%}")
    
    with col3:
        critical_count = len(df[df['STATUS'] == 'Critical'])
        st.metric("Critical Towers", critical_count)
    
    with col4:
        avg_signal = df['SIGNAL_STRENGTH'].mean()
        st.metric("Avg Signal Strength", f"{avg_signal:.1f} dBm")

def main():
    st.title("🗺️ Cell Tower Lookup")
    st.markdown("Explore individual cell tower performance metrics and real-time status")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading cell tower data..."):
        df = load_cell_tower_data()
    
    if df is None or df.empty:
        st.error("No cell tower data available.")
        return
    
    # Display statistics
    display_statistics(df)
    st.markdown("---")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter Options")
    
    # Region filter
    regions = ['All'] + sorted(df['REGION'].unique().tolist())
    selected_region = st.sidebar.selectbox("Region", regions)
    
    # Status filter
    statuses = ['All'] + sorted(df['STATUS'].unique().tolist())
    selected_status = st.sidebar.selectbox("Status", statuses)
    
    # Failure rate filter
    max_failure_rate = st.sidebar.slider(
        "Max Failure Rate (%)",
        0.0, 100.0, 100.0, 0.5
    )
    
    # Apply filters
    filtered_df = df.copy()
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['REGION'] == selected_region]
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['STATUS'] == selected_status]
    filtered_df = filtered_df[filtered_df['FAILURE_RATE'] <= max_failure_rate / 100]
    
    st.sidebar.markdown(f"**Showing {len(filtered_df)} of {len(df)} towers**")
    
    # Tower selection
    st.sidebar.markdown("---")
    st.sidebar.header("🎯 Select Tower")
    tower_ids = filtered_df['CELL_TOWER_ID'].tolist()
    selected_tower = st.sidebar.selectbox("Tower ID", tower_ids)
    
    # Main content layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_tower_map(filtered_df, selected_tower)
    
    with col2:
        if selected_tower:
            tower_data = filtered_df[filtered_df['CELL_TOWER_ID'] == selected_tower].iloc[0]
            display_tower_details(tower_data)
    
    # Data table
    st.markdown("---")
    st.markdown("### 📋 Tower Data Table")
    
    # Format the dataframe for display
    display_df = filtered_df[[
        'CELL_TOWER_ID', 'REGION', 'STATUS', 'FAILURE_RATE',
        'SIGNAL_STRENGTH', 'COVERAGE_RADIUS', 'SEVERITY'
    ]].copy()
    
    display_df['FAILURE_RATE'] = display_df['FAILURE_RATE'].apply(lambda x: f"{x:.2%}")
    display_df['SIGNAL_STRENGTH'] = display_df['SIGNAL_STRENGTH'].apply(lambda x: f"{x:.1f} dBm")
    display_df['COVERAGE_RADIUS'] = display_df['COVERAGE_RADIUS'].apply(lambda x: f"{x:.2f} km")
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

if __name__ == "__main__":
    main()

