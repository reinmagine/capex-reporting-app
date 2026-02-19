"""
Flexible column finder utility
Handles finding columns with various naming conventions
"""
import pandas as pd
from config import COLUMN_MAPPINGS


class ColumnMapper:
    """Utility for finding columns by flexible name matching"""
    
    @staticmethod
    def find_column(df, column_aliases):
        """
        Find a column in DataFrame by checking multiple possible names
        
        Args:
            df: pandas DataFrame
            column_aliases: list of possible column names
            
        Returns:
            Column name if found, None otherwise
        """
        if not column_aliases:
            return None
            
        df_cols = df.columns.tolist()
        
        # First try exact match (case-insensitive)
        for col in df_cols:
            if col.lower() in [alias.lower() for alias in column_aliases]:
                return col
        
        # Then try partial match
        for col in df_cols:
            col_lower = col.lower()
            for alias in column_aliases:
                if alias.lower() in col_lower or col_lower in alias.lower():
                    return col
        
        return None
    
    @staticmethod
    def find_columns_for_file_type(df, file_type):
        """
        Find all expected columns for a given file type
        
        Args:
            df: pandas DataFrame
            file_type: 'cji5', 'cji3', 'rfp', 'reclass', or 'zmm'
            
        Returns:
            Dictionary of found columns or None
        """
        if file_type not in COLUMN_MAPPINGS:
            return None
        
        mappings = COLUMN_MAPPINGS[file_type]
        found_cols = {}
        
        for column_key, aliases in mappings.items():
            found_col = ColumnMapper.find_column(df, aliases)
            found_cols[column_key] = found_col
        
        return found_cols
    
    @staticmethod
    def get_column_safety(df, column_aliases, default=None):
        """
        Get a column with a default fallback
        
        Args:
            df: pandas DataFrame
            column_aliases: list of possible column names
            default: value to return if not found
            
        Returns:
            Column name or default value
        """
        col = ColumnMapper.find_column(df, column_aliases)
        return col if col is not None else default
