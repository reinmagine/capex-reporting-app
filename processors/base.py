"""
Base processor class for file processing
Provides common functionality for all file type processors
"""
import pandas as pd
import re
from utils.column_mapper import ColumnMapper
from utils.currency import CurrencyConverter
from utils.validators import FileValidator
from config import SPECIAL_MARKERS, OUTPUT_COLUMNS


class BaseProcessor:
    """Base class for file processors"""
    
    def __init__(self, file_type):
        self.file_type = file_type
        self.df = None
        self.columns = {}
    
    def load_file(self, filepath):
        """Load Excel file"""
        self.df = pd.read_excel(filepath)
        return self.df
    
    def validate_and_prepare(self):
        """Validate file and prepare columns"""
        self.columns = FileValidator.validate_and_get_columns(self.df, self.file_type)
        return self.columns
    
    def get_validation_report(self):
        """Get file validation report"""
        return FileValidator.get_validation_report(self.df, self.file_type)
    
    def convert_reference_to_numeric(self, column_key):
        """
        Convert reference/document number column to numeric format
        
        Args:
            column_key: key in self.columns dict (e.g., 'reference_doc', 'purch_doc')
        """
        if column_key not in self.columns or self.columns[column_key] is None:
            return
        
        col_name = self.columns[column_key]
        self.df[col_name] = pd.to_numeric(self.df[col_name], errors='coerce')
    
    def convert_currency(self, exchange_rates=None):
        """
        Convert currency to USD
        
        Args:
            exchange_rates: optional dict of exchange rates
        """
        currency_col = self.columns.get('trans_currency')
        amount_col = self.columns.get('value_amount')
        
        if not currency_col or not amount_col:
            raise ValueError("Currency or amount column not found")
        
        self.df = CurrencyConverter.apply_currency_conversion(
            self.df,
            currency_col,
            amount_col,
            output_col=OUTPUT_COLUMNS['usd_amount'],
            exchange_rates=exchange_rates
        )
    
    def blank_subtotal_rows(self, identifier_col_key='object'):
        """
        Blank out Amount_USD for subtotal rows (rows where identifier column is empty)
        
        Args:
            identifier_col_key: column key to check for blank rows (e.g., 'object', 'project')
        """
        if identifier_col_key not in self.columns or self.columns[identifier_col_key] is None:
            return
        
        col_name = self.columns[identifier_col_key]
        if OUTPUT_COLUMNS['usd_amount'] in self.df.columns:
            mask = self.df[col_name].isna() | (self.df[col_name] == '')
            self.df.loc[mask, OUTPUT_COLUMNS['usd_amount']] = None
    
    def filter_by_marker(self, marker_key, column_key=None):
        """
        Filter dataframe to include only rows with specific marker
        
        Args:
            marker_key: key in SPECIAL_MARKERS (e.g., 'car_plan')
            column_key: column key to search in (defaults based on marker_key)
            
        Returns:
            Filtered DataFrame
        """
        marker = SPECIAL_MARKERS.get(marker_key)
        if not marker:
            return self.df.copy()
        
        # Determine column to search
        if column_key and column_key in self.columns and self.columns[column_key]:
            search_col = self.columns[column_key]
        elif marker_key == 'car_plan':
            search_col = self.columns.get('project')
        else:
            search_col = self.columns.get('object')
        
        if not search_col:
            return self.df.copy()
        
        return self.df[self.df[search_col].astype(str).str.contains(marker, na=False)]
    
    def remove_marker(self, marker_key, column_key='object'):
        """
        Remove rows containing specific marker from dataframe
        
        Args:
            marker_key: key in SPECIAL_MARKERS (e.g., 'cbip_code')
            column_key: column key to search in
        """
        marker = SPECIAL_MARKERS.get(marker_key)
        if not marker or column_key not in self.columns or not self.columns[column_key]:
            return self.df
        
        search_col = self.columns[column_key]
        original_count = len(self.df)
        self.df = self.df[~self.df[search_col].astype(str).str.contains(marker, na=False)]
        removed_count = original_count - len(self.df)
        
        return removed_count
    
    def delimit_pr_number(self, pr_value):
        """
        Remove v1, v2, v3, etc. from PR numbers
        
        Args:
            pr_value: PR number value
            
        Returns:
            Delimited PR number
        """
        if pd.isna(pr_value):
            return pr_value
        
        pr_str = str(pr_value)
        # Remove patterns like v1, v2, v3, etc.
        pr_str = re.sub(r'v\d+', '', pr_str, flags=re.IGNORECASE)
        pr_str = pr_str.strip()
        
        return pr_str
    
    def get_dataframe(self):
        """Return processed dataframe"""
        return self.df
    
    def save(self, filepath, sheet_name='Sheet1', index=False):
        """
        Save dataframe to Excel
        
        Args:
            filepath: output file path
            sheet_name: Excel sheet name
            index: whether to include index
        """
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            self.df.to_excel(writer, sheet_name=sheet_name, index=index)
