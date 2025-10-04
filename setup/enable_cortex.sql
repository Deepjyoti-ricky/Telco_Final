-- =====================================================
-- Telco Network Optimization Suite - Cortex Setup
-- =====================================================
-- Enable Snowflake Cortex features for AI analytics

USE DATABASE TELCO_NETWORK_OPTIMIZATION_PROD;
USE SCHEMA RAW;

-- =====================================================
-- 1. ENABLE CROSS-REGION INFERENCE (if needed)
-- =====================================================

-- Check current region
SELECT CURRENT_REGION();

-- Enable cross-region inference for Cortex
-- Note: This may incur additional costs
/*
ALTER ACCOUNT SET ENABLE_CROSS_REGION_INFERENCE = TRUE;
*/

-- =====================================================
-- 2. CREATE CORTEX SEARCH SERVICE FOR SUPPORT TICKETS
-- =====================================================

CREATE OR REPLACE CORTEX SEARCH SERVICE support_ticket_search
ON ISSUE_DESCRIPTION
ATTRIBUTES TICKET_ID, ISSUE_TYPE, STATUS, PRIORITY, SENTIMENT_SCORE
WAREHOUSE = COMPUTE_WH
TARGET_LAG = '1 hour'
AS (
    SELECT 
        TICKET_ID,
        ISSUE_TYPE,
        ISSUE_DESCRIPTION,
        STATUS,
        PRIORITY,
        SENTIMENT_SCORE,
        TICKET_DATE
    FROM SUPPORT_TICKETS
);

COMMENT ON CORTEX SEARCH SERVICE support_ticket_search IS 'Semantic search for support ticket issues';

-- =====================================================
-- 3. CREATE CORTEX SEARCH SERVICE FOR NETWORK ANALYTICS
-- =====================================================

CREATE OR REPLACE CORTEX SEARCH SERVICE network_analytics_search
ON CELL_TOWER_ID, REGION, STATUS
WAREHOUSE = COMPUTE_WH
TARGET_LAG = '1 hour'
AS (
    SELECT 
        CELL_TOWER_ID,
        REGION,
        STATUS,
        FAILURE_RATE,
        SIGNAL_STRENGTH,
        EQUIPMENT_TYPE
    FROM CELL_TOWERS
);

COMMENT ON CORTEX SEARCH SERVICE network_analytics_search IS 'Search service for network analytics';

-- =====================================================
-- 4. EXAMPLE CORTEX FUNCTIONS
-- =====================================================

-- Sentiment Analysis Example
-- Analyze sentiment of support ticket descriptions
/*
SELECT 
    TICKET_ID,
    ISSUE_DESCRIPTION,
    SNOWFLAKE.CORTEX.SENTIMENT(ISSUE_DESCRIPTION) as AI_SENTIMENT_SCORE,
    SENTIMENT_SCORE as ORIGINAL_SCORE
FROM SUPPORT_TICKETS
LIMIT 10;
*/

-- Text Summarization Example
-- Summarize long issue descriptions
/*
SELECT 
    TICKET_ID,
    SNOWFLAKE.CORTEX.SUMMARIZE(ISSUE_DESCRIPTION) as SUMMARY
FROM SUPPORT_TICKETS
WHERE LENGTH(ISSUE_DESCRIPTION) > 100
LIMIT 5;
*/

-- Classification Example
-- Classify issue types
/*
SELECT 
    TICKET_ID,
    ISSUE_DESCRIPTION,
    SNOWFLAKE.CORTEX.CLASSIFY_TEXT(
        ISSUE_DESCRIPTION,
        ['Network Issue', 'Billing Issue', 'Hardware Problem', 'Service Request']
    ) as CLASSIFIED_TYPE,
    ISSUE_TYPE as ORIGINAL_TYPE
FROM SUPPORT_TICKETS
LIMIT 10;
*/

-- Complete (LLM) Example
-- Generate insights using LLM
/*
SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'mistral-large',
        'Analyze this network data and provide recommendations: 
         Average failure rate: 4.2%, 
         Total support tickets: 1247, 
         High risk towers: 15'
    ) as AI_INSIGHTS;
*/

-- =====================================================
-- 5. CREATE VIEW FOR CORTEX-ENHANCED ANALYTICS
-- =====================================================

CREATE OR REPLACE VIEW VW_ENHANCED_SUPPORT_TICKETS AS
SELECT 
    st.TICKET_ID,
    st.CUSTOMER_ID,
    st.CELL_TOWER_ID,
    st.TICKET_DATE,
    st.ISSUE_TYPE,
    st.ISSUE_DESCRIPTION,
    st.STATUS,
    st.PRIORITY,
    st.SENTIMENT_SCORE,
    ct.REGION,
    ct.FAILURE_RATE,
    ct.STATUS as TOWER_STATUS,
    -- AI-enhanced fields (uncomment when Cortex is available)
    -- SNOWFLAKE.CORTEX.SENTIMENT(st.ISSUE_DESCRIPTION) as AI_SENTIMENT,
    -- SNOWFLAKE.CORTEX.SUMMARIZE(st.ISSUE_DESCRIPTION) as SUMMARY,
    CASE 
        WHEN st.SENTIMENT_SCORE < 2 THEN 'Very Negative'
        WHEN st.SENTIMENT_SCORE < 3 THEN 'Negative'
        WHEN st.SENTIMENT_SCORE < 4 THEN 'Neutral'
        WHEN st.SENTIMENT_SCORE < 4.5 THEN 'Positive'
        ELSE 'Very Positive'
    END as SENTIMENT_CATEGORY
FROM SUPPORT_TICKETS st
LEFT JOIN CELL_TOWERS ct ON st.CELL_TOWER_ID = ct.CELL_TOWER_ID;

-- =====================================================
-- 6. GRANTS FOR CORTEX USAGE
-- =====================================================

-- Grant usage on Cortex functions
GRANT USAGE ON DATABASE TELCO_NETWORK_OPTIMIZATION_PROD TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA RAW TO ROLE SYSADMIN;

-- =====================================================
-- VERIFICATION
-- =====================================================

-- Show Cortex search services
SHOW CORTEX SEARCH SERVICES;

-- Describe search service
DESC CORTEX SEARCH SERVICE support_ticket_search;

-- Test search service
/*
SELECT CORTEX_SEARCH_SERVICE(
    'support_ticket_search',
    'network connectivity issues'
) as SEARCH_RESULTS;
*/

-- =====================================================
-- SUSPEND/RESUME CORTEX SEARCH SERVICES
-- =====================================================

-- To save costs when not using the app:
-- ALTER CORTEX SEARCH SERVICE support_ticket_search SUSPEND;
-- ALTER CORTEX SEARCH SERVICE network_analytics_search SUSPEND;

-- To resume when using the app:
-- ALTER CORTEX SEARCH SERVICE support_ticket_search RESUME;
-- ALTER CORTEX SEARCH SERVICE network_analytics_search RESUME;

