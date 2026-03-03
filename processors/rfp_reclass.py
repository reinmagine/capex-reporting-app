"""
RFP and Reclass file processors (STEP 12-13)
Handles currency conversion and total calculation with CBIP filtering
Supports both traditional (pandas-based) and formula-based (fast) processing
"""
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter
from processors.base import BaseProcessor
from config import OUTPUT_COLUMNS


class RFPReclassProcessor(BaseProcessor):
    """Processor for RFP and Reclass files"""
    
    def __init__(self, file_type):
        if file_type not in ['rfp', 'reclass']:
            raise ValueError(f"Invalid file type: {file_type}")
        super().__init__(file_type)
        self.wb = None
        self.ws = None
        self.file_path = None
    
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
    
    def process_with_total_formula(self, file_path, exchange_rates=None, remove_cbip=False):
        """
        Fast formula-based processing (instant file save)
        Creates Excel formulas for currency conversion instead of calculating values
        
        Args:
            file_path: Path to input file
            exchange_rates: Optional custom exchange rates dict
            remove_cbip: Whether to remove M-CBIP-25 entries
        """
        # Load file with openpyxl
        self.file_path = file_path
        self.df = pd.read_excel(file_path)
        self.wb = openpyxl.load_workbook(file_path)
        self.ws = self.wb.active
        
        # Validate columns
        self.validate_and_prepare()
        
        if exchange_rates is None:
            exchange_rates = {'PHP': 57, 'SGD': 1.34}
        
        # Get column mappings
        currency_col = self.columns.get('trans_currency')
        amount_col = self.columns.get('value_amount')
        
        if not all([currency_col, amount_col]):
            raise ValueError(f"Required columns not found for formula processing. Found: {self.columns}")
        
        # Get column indices
        currency_idx = self._get_column_index(currency_col)
        amount_idx = self._get_column_index(amount_col)
        
        currency_letter = get_column_letter(currency_idx)
        amount_letter = get_column_letter(amount_idx)
        
        # Add new column for USD conversion with formula
        usd_col_idx = self.ws.max_column + 1
        usd_col_letter = get_column_letter(usd_col_idx)
        
        # Add header
        self.ws.cell(row=1, column=usd_col_idx).value = OUTPUT_COLUMNS['usd_amount']
        
        # Add formula for currency conversion (case-insensitive using UPPER())
        php_rate = exchange_rates.get('PHP', 57)
        sgd_rate = exchange_rates.get('SGD', 1.34)
        
        # Get Object column for checking subtotal rows
        object_col = self.columns.get('object')
        object_idx = None
        if object_col:
            try:
                object_idx = self._get_column_index(object_col)
            except ValueError:
                pass  # Object column not found, write formulas for all rows
        
        for row in range(2, self.ws.max_row + 1):
            cell_obj = self.ws.cell(row=row, column=usd_col_idx)
            
            # Check if this is a subtotal row (where Object column is empty)
            is_subtotal = False
            if object_idx:
                object_cell = self.ws.cell(row=row, column=object_idx)
                if not object_cell.value or str(object_cell.value).strip() == '':
                    # This is a subtotal row - clear the cell and skip
                    cell_obj.value = None
                    is_subtotal = True
            
            # Only write formula for data rows (not subtotal rows)
            if not is_subtotal:
                # Use UPPER() to make currency comparison case-insensitive
                formula = (
                    f"=IF(UPPER({currency_letter}{row})=\"PHP\",{amount_letter}{row}/{php_rate},"
                    f"IF(UPPER({currency_letter}{row})=\"SGD\",{amount_letter}{row}/{sgd_rate},"
                    f"{amount_letter}{row}))"
                )
                cell_obj.value = formula
        
        return self
    
    def _get_column_index(self, column_name: str) -> int:
        """Get column index (1-based) from column name in header row"""
        for idx, cell in enumerate(self.ws[1], start=1):
            if cell.value == column_name:
                return idx
        raise ValueError(f"Column '{column_name}' not found in row 1")
