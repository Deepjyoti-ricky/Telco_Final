"""
Snowflake connection utilities for the Telco Network Optimization Suite
"""

import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session

def get_snowflake_connection():
    """
    Get Snowflake connection session
    
    Returns:
        Session: Active Snowflake session
    """
    try:
        # Try to get the active session (for Streamlit in Snowflake)
        session = get_active_session()
        return session
    except Exception:
        # Fallback for local development with connection parameters
        try:
            connection_parameters = {
                "account": st.secrets.get("snowflake_account", ""),
                "user": st.secrets.get("snowflake_user", ""),
                "password": st.secrets.get("snowflake_password", ""),
                "role": st.secrets.get("snowflake_role", ""),
                "warehouse": st.secrets.get("snowflake_warehouse", ""),
                "database": st.secrets.get("snowflake_database", "TELCO_NETWORK_OPTIMIZATION_PROD"),
                "schema": st.secrets.get("snowflake_schema", "RAW")
            }
            
            # Filter out empty values
            connection_parameters = {k: v for k, v in connection_parameters.items() if v}
            
            if len(connection_parameters) > 0:
                session = Session.builder.configs(connection_parameters).create()
                return session
            else:
                st.error("No Snowflake connection available. Please configure connection parameters.")
                return None
        except Exception as e:
            st.error(f"Failed to establish Snowflake connection: {str(e)}")
            return None

def execute_query(query, params=None):
    """
    Execute a SQL query and return results as pandas DataFrame
    
    Args:
        query (str): SQL query to execute
        params (dict): Optional query parameters
    
    Returns:
        pd.DataFrame: Query results
    """
    try:
        session = get_snowflake_connection()
        if session:
            if params:
                result = session.sql(query, params).to_pandas()
            else:
                result = session.sql(query).to_pandas()
            return result
        return None
    except Exception as e:
        st.error(f"Query execution failed: {str(e)}")
        return None

def get_database_context():
    """
    Get current database context information
    
    Returns:
        dict: Database, schema, and warehouse information
    """
    try:
        session = get_snowflake_connection()
        if session:
            context = {
                'database': session.get_current_database(),
                'schema': session.get_current_schema(),
                'warehouse': session.get_current_warehouse(),
                'role': session.get_current_role()
            }
            return context
        return {}
    except Exception as e:
        st.warning(f"Could not fetch database context: {str(e)}")
        return {}

