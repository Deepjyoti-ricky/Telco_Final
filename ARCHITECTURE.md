# 🏗️ Architecture Documentation

## System Architecture Overview

This document describes the technical architecture of the Telco Network Optimization Suite.

---

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                     (Streamlit Frontend)                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   Home   │  │  Tower   │  │   Geo    │  │    AI    │       │
│  │Dashboard │  │  Lookup  │  │ Analysis │  │Analytics │  ...  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   APPLICATION LAYER                              │
│                  (Python/Streamlit)                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Database   │  │     Data     │  │Visualization │         │
│  │ Connectivity │  │  Processing  │  │   Utilities  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                     DATA LAYER                                   │
│              (Snowflake Cloud Platform)                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│  │  Snowpark  │  │   Cortex   │  │  External  │               │
│  │   Python   │  │  AI/ML     │  │   Access   │               │
│  └────────────┘  └────────────┘  └────────────┘               │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   STORAGE LAYER                                  │
│              (Snowflake Database)                               │
├─────────────────────────────────────────────────────────────────┤
│  📊 Cell Towers  │  🎫 Tickets  │  📈 Metrics  │  👥 Customers│
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Architecture

### 1. User Interaction Flow

```
User Request
    │
    ▼
Streamlit Page Load
    │
    ├──▶ Check Cache (@st.cache_data)
    │        │
    │        ├──▶ Cache Hit ──▶ Return Cached Data
    │        │
    │        └──▶ Cache Miss
    │                 │
    │                 ▼
    └──▶ Snowflake Query
              │
              ▼
         Execute SQL
              │
              ▼
         Fetch Results
              │
              ▼
         Process Data (pandas)
              │
              ▼
         Generate Visualization
              │
              ▼
         Render to User
              │
              ▼
         Update Cache
```

### 2. Database Query Flow

```
Application Layer
    │
    ▼
utils/snowflake_connection.py
    │
    ├──▶ get_snowflake_connection()
    │        │
    │        ├──▶ Try: get_active_session() [Snowflake Native]
    │        │
    │        └──▶ Fallback: Session.builder [Local Development]
    │
    ▼
execute_query(sql)
    │
    ▼
Snowflake Query Processing
    │
    ├──▶ Query Result Cache Check
    │
    ├──▶ Execute on Warehouse
    │
    └──▶ Return pandas DataFrame
         │
         ▼
Application Processing
    │
    └──▶ Visualization/Display
```

---

## 🗂️ Component Architecture

### Frontend Components (Streamlit)

```
main.py (Entry Point)
    │
    ├──▶ Page Configuration
    ├──▶ Custom CSS Styling
    ├──▶ Header & Navigation
    ├──▶ KPI Metrics
    ├──▶ Feature Cards
    └──▶ Quick Insights

pages/
    │
    ├──▶ 1_Cell_Tower_Lookup.py
    │       ├─ Interactive Map (PyDeck)
    │       ├─ Tower Selection
    │       ├─ Detail View
    │       └─ Performance Gauges
    │
    ├──▶ 2_Geospatial_Analysis.py
    │       ├─ Heatmap Layer
    │       ├─ Correlation Plots
    │       ├─ Regional Stats
    │       └─ Priority Areas
    │
    ├──▶ 3_AI_Analytics.py
    │       ├─ Predictions
    │       ├─ Anomaly Detection
    │       ├─ Trend Analysis
    │       └─ AI Insights
    │
    └──▶ 4_Performance_Dashboard.py
            ├─ Executive Summary
            ├─ Trend Charts
            ├─ Regional Comparison
            └─ Export Options
```

### Backend Utilities

```
utils/
    │
    ├──▶ snowflake_connection.py
    │       ├─ get_snowflake_connection()
    │       ├─ execute_query()
    │       └─ get_database_context()
    │
    ├──▶ data_processing.py
    │       ├─ calculate_failure_severity()
    │       ├─ aggregate_metrics_by_region()
    │       ├─ calculate_correlation()
    │       ├─ detect_anomalies()
    │       └─ prepare_heatmap_data()
    │
    └──▶ visualizations.py
            ├─ create_scatter_map()
            ├─ create_heatmap_layer()
            ├─ create_scatter_plot()
            ├─ create_bar_chart()
            ├─ create_line_chart()
            └─ create_gauge_chart()
```

---

## 🗄️ Database Schema Architecture

### Entity-Relationship Diagram

```
┌──────────────────┐
│   CELL_TOWERS    │
│==================│
│ CELL_TOWER_ID PK │◄────┐
│ LATITUDE         │     │
│ LONGITUDE        │     │
│ FAILURE_RATE     │     │
│ STATUS           │     │
│ REGION           │     │
└──────────────────┘     │
         │               │
         │ 1             │ 1
         │               │
         │ N             │ N
         ▼               │
┌──────────────────┐    │
│ NETWORK_METRICS  │    │
│==================│    │
│ METRIC_ID     PK │    │
│ CELL_TOWER_ID FK │────┘
│ METRIC_DATE      │
│ FAILURE_RATE     │
│ SIGNAL_STRENGTH  │
└──────────────────┘

┌──────────────────┐         ┌──────────────────┐
│   CUSTOMERS      │         │ SUPPORT_TICKETS  │
│==================│    ┌────│==================│
│ CUSTOMER_ID   PK │◄───┤  1 │ TICKET_ID     PK │
│ CUSTOMER_NAME    │    │  N │ CUSTOMER_ID   FK │
│ EMAIL            │    └────│ CELL_TOWER_ID FK │──┐
│ SERVICE_PLAN     │         │ TICKET_DATE      │  │
└──────────────────┘         │ ISSUE_TYPE       │  │
                             │ SENTIMENT_SCORE  │  │ N
                             └──────────────────┘  │
                                                   │ 1
                             ┌──────────────────┐  │
                             │ MAINTENANCE_     │  │
                             │    SCHEDULE      │  │
                             │==================│  │
                             │ MAINTENANCE_ID PK│  │
                             │ CELL_TOWER_ID FK │◄─┘
                             │ SCHEDULED_DATE   │
                             │ STATUS           │
                             └──────────────────┘
```

### Data Model Details

**Primary Tables**:
1. **CELL_TOWERS**: Master table for tower infrastructure
2. **SUPPORT_TICKETS**: Customer issues and complaints
3. **NETWORK_METRICS**: Time-series performance data
4. **MAINTENANCE_SCHEDULE**: Maintenance tracking
5. **CUSTOMERS**: Customer master data

**Indexes**:
- Primary keys on all tables
- Foreign key indexes
- Date-based indexes for time-series queries
- Region and status indexes for filtering

---

## 🔐 Security Architecture

### Authentication Flow

```
User
  │
  ▼
Snowflake Authentication
  │
  ├──▶ Username/Password
  ├──▶ SSO (SAML)
  ├──▶ OAuth
  └──▶ Key Pair
       │
       ▼
  Session Creation
       │
       ▼
  Role Assignment
       │
       ├──▶ ACCOUNTADMIN (Full access)
       ├──▶ SYSADMIN (Admin tasks)
       ├──▶ TELCO_ANALYST (Read/Write)
       └──▶ TELCO_VIEWER (Read-only)
            │
            ▼
       Streamlit App Access
            │
            └──▶ Row-Level Security (if configured)
```

### Network Security

```
Internet
    │
    ▼
Snowflake Security Layer
    │
    ├──▶ SSL/TLS Encryption
    ├──▶ IP Whitelisting
    └──▶ Network Policies
         │
         ▼
    Application Layer
         │
         ├──▶ External Access Integration
         │       └──▶ Mapbox API (maps.mapbox.com)
         │
         └──▶ Internal Resources
                 └──▶ Database Tables
```

---

## ⚡ Performance Architecture

### Caching Strategy

```
Query Request
    │
    ▼
Streamlit Cache Check (@st.cache_data)
    │
    ├──▶ Cache Hit
    │       └──▶ Return immediately (microseconds)
    │
    └──▶ Cache Miss
            │
            ▼
       Snowflake Query
            │
            ▼
       Query Result Cache (Snowflake)
            │
            ├──▶ Cache Hit
            │       └──▶ Return from cache (seconds)
            │
            └──▶ Cache Miss
                    │
                    ▼
               Execute Query
                    │
                    ▼
               Store in Caches
                    │
                    └──▶ Return Results
```

### Compute Architecture

```
┌─────────────────────────────────────┐
│      User Requests                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Snowflake Warehouse (TELCO_WH)    │
│   ┌─────────────────────────────┐   │
│   │  Size: SMALL                │   │
│   │  Clusters: 1                │   │
│   │  Auto-Suspend: 5 min        │   │
│   │  Auto-Resume: TRUE          │   │
│   └─────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Query Processing                 │
│   ┌─────────────────────────────┐   │
│   │  Parse & Optimize           │   │
│   │  Execute (parallel)         │   │
│   │  Return Results             │   │
│   └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 🔄 Integration Architecture

### External Integrations

```
Telco Network App
    │
    ├──▶ Mapbox API
    │       └──▶ External Access Integration
    │              └──▶ Network Rule (api.mapbox.com)
    │
    ├──▶ Snowflake Cortex
    │       ├──▶ Sentiment Analysis
    │       ├──▶ Text Summarization
    │       ├──▶ Classification
    │       └──▶ LLM (Complete)
    │
    └──▶ Future Integrations
            ├──▶ Email Service (SendGrid)
            ├──▶ SMS Alerts (Twilio)
            ├──▶ Slack Notifications
            └──▶ REST APIs
```

---

## 📊 Deployment Architecture

### Snowflake Native Deployment

```
GitHub Repository
    │
    ▼
Git Repository Integration
    │
    ▼
Snowflake Git Repository
    │
    ▼
Streamlit App Creation
    │
    ├──▶ Code Files (main.py, pages/, utils/)
    ├──▶ Configuration (requirements.txt)
    ├──▶ Database (TELCO_NETWORK_OPTIMIZATION_PROD)
    ├──▶ Schema (RAW)
    ├──▶ Warehouse (TELCO_WH)
    └──▶ External Access (map_access_int)
         │
         ▼
    Running Application
         │
         └──▶ User Access (URL)
```

### Local Development Architecture

```
Developer Machine
    │
    ├──▶ Python Virtual Environment
    │       └──▶ Install requirements.txt
    │
    ├──▶ Streamlit Local Server
    │       └──▶ streamlit run main.py
    │
    └──▶ Snowflake Connection
            └──▶ .streamlit/secrets.toml
                 │
                 ▼
            Snowflake Account
                 │
                 └──▶ Database Access
```

---

## 🔧 Technology Stack Details

### Frontend Stack
- **Streamlit 1.28+**: Web framework
- **Custom CSS**: Styling
- **Plotly 5.18+**: Interactive charts
- **PyDeck 0.8+**: 3D maps
- **Altair 5.0+**: Declarative viz

### Backend Stack
- **Python 3.8+**: Language
- **Pandas 2.0+**: Data manipulation
- **NumPy 1.24+**: Numerical computing
- **SciPy 1.11+**: Statistical analysis
- **H3-py 3.7+**: Geospatial indexing

### Data Platform
- **Snowflake**: Cloud data platform
- **Snowpark Python**: Data processing
- **Cortex AI**: ML/AI functions
- **External Access**: API integration

---

## 📈 Scalability Architecture

### Horizontal Scaling

```
Increasing Load
    │
    ▼
Warehouse Scaling Options
    │
    ├──▶ Scale Up (Size)
    │       ├─ XSMALL → SMALL
    │       ├─ SMALL → MEDIUM
    │       ├─ MEDIUM → LARGE
    │       └─ LARGE → X-LARGE → ...
    │
    └──▶ Scale Out (Clusters)
            ├─ Multi-cluster warehouse
            ├─ Auto-scale (min-max)
            └─ Query queuing
```

### Data Scaling

```
Data Growth
    │
    ├──▶ Table Partitioning
    │       └──▶ By date (METRIC_DATE)
    │
    ├──▶ Clustering Keys
    │       └──▶ On frequently filtered columns
    │
    ├──▶ Materialized Views
    │       └──▶ For complex aggregations
    │
    └──▶ Result Caching
            └──▶ Automatic by Snowflake
```

---

## 🎯 Design Patterns

### 1. **Separation of Concerns**
- UI Layer (pages/)
- Business Logic (utils/)
- Data Layer (Snowflake)

### 2. **DRY (Don't Repeat Yourself)**
- Reusable utility functions
- Centralized connection management
- Shared visualization components

### 3. **Configuration over Code**
- External configuration files
- Environment-specific settings
- Secrets management

### 4. **Fail-Safe Design**
- Graceful error handling
- Fallback to sample data
- User-friendly error messages

---

## 🔍 Monitoring Architecture

### Application Monitoring

```
Streamlit App
    │
    ├──▶ User Interactions
    │       └──▶ Streamlit Session State
    │
    ├──▶ Query Performance
    │       └──▶ Snowflake Query History
    │
    └──▶ Error Tracking
            └──▶ Exception Handling
```

### Database Monitoring

```sql
-- Query Performance
SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY

-- Warehouse Usage
SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY

-- Credit Consumption
SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY

-- Login History
SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY
```

---

## 📝 Summary

This architecture provides:

✅ **Scalable**: Handles growing data and users  
✅ **Secure**: Multiple layers of security  
✅ **Performant**: Optimized caching and queries  
✅ **Maintainable**: Clear separation of concerns  
✅ **Extensible**: Easy to add new features  
✅ **Reliable**: Fail-safe design patterns  
✅ **Cost-Effective**: Auto-suspend and caching  

---

*Architecture designed for production-grade telecom analytics*

