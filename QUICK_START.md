# ⚡ Quick Start Guide

Get your Telco Network Optimization Suite up and running in 15 minutes!

---

## 🎯 What You'll Need

- Snowflake account with admin access
- 15 minutes of your time

---

## 📝 Step-by-Step Instructions

### 1️⃣ Create Database (2 minutes)

Open a SQL worksheet in Snowsight and run:

```sql
-- Create database and schema
CREATE DATABASE TELCO_NETWORK_OPTIMIZATION_PROD;
CREATE SCHEMA TELCO_NETWORK_OPTIMIZATION_PROD.RAW;
USE SCHEMA TELCO_NETWORK_OPTIMIZATION_PROD.RAW;

-- Create warehouse
CREATE WAREHOUSE TELCO_WH
  WAREHOUSE_SIZE = 'SMALL'
  AUTO_SUSPEND = 300
  AUTO_RESUME = TRUE;
```

### 2️⃣ Create Tables (3 minutes)

Copy the entire contents of `setup/create_tables.sql` and run it in your SQL worksheet.

**Verify**:
```sql
SHOW TABLES;  -- Should show 5 tables
```

### 3️⃣ Load Sample Data (3 minutes)

Copy the entire contents of `setup/populate_sample_data.sql` and run it.

**Verify**:
```sql
SELECT 
    'CELL_TOWERS' as table_name, COUNT(*) as rows FROM CELL_TOWERS
UNION ALL
SELECT 'SUPPORT_TICKETS', COUNT(*) FROM SUPPORT_TICKETS
UNION ALL
SELECT 'CUSTOMERS', COUNT(*) FROM CUSTOMERS;
```

Expected: 200 cell towers, 5000 tickets, 1000 customers

### 4️⃣ Setup Mapbox Access (2 minutes)

Copy and run `setup/mapbox_access_setup.sql`:

```sql
-- Create network rule
CREATE NETWORK RULE map_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('api.mapbox.com');

-- Create external access integration
CREATE EXTERNAL ACCESS INTEGRATION map_access_int
  ALLOWED_NETWORK_RULES = (map_network_rule)
  ENABLED = TRUE;
```

### 5️⃣ Create Streamlit App (5 minutes)

**Option A: From Git Repository**

1. Create API integration:
```sql
CREATE API INTEGRATION git_telco_app
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/')
  ENABLED = TRUE;
```

2. In Snowsight:
   - Go to **Projects** → **Streamlit**
   - Click **+ Streamlit App** → **Create from repository**
   - Enter your GitHub repository URL
   - Select `main.py` as entry point
   - Choose database: `TELCO_NETWORK_OPTIMIZATION_PROD`, schema: `RAW`
   - Select warehouse: `TELCO_WH`

**Option B: Manual Upload**

1. In Snowsight:
   - Go to **Projects** → **Streamlit**
   - Click **+ Streamlit App**
   - Name: `TELCO_NETWORK_APP`
   - Database: `TELCO_NETWORK_OPTIMIZATION_PROD`
   - Schema: `RAW`
   - Warehouse: `TELCO_WH`

2. Copy contents of `main.py` to the editor

3. Create the `utils` folder and copy:
   - `utils/__init__.py`
   - `utils/snowflake_connection.py`
   - `utils/data_processing.py`
   - `utils/visualizations.py`

4. Create the `pages` folder and copy all page files

5. Add packages (click ⚙️):
   - streamlit
   - snowflake-snowpark-python
   - pandas
   - numpy
   - plotly
   - pydeck
   - h3-py
   - scipy

### 6️⃣ Enable Map Access (1 minute)

After creating the app, run:

```sql
-- Get your app name
SHOW STREAMLITS IN SCHEMA RAW;

-- Enable external access (replace YOUR_APP_NAME)
ALTER STREAMLIT TELCO_NETWORK_OPTIMIZATION_PROD.RAW.YOUR_APP_NAME
  SET EXTERNAL_ACCESS_INTEGRATIONS = (map_access_int);
```

### 7️⃣ Launch! (1 minute)

Click the **Run** button in Streamlit or navigate to your app URL.

You should see:
- ✅ Home dashboard with metrics
- ✅ Interactive cell tower map
- ✅ Heatmap visualizations
- ✅ AI analytics charts
- ✅ Performance dashboard

---

## 🎉 Success!

Your Telco Network Optimization Suite is ready!

### What to Do Next

1. **Explore the Data**:
   - Navigate to Cell Tower Lookup
   - Select different towers
   - Filter by region and status

2. **Analyze Patterns**:
   - Go to Geospatial Analysis
   - View heatmaps
   - Check correlations

3. **Review Insights**:
   - Open AI Analytics
   - See predictions
   - Review recommendations

4. **Monitor Performance**:
   - Visit Performance Dashboard
   - Export reports
   - Track trends

---

## 🐛 Quick Troubleshooting

### Maps Not Showing?

```sql
-- Check external access
SHOW EXTERNAL ACCESS INTEGRATIONS;

-- Reassign to your app
ALTER STREAMLIT YOUR_APP_NAME
  SET EXTERNAL_ACCESS_INTEGRATIONS = (map_access_int);
```

### No Data Displaying?

```sql
-- Verify data exists
SELECT COUNT(*) FROM CELL_TOWERS;

-- If 0, rerun populate_sample_data.sql
```

### Package Import Errors?

In Streamlit editor:
1. Click ⚙️ (Settings)
2. Go to Packages
3. Add missing package
4. Click Run

### App Won't Load?

1. Check warehouse is running:
   ```sql
   SHOW WAREHOUSES LIKE 'TELCO_WH';
   ```

2. Verify permissions:
   ```sql
   SHOW GRANTS TO USER CURRENT_USER();
   ```

3. Restart the app (click Stop, then Run)

---

## 📚 Learn More

- **Full Documentation**: See [README.md](README.md)
- **Detailed Deployment**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Snowflake Docs**: [docs.snowflake.com](https://docs.snowflake.com)

---

## 💡 Pro Tips

1. **Save Credits**: Set auto-suspend to 60 seconds during testing
   ```sql
   ALTER WAREHOUSE TELCO_WH SET AUTO_SUSPEND = 60;
   ```

2. **Enable Caching**: Already built into the app with `@st.cache_data`

3. **Add Real Data**: Replace sample data with your production data once comfortable

4. **Customize**: Modify colors, metrics, and layouts in the code

5. **Share**: Grant access to your team:
   ```sql
   GRANT USAGE ON STREAMLIT YOUR_APP_NAME TO ROLE YOUR_ROLE;
   ```

---

## 🎯 Next Steps

### Immediate (First Hour)
- [ ] Explore all 5 pages
- [ ] Test all interactive features
- [ ] Review sample data

### Short-term (First Week)
- [ ] Customize dashboard metrics
- [ ] Add your company branding
- [ ] Integrate with real data sources

### Long-term (First Month)
- [ ] Enable Cortex AI features
- [ ] Set up automated data pipelines
- [ ] Create custom reports
- [ ] Train your team

---

**Need Help?** 

- Check [README.md](README.md) for detailed docs
- Review [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for advanced setup
- Contact your Snowflake account team

---

**Congratulations! You're now ready to optimize your telecom network!** 🎊

