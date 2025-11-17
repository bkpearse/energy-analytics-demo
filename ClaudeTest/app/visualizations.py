"""
Data visualization utilities using Plotly.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Visualizer:
    """Creates visualizations from query results."""

    def __init__(self):
        """Initialize visualizer with default styling."""
        self.color_scheme = px.colors.qualitative.Set2

    def create_visualization(self,
                           df: pd.DataFrame,
                           viz_type: str,
                           columns_to_visualize: Optional[Dict[str, str]] = None,
                           title: Optional[str] = None) -> Optional[go.Figure]:
        """
        Create a visualization based on the specified type.

        Args:
            df: DataFrame with query results
            viz_type: Type of visualization (table, bar, line, pie, scatter)
            columns_to_visualize: Dictionary with column mappings (x, y, etc.)
            title: Optional title for the chart

        Returns:
            Plotly figure object or None if visualization cannot be created
        """
        if df.empty:
            logger.warning("Cannot create visualization: DataFrame is empty")
            return None

        try:
            if viz_type == 'table':
                return self._create_table(df, title)
            elif viz_type == 'bar':
                return self._create_bar_chart(df, columns_to_visualize, title)
            elif viz_type == 'line':
                return self._create_line_chart(df, columns_to_visualize, title)
            elif viz_type == 'pie':
                return self._create_pie_chart(df, columns_to_visualize, title)
            elif viz_type == 'scatter':
                return self._create_scatter_plot(df, columns_to_visualize, title)
            else:
                logger.warning(f"Unknown visualization type: {viz_type}")
                return self._create_table(df, title)
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            # Fallback to table view
            return self._create_table(df, title)

    def _create_table(self, df: pd.DataFrame, title: Optional[str] = None) -> go.Figure:
        """Create an interactive table."""
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(df.columns),
                fill_color='paleturquoise',
                align='left',
                font=dict(size=12, color='black')
            ),
            cells=dict(
                values=[df[col] for col in df.columns],
                fill_color='lavender',
                align='left',
                font=dict(size=11)
            )
        )])

        if title:
            fig.update_layout(title=title)

        return fig

    def _create_bar_chart(self,
                         df: pd.DataFrame,
                         columns: Optional[Dict[str, str]] = None,
                         title: Optional[str] = None) -> go.Figure:
        """Create a bar chart."""
        # Auto-detect columns if not specified
        if not columns or 'x' not in columns or 'y' not in columns:
            columns = self._auto_detect_columns(df, 'bar')

        x_col = columns.get('x')
        y_col = columns.get('y')
        color_col = columns.get('color')

        if not x_col or not y_col:
            return self._create_table(df, title)

        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
            color_discrete_sequence=self.color_scheme
        )

        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
            hovermode='x unified'
        )

        return fig

    def _create_line_chart(self,
                          df: pd.DataFrame,
                          columns: Optional[Dict[str, str]] = None,
                          title: Optional[str] = None) -> go.Figure:
        """Create a line chart."""
        # Auto-detect columns if not specified
        if not columns or 'x' not in columns or 'y' not in columns:
            columns = self._auto_detect_columns(df, 'line')

        x_col = columns.get('x')
        y_col = columns.get('y')
        color_col = columns.get('color')

        if not x_col or not y_col:
            return self._create_table(df, title)

        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
            color_discrete_sequence=self.color_scheme,
            markers=True
        )

        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
            hovermode='x unified'
        )

        return fig

    def _create_pie_chart(self,
                         df: pd.DataFrame,
                         columns: Optional[Dict[str, str]] = None,
                         title: Optional[str] = None) -> go.Figure:
        """Create a pie chart."""
        # Auto-detect columns if not specified
        if not columns or 'labels' not in columns or 'values' not in columns:
            columns = self._auto_detect_columns(df, 'pie')

        labels_col = columns.get('labels')
        values_col = columns.get('values')

        if not labels_col or not values_col:
            return self._create_table(df, title)

        fig = px.pie(
            df,
            names=labels_col,
            values=values_col,
            title=title,
            color_discrete_sequence=self.color_scheme
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')

        return fig

    def _create_scatter_plot(self,
                            df: pd.DataFrame,
                            columns: Optional[Dict[str, str]] = None,
                            title: Optional[str] = None) -> go.Figure:
        """Create a scatter plot."""
        # Auto-detect columns if not specified
        if not columns or 'x' not in columns or 'y' not in columns:
            columns = self._auto_detect_columns(df, 'scatter')

        x_col = columns.get('x')
        y_col = columns.get('y')
        color_col = columns.get('color')
        size_col = columns.get('size')

        if not x_col or not y_col:
            return self._create_table(df, title)

        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            size=size_col,
            title=title,
            color_discrete_sequence=self.color_scheme
        )

        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title()
        )

        return fig

    def _auto_detect_columns(self, df: pd.DataFrame, viz_type: str) -> Dict[str, str]:
        """
        Auto-detect which columns to use for visualization.

        Args:
            df: DataFrame with data
            viz_type: Type of visualization

        Returns:
            Dictionary with column mappings
        """
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        non_numeric_cols = df.select_dtypes(exclude=['number']).columns.tolist()

        if viz_type in ['bar', 'line', 'scatter']:
            # First column as x, first numeric as y
            x_col = df.columns[0] if len(df.columns) > 0 else None
            y_col = numeric_cols[0] if numeric_cols else (df.columns[1] if len(df.columns) > 1 else None)

            result = {'x': x_col, 'y': y_col}

            # Add color if there's a third column
            if len(df.columns) > 2 and len(non_numeric_cols) > 1:
                result['color'] = non_numeric_cols[1]

            return result

        elif viz_type == 'pie':
            # First non-numeric as labels, first numeric as values
            labels_col = non_numeric_cols[0] if non_numeric_cols else df.columns[0]
            values_col = numeric_cols[0] if numeric_cols else (df.columns[1] if len(df.columns) > 1 else None)

            return {'labels': labels_col, 'values': values_col}

        return {}

    def format_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Format DataFrame for display (round numbers, format dates, etc.).

        Args:
            df: DataFrame to format

        Returns:
            Formatted DataFrame
        """
        df = df.copy()

        for col in df.columns:
            # Round numeric columns
            if pd.api.types.is_numeric_dtype(df[col]):
                if df[col].dtype == 'float64':
                    df[col] = df[col].round(2)

            # Format datetime columns
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M')

        return df
