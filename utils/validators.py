"""
File validation utility
Validates file structure and required columns before processing
"""
import pandas as pd
from utils.column_mapper import ColumnMapper
from config import COLUMN_MAPPINGS


class FileValidator:
    """Validates Excel files before processing"""
    
    @staticmethod
    def validate_file_type(df, file_type):
        """
        Validate if file structure matches expected file type
        
        Args:
            df: pandas DataFrame
            file_type: 'cji5', 'cji3', 'rfp', 'reclass', or 'zmm'
            
        Returns:
            Tuple (is_valid: bool, missing_columns: list, found_columns: dict)
        """
        if file_type not in COLUMN_MAPPINGS:
            return False, [f"Unknown file type: {file_type}"], {}
        
        required_mappings = COLUMN_MAPPINGS[file_type]
        found_cols = {}
        missing = []
        
        for col_key, aliases in required_mappings.items():
            found_col = ColumnMapper.find_column(df, aliases)
            if found_col:
                found_cols[col_key] = found_col
            else:
                missing.append(f"{col_key} (aliases: {', '.join(aliases)})")
        
        # For CJI files, both reference/purch_doc and currency columns are required
        required_keys = {
            'cji5': ['reference_doc', 'trans_currency', 'value_amount'],
            'cji3': ['purch_doc', 'trans_currency', 'value_amount'],
            'rfp': ['trans_currency', 'value_amount'],
            'reclass': ['trans_currency', 'value_amount'],
            'zmm': ['ariba_pr_ref']
        }.get(file_type, [])
        
        is_valid = all(key in found_cols and found_cols[key] is not None for key in required_keys)
        
        return is_valid, missing, found_cols
    
    @staticmethod
    def validate_and_get_columns(df, file_type):
        """
        Validate file and return column mappings, raising exception if invalid
        
        Args:
            df: pandas DataFrame
            file_type: file type to validate
            
        Returns:
            Dictionary of found columns
            
        Raises:
            ValueError if file is invalid
        """
        is_valid, missing, found_cols = FileValidator.validate_file_type(df, file_type)
        
        if not is_valid:
            raise ValueError(
                f"Invalid {file_type.upper()} file structure. Missing: {', '.join(missing)}"
            )
        
        return found_cols
    
    @staticmethod
    def check_empty_rows(df):
        """
        Check for completely empty rows
        
        Returns:
            Count of empty rows
        """
        empty_rows = df.dropna(how='all')
        return len(df) - len(empty_rows)
    
    @staticmethod
    def check_data_quality(df, percent_threshold=10):
        """
        Check data quality - warn if too many null values
        
        Args:
            df: pandas DataFrame
            percent_threshold: warning threshold percentage
            
        Returns:
            Dict with quality metrics
        """
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isna().sum().sum()
        null_percent = (null_cells / total_cells) * 100
        
        quality = {
            'total_cells': total_cells,
            'null_cells': null_cells,
            'null_percent': null_percent,
            'is_acceptable': null_percent <= percent_threshold,
            'message': f"Data quality: {null_percent:.1f}% null values"
        }
        
        if not quality['is_acceptable']:
            quality['message'] += f" (Warning: exceeds {percent_threshold}% threshold)"
        
        return quality
    
    @staticmethod
    def get_validation_report(df, file_type):
        """
        Get comprehensive validation report
        
        Returns:
            Dictionary with full validation details
        """
        is_valid, missing, found_cols = FileValidator.validate_file_type(df, file_type)
        quality = FileValidator.check_data_quality(df)
        empty_count = FileValidator.check_empty_rows(df)
        
        report = {
            'is_valid': is_valid,
            'file_type': file_type,
            'row_count': len(df),
            'column_count': len(df.columns),
            'empty_rows': empty_count,
            'found_columns': found_cols,
            'missing_columns': missing,
            'data_quality': quality,
            'valid_for_processing': is_valid and quality['is_acceptable']
        }
        
        return report
