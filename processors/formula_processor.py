"""
Formula-based processor for all file types (CJI, RFP, Reclass, ZMM)
Generates Excel formulas instead of calculating values in pandas
Dramatically faster processing - formulas calculated by Excel when opened
"""

import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter
from pathlib import Path
from typing import Dict, Optional
import shutil
from utils.column_mapper import ColumnMapper
from utils.validators import FileValidator
from config import SPECIAL_MARKERS, OUTPUT_COLUMNS


class FormulaBasedProcessor:
    """
    Base processor that uses Excel formulas instead of pandas calculations
    Creates new columns with formulas that Excel evaluates on open
    """
    
    def __init__(self, file_type: str):
        self.file_type = file_type
        self.file_path = None
        self.df = None
        self.wb = None
        self.ws = None
        self.columns = {}
        self.output_path = None
        self.last_col_idx = 0  # Track where to add new columns
        
    def load_file(self, filepath: str) -> bool:
        """Load Excel file using both pandas and openpyxl"""
        try:
            self.file_path = filepath
            # Load with pandas for validation and metadata
            self.df = pd.read_excel(filepath)
            # Load workbook with openpyxl for formula writing
            self.wb = openpyxl.load_workbook(filepath)
            self.ws = self.wb.active
            return True
        except Exception as e:
            raise Exception(f"Error loading file: {str(e)}")
    
    def validate_and_prepare(self):
        """Validate file and map columns"""
        self.columns = FileValidator.validate_and_get_columns(self.df, self.file_type)
        self.last_col_idx = self.ws.max_column
        return self.columns
    
    def add_formula_column(self, header: str, formula_template: str, 
                          start_row: int = 2) -> int:
        """
        Add a new column with formula to worksheet
        
        Args:
            header: Column header text
            formula_template: Formula template with {row} placeholder (e.g., "=A{row}*2")
            start_row: First row to add formula (default 2, skipping header)
            
        Returns:
            Column index added
        """
        col_idx = self.last_col_idx + 1
        col_letter = get_column_letter(col_idx)
        
        # Add header
        self.ws.cell(row=1, column=col_idx).value = header
        
        # Add formulas
        last_row = self.ws.max_row
        for row in range(start_row, last_row + 1):
            formula = formula_template.format(row=row)
            self.ws.cell(row=row, column=col_idx).value = formula
        
        self.last_col_idx = col_idx
        return col_idx
    
    def save(self, output_path: str):
        """
        Save workbook with formulas intact
        
        Args:
            output_path: Path to save processed file
        """
        self.output_path = output_path
        self.wb.save(output_path)


class CJIFormulaProcessor(FormulaBasedProcessor):
    """Formula-based CJI processor - much faster than pandas approach"""
    
    def process_basic(self, exchange_rates: Optional[Dict] = None):
        """
        Process CJI file using formulas
        STEP 4: Convert reference to numeric
        STEP 5: Convert currency to USD
        """
        if self.df is None or not self.wb:
            raise ValueError("File not loaded. Call load_file() first.")
        
        if exchange_rates is None:
            exchange_rates = {'PHP': 57, 'SGD': 1.34}
        
        # Get column mappings
        ref_col_key = 'reference_doc' if self.file_type == 'cji5' else 'purch_doc'
        ref_col = self.columns.get(ref_col_key)
        currency_col = self.columns.get('trans_currency')
        amount_col = self.columns.get('value_amount')
        
        if not all([ref_col, currency_col, amount_col]):
            raise ValueError("Required columns not found")
        
        # Get column letters
        ref_idx = self._get_column_index(ref_col)
        currency_idx = self._get_column_index(currency_col)
        amount_idx = self._get_column_index(amount_col)
        
        ref_letter = get_column_letter(ref_idx)
        currency_letter = get_column_letter(currency_idx)
        amount_letter = get_column_letter(amount_idx)
        
        # STEP 4: Add numeric reference column
        numeric_formula = f"=VALUE({ref_letter}{{row}})"
        self.add_formula_column(
            f"{OUTPUT_COLUMNS.get('reference_doc', 'Reference_Numeric')}", 
            numeric_formula
        )
        
        # STEP 5: Add currency conversion column
        # Create nested IF formula for currency conversion
        php_rate = exchange_rates.get('PHP', 57)
        sgd_rate = exchange_rates.get('SGD', 1.34)
        
        conversion_formula = (
            f"=IF({currency_letter}{{row}}=\"PHP\",{amount_letter}{{row}}/{php_rate},"
            f"IF({currency_letter}{{row}}=\"SGD\",{amount_letter}{{row}}/{sgd_rate},"
            f"{amount_letter}{{row}}))"
        )
        self.add_formula_column(OUTPUT_COLUMNS['usd_amount'], conversion_formula)
        
        return self
    
    def _get_column_index(self, column_name: str) -> int:
        """Get column index (1-based) from column name"""
        for idx, cell in enumerate(self.ws[1], start=1):
            if cell.value == column_name:
                return idx
        raise ValueError(f"Column '{column_name}' not found")


class RFPReclassFormulaProcessor(FormulaBasedProcessor):
    """Formula-based RFP/Reclass processor"""
    
    def process_with_total(self, exchange_rates: Optional[Dict] = None, 
                          remove_cbip: bool = False):
        """
        Process RFP/Reclass file
        STEP 5: Convert currency to USD
        Calculate totals using formulas
        """
        if self.df is None or not self.wb:
            raise ValueError("File not loaded. Call load_file() first.")
        
        if exchange_rates is None:
            exchange_rates = {'PHP': 57, 'SGD': 1.34}
        
        currency_col = self.columns.get('trans_currency')
        amount_col = self.columns.get('value_amount')
        
        if not all([currency_col, amount_col]):
            raise ValueError("Required columns not found")
        
        # Get column indices
        currency_idx = self._get_column_index(currency_col)
        amount_idx = self._get_column_index(amount_col)
        
        currency_letter = get_column_letter(currency_idx)
        amount_letter = get_column_letter(amount_idx)
        
        # Add currency conversion column
        php_rate = exchange_rates.get('PHP', 57)
        sgd_rate = exchange_rates.get('SGD', 1.34)
        
        conversion_formula = (
            f"=IF({currency_letter}{{row}}=\"PHP\",{amount_letter}{{row}}/{php_rate},"
            f"IF({currency_letter}{{row}}=\"SGD\",{amount_letter}{{row}}/{sgd_rate},"
            f"{amount_letter}{{row}}))"
        )
        self.add_formula_column(OUTPUT_COLUMNS['usd_amount'], conversion_formula)
        
        return self
    
    def _get_column_index(self, column_name: str) -> int:
        """Get column index (1-based) from column name"""
        for idx, cell in enumerate(self.ws[1], start=1):
            if cell.value == column_name:
                return idx
        raise ValueError(f"Column '{column_name}' not found")


class ZMMFormulaProcessor(FormulaBasedProcessor):
    """Formula-based ZMM processor - copy and formula-based operations"""
    
    def process_basic(self):
        """
        Process ZMM file
        STEP: Copy PR numbers and related columns
        """
        if self.df is None or not self.wb:
            raise ValueError("File not loaded. Call load_file() first.")
        
        # Get PR column
        pr_col = self.columns.get('pr_number')
        
        if not pr_col:
            return self
        
        pr_idx = self._get_column_index(pr_col)
        pr_letter = get_column_letter(pr_idx)
        
        # Add PR column (copy operation)
        self.add_formula_column(f"{OUTPUT_COLUMNS.get('pr_number', 'PR_Number_Copy')}", 
                               f"={pr_letter}{{row}}")
        
        return self
    
    def _get_column_index(self, column_name: str) -> int:
        """Get column index (1-based) from column name"""
        for idx, cell in enumerate(self.ws[1], start=1):
            if cell.value == column_name:
                return idx
        raise ValueError(f"Column '{column_name}' not found")
