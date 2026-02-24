"""
VLOOKUP and external file lookup utilities
Handles Excel-like VLOOKUP operations and cross-workbook references
"""

import pandas as pd
import openpyxl
from pathlib import Path
from typing import Any, Optional, List, Dict, Tuple


class VLookupHelper:
    """Utility class for VLOOKUP and lookup operations"""
    
    @staticmethod
    def vlookup(lookup_value: Any, table_array: pd.DataFrame, col_index: int, 
                range_lookup: bool = False, not_found_value: str = "N/A") -> Any:
        """
        Perform VLOOKUP-like operation
        
        Args:
            lookup_value: Value to search for (matches first column)
            table_array: DataFrame to search in
            col_index: Column index to return (1-based, like Excel)
            range_lookup: If True, allows approximate match (default False for exact)
            not_found_value: Value to return if not found
            
        Returns:
            Result from specified column or not_found_value if not found
        """
        if table_array.empty or lookup_value is None:
            return not_found_value
        
        # Get first column for lookup
        first_col = table_array.iloc[:, 0]
        
        # Convert col_index from 1-based to 0-based
        result_col_idx = col_index - 1
        
        if result_col_idx < 0 or result_col_idx >= len(table_array.columns):
            return not_found_value
        
        # Find matching row
        matches = first_col == lookup_value
        
        if not matches.any():
            return not_found_value
        
        # Get first match
        match_idx = matches.idxmax()
        result = table_array.iloc[match_idx, result_col_idx]
        
        # Return result or not_found_value
        return result if pd.notna(result) else not_found_value
    
    @staticmethod
    def vlookup_column(col_values: List[Any], lookup_table: pd.DataFrame, col_index: int,
                       not_found_value: str = "N/A") -> List[Any]:
        """
        Apply VLOOKUP to a column of values
        
        Args:
            col_values: List of lookup values
            lookup_table: DataFrame to search in
            col_index: Column index to return (1-based)
            not_found_value: Value to return if not found
            
        Returns:
            List of results
        """
        return [VLookupHelper.vlookup(val, lookup_table, col_index, 
                                      not_found_value=not_found_value) 
                for val in col_values]


class ExternalFileLookup:
    """Handle lookups in external Excel files with caching"""
    
    # Cache loaded files to avoid repeated I/O
    _file_cache: Dict[str, Dict[str, pd.DataFrame]] = {}
    
    @staticmethod
    def load_external_file(file_path: str, sheet_name: str) -> pd.DataFrame:
        """
        Load data from external Excel file with caching
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name to load
            
        Returns:
            DataFrame with loaded data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If sheet doesn't exist
        """
        file_path = str(Path(file_path).resolve())
        
        # Check cache
        if file_path in ExternalFileLookup._file_cache:
            if sheet_name in ExternalFileLookup._file_cache[file_path]:
                return ExternalFileLookup._file_cache[file_path][sheet_name]
        
        # Load file
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
            
            # Cache it
            if file_path not in ExternalFileLookup._file_cache:
                ExternalFileLookup._file_cache[file_path] = {}
            
            ExternalFileLookup._file_cache[file_path][sheet_name] = df
            
            return df
        except Exception as e:
            raise ValueError(f"Error loading sheet '{sheet_name}' from {file_path}: {str(e)}")
    
    @staticmethod
    def vlookup_external(lookup_value: Any, file_path: str, sheet_name: str,
                        col_index: int, not_found_value: str = "#N/A") -> Any:
        """
        Perform VLOOKUP on external Excel file
        
        Args:
            lookup_value: Value to search for
            file_path: Path to external Excel file
            sheet_name: Sheet name containing lookup table
            col_index: Column index to return (1-based)
            not_found_value: Value to return if not found
            
        Returns:
            Result from specified column or not_found_value
        """
        try:
            df = ExternalFileLookup.load_external_file(file_path, sheet_name)
            return VLookupHelper.vlookup(lookup_value, df, col_index, 
                                        not_found_value=not_found_value)
        except Exception as e:
            return f"Error: {str(e)[:50]}"
    
    @staticmethod
    def vlookup_external_column(col_values: List[Any], file_path: str, sheet_name: str,
                               col_index: int, not_found_value: str = "#N/A") -> List[Any]:
        """
        Apply VLOOKUP to external file for a column of values
        
        Args:
            col_values: List of lookup values
            file_path: Path to external Excel file
            sheet_name: Sheet name containing lookup table
            col_index: Column index to return (1-based)
            not_found_value: Value to return if not found
            
        Returns:
            List of results
        """
        try:
            df = ExternalFileLookup.load_external_file(file_path, sheet_name)
            return VLookupHelper.vlookup_column(col_values, df, col_index, 
                                               not_found_value=not_found_value)
        except Exception as e:
            error_msg = f"Error: {str(e)[:50]}"
            return [error_msg] * len(col_values)
    
    @staticmethod
    def clear_cache():
        """Clear the file cache"""
        ExternalFileLookup._file_cache.clear()


class NameFormatter:
    """Helper for formatting names (Last, First to First Last)"""
    
    @staticmethod
    def reform_name(full_name: str) -> str:
        """
        Reformat name from "Last, First" to "First Last"
        
        Args:
            full_name: Name in "Last, First" format or already "First Last"
            
        Returns:
            Name in "First Last" format, or original if parsing fails
        """
        if not full_name or pd.isna(full_name):
            return ""
        
        full_name = str(full_name).strip()
        
        # Check if it contains comma (Last, First format)
        if ',' in full_name:
            parts = [p.strip() for p in full_name.split(',')]
            if len(parts) >= 2:
                last_name = parts[0].strip()
                first_name = parts[1].strip().split()[0]  # Get first word of first name
                return f"{first_name} {last_name}"
        
        # Try to use Excel PROPER function equivalent
        return full_name.title()
