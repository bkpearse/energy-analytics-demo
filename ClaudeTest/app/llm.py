"""
Claude API integration for natural language to SQL conversion.
"""
import os
from anthropic import Anthropic
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SQLGenerator:
    """Generates SQL queries from natural language using Claude."""

    def __init__(self, schema_context: str):
        """
        Initialize the SQL generator.

        Args:
            schema_context: String description of the database schema
        """
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.schema_context = schema_context
        self.model = "claude-sonnet-4-5-20250929"

    def generate_sql(self, user_question: str, conversation_history: Optional[list] = None) -> Dict[str, Any]:
        """
        Generate SQL query from natural language question.

        Args:
            user_question: Natural language question from user
            conversation_history: Optional list of previous messages for context

        Returns:
            Dictionary with:
                - sql: Generated SQL query
                - explanation: Explanation of what the query does
                - visualization_type: Suggested visualization type
                - success: Boolean indicating if generation was successful
                - error: Error message if unsuccessful
        """
        system_prompt = f"""You are an expert SQL query generator for an energy B2B sales and commission analytics database.

DATABASE SCHEMA:
{self.schema_context}

YOUR TASK:
Generate PostgreSQL-compatible SQL queries based on user questions. Always respond in this exact JSON format:

{{
    "sql": "SELECT ... FROM ... WHERE ...",
    "explanation": "Brief explanation of what the query does and what insights it provides",
    "visualization_type": "table|bar|line|pie|scatter",
    "columns_to_visualize": {{"x": "column_name", "y": "column_name"}} or null for tables
}}

RULES:
1. Only generate SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Use proper PostgreSQL syntax
3. Always use table aliases for clarity
4. Include appropriate WHERE clauses, GROUP BY, ORDER BY as needed
5. Use aggregate functions (SUM, COUNT, AVG) when analyzing totals or averages
6. Format dates using PostgreSQL date functions
7. Limit results to reasonable amounts (use LIMIT when appropriate)
8. Choose the most appropriate visualization type:
   - table: For detailed data, lists, or when no clear numeric relationship
   - bar: For comparing categories or time periods
   - line: For trends over time
   - pie: For showing composition/percentages (use sparingly)
   - scatter: For correlation between two numeric variables

COMMON BUSINESS QUESTIONS:
- Sales performance by rep, team, or time period
- Commission calculations and payments
- Pipeline analysis and deal stages
- Customer analytics and account health
- Activity tracking and engagement metrics
- Product performance
- Revenue trends and forecasting

Be concise but accurate. If the question is ambiguous, make reasonable assumptions based on common business analytics needs."""

        try:
            messages = []

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add current question
            messages.append({
                "role": "user",
                "content": user_question
            })

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=messages
            )

            # Parse response
            response_text = response.content[0].text

            # Try to parse as JSON
            import json
            try:
                result = json.loads(response_text)
                result['success'] = True
                result['error'] = None
                return result
            except json.JSONDecodeError:
                # If not JSON, try to extract SQL from markdown code blocks
                if '```sql' in response_text:
                    sql = response_text.split('```sql')[1].split('```')[0].strip()
                    return {
                        'sql': sql,
                        'explanation': 'Query generated from natural language',
                        'visualization_type': 'table',
                        'columns_to_visualize': None,
                        'success': True,
                        'error': None
                    }
                else:
                    return {
                        'sql': None,
                        'explanation': response_text,
                        'visualization_type': None,
                        'columns_to_visualize': None,
                        'success': False,
                        'error': 'Could not parse SQL from response'
                    }

        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            return {
                'sql': None,
                'explanation': None,
                'visualization_type': None,
                'columns_to_visualize': None,
                'success': False,
                'error': str(e)
            }

    def refine_query(self, original_question: str, original_sql: str,
                     user_feedback: str) -> Dict[str, Any]:
        """
        Refine a SQL query based on user feedback.

        Args:
            original_question: Original user question
            original_sql: Previously generated SQL
            user_feedback: User's feedback or clarification

        Returns:
            Dictionary with refined query information
        """
        refinement_prompt = f"""The user asked: "{original_question}"

I generated this SQL:
```sql
{original_sql}
```

The user provided this feedback: "{user_feedback}"

Please generate an improved SQL query that addresses their feedback."""

        return self.generate_sql(refinement_prompt)


def build_schema_context(schema_info: Dict[str, Any]) -> str:
    """
    Build a formatted schema context string for Claude.

    Args:
        schema_info: Dictionary with table and column information

    Returns:
        Formatted string describing the schema
    """
    context = []

    for table_name, table_data in schema_info.items():
        context.append(f"\nTABLE: {table_name}")
        context.append("Columns:")

        for column in table_data['columns']:
            constraint = f" ({column['constraint']})" if column.get('constraint') else ""
            nullable = " NULL" if column['nullable'] else " NOT NULL"
            context.append(f"  - {column['name']}: {column['type']}{nullable}{constraint}")

    # Add descriptions of key tables
    descriptions = {
        'customers': 'Contains B2B customer/account information including company details and energy consumption',
        'sales_reps': 'Sales representatives and account managers',
        'deals': 'Sales opportunities and closed deals with values and dates',
        'products': 'Energy products and services offered',
        'deal_line_items': 'Individual products/services within each deal',
        'commission_tiers': 'Commission rate structure based on deal values',
        'commissions': 'Actual commission payments to sales reps',
        'activities': 'Sales activities like calls, meetings, and emails',
        'sales_pipeline': 'VIEW: Current state of all deals in the pipeline',
        'monthly_sales_performance': 'VIEW: Aggregated monthly sales metrics by rep'
    }

    context.append("\n\nTABLE DESCRIPTIONS:")
    for table, description in descriptions.items():
        if table in schema_info or table.endswith('_performance') or table == 'sales_pipeline':
            context.append(f"  - {table}: {description}")

    return '\n'.join(context)
