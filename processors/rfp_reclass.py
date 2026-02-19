"""
RFP and Reclass file processors (STEP 12-13)
Handles currency conversion and total calculation with CBIP filtering
"""
import pandas as pd
from processors.base import BaseProcessor
from config import OUTPUT_COLUMNS


class RFPReclassProcessor(BaseProcessor):
    """Processor for RFP and Reclass files"""
    
    def __init__(self, file_type):
        if file_type not in ['rfp', 'reclass']:
            raise ValueError(f"Invalid file type: {file_type}")
        super().__init__(file_type)
    
    def process_basic(self, exchange_rates=None, remove_cbip=False):
        """
        Basic RFP/Reclass processing: Convert currency and calculate totals
        
        Args:
            exchange_rates: optional custom exchange rates dict
            remove_cbip: whether to remove M-CBIP-25 entries
            
        Returns:
            Processed DataFrame
        """
        # Remove M-CBIP-25 if requested
        if remove_cbip:
            self.remove_marker('cbip_code', 'object')
        
        # STEP 5/12/13: Convert currency to USD
        self.convert_currency(exchange_rates)
        
        # Blank out amounts for subtotal rows (rows with empty Object)
        self.blank_subtotal_rows('object')
        
        return self.df
    
    def calculate_total(self, exclude_blanks=True):
        """
        Calculate total amount from USD conversion column
        
        Args:
            exclude_blanks: whether to exclude blank Object rows
            
        Returns:
            Total amount
        """
        if OUTPUT_COLUMNS['usd_amount'] not in self.df.columns:
            return 0
        
        if exclude_blanks:
            object_col = self.columns.get('object')
            if object_col:
                valid_rows = self.df[
                    self.df[object_col].notna() & (self.df[object_col] != '')
                ]
                return valid_rows[OUTPUT_COLUMNS['usd_amount']].sum()
        
        return self.df[OUTPUT_COLUMNS['usd_amount']].sum()
    
    def add_total_row(self, total_label='TOTAL AMOUNT'):
        """
        Add total row to dataframe
        
        Args:
            total_label: label for total row
            
        Returns:
            DataFrame with total row appended
        """
        total = self.calculate_total()
        
        # Create total row
        total_row = pd.DataFrame(
            [[''] * (len(self.df.columns) - 1) + [total]],
            columns=self.df.columns
        )
        total_row.iloc[0, 0] = total_label
        
        self.df = pd.concat([self.df, total_row], ignore_index=True)
        
        return self.df
    
    def process_with_total(self, exchange_rates=None, remove_cbip=False, 
                          total_label='TOTAL AMOUNT'):
        """
        Process file and add total row
        
        Args:
            exchange_rates: optional custom exchange rates dict
            remove_cbip: whether to remove M-CBIP-25 entries
            total_label: label for total row
            
        Returns:
            Processed DataFrame with total
        """
        self.process_basic(exchange_rates, remove_cbip)
        self.add_total_row(total_label)
        
        return self.df
    
    def get_summary(self):
        """
        Get processing summary
        
        Returns:
            Dictionary with summary stats
        """
        total = self.calculate_total()
        object_col = self.columns.get('object')
        
        valid_rows = self.df.copy()
        if object_col:
            valid_rows = self.df[
                self.df[object_col].notna() & (self.df[object_col] != '')
            ]
        
        summary = {
            'file_type': self.file_type,
            'total_rows': len(self.df),
            'valid_rows': len(valid_rows),
            'total_usd': round(total, 2),
            'average_amount': round(valid_rows[OUTPUT_COLUMNS['usd_amount']].mean(), 2)
            if OUTPUT_COLUMNS['usd_amount'] in valid_rows.columns else 0
        }
        
        return summary
