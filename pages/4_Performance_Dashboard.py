"""
Performance Dashboard
====================
Comprehensive dashboard with trend analysis and executive reporting
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.snowflake_connection import execute_query
from utils.visualizations import create_line_chart, create_bar_chart, create_gauge_chart

# Page configuration
st.set_page_config(
    page_title="Performance Dashboard",
    page_icon="📈",
    layout="wide"
)

@st.cache_data(ttl=300)
def load_dashboard_data():
    """Load comprehensive dashboard data"""
    # Generate sample data for demonstration
    return generate_sample_dashboard_data()

def generate_sample_dashboard_data():
    """Generate comprehensive sample data"""
    np.random.seed(42)
    
    # Time series data (last 90 days)
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    
    # Network metrics over time
    network_metrics = pd.DataFrame({
        'DATE': dates,
        'FAILURE_RATE': np.random.beta(2, 50, 90),
        'AVG_SIGNAL_STRENGTH': np.random.normal(-75, 10, 90),
        'ACTIVE_TOWERS': np.random.poisson(185, 90) + 10,
        'DOWNTIME_HOURS': np.random.exponential(2, 90)
    })
    
    # Regional performance
    regions = ['North', 'South', 'East', 'West', 'Central']
    regional_data = pd.DataFrame({
        'REGION': regions,
        'AVG_FAILURE_RATE': np.random.beta(2, 50, 5),
        'TOTAL_TOWERS': np.random.randint(30, 50, 5),
        'AVG_TICKETS': np.random.poisson(300, 5),
        'CUSTOMER_SATISFACTION': np.random.beta(8, 2, 5) * 5
    })
    
    # Tower status distribution
    status_data = pd.DataFrame({
        'STATUS': ['Operational', 'Warning', 'Critical', 'Maintenance'],
        'COUNT': [140, 30, 15, 10]
    })
    
    return {
        'network_metrics': network_metrics,
        'regional_data': regional_data,
        'status_data': status_data
    }

def display_executive_summary(data):
    """Display executive summary with key metrics"""
    st.markdown("### 📊 Executive Summary")
    
    network_metrics = data['network_metrics']
    latest = network_metrics.iloc[-1]
    previous = network_metrics.iloc[-8]  # Week ago
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        current_failure = latest['FAILURE_RATE']
        prev_failure = previous['FAILURE_RATE']
        delta = ((current_failure - prev_failure) / prev_failure * 100) if prev_failure != 0 else 0
        
        st.metric(
            "Network Availability",
            f"{(1 - current_failure) * 100:.2f}%",
            delta=f"{-delta:.1f}%",
            delta_color="normal"
        )
    
    with col2:
        current_towers = latest['ACTIVE_TOWERS']
        prev_towers = previous['ACTIVE_TOWERS']
        
        st.metric(
            "Active Towers",
            f"{int(current_towers)}",
            delta=f"{int(current_towers - prev_towers)}",
            delta_color="normal"
        )
    
    with col3:
        avg_signal = latest['AVG_SIGNAL_STRENGTH']
        prev_signal = previous['AVG_SIGNAL_STRENGTH']
        
        st.metric(
            "Avg Signal Quality",
            f"{avg_signal:.1f} dBm",
            delta=f"{avg_signal - prev_signal:.1f} dBm",
            delta_color="normal"
        )
    
    with col4:
        total_downtime = network_metrics.tail(7)['DOWNTIME_HOURS'].sum()
        prev_downtime = network_metrics.iloc[-14:-7]['DOWNTIME_HOURS'].sum()
        
        st.metric(
            "Weekly Downtime",
            f"{total_downtime:.1f} hrs",
            delta=f"{total_downtime - prev_downtime:.1f} hrs",
            delta_color="inverse"
        )
    
    with col5:
        # Calculate SLA compliance (99.9% target)
        sla_target = 0.999
        current_availability = 1 - current_failure
        sla_compliance = (current_availability / sla_target) * 100
        
        st.metric(
            "SLA Compliance",
            f"{min(sla_compliance, 100):.1f}%",
            delta=f"{sla_compliance - 100:.1f}%" if sla_compliance < 100 else "Target Met ✓"
        )

def display_trend_analysis(data):
    """Display trend analysis charts"""
    st.markdown("### 📈 Performance Trends")
    
    network_metrics = data['network_metrics']
    
    # Create tabs for different metrics
    tab1, tab2, tab3 = st.tabs(["Network Health", "Signal Quality", "Downtime Analysis"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Failure rate over time
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=network_metrics['DATE'],
                y=network_metrics['FAILURE_RATE'] * 100,
                mode='lines',
                name='Failure Rate',
                line=dict(color='#EF4444', width=2),
                fill='tozeroy'
            ))
            
            # Add SLA threshold line
            fig.add_hline(
                y=0.1, line_dash="dash", line_color="green",
                annotation_text="SLA Threshold (0.1%)"
            )
            
            fig.update_layout(
                title='Network Failure Rate Trend',
                xaxis_title='Date',
                yaxis_title='Failure Rate (%)',
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Current health gauge
            current_health = (1 - network_metrics.iloc[-1]['FAILURE_RATE']) * 100
            
            health_gauge = create_gauge_chart(
                value=current_health,
                title="Current Network Health",
                max_value=100,
                threshold_colors=[
                    {'range': [0, 95], 'color': "red"},
                    {'range': [95, 99], 'color': "yellow"},
                    {'range': [99, 100], 'color': "lightgreen"}
                ]
            )
            
            st.plotly_chart(health_gauge, use_container_width=True)
            
            # Statistics
            st.markdown("#### 30-Day Statistics")
            last_30 = network_metrics.tail(30)
            st.metric("Avg Failure Rate", f"{last_30['FAILURE_RATE'].mean():.3%}")
            st.metric("Best Day", f"{last_30['FAILURE_RATE'].min():.3%}")
            st.metric("Worst Day", f"{last_30['FAILURE_RATE'].max():.3%}")
    
    with tab2:
        # Signal strength analysis
        fig = go.Figure()
        
        # Calculate rolling average
        network_metrics['signal_ma'] = network_metrics['AVG_SIGNAL_STRENGTH'].rolling(window=7).mean()
        
        fig.add_trace(go.Scatter(
            x=network_metrics['DATE'],
            y=network_metrics['AVG_SIGNAL_STRENGTH'],
            mode='markers',
            name='Daily Signal',
            marker=dict(color='#3B82F6', size=4, opacity=0.5)
        ))
        
        fig.add_trace(go.Scatter(
            x=network_metrics['DATE'],
            y=network_metrics['signal_ma'],
            mode='lines',
            name='7-Day Average',
            line=dict(color='#1E3A8A', width=3)
        ))
        
        fig.update_layout(
            title='Average Signal Strength Trend',
            xaxis_title='Date',
            yaxis_title='Signal Strength (dBm)',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Cumulative downtime
            network_metrics['cumulative_downtime'] = network_metrics['DOWNTIME_HOURS'].cumsum()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=network_metrics['DATE'],
                y=network_metrics['cumulative_downtime'],
                mode='lines',
                fill='tozeroy',
                name='Cumulative Downtime',
                line=dict(color='#F59E0B')
            ))
            
            fig.update_layout(
                title='Cumulative Network Downtime',
                xaxis_title='Date',
                yaxis_title='Total Hours',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Downtime by day of week
            network_metrics['day_of_week'] = network_metrics['DATE'].dt.day_name()
            dow_downtime = network_metrics.groupby('day_of_week')['DOWNTIME_HOURS'].mean().reindex([
                'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
            ])
            
            fig = go.Figure(go.Bar(
                x=dow_downtime.index,
                y=dow_downtime.values,
                marker_color='#F59E0B'
            ))
            
            fig.update_layout(
                title='Average Downtime by Day of Week',
                xaxis_title='Day',
                yaxis_title='Avg Hours',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)

def display_regional_performance(data):
    """Display regional performance comparison"""
    st.markdown("### 🌍 Regional Performance")
    
    regional_data = data['regional_data']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Regional failure rates
        fig = px.bar(
            regional_data.sort_values('AVG_FAILURE_RATE', ascending=False),
            x='REGION',
            y='AVG_FAILURE_RATE',
            title='Average Failure Rate by Region',
            labels={'AVG_FAILURE_RATE': 'Failure Rate', 'REGION': 'Region'},
            color='AVG_FAILURE_RATE',
            color_continuous_scale='RdYlGn_r'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Customer satisfaction by region
        fig = px.bar(
            regional_data.sort_values('CUSTOMER_SATISFACTION', ascending=False),
            x='REGION',
            y='CUSTOMER_SATISFACTION',
            title='Customer Satisfaction by Region',
            labels={'CUSTOMER_SATISFACTION': 'Satisfaction Score', 'REGION': 'Region'},
            color='CUSTOMER_SATISFACTION',
            color_continuous_scale='RdYlGn'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Regional comparison table
    st.markdown("#### Regional Metrics Summary")
    
    display_regional = regional_data.copy()
    display_regional['AVG_FAILURE_RATE'] = display_regional['AVG_FAILURE_RATE'].apply(lambda x: f"{x:.2%}")
    display_regional['CUSTOMER_SATISFACTION'] = display_regional['CUSTOMER_SATISFACTION'].apply(lambda x: f"{x:.2f}/5.0")
    
    st.dataframe(
        display_regional,
        use_container_width=True,
        hide_index=True,
        column_config={
            "REGION": "Region",
            "AVG_FAILURE_RATE": "Avg Failure Rate",
            "TOTAL_TOWERS": "Total Towers",
            "AVG_TICKETS": "Avg Tickets",
            "CUSTOMER_SATISFACTION": "Satisfaction"
        }
    )

def display_tower_status_distribution(data):
    """Display tower status distribution"""
    st.markdown("### 📡 Tower Status Distribution")
    
    status_data = data['status_data']
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Pie chart
        fig = px.pie(
            status_data,
            values='COUNT',
            names='STATUS',
            title='Tower Status Distribution',
            color='STATUS',
            color_discrete_map={
                'Operational': '#10B981',
                'Warning': '#F59E0B',
                'Critical': '#EF4444',
                'Maintenance': '#6B7280'
            }
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Status table with counts
        total_towers = status_data['COUNT'].sum()
        status_data['PERCENTAGE'] = (status_data['COUNT'] / total_towers * 100).round(1)
        
        st.markdown("#### Status Breakdown")
        
        for _, row in status_data.iterrows():
            status_emoji = {
                'Operational': '🟢',
                'Warning': '🟡',
                'Critical': '🔴',
                'Maintenance': '🔧'
            }.get(row['STATUS'], '⚪')
            
            st.markdown(f"""
            **{status_emoji} {row['STATUS']}**  
            Count: {row['COUNT']} towers ({row['PERCENTAGE']}%)
            """)
            
            st.progress(row['PERCENTAGE'] / 100)

def main():
    st.title("📈 Performance Dashboard")
    st.markdown("Comprehensive network performance metrics and trend analysis")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading dashboard data..."):
        data = load_dashboard_data()
    
    # Date range selector
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("##### Analysis Period")
    
    with col2:
        date_range = st.selectbox(
            "Time Range",
            options=['Last 7 Days', 'Last 30 Days', 'Last 90 Days'],
            index=2
        )
    
    with col3:
        auto_refresh = st.checkbox("Auto-refresh", value=False)
    
    st.markdown("---")
    
    # Executive summary
    display_executive_summary(data)
    
    st.markdown("---")
    
    # Trend analysis
    display_trend_analysis(data)
    
    st.markdown("---")
    
    # Regional performance
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_regional_performance(data)
    
    with col2:
        display_tower_status_distribution(data)
    
    # Export options
    st.markdown("---")
    st.markdown("### 📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Executive Report", use_container_width=True):
            st.info("Executive report export functionality")
    
    with col2:
        if st.button("📈 Export Detailed Metrics", use_container_width=True):
            st.info("Detailed metrics export functionality")
    
    with col3:
        if st.button("📧 Email Report", use_container_width=True):
            st.info("Email report functionality")

if __name__ == "__main__":
    main()

