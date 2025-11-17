"""
Main Streamlit application for AI-powered analytics chat.
"""
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import DatabaseManager
from app.llm import SQLGenerator, build_schema_context
from app.visualizations import Visualizer
from app.auth import AuthManager, init_session_state, login_page, logout

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Analytics Chat",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize managers
@st.cache_resource
def get_managers():
    """Initialize and cache manager instances."""
    db_manager = DatabaseManager()
    auth_manager = AuthManager()
    visualizer = Visualizer()
    return db_manager, auth_manager, visualizer


def initialize_sql_generator(db_manager):
    """Initialize SQL generator with schema context."""
    if 'sql_generator' not in st.session_state:
        schema_info = db_manager.get_schema_info()
        schema_context = build_schema_context(schema_info)
        st.session_state.sql_generator = SQLGenerator(schema_context)
    return st.session_state.sql_generator


def display_sidebar(auth_manager):
    """Display sidebar with user info and controls."""
    with st.sidebar:
        st.title("📊 Analytics Chat")

        if st.session_state.authenticated:
            user_info = st.session_state.user_info
            st.write(f"**User:** {user_info.get('name', st.session_state.username)}")
            st.write(f"**Role:** {user_info.get('role', 'N/A')}")

            if st.button("🚪 Logout"):
                logout()

            st.divider()

            st.subheader("💡 Example Questions")
            examples = [
                "Show top 10 sales reps by revenue this month",
                "What's our total pipeline value by deal stage?",
                "Show commission payments in the last quarter",
                "Which products generate the most revenue?",
                "Show sales trends over the last 6 months",
                "List all open deals over $50,000",
                "What's the average deal size by team?",
                "Show customer acquisition by month"
            ]

            for example in examples:
                if st.button(example, key=f"example_{hash(example)}", use_container_width=True):
                    st.session_state.current_question = example
                    st.rerun()

            st.divider()

            # Display user permissions
            with st.expander("ℹ️ Your Permissions"):
                perms = user_info.get('permissions', {})
                st.write(f"View Sensitive Data: {'✅' if perms.get('can_view_sensitive') else '❌'}")
                st.write(f"Export Data: {'✅' if perms.get('can_export') else '❌'}")
                st.write(f"View All Reps: {'✅' if perms.get('can_view_all_reps') else '❌'}")
                st.write(f"View Commissions: {'✅' if perms.get('can_view_commissions') else '❌'}")
                st.write(f"Max Query Rows: {perms.get('max_query_rows', 500)}")


def display_query_result(df, explanation, viz_type, columns_to_visualize, visualizer, auth_manager):
    """Display query results with visualization and explanation."""
    # Show explanation
    with st.expander("📝 Query Explanation", expanded=False):
        st.write(explanation)

    # Show results count
    st.info(f"📊 Retrieved {len(df)} rows")

    # Create visualization
    if viz_type and viz_type != 'table':
        try:
            fig = visualizer.create_visualization(
                df,
                viz_type,
                columns_to_visualize,
                title="Query Results"
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not create {viz_type} visualization: {e}")
            viz_type = 'table'

    # Always show data table
    st.subheader("📋 Data Table")
    formatted_df = visualizer.format_dataframe(df)
    st.dataframe(formatted_df, use_container_width=True, height=400)

    # Export option
    if st.session_state.user_info.get('permissions', {}).get('can_export', False):
        csv = formatted_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="query_results.csv",
            mime="text/csv"
        )


def main():
    """Main application logic."""
    # Initialize session state
    init_session_state()

    # Get managers
    db_manager, auth_manager, visualizer = get_managers()

    # Check authentication
    if not st.session_state.authenticated:
        login_page(auth_manager)
        return

    # Display sidebar
    display_sidebar(auth_manager)

    # Main content area
    st.title("💬 Ask Questions About Your Data")
    st.write("Ask questions in natural language and get instant insights from your sales data.")

    # Initialize SQL generator
    sql_generator = initialize_sql_generator(db_manager)

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""

    # Display chat history
    for i, chat in enumerate(st.session_state.chat_history):
        with st.chat_message("user"):
            st.write(chat['question'])

        with st.chat_message("assistant"):
            if chat.get('error'):
                st.error(chat['error'])
            else:
                display_query_result(
                    chat['data'],
                    chat['explanation'],
                    chat['viz_type'],
                    chat.get('columns_to_visualize'),
                    visualizer,
                    auth_manager
                )

                # Show SQL query
                with st.expander("🔍 View SQL Query"):
                    st.code(chat['sql'], language='sql')

    # Chat input
    question = st.chat_input("Ask a question about your data...")

    # Handle example button clicks
    if st.session_state.current_question:
        question = st.session_state.current_question
        st.session_state.current_question = ""

    if question:
        # Display user message
        with st.chat_message("user"):
            st.write(question)

        # Generate and execute query
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                # Generate SQL
                result = sql_generator.generate_sql(question)

                if not result['success']:
                    st.error(f"❌ Error: {result['error']}")
                    st.session_state.chat_history.append({
                        'question': question,
                        'error': result['error']
                    })
                    return

                sql = result['sql']
                explanation = result['explanation']
                viz_type = result['visualization_type']
                columns_to_visualize = result.get('columns_to_visualize')

                # Apply row-level security
                sql = auth_manager.apply_row_level_security(st.session_state.username, sql)

                # Validate query
                is_valid, error_msg = db_manager.validate_query(sql)
                if not is_valid:
                    st.error(f"❌ Security Error: {error_msg}")
                    st.session_state.chat_history.append({
                        'question': question,
                        'error': error_msg
                    })
                    return

                # Apply row limit
                max_rows = auth_manager.get_max_query_rows(st.session_state.username)
                if 'LIMIT' not in sql.upper():
                    sql = sql.rstrip(';') + f' LIMIT {max_rows}'

                # Execute query
                try:
                    df = db_manager.execute_query(sql)

                    if df.empty:
                        st.warning("⚠️ No results found for your query.")
                        st.session_state.chat_history.append({
                            'question': question,
                            'error': 'No results found'
                        })
                        return

                    # Display results
                    display_query_result(
                        df,
                        explanation,
                        viz_type,
                        columns_to_visualize,
                        visualizer,
                        auth_manager
                    )

                    # Show SQL query
                    with st.expander("🔍 View SQL Query"):
                        st.code(sql, language='sql')

                    # Add to chat history
                    st.session_state.chat_history.append({
                        'question': question,
                        'sql': sql,
                        'data': df,
                        'explanation': explanation,
                        'viz_type': viz_type,
                        'columns_to_visualize': columns_to_visualize
                    })

                except Exception as e:
                    st.error(f"❌ Database Error: {str(e)}")
                    st.session_state.chat_history.append({
                        'question': question,
                        'error': str(e)
                    })

    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()


if __name__ == "__main__":
    main()
