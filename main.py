"""
Telco Network Optimization Suite
==================================
A comprehensive Streamlit application for analyzing cell tower performance,
customer support data, and network optimization using AI-powered insights.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from utils.snowflake_connection import get_snowflake_connection

# Page configuration
st.set_page_config(
    page_title="Telco Network Optimization Suite",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
        background: linear-gradient(90deg, #3B82F6 0%, #1E3A8A 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #E5E7EB;
        transition: transform 0.2s;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        border-color: #3B82F6;
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #3B82F6 0%, #1E3A8A 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

def display_header():
    """Display the main header section"""
    st.markdown('<h1 class="main-header">📡 Telco Network Optimization Suite</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Advanced Analytics for Network Performance & Customer Intelligence</p>', unsafe_allow_html=True)
    st.markdown("---")

def fetch_dashboard_metrics():
    """Fetch key metrics for the dashboard"""
    try:
        conn = get_snowflake_connection()
        
        # Fetch cell tower metrics
        tower_query = """
        SELECT 
            COUNT(DISTINCT CELL_TOWER_ID) as total_towers,
            AVG(FAILURE_RATE) as avg_failure_rate,
            SUM(CASE WHEN FAILURE_RATE > 0.05 THEN 1 ELSE 0 END) as high_risk_towers
        FROM CELL_TOWERS
        """
        tower_metrics = conn.cursor().execute(tower_query).fetch_pandas_all()
        
        # Fetch support ticket metrics
        ticket_query = """
        SELECT 
            COUNT(*) as total_tickets,
            AVG(SENTIMENT_SCORE) as avg_sentiment,
            COUNT(CASE WHEN STATUS = 'OPEN' THEN 1 END) as open_tickets
        FROM SUPPORT_TICKETS
        WHERE TICKET_DATE >= DATEADD(day, -30, CURRENT_DATE())
        """
        ticket_metrics = conn.cursor().execute(ticket_query).fetch_pandas_all()
        
        conn.close()
        
        return {
            'total_towers': int(tower_metrics['TOTAL_TOWERS'].iloc[0]) if not tower_metrics.empty else 0,
            'avg_failure_rate': float(tower_metrics['AVG_FAILURE_RATE'].iloc[0]) if not tower_metrics.empty else 0.0,
            'high_risk_towers': int(tower_metrics['HIGH_RISK_TOWERS'].iloc[0]) if not tower_metrics.empty else 0,
            'total_tickets': int(ticket_metrics['TOTAL_TICKETS'].iloc[0]) if not ticket_metrics.empty else 0,
            'avg_sentiment': float(ticket_metrics['AVG_SENTIMENT'].iloc[0]) if not ticket_metrics.empty else 0.0,
            'open_tickets': int(ticket_metrics['OPEN_TICKETS'].iloc[0]) if not ticket_metrics.empty else 0
        }
    except Exception as e:
        st.warning(f"Unable to fetch metrics: {str(e)}")
        return {
            'total_towers': 0,
            'avg_failure_rate': 0.0,
            'high_risk_towers': 0,
            'total_tickets': 0,
            'avg_sentiment': 0.0,
            'open_tickets': 0
        }

def display_kpi_metrics(metrics):
    """Display key performance indicators"""
    st.subheader("📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Cell Towers",
            value=f"{metrics['total_towers']:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Average Failure Rate",
            value=f"{metrics['avg_failure_rate']:.2%}",
            delta=f"{-0.5:.1%}" if metrics['avg_failure_rate'] < 0.05 else f"{0.3:.1%}",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="High Risk Towers",
            value=f"{metrics['high_risk_towers']:,}",
            delta=f"-{5}" if metrics['high_risk_towers'] < 100 else f"+{10}",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="Open Support Tickets",
            value=f"{metrics['open_tickets']:,}",
            delta=f"-{12}" if metrics['open_tickets'] < 1000 else f"+{25}",
            delta_color="inverse"
        )
    
    st.markdown("---")

def display_features():
    """Display feature cards for navigation"""
    st.subheader("🚀 Application Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🗺️ Cell Tower Lookup</h3>
            <p>Interactive map interface to examine individual cell tower performance metrics, 
            including failure rates, coverage areas, and real-time status monitoring.</p>
            <ul>
                <li>Real-time tower status</li>
                <li>Performance metrics visualization</li>
                <li>Geographic coverage analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        if st.button("Open Cell Tower Lookup →", key="tower_btn"):
            st.switch_page("pages/1_Cell_Tower_Lookup.py")
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🔥 Geospatial Analysis</h3>
            <p>Advanced heatmap overlays to visualize support ticket density, sentiment analysis, 
            and correlation between network failures and customer complaints.</p>
            <ul>
                <li>Support ticket density mapping</li>
                <li>Sentiment analysis heatmaps</li>
                <li>Failure rate correlations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        if st.button("Open Geospatial Analysis →", key="geo_btn"):
            st.switch_page("pages/2_Geospatial_Analysis.py")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 AI-Powered Analytics</h3>
            <p>Leverage Snowflake Cortex for intelligent insights, predictive analytics, 
            and natural language queries about network performance.</p>
            <ul>
                <li>Predictive failure analysis</li>
                <li>Natural language queries</li>
                <li>Automated recommendations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        if st.button("Open AI Analytics →", key="ai_btn"):
            st.switch_page("pages/3_AI_Analytics.py")
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <h3>📈 Performance Dashboard</h3>
            <p>Comprehensive dashboard with trend analysis, comparative metrics, 
            and executive summaries for decision-making.</p>
            <ul>
                <li>Historical trend analysis</li>
                <li>Regional performance comparison</li>
                <li>Executive reporting</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        if st.button("Open Performance Dashboard →", key="perf_btn"):
            st.switch_page("pages/4_Performance_Dashboard.py")

def display_quick_insights(metrics):
    """Display quick insights and alerts"""
    st.markdown("---")
    st.subheader("⚡ Quick Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Network Health Status**: 
        - Overall health score: **{:.1f}/10**
        - {} towers requiring immediate attention
        - Average customer sentiment: **{:.2f}/5.0**
        """.format(
            8.5 - (metrics['avg_failure_rate'] * 100),
            metrics['high_risk_towers'],
            metrics['avg_sentiment']
        ))
    
    with col2:
        st.warning("""
        **Priority Actions**:
        - Review {} high-risk towers with failure rates > 5%
        - Address {} open support tickets from the last 30 days
        - Investigate correlation between failures and customer sentiment
        """.format(metrics['high_risk_towers'], metrics['open_tickets']))

def main():
    """Main application entry point"""
    display_header()
    
    # Fetch and display metrics
    with st.spinner("Loading dashboard metrics..."):
        metrics = fetch_dashboard_metrics()
    
    display_kpi_metrics(metrics)
    display_features()
    display_quick_insights(metrics)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6B7280; padding: 2rem;'>
        <p>© 2025 Telco Network Optimization Suite | Powered by Snowflake & Streamlit</p>
        <p>Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%B %d, %Y at %H:%M")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()

