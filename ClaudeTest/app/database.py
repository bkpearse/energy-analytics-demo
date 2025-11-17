"""
Database operations using in-memory mock data.
No PostgreSQL required - perfect for demos and showcasing.
"""
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
import pandasql as ps

from app.mock_data import MOCK_DATA, get_sales_pipeline_view, get_monthly_sales_performance_view

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Handles database operations using in-memory pandas DataFrames."""

    def __init__(self):
        """Initialize with mock data."""
        self.data = MOCK_DATA

        # Create views
        self.data['sales_pipeline'] = get_sales_pipeline_view(
            self.data['deals'],
            self.data['customers'],
            self.data['sales_reps']
        )
        self.data['monthly_sales_performance'] = get_monthly_sales_performance_view(
            self.data['deals'],
            self.data['sales_reps'],
            self.data['commissions']
        )

        logger.info("Mock database initialized with sample data")

    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """
        Execute a SQL query against mock data using pandasql.

        Args:
            query: SQL query string
            params: Not used with pandasql (kept for compatibility)

        Returns:
            pd.DataFrame with query results
        """
        try:
            # Make all tables available to pandasql
            locals_dict = self.data.copy()

            # Execute query using pandasql
            result = ps.sqldf(query, locals_dict)

            logger.info(f"Query executed successfully. Returned {len(result)} rows.")
            return result

        except Exception as e:
            logger.error(f"Query execution error: {e}")
            logger.error(f"Query was: {query}")
            raise

    def execute_query_dict(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as a list of dictionaries.

        Args:
            query: SQL query string
            params: Not used (kept for compatibility)

        Returns:
            List of dictionaries with query results
        """
        try:
            df = self.execute_query(query, params)
            results = df.to_dict('records')
            logger.info(f"Query executed successfully. Returned {len(results)} rows.")
            return results
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get database schema information for all tables.

        Returns:
            Dictionary with table and column information
        """
        schema = {}

        for table_name, df in self.data.items():
            schema[table_name] = {
                'columns': []
            }

            for col_name, col_type in df.dtypes.items():
                # Convert pandas dtype to SQL-like type
                if pd.api.types.is_integer_dtype(col_type):
                    sql_type = 'INTEGER'
                elif pd.api.types.is_float_dtype(col_type):
                    sql_type = 'DECIMAL'
                elif pd.api.types.is_datetime64_any_dtype(col_type):
                    sql_type = 'TIMESTAMP'
                elif pd.api.types.is_bool_dtype(col_type):
                    sql_type = 'BOOLEAN'
                else:
                    sql_type = 'VARCHAR'

                schema[table_name]['columns'].append({
                    'name': col_name,
                    'type': sql_type,
                    'nullable': True,
                    'constraint': None
                })

        return schema

    def get_table_sample(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """
        Get a sample of rows from a table.

        Args:
            table_name: Name of the table
            limit: Number of rows to return

        Returns:
            DataFrame with sample rows
        """
        if table_name not in self.data:
            raise ValueError(f"Table '{table_name}' not found")

        return self.data[table_name].head(limit)

    def validate_query(self, query: str) -> tuple[bool, str]:
        """
        Validate that a query is safe to execute (read-only).

        Args:
            query: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Remove comments and extra whitespace
        cleaned_query = ' '.join(query.split()).upper()

        # Check for dangerous keywords
        dangerous_keywords = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER',
            'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE'
        ]

        for keyword in dangerous_keywords:
            if keyword in cleaned_query:
                return False, f"Query contains prohibited keyword: {keyword}"

        # Must be a SELECT query or WITH clause
        if not cleaned_query.strip().startswith('SELECT') and not cleaned_query.strip().startswith('WITH'):
            return False, "Only SELECT queries are allowed"

        return True, ""

    def test_connection(self) -> bool:
        """Test database connection (always returns True for mock data)."""
        try:
            # Test a simple query
            result = self.execute_query("SELECT 1 as test")
            return len(result) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_available_tables(self) -> List[str]:
        """Get list of available tables."""
        return list(self.data.keys())

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a specific table."""
        if table_name not in self.data:
            raise ValueError(f"Table '{table_name}' not found")

        df = self.data[table_name]
        return {
            'name': table_name,
            'row_count': len(df),
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
