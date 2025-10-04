-- =====================================================
-- Telco Network Optimization Suite - Mapbox Access
-- =====================================================
-- Setup network access for Mapbox tiles (no API key required)

USE DATABASE TELCO_NETWORK_OPTIMIZATION_PROD;
USE SCHEMA RAW;

-- =====================================================
-- 1. CREATE NETWORK RULE FOR MAPBOX
-- =====================================================

CREATE OR REPLACE NETWORK RULE map_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('api.mapbox.com');

COMMENT ON NETWORK RULE map_network_rule IS 'Allow access to Mapbox tile services';

-- =====================================================
-- 2. CREATE EXTERNAL ACCESS INTEGRATION
-- =====================================================

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION map_access_int
  ALLOWED_NETWORK_RULES = (map_network_rule)
  ENABLED = TRUE;

COMMENT ON INTEGRATION map_access_int IS 'External access integration for Mapbox without API key';

-- =====================================================
-- 3. GRANT USAGE ON INTEGRATION
-- =====================================================

-- Grant to appropriate roles (adjust as needed)
GRANT USAGE ON INTEGRATION map_access_int TO ROLE ACCOUNTADMIN;
GRANT USAGE ON INTEGRATION map_access_int TO ROLE SYSADMIN;

-- =====================================================
-- 4. UPDATE STREAMLIT APP TO USE INTEGRATION
-- =====================================================

-- NOTE: After creating your Streamlit app, run this command
-- Replace YOUR_APP_NAME with the actual name of your Streamlit app

/*
ALTER STREAMLIT TELCO_NETWORK_OPTIMIZATION_PROD.RAW.YOUR_APP_NAME
  SET EXTERNAL_ACCESS_INTEGRATIONS = (map_access_int);
*/

-- =====================================================
-- VERIFICATION
-- =====================================================

-- Show network rules
SHOW NETWORK RULES LIKE 'map_network_rule';

-- Show external access integrations
SHOW EXTERNAL ACCESS INTEGRATIONS LIKE 'map_access_int';

-- Show Streamlit apps (to get the correct app name)
SHOW STREAMLITS IN SCHEMA RAW;

-- =====================================================
-- TROUBLESHOOTING
-- =====================================================

/*
If maps are not displaying in your Streamlit app:

1. Verify the external access integration is created:
   SHOW EXTERNAL ACCESS INTEGRATIONS;

2. Check your Streamlit app configuration:
   SHOW STREAMLITS;
   DESC STREAMLIT YOUR_APP_NAME;

3. Ensure the integration is assigned to your app:
   ALTER STREAMLIT YOUR_APP_NAME
     SET EXTERNAL_ACCESS_INTEGRATIONS = (map_access_int);

4. Try recreating the Streamlit app or restarting it

5. Check for any network policy restrictions in your account
*/

