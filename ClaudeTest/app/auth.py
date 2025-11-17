"""
Authentication and authorization utilities.
"""
import yaml
import streamlit as st
from typing import Dict, Any, Optional
import bcrypt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthManager:
    """Handles user authentication and authorization."""

    def __init__(self, config_path: str = 'config/users.yaml'):
        """
        Initialize authentication manager.

        Args:
            config_path: Path to users configuration file
        """
        self.config_path = config_path
        self.users = {}
        self.roles = {}
        self._load_config()

    def _load_config(self):
        """Load user and role configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.users = config.get('credentials', {}).get('usernames', {})
                self.roles = config.get('roles', {})
                logger.info(f"Loaded {len(self.users)} users and {len(self.roles)} roles")
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            self.users = {}
            self.roles = {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.users = {}
            self.roles = {}

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate a user.

        Args:
            username: Username
            password: Password

        Returns:
            True if authentication successful, False otherwise
        """
        if username not in self.users:
            return False

        user_data = self.users[username]
        stored_hash = user_data.get('password', '').encode()

        try:
            return bcrypt.checkpw(password.encode(), stored_hash)
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user information.

        Args:
            username: Username

        Returns:
            Dictionary with user information or None if user not found
        """
        if username not in self.users:
            return None

        user_data = self.users[username].copy()
        role = user_data.get('role', 'sales_rep')

        # Add role permissions
        role_info = self.roles.get(role, {})
        user_data['permissions'] = role_info

        return user_data

    def get_user_role(self, username: str) -> str:
        """
        Get user's role.

        Args:
            username: Username

        Returns:
            Role name
        """
        if username not in self.users:
            return 'sales_rep'  # Default role
        return self.users[username].get('role', 'sales_rep')

    def has_permission(self, username: str, permission: str) -> bool:
        """
        Check if user has a specific permission.

        Args:
            username: Username
            permission: Permission name

        Returns:
            True if user has permission, False otherwise
        """
        user_info = self.get_user_info(username)
        if not user_info:
            return False

        permissions = user_info.get('permissions', {})
        return permissions.get(permission, False)

    def get_max_query_rows(self, username: str) -> int:
        """
        Get maximum number of rows user can query.

        Args:
            username: Username

        Returns:
            Maximum number of rows
        """
        user_info = self.get_user_info(username)
        if not user_info:
            return 500  # Default limit

        permissions = user_info.get('permissions', {})
        return permissions.get('max_query_rows', 500)

    def apply_row_level_security(self, username: str, sql: str) -> str:
        """
        Apply row-level security filters to SQL query based on user role.

        Args:
            username: Username
            sql: Original SQL query

        Returns:
            Modified SQL query with security filters applied
        """
        user_info = self.get_user_info(username)
        if not user_info:
            return sql

        permissions = user_info.get('permissions', {})
        role = user_info.get('role', 'sales_rep')

        # If user is admin or analyst, no filtering needed
        if role in ['admin', 'analyst']:
            return sql

        # For sales reps, filter to only their own data
        if role == 'sales_rep':
            # This is a simplified example - in production, you'd need more sophisticated parsing
            # You might want to use a SQL parser library like sqlparse
            if 'WHERE' in sql.upper():
                sql = sql.replace('WHERE', f"WHERE sales_rep_id = '{username}' AND", 1)
            else:
                # Find the FROM clause and add WHERE after it
                # This is simplified - production code should use proper SQL parsing
                sql = sql + f" WHERE sales_rep_id = '{username}'"

        # For managers, filter to their team
        if role == 'manager':
            if not permissions.get('can_view_all_reps', False):
                # You would need to implement team filtering logic here
                pass

        return sql

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Generate bcrypt hash for a password.

        Args:
            password: Plain text password

        Returns:
            Bcrypt hash string
        """
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def init_session_state():
    """Initialize Streamlit session state for authentication."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None


def login_page(auth_manager: AuthManager):
    """
    Display login page.

    Args:
        auth_manager: AuthManager instance

    Returns:
        True if login successful, False otherwise
    """
    st.title("🔐 Analytics Chat Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if auth_manager.authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_info = auth_manager.get_user_info(username)
                st.success("Login successful!")
                st.rerun()
                return True
            else:
                st.error("Invalid username or password")
                return False

    return False


def logout():
    """Logout current user."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_info = None
    st.rerun()
