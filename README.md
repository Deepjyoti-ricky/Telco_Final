# 📡 Telco Network Optimization Suite

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Snowflake](https://img.shields.io/badge/snowflake-enabled-00C7D4.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**A comprehensive Streamlit application for visualizing and analyzing cell tower performance, customer support data, and network optimization using AI-powered insights.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Architecture](#-architecture)

</div>

---

## 🌟 Features

### 📊 Comprehensive Analytics
- **Real-time Network Monitoring**: Track cell tower performance metrics including failure rates, signal strength, and coverage
- **Customer Support Intelligence**: Analyze support ticket patterns, sentiment, and resolution times
- **Geospatial Analysis**: Interactive heatmaps for visualizing network issues and customer impact
- **Predictive Analytics**: Forecast network issues and support ticket volumes using AI

### 🤖 AI-Powered Insights
- **Snowflake Cortex Integration**: Leverage advanced AI for sentiment analysis and insights generation
- **Anomaly Detection**: Automatically identify unusual patterns in network performance
- **Natural Language Queries**: Ask questions about your network in plain English
- **Automated Recommendations**: Get actionable suggestions for network optimization

### 🗺️ Interactive Visualizations
- **3D Cell Tower Maps**: Explore tower locations with performance overlays
- **Heatmap Overlays**: Visualize support ticket density and sentiment distribution
- **Correlation Analysis**: Understand relationships between network failures and customer complaints
- **Executive Dashboards**: High-level KPIs and trend analysis for decision-makers

### 🔧 Professional Features
- **Multi-page Application**: Organized interface with dedicated pages for different analyses
- **Responsive Design**: Modern, professional UI with smooth navigation
- **Export Capabilities**: Download reports and data for offline analysis
- **Real-time Updates**: Auto-refresh options for monitoring dashboards

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Application Pages](#-application-pages)
- [Configuration](#%EF%B8%8F-configuration)
- [Database Setup](#-database-setup)
- [Deployment](#-deployment)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## Prerequisites

Before you begin, ensure you have:

- **Snowflake Account** with:
  - Database creation privileges
  - Streamlit in Snowflake enabled
  - (Optional) Cortex AI features enabled
- **Python 3.8+** (for local development)
- **Git** (for version control)

---

## 🚀 Installation

### Option 1: Deploy to Snowflake (Recommended)

1. **Create API Integration** (one-time setup):
```sql
CREATE OR REPLACE API INTEGRATION git_telco_app
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/')
  ENABLED = TRUE;
```

2. **Create Git Repository in Snowflake**:
```sql
CREATE OR REPLACE GIT REPOSITORY telco_network_repo
  ORIGIN = 'https://github.com/YOUR-USERNAME/telco-network-optimization'
  API_INTEGRATION = git_telco_app;
```

3. **Create Streamlit App**:
   - Navigate to Snowsight → Projects → Streamlit
   - Click "+ Streamlit App" → "Create from repository"
   - Select your Git repository
   - Choose `main.py` as the entry point
   - Select database: `TELCO_NETWORK_OPTIMIZATION_PROD`, schema: `RAW`
   - Deploy the app

### Option 2: Local Development

1. **Clone the repository**:
```bash
git clone <your-repo-url>
cd "Network final"
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure secrets**:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your Snowflake credentials
```

5. **Run the application**:
```bash
streamlit run main.py
```

---

## ⚡ Quick Start

### Step 1: Database Setup

Run the setup scripts in order:

```sql
-- 1. Create tables
@setup/create_tables.sql

-- 2. Populate sample data
@setup/populate_sample_data.sql

-- 3. Setup Mapbox access (for maps)
@setup/mapbox_access_setup.sql

-- 4. (Optional) Enable Cortex AI
@setup/enable_cortex.sql
```

### Step 2: Configure Streamlit App

After creating your Streamlit app in Snowflake, enable external access:

```sql
-- Get your app name
SHOW STREAMLITS IN SCHEMA RAW;

-- Enable Mapbox access
ALTER STREAMLIT TELCO_NETWORK_OPTIMIZATION_PROD.RAW.YOUR_APP_NAME
  SET EXTERNAL_ACCESS_INTEGRATIONS = (map_access_int);
```

### Step 3: Launch the Application

Navigate to your Streamlit app URL in Snowflake and start exploring!

---

## 📱 Application Pages

### 1. **Home Dashboard** (`main.py`)
The landing page providing:
- Overview of key network metrics
- Quick insights and alerts
- Navigation to all features
- Executive summary cards

### 2. **Cell Tower Lookup** (`pages/1_Cell_Tower_Lookup.py`)
Interactive tower exploration:
- 3D map with tower locations
- Individual tower performance metrics
- Failure rate and signal strength gauges
- Maintenance history
- Filterable by region, status, and performance

### 3. **Geospatial Analysis** (`pages/2_Geospatial_Analysis.py`)
Advanced heatmap visualizations:
- Support ticket density maps
- Customer sentiment heatmaps
- Failure rate correlations
- Regional performance comparison
- Priority area identification

### 4. **AI-Powered Analytics** (`pages/3_AI_Analytics.py`)
Intelligent insights and predictions:
- Support ticket volume forecasting
- Anomaly detection in network metrics
- AI-generated recommendations
- Trend analysis with predictions
- Risk assessment scoring

### 5. **Performance Dashboard** (`pages/4_Performance_Dashboard.py`)
Executive reporting:
- Network availability trends
- SLA compliance monitoring
- Regional performance comparison
- Tower status distribution
- Export capabilities for reports

---

## ⚙️ Configuration

### Streamlit Configuration

Edit `.streamlit/config.toml` for application settings:

```toml
[theme]
primaryColor = "#3B82F6"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F3F4F6"

[server]
maxUploadSize = 200
```

### Database Configuration

Default database and schema:
- Database: `TELCO_NETWORK_OPTIMIZATION_PROD`
- Schema: `RAW`

To use different names, update the SQL scripts and connection strings.

### Environment Variables

For local development, create `.streamlit/secrets.toml`:

```toml
[snowflake]
account = "your-account"
user = "your-user"
password = "your-password"
warehouse = "COMPUTE_WH"
database = "TELCO_NETWORK_OPTIMIZATION_PROD"
schema = "RAW"
```

---

## 🗄️ Database Setup

### Tables Created

1. **CELL_TOWERS**: Tower infrastructure and performance data
2. **SUPPORT_TICKETS**: Customer support tickets and issues
3. **NETWORK_METRICS**: Time-series performance metrics
4. **MAINTENANCE_SCHEDULE**: Scheduled and completed maintenance
5. **CUSTOMERS**: Customer information and service details

### Sample Data

The `populate_sample_data.sql` script generates:
- 200 cell towers
- 1,000 customers
- 5,000 support tickets
- 50,000 network metric records
- 500 maintenance records

### Data Model

```
CELL_TOWERS (1) ─────── (*) SUPPORT_TICKETS
     │
     ├────────── (*) NETWORK_METRICS
     │
     └────────── (*) MAINTENANCE_SCHEDULE

CUSTOMERS (1) ─────── (*) SUPPORT_TICKETS
```

---

## 🚢 Deployment

### Deploying to Snowflake

**Step 1**: Prepare your repository
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

**Step 2**: Create Streamlit app in Snowflake
- Use Snowsight UI or SQL commands
- Point to your Git repository
- Select `main.py` as entry point

**Step 3**: Configure external access
```sql
ALTER STREAMLIT YOUR_APP_NAME
  SET EXTERNAL_ACCESS_INTEGRATIONS = (map_access_int);
```

**Step 4**: Add required packages
In the Streamlit editor, add these packages:
- streamlit
- snowflake-snowpark-python
- pandas
- plotly
- pydeck
- h3-py
- scipy
- numpy
- altair
- matplotlib
- branca

### Production Considerations

1. **Security**:
   - Use service accounts with minimal privileges
   - Enable MFA for Snowflake accounts
   - Regularly rotate credentials
   - Review and audit access logs

2. **Performance**:
   - Use appropriate warehouse sizes
   - Enable query result caching
   - Implement data partitioning
   - Monitor query performance

3. **Cost Optimization**:
   - Suspend Cortex search services when not in use
   - Use AUTO_SUSPEND for warehouses
   - Implement data retention policies
   - Monitor credit usage

---

## 🏗️ Architecture

### Technology Stack

```
┌─────────────────────────────────────┐
│         Streamlit UI Layer          │
│  (Multi-page app with visualizations)│
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Application Layer              │
│  • Data Processing (utils/)          │
│  • Visualization (utils/)            │
│  • Connection Management             │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        Snowflake Layer               │
│  • Snowpark Session                  │
│  • Cortex AI Services                │
│  • External Access Integration       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Data Layer                   │
│  • Cell Towers                       │
│  • Support Tickets                   │
│  • Network Metrics                   │
│  • Maintenance Schedule              │
└─────────────────────────────────────┘
```

### File Structure

```
Network final/
├── main.py                          # Landing page
├── pages/                           # Application pages
│   ├── 1_Cell_Tower_Lookup.py
│   ├── 2_Geospatial_Analysis.py
│   ├── 3_AI_Analytics.py
│   └── 4_Performance_Dashboard.py
├── utils/                           # Utility modules
│   ├── __init__.py
│   ├── snowflake_connection.py     # Database connectivity
│   ├── data_processing.py          # Data transformation
│   └── visualizations.py           # Chart creation
├── setup/                           # SQL setup scripts
│   ├── create_tables.sql
│   ├── populate_sample_data.sql
│   ├── mapbox_access_setup.sql
│   └── enable_cortex.sql
├── .streamlit/                      # Configuration
│   ├── config.toml
│   └── secrets.toml.example
├── requirements.txt                 # Python dependencies
├── .gitignore
└── README.md                        # Documentation
```

---

## 🔧 Troubleshooting

### Maps Not Displaying

**Problem**: Maps show blank or fail to load

**Solutions**:
1. Verify external access integration:
   ```sql
   SHOW EXTERNAL ACCESS INTEGRATIONS;
   ```

2. Check Streamlit app configuration:
   ```sql
   DESC STREAMLIT YOUR_APP_NAME;
   ```

3. Re-assign integration:
   ```sql
   ALTER STREAMLIT YOUR_APP_NAME
     SET EXTERNAL_ACCESS_INTEGRATIONS = (map_access_int);
   ```

### Connection Errors

**Problem**: Cannot connect to Snowflake

**Solutions**:
1. Verify credentials in `secrets.toml`
2. Check network connectivity
3. Ensure warehouse is running
4. Verify role has necessary permissions

### Data Not Loading

**Problem**: Tables appear empty or queries fail

**Solutions**:
1. Run setup scripts in order
2. Check table permissions:
   ```sql
   SHOW GRANTS ON TABLE CELL_TOWERS;
   ```
3. Verify data was inserted:
   ```sql
   SELECT COUNT(*) FROM CELL_TOWERS;
   ```

### Cortex Features Not Available

**Problem**: AI features return errors

**Solutions**:
1. Verify Cortex is enabled in your region
2. Check account permissions
3. Enable cross-region inference if needed
4. Contact Snowflake support for access

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Snowflake](https://www.snowflake.com/)
- Maps by [Mapbox](https://www.mapbox.com/)
- Inspired by the original repositories by [Deepjyoti-ricky](https://github.com/Deepjyoti-ricky/Telco_v4) and [sfc-gh-sweingartner](https://github.com/sfc-gh-sweingartner/network_optmise)

---

## 📧 Support

For questions or support:
- Open an issue on GitHub
- Contact your Snowflake account team
- Review Snowflake documentation

---

<div align="center">

**Built with ❤️ using Snowflake and Streamlit**

</div>

