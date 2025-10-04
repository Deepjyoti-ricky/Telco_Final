# 🚀 Deployment Guide - Telco Network Optimization Suite

This guide provides detailed step-by-step instructions for deploying the Telco Network Optimization Suite to Snowflake.

---

## 📋 Prerequisites Checklist

Before starting deployment, ensure you have:

- [ ] Snowflake account with **ACCOUNTADMIN** or **SYSADMIN** role
- [ ] Streamlit in Snowflake enabled (contact your account team if not)
- [ ] GitHub account (for repository hosting)
- [ ] Git installed locally
- [ ] Snowflake CLI or SnowSQL installed (optional, for advanced users)

---

## 🎯 Deployment Steps

### Phase 1: Repository Setup

#### Step 1.1: Create GitHub Repository

1. Log in to GitHub
2. Create a new repository (public or private)
3. Clone this project to your local machine
4. Push to your GitHub repository:

```bash
cd "Network final"
git init
git add .
git commit -m "Initial commit: Telco Network Optimization Suite"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

---

### Phase 2: Snowflake Configuration

#### Step 2.1: Create API Integration

Connect to Snowflake and run:

```sql
-- Use ACCOUNTADMIN role
USE ROLE ACCOUNTADMIN;

-- Create API integration for GitHub
CREATE OR REPLACE API INTEGRATION git_telco_integration
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/')
  ENABLED = TRUE;

-- Verify creation
SHOW API INTEGRATIONS LIKE 'git_telco_integration';
```

#### Step 2.2: Create Database and Schema

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS TELCO_NETWORK_OPTIMIZATION_PROD;

-- Create schema
CREATE SCHEMA IF NOT EXISTS TELCO_NETWORK_OPTIMIZATION_PROD.RAW;

-- Set context
USE DATABASE TELCO_NETWORK_OPTIMIZATION_PROD;
USE SCHEMA RAW;
```

#### Step 2.3: Create Warehouse

```sql
-- Create compute warehouse
CREATE WAREHOUSE IF NOT EXISTS TELCO_WH
  WAREHOUSE_SIZE = 'SMALL'
  AUTO_SUSPEND = 300
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Warehouse for Telco Network Optimization Suite';

-- Grant usage
GRANT USAGE ON WAREHOUSE TELCO_WH TO ROLE SYSADMIN;
```

#### Step 2.4: Create Tables

Run the setup script:

```sql
-- Execute create_tables.sql
-- Copy and paste contents from setup/create_tables.sql
```

Or use SnowSQL:

```bash
snowsql -a your-account -u your-user \
  -f setup/create_tables.sql
```

#### Step 2.5: Populate Sample Data

```sql
-- Execute populate_sample_data.sql
-- Copy and paste contents from setup/populate_sample_data.sql
```

**Important**: This will create ~56,700 sample records. Adjust ROWCOUNT in the script if needed.

#### Step 2.6: Setup Mapbox Access

```sql
-- Execute mapbox_access_setup.sql
-- This enables map visualizations without API key
```

---

### Phase 3: Streamlit App Deployment

#### Step 3.1: Create Git Repository in Snowflake

```sql
-- Create Git repository
CREATE OR REPLACE GIT REPOSITORY telco_network_repo
  ORIGIN = 'https://github.com/YOUR-USERNAME/YOUR-REPO.git'
  API_INTEGRATION = git_telco_integration
  GIT_CREDENTIALS = NULL;  -- For public repos

-- For private repos, create and use credentials:
-- CREATE SECRET git_secret
--   TYPE = PASSWORD
--   USERNAME = 'your-github-username'
--   PASSWORD = 'your-github-token';
-- 
-- CREATE GIT REPOSITORY telco_network_repo
--   ORIGIN = 'https://github.com/YOUR-USERNAME/YOUR-REPO.git'
--   API_INTEGRATION = git_telco_integration
--   GIT_CREDENTIALS = git_secret;

-- Verify repository
SHOW GIT REPOSITORIES;
```

#### Step 3.2: Create Streamlit App via Snowsight

**Option A: Using Snowsight UI (Recommended)**

1. Navigate to **Snowsight** → **Projects** → **Streamlit**
2. Click **+ Streamlit App** dropdown → **Create from repository**
3. Fill in the form:
   - **App Name**: `TELCO_NETWORK_APP`
   - **Repository**: Select `telco_network_repo`
   - **Entry Point**: `main.py`
   - **Database**: `TELCO_NETWORK_OPTIMIZATION_PROD`
   - **Schema**: `RAW`
   - **Warehouse**: `TELCO_WH`
4. Click **Create**

**Option B: Using SQL**

```sql
CREATE STREAMLIT TELCO_NETWORK_APP
  ROOT_LOCATION = '@telco_network_repo/branches/main'
  MAIN_FILE = 'main.py'
  QUERY_WAREHOUSE = TELCO_WH
  COMMENT = 'Telco Network Optimization Suite';
```

#### Step 3.3: Configure External Access

After creating the app, enable Mapbox access:

```sql
-- Get the app name
SHOW STREAMLITS IN SCHEMA RAW;

-- Assign external access integration
ALTER STREAMLIT TELCO_NETWORK_OPTIMIZATION_PROD.RAW.TELCO_NETWORK_APP
  SET EXTERNAL_ACCESS_INTEGRATIONS = (map_access_int);
```

#### Step 3.4: Add Python Packages

In Snowsight, open your Streamlit app in edit mode and add these packages:

1. Click **⚙️ Settings** → **Packages**
2. Add the following packages:
   - `streamlit`
   - `snowflake-snowpark-python`
   - `pandas`
   - `numpy`
   - `plotly`
   - `pydeck`
   - `h3-py`
   - `scipy`
   - `altair`
   - `matplotlib`
   - `branca`

Or use the package file from the repository.

---

### Phase 4: Enable AI Features (Optional)

#### Step 4.1: Enable Cortex

```sql
-- Check if Cortex is available in your region
SELECT SYSTEM$CORTEX_AVAILABLE();

-- Execute enable_cortex.sql
-- Copy and paste contents from setup/enable_cortex.sql
```

#### Step 4.2: Create Cortex Search Services

```sql
-- Create search service for support tickets
CREATE CORTEX SEARCH SERVICE support_ticket_search
ON ISSUE_DESCRIPTION
ATTRIBUTES TICKET_ID, ISSUE_TYPE, STATUS
WAREHOUSE = TELCO_WH
TARGET_LAG = '1 hour'
AS (
    SELECT 
        TICKET_ID,
        ISSUE_TYPE,
        ISSUE_DESCRIPTION,
        STATUS,
        SENTIMENT_SCORE
    FROM SUPPORT_TICKETS
);
```

---

### Phase 5: Testing and Validation

#### Step 5.1: Test Database Connection

```sql
-- Verify all tables exist and have data
SELECT 'CELL_TOWERS' as table_name, COUNT(*) as row_count FROM CELL_TOWERS
UNION ALL
SELECT 'SUPPORT_TICKETS', COUNT(*) FROM SUPPORT_TICKETS
UNION ALL
SELECT 'NETWORK_METRICS', COUNT(*) FROM NETWORK_METRICS
UNION ALL
SELECT 'MAINTENANCE_SCHEDULE', COUNT(*) FROM MAINTENANCE_SCHEDULE
UNION ALL
SELECT 'CUSTOMERS', COUNT(*) FROM CUSTOMERS;
```

Expected results:
- CELL_TOWERS: 200 rows
- SUPPORT_TICKETS: 5,000 rows
- NETWORK_METRICS: ~50,000 rows
- MAINTENANCE_SCHEDULE: 500 rows
- CUSTOMERS: 1,000 rows

#### Step 5.2: Test Streamlit App

1. Navigate to your Streamlit app URL
2. Verify the home page loads
3. Test each page:
   - Cell Tower Lookup: Maps should display
   - Geospatial Analysis: Heatmaps should render
   - AI Analytics: Charts should show predictions
   - Performance Dashboard: All metrics should display

#### Step 5.3: Test External Access

Check if maps are loading:
1. Go to Cell Tower Lookup page
2. Verify the map displays with tower markers
3. If maps don't load, revisit Phase 3, Step 3.3

---

### Phase 6: User Access and Permissions

#### Step 6.1: Grant Access to Users

```sql
-- Create a role for app users
CREATE ROLE IF NOT EXISTS TELCO_APP_USER;

-- Grant database and schema usage
GRANT USAGE ON DATABASE TELCO_NETWORK_OPTIMIZATION_PROD TO ROLE TELCO_APP_USER;
GRANT USAGE ON SCHEMA RAW TO ROLE TELCO_APP_USER;

-- Grant table access
GRANT SELECT ON ALL TABLES IN SCHEMA RAW TO ROLE TELCO_APP_USER;

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE TELCO_WH TO ROLE TELCO_APP_USER;

-- Grant Streamlit app access
GRANT USAGE ON STREAMLIT TELCO_NETWORK_APP TO ROLE TELCO_APP_USER;

-- Assign role to users
GRANT ROLE TELCO_APP_USER TO USER your_user;
```

#### Step 6.2: Share App URL

The app URL format:
```
https://app.snowflake.com/[region]/[account]/#/streamlit-apps/[app_id]
```

Get the exact URL from Snowsight or via SQL:
```sql
SHOW STREAMLITS;
-- Copy the app URL from the results
```

---

## 🔒 Security Best Practices

### 1. Role-Based Access Control

```sql
-- Create separate roles for different access levels
CREATE ROLE TELCO_ADMIN;
CREATE ROLE TELCO_ANALYST;
CREATE ROLE TELCO_VIEWER;

-- Grant appropriate permissions to each role
-- TELCO_ADMIN: Full access including write
GRANT ALL ON DATABASE TELCO_NETWORK_OPTIMIZATION_PROD TO ROLE TELCO_ADMIN;

-- TELCO_ANALYST: Read and limited write
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA RAW TO ROLE TELCO_ANALYST;

-- TELCO_VIEWER: Read-only
GRANT SELECT ON ALL TABLES IN SCHEMA RAW TO ROLE TELCO_VIEWER;
```

### 2. Network Policies (Optional)

```sql
-- Create network policy to restrict access by IP
CREATE NETWORK POLICY telco_app_policy
  ALLOWED_IP_LIST = ('192.168.1.0/24', '10.0.0.0/8')
  BLOCKED_IP_LIST = ();

-- Apply to users
ALTER USER your_user SET NETWORK_POLICY = telco_app_policy;
```

### 3. Secret Management

For production:
- Never commit secrets to Git
- Use Snowflake's SECRET objects
- Rotate credentials regularly
- Enable MFA for all admin accounts

---

## 💰 Cost Optimization

### 1. Warehouse Auto-Suspend

```sql
-- Set aggressive auto-suspend for dev/test
ALTER WAREHOUSE TELCO_WH SET AUTO_SUSPEND = 60;  -- 1 minute

-- Moderate auto-suspend for production
ALTER WAREHOUSE TELCO_WH SET AUTO_SUSPEND = 300;  -- 5 minutes
```

### 2. Query Result Caching

Enable result caching in Streamlit:
```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    # Your data loading code
    pass
```

### 3. Suspend Cortex Services

When not using the app:
```sql
-- Suspend search services
ALTER CORTEX SEARCH SERVICE support_ticket_search SUSPEND;
ALTER CORTEX SEARCH SERVICE network_analytics_search SUSPEND;

-- Resume when needed
ALTER CORTEX SEARCH SERVICE support_ticket_search RESUME;
```

---

## 🔄 Updating the Application

### Update from Git

```sql
-- Fetch latest changes
ALTER GIT REPOSITORY telco_network_repo FETCH;

-- Update Streamlit app to use latest code
ALTER STREAMLIT TELCO_NETWORK_APP
  SET ROOT_LOCATION = '@telco_network_repo/branches/main';
```

### Update via Snowsight

1. Open Streamlit app in edit mode
2. Click **Pull** to get latest changes
3. Click **Run** to reload the app

---

## 🐛 Common Issues and Solutions

### Issue 1: Git Repository Not Accessible

**Error**: `Git repository access denied`

**Solution**:
```sql
-- Check API integration
SHOW API INTEGRATIONS;

-- Recreate if needed
DROP API INTEGRATION IF EXISTS git_telco_integration;
-- Then recreate from Step 2.1
```

### Issue 2: Package Import Errors

**Error**: `ModuleNotFoundError: No module named 'plotly'`

**Solution**:
1. Open Streamlit app in edit mode
2. Add missing packages via UI
3. Or add to `requirements.txt` in repository

### Issue 3: Data Not Displaying

**Error**: Empty charts or "No data available" messages

**Solution**:
```sql
-- Check if tables have data
SELECT COUNT(*) FROM CELL_TOWERS;

-- If empty, rerun populate_sample_data.sql
```

### Issue 4: Cortex Functions Failing

**Error**: `Cortex function not available`

**Solution**:
1. Check if Cortex is enabled: `SELECT SYSTEM$CORTEX_AVAILABLE();`
2. Verify your region supports Cortex
3. Contact Snowflake support if needed

---

## 📊 Monitoring and Maintenance

### Monitor Warehouse Usage

```sql
-- Query history
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE WAREHOUSE_NAME = 'TELCO_WH'
  AND START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY START_TIME DESC
LIMIT 100;

-- Credit usage
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE WAREHOUSE_NAME = 'TELCO_WH'
  AND START_TIME >= DATEADD(day, -30, CURRENT_TIMESTAMP());
```

### Application Health Check

```sql
-- Check Streamlit app status
SHOW STREAMLITS;

-- Check table freshness
SELECT 
    TABLE_NAME,
    LAST_ALTERED,
    ROW_COUNT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'RAW';
```

---

## 🎓 Next Steps

After successful deployment:

1. **Customize the Application**:
   - Modify SQL queries for your data
   - Adjust visualizations
   - Add custom pages

2. **Integrate Real Data**:
   - Replace sample data with production data
   - Set up data pipelines
   - Configure real-time updates

3. **Enhance Security**:
   - Implement row-level security
   - Add audit logging
   - Configure data masking

4. **Scale for Production**:
   - Increase warehouse size as needed
   - Implement multi-cluster warehouses
   - Add monitoring and alerting

---

## 📞 Support

If you encounter issues:

1. Check the [Troubleshooting](#-common-issues-and-solutions) section
2. Review Snowflake documentation
3. Contact your Snowflake account team
4. Open an issue on GitHub

---

**Deployment Complete!** 🎉

Your Telco Network Optimization Suite is now live and ready to use.

