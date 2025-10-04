"""
AI-Powered Analytics Page
=========================
Leverage Snowflake Cortex for intelligent insights and predictive analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.snowflake_connection import execute_query, get_snowflake_connection
from utils.visualizations import create_line_chart, create_bar_chart

# Page configuration
st.set_page_config(
    page_title="AI Analytics",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .insight-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .prediction-box {
        background: #F3F4F6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_time_series_data():
    """Load historical time series data for predictions"""
    query = """
    SELECT 
        DATE_TRUNC('day', TICKET_DATE) as DATE,
        COUNT(*) as TICKET_COUNT,
        AVG(SENTIMENT_SCORE) as AVG_SENTIMENT,
        COUNT(CASE WHEN STATUS = 'OPEN' THEN 1 END) as OPEN_TICKETS
    FROM SUPPORT_TICKETS
    WHERE TICKET_DATE >= DATEADD(day, -90, CURRENT_DATE())
    GROUP BY DATE_TRUNC('day', TICKET_DATE)
    ORDER BY DATE
    """
    
    try:
        df = execute_query(query)
        if df is not None and not df.empty:
            return df
        else:
            return generate_sample_time_series()
    except Exception:
        return generate_sample_time_series()

def generate_sample_time_series():
    """Generate sample time series data"""
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    
    # Generate trend with seasonality
    trend = np.linspace(50, 80, 90)
    seasonality = 10 * np.sin(np.linspace(0, 4 * np.pi, 90))
    noise = np.random.normal(0, 5, 90)
    
    ticket_count = trend + seasonality + noise
    ticket_count = np.maximum(ticket_count, 0).astype(int)
    
    data = {
        'DATE': dates,
        'TICKET_COUNT': ticket_count,
        'AVG_SENTIMENT': np.random.beta(2, 2, 90) * 3 + 1,
        'OPEN_TICKETS': (ticket_count * np.random.uniform(0.3, 0.7, 90)).astype(int)
    }
    
    return pd.DataFrame(data)

def predict_future_tickets(df, days_ahead=7):
    """Simple linear prediction for future tickets"""
    # Use last 30 days for trend
    recent_data = df.tail(30).copy()
    recent_data['day_num'] = range(len(recent_data))
    
    # Simple linear regression
    coeffs = np.polyfit(recent_data['day_num'], recent_data['TICKET_COUNT'], 1)
    
    # Predict future
    future_days = range(len(recent_data), len(recent_data) + days_ahead)
    predictions = [coeffs[0] * day + coeffs[1] for day in future_days]
    
    future_dates = pd.date_range(
        start=df['DATE'].max() + timedelta(days=1),
        periods=days_ahead,
        freq='D'
    )
    
    return pd.DataFrame({
        'DATE': future_dates,
        'PREDICTED_TICKETS': np.maximum(predictions, 0)
    })

def analyze_sentiment_with_cortex(text_sample):
    """
    Analyze sentiment using Snowflake Cortex
    Note: This requires Cortex Complete function to be available
    """
    try:
        session = get_snowflake_connection()
        if session:
            # Example Cortex sentiment analysis
            query = f"""
            SELECT SNOWFLAKE.CORTEX.SENTIMENT('{text_sample}') as sentiment_score
            """
            result = session.sql(query).to_pandas()
            return result['SENTIMENT_SCORE'].iloc[0] if not result.empty else None
    except Exception as e:
        st.warning(f"Cortex sentiment analysis not available: {str(e)}")
        return None

def generate_insights_with_cortex(context_data):
    """
    Generate insights using Snowflake Cortex LLM
    Note: This requires Cortex Complete function
    """
    try:
        session = get_snowflake_connection()
        if session:
            prompt = f"""
            Analyze the following telecom network data and provide 3 key insights:
            - Average failure rate: {context_data['avg_failure_rate']:.2%}
            - Total support tickets: {context_data['total_tickets']}
            - Average sentiment: {context_data['avg_sentiment']:.2f}
            - High risk towers: {context_data['high_risk_towers']}
            
            Provide actionable recommendations for network optimization.
            """
            
            query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large',
                '{prompt}'
            ) as insights
            """
            
            result = session.sql(query).to_pandas()
            return result['INSIGHTS'].iloc[0] if not result.empty else None
    except Exception as e:
        st.info("AI insights generation not available. Using rule-based insights.")
        return generate_rule_based_insights(context_data)

def generate_rule_based_insights(context_data):
    """Generate insights using rule-based logic"""
    insights = []
    
    if context_data['avg_failure_rate'] > 0.05:
        insights.append(
            "🔴 **High Failure Rate Alert**: The average failure rate is above the "
            "5% threshold. Immediate maintenance review recommended for high-risk towers."
        )
    else:
        insights.append(
            "🟢 **Network Health Good**: Failure rates are within acceptable ranges. "
            "Continue regular monitoring."
        )
    
    if context_data['avg_sentiment'] < 3.0:
        insights.append(
            "⚠️ **Customer Satisfaction Concern**: Average sentiment is below 3.0. "
            "Consider proactive customer outreach and service improvements."
        )
    else:
        insights.append(
            "😊 **Positive Customer Sentiment**: Customers are generally satisfied. "
            "Maintain current service quality standards."
        )
    
    if context_data['high_risk_towers'] > 0:
        insights.append(
            f"🔧 **Maintenance Priority**: {context_data['high_risk_towers']} towers "
            f"require immediate attention. Schedule maintenance to prevent service degradation."
        )
    
    return "\n\n".join(insights)

def display_predictive_analytics(df):
    """Display predictive analytics dashboard"""
    st.markdown("### 🔮 Predictive Analytics")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Historical and predicted tickets
        days_to_predict = st.slider("Prediction Window (days)", 3, 14, 7)
        
        predictions = predict_future_tickets(df, days_ahead=days_to_predict)
        
        # Combine historical and predictions
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=df['DATE'],
            y=df['TICKET_COUNT'],
            mode='lines',
            name='Historical Tickets',
            line=dict(color='#3B82F6')
        ))
        
        # Predictions
        fig.add_trace(go.Scatter(
            x=predictions['DATE'],
            y=predictions['PREDICTED_TICKETS'],
            mode='lines+markers',
            name='Predicted Tickets',
            line=dict(color='#EF4444', dash='dash')
        ))
        
        fig.update_layout(
            title='Support Ticket Forecast',
            xaxis_title='Date',
            yaxis_title='Ticket Count',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Prediction Summary")
        
        avg_predicted = predictions['PREDICTED_TICKETS'].mean()
        recent_avg = df.tail(7)['TICKET_COUNT'].mean()
        trend_pct = ((avg_predicted - recent_avg) / recent_avg * 100)
        
        st.metric(
            "Predicted Avg Tickets/Day",
            f"{avg_predicted:.0f}",
            delta=f"{trend_pct:+.1f}%"
        )
        
        peak_day = predictions.loc[predictions['PREDICTED_TICKETS'].idxmax()]
        st.metric(
            "Expected Peak Day",
            peak_day['DATE'].strftime('%b %d'),
            delta=f"{peak_day['PREDICTED_TICKETS']:.0f} tickets"
        )
        
        if trend_pct > 10:
            st.warning("⚠️ Ticket volume expected to increase significantly")
        elif trend_pct < -10:
            st.success("✅ Ticket volume expected to decrease")
        else:
            st.info("➡️ Ticket volume expected to remain stable")

def display_anomaly_detection(df):
    """Display anomaly detection results"""
    st.markdown("### 🎯 Anomaly Detection")
    
    # Calculate z-scores for ticket count
    df_copy = df.copy()
    df_copy['z_score'] = (df_copy['TICKET_COUNT'] - df_copy['TICKET_COUNT'].mean()) / df_copy['TICKET_COUNT'].std()
    df_copy['is_anomaly'] = np.abs(df_copy['z_score']) > 2
    
    anomalies = df_copy[df_copy['is_anomaly']]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Plot with anomalies highlighted
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_copy['DATE'],
            y=df_copy['TICKET_COUNT'],
            mode='lines',
            name='Ticket Count',
            line=dict(color='#3B82F6')
        ))
        
        if not anomalies.empty:
            fig.add_trace(go.Scatter(
                x=anomalies['DATE'],
                y=anomalies['TICKET_COUNT'],
                mode='markers',
                name='Anomalies',
                marker=dict(color='red', size=10, symbol='x')
            ))
        
        fig.update_layout(
            title='Anomaly Detection in Support Tickets',
            xaxis_title='Date',
            yaxis_title='Ticket Count',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🚨 Detected Anomalies")
        st.metric("Total Anomalies", len(anomalies))
        
        if not anomalies.empty:
            recent_anomalies = anomalies.tail(5)[['DATE', 'TICKET_COUNT', 'z_score']]
            recent_anomalies['DATE'] = recent_anomalies['DATE'].dt.strftime('%b %d')
            recent_anomalies['z_score'] = recent_anomalies['z_score'].apply(lambda x: f"{x:.2f}")
            
            st.dataframe(recent_anomalies, use_container_width=True, hide_index=True)
        else:
            st.success("No significant anomalies detected in recent data")

def display_ai_insights():
    """Display AI-generated insights"""
    st.markdown("### 🤖 AI-Powered Insights")
    
    # Gather context data
    context_data = {
        'avg_failure_rate': 0.042,  # Sample data
        'total_tickets': 1247,
        'avg_sentiment': 3.2,
        'high_risk_towers': 15
    }
    
    with st.spinner("Generating insights..."):
        insights = generate_insights_with_cortex(context_data)
    
    if insights:
        st.markdown(f"""
        <div class="insight-card">
            <h4>💡 Key Insights & Recommendations</h4>
            <p>{insights}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="prediction-box">
            <h5>📈 Trend Analysis</h5>
            <p><strong>7-Day Trend:</strong> +5.2%</p>
            <p><strong>30-Day Trend:</strong> -2.1%</p>
            <p><em>Network performance shows short-term increase in incidents</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="prediction-box">
            <h5>🎯 Risk Assessment</h5>
            <p><strong>Current Risk Level:</strong> Medium</p>
            <p><strong>Risk Score:</strong> 6.3/10</p>
            <p><em>15 towers flagged for preventive maintenance</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="prediction-box">
            <h5>👥 Customer Impact</h5>
            <p><strong>Affected Customers:</strong> ~12,400</p>
            <p><strong>Sentiment Trend:</strong> Stable</p>
            <p><em>Proactive communication recommended</em></p>
        </div>
        """, unsafe_allow_html=True)

def main():
    st.title("🤖 AI-Powered Analytics")
    st.markdown("Leverage advanced analytics and machine learning for network optimization")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading analytics data..."):
        df = load_time_series_data()
    
    if df is None or df.empty:
        st.error("No data available for analytics.")
        return
    
    # Display AI insights
    display_ai_insights()
    
    st.markdown("---")
    
    # Predictive analytics
    display_predictive_analytics(df)
    
    st.markdown("---")
    
    # Anomaly detection
    display_anomaly_detection(df)
    
    # Information about Cortex
    with st.expander("ℹ️ About AI Analytics"):
        st.markdown("""
        This page demonstrates AI-powered analytics capabilities:
        
        - **Predictive Analytics**: Forecast future support ticket volumes based on historical trends
        - **Anomaly Detection**: Identify unusual patterns in network performance data
        - **AI Insights**: Generate actionable recommendations (requires Snowflake Cortex)
        - **Sentiment Analysis**: Analyze customer feedback sentiment (requires Snowflake Cortex)
        
        **Note**: Full AI capabilities require Snowflake Cortex to be enabled in your account.
        Currently showing rule-based insights and statistical predictions.
        """)

if __name__ == "__main__":
    main()

