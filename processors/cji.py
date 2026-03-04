"""
CJI5 and CJI3 file processors (STEP 4-7)
Handles conversion of reference documents and currency
Supports both traditional (pandas-based) and formula-based (fast) processing
"""
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter
from processors.base import BaseProcessor
from config import OUTPUT_COLUMNS


class CJIProcessor(BaseProcessor):
    """Processor for CJI5 and CJI3 files"""
    
    def __init__(self, file_type):
        if file_type not in ['cji5', 'cji3']:
            raise ValueError(f"Invalid CJI file type: {file_type}")
        super().__init__(file_type)
        self.wb = None
        self.ws = None
        self.file_path = None
    
    def process_basic(self, exchange_rates=None):
        """
        Basic CJI processing: Convert reference and currency
        
        Args:
            exchange_rates: optional custom exchange rates dict
            
        Returns:
            Processed DataFrame
        """
        # STEP 4: Convert reference document to numeric
        ref_col_key = 'reference_doc' if self.file_type == 'cji5' else 'purch_doc'
        self.convert_reference_to_numeric(ref_col_key)
        
        # STEP 5: Convert currency to USD
        self.convert_currency(exchange_rates)
        
        # Blank out amounts for subtotal rows
        self.blank_subtotal_rows('project')
        
        return self.df
    
    def process_with_pivot(self, exchange_rates=None):
        """
        CJI processing with pivot table generation (STEP 6-7)
        
        Args:
            exchange_rates: optional custom exchange rates dict
            
        Returns:
            Tuple of (processed_df, pivot_df)
        """
        # First do basic processing
        self.process_basic(exchange_rates)
        
        # Prepare data for pivot (exclude subtotal rows)
        project_col = self.columns.get('project')
        if project_col:
            df_for_pivot = self.df[
                self.df[project_col].notna() & (self.df[project_col] != '')
            ].copy()
        else:
            df_for_pivot = self.df.copy()
        
        # Create pivot table
        ref_col_key = 'reference_doc' if self.file_type == 'cji5' else 'purch_doc'
        ref_col = self.columns.get(ref_col_key)
        
        if self.file_type == 'cji5':
            # STEP 6: CJI5 Pivot
            # Columns: Reference Document Category, Rows: Reference Document number, Values: Amount_USD
            cat_col = self.columns.get('reference_category')
            if cat_col:
                pivot = pd.pivot_table(
                    df_for_pivot,
                    values=OUTPUT_COLUMNS['usd_amount'],
                    index=ref_col,
                    columns=cat_col,
                    aggfunc='sum',
                    fill_value=0,
                    margins=True
                )
            else:
                pivot = pd.pivot_table(
                    df_for_pivot,
                    values=OUTPUT_COLUMNS['usd_amount'],
                    index=ref_col,
                    aggfunc='sum',
                    fill_value=0,
                    margins=True
                )
        else:
            # STEP 7: CJI3 Pivot
            # Rows: Purchasing Document Number, Values: Amount_USD
            pivot = pd.pivot_table(
                df_for_pivot,
                values=OUTPUT_COLUMNS['usd_amount'],
                index=ref_col,
                aggfunc='sum',
                fill_value=0,
                margins=True
            )
        
        return self.df, pivot
    
    def process_without_carplan(self, exchange_rates=None):
        """
        Process CJI file excluding car plan entries (STEP 14)
        
        Args:
            exchange_rates: optional custom exchange rates dict
            
        Returns:
            Processed DataFrame without car plan
        """
        # Remove car plan entries (GNT-OTACP-25)
        carplan_marker = 'GNT-OTACP-25'
        project_col = self.columns.get('project')
        
        if project_col:
            original_count = len(self.df)
            self.df = self.df[
                ~self.df[project_col].astype(str).str.contains(carplan_marker, na=False)
            ]
            removed_count = original_count - len(self.df)
            
            # Now process remaining data
            self.process_basic(exchange_rates)
            
            return self.df, removed_count
        
        # If no project column, just do normal processing
        self.process_basic(exchange_rates)
        return self.df, 0
    
    def separate_carplan(self):
        """
        Separate car plan entries from main file (STEP 1)
        
        Returns:
            Tuple of (main_df, carplan_df)
        """
        carplan_marker = 'GNT-OTACP-25'
        project_col = self.columns.get('project')
        
        if not project_col:
            return self.df, None
        
        carplan_mask = self.df[project_col].astype(str).str.contains(carplan_marker, na=False)
        carplan_df = self.df[carplan_mask].copy()
        main_df = self.df[~carplan_mask].copy()
        
        self.df = main_df
    
    def process_basic_formula(self, file_path, exchange_rates=None):
        """
        Fast formula-based processing (instant file save)
        Creates Excel formulas instead of calculating values in pandas
        STEP 4: Convert reference to numeric via formula
        STEP 5: Convert currency to USD via formula
        
        Args:
            file_path: Path to input file
            exchange_rates: Optional custom exchange rates dict
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
        ref_col_key = 'reference_doc' if self.file_type == 'cji5' else 'purch_doc'
        ref_col = self.columns.get(ref_col_key)
        currency_col = self.columns.get('trans_currency')
        amount_col = self.columns.get('value_amount')
        project_col = self.columns.get('project')
        
        if not all([ref_col, currency_col, amount_col]):
            raise ValueError(f"Required columns not found for formula processing. Found: {self.columns}")
        
        # Get column indices
        ref_idx = self._get_column_index(ref_col)
        currency_idx = self._get_column_index(currency_col)
        amount_idx = self._get_column_index(amount_col)
        project_idx = self._get_column_index(project_col) if project_col else None
        
        ref_letter = get_column_letter(ref_idx)
        currency_letter = get_column_letter(currency_idx)
        amount_letter = get_column_letter(amount_idx)
        
        # Add new columns with formulas
        last_col = self.ws.max_column
        
        # Column: Reference as numeric
        usd_col_idx = last_col + 1
        usd_col_letter = get_column_letter(usd_col_idx)
        
        # Add header
        self.ws.cell(row=1, column=usd_col_idx).value = OUTPUT_COLUMNS['usd_amount']
        
        # Add formula for currency conversion (case-insensitive using UPPER())
        php_rate = exchange_rates.get('PHP', 57)
        sgd_rate = exchange_rates.get('SGD', 1.34)
        
        for row in range(2, self.ws.max_row + 1):
            cell_obj = self.ws.cell(row=row, column=usd_col_idx)
            
            # Check if this is a subtotal row (where project column is empty)
            is_subtotal = False
            if project_idx:
                project_cell = self.ws.cell(row=row, column=project_idx)
                if not project_cell.value or str(project_cell.value).strip() == '':
                    # This is a subtotal row - do NOT add formula
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
