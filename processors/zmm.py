"""
ZMM file processor (STEP 17)
Handles PR number delimiting and column copying
Supports both traditional (pandas-based) and formula-based (fast) processing
"""
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter
from processors.base import BaseProcessor
from config import OUTPUT_COLUMNS


class ZMMProcessor(BaseProcessor):
    """Processor for ZMM files"""
    
    def __init__(self):
        super().__init__('zmm')
        self.wb = None
        self.ws = None
        self.file_path = None
    
    def process_basic(self):
        """
        Basic ZMM processing: Delimit PR, copy columns
        
        Returns:
            Processed DataFrame
        """
        pr_col = self.columns.get('ariba_pr_ref')
        if not pr_col:
            raise ValueError("Ariba PR Reference column not found")
        
        # Get PR data
        pr_data = self.df[pr_col].copy()
        
        # Delimit PR numbers (remove v1, v2, v3, etc.)
        pr_data_delimited = pr_data.apply(self.delimit_pr_number)
        
        # Convert to numeric
        pr_data_numeric = pd.to_numeric(pr_data_delimited, errors='coerce')
        
        # Find columns to copy
        po_col = self.columns.get('po_number')
        vendor_col = self.columns.get('vendor')
        
        # Insert new columns after original PR column
        # Find position of PR column
        pr_col_index = self.df.columns.get_loc(pr_col)
        
        # Insert columns at position C (index 2)
        insert_position = 2
        
        # Insert PR delimited
        self.df.insert(
            insert_position,
            OUTPUT_COLUMNS['pr_ref_delimited'],
            pr_data_delimited
        )
        
        # Insert PR numeric
        self.df.insert(
            insert_position + 1,
            OUTPUT_COLUMNS['pr_ref_numeric'],
            pr_data_numeric
        )
        
        # Insert PR copy
        self.df.insert(
            insert_position + 2,
            OUTPUT_COLUMNS['pr_ref_copy'],
            pr_data_delimited.copy()
        )
        
        # Copy PO column if exists
        if po_col:
            self.df.insert(
                insert_position + 3,
                OUTPUT_COLUMNS['po_copy'],
                self.df[po_col].copy()
            )
        
        # Copy Vendor column if exists
        if vendor_col:
            vendor_insert_pos = insert_position + 4 if po_col else insert_position + 3
            self.df.insert(
                vendor_insert_pos,
                OUTPUT_COLUMNS['vendor_copy'],
                self.df[vendor_col].copy()
            )
        
        return self.df
    
    def get_pr_statistics(self):
        """
        Get statistics about PR numbers
        
        Returns:
            Dictionary with PR statistics
        """
        pr_numeric_col = OUTPUT_COLUMNS['pr_ref_numeric']
        if pr_numeric_col not in self.df.columns:
            return {}
        
        pr_col = self.df[pr_numeric_col].dropna()
        
        stats = {
            'total_prs': len(pr_col),
            'unique_prs': pr_col.nunique(),
            'min_pr': pr_col.min(),
            'max_pr': pr_col.max(),
            'duplicates': len(pr_col) - pr_col.nunique()
        }
        
        return stats
    
    def process_basic_formula(self, file_path):
        """
        Fast formula-based processing for ZMM files
        Creates formulas for PR number processing instead of pandas calculations
        
        Args:
            file_path: Path to input ZMM file
        """
        # Load file with openpyxl
        self.file_path = file_path
        self.df = pd.read_excel(file_path)
        self.wb = openpyxl.load_workbook(file_path)
        self.ws = self.wb.active
        
        # Validate columns
        self.validate_and_prepare()
        
        # Get PR column
        pr_col = self.columns.get('ariba_pr_ref')
        if not pr_col:
            raise ValueError("Ariba PR Reference column not found")
        
        # Get column index
        pr_idx = self._get_column_index(pr_col)
        pr_letter = get_column_letter(pr_idx)
        
        # Add new columns with formulas
        # Column for PR delimited (remove v1, v2, etc.)
        delimit_col_idx = self.ws.max_column + 1
        delimit_col_letter = get_column_letter(delimit_col_idx)
        
        # Add header
        self.ws.cell(row=1, column=delimit_col_idx).value = OUTPUT_COLUMNS['pr_ref_delimited']
        
        # Add formula to remove version numbers (v1, v2, etc.)
        for row in range(2, self.ws.max_row + 1):
            # Formula to remove v followed by numbers
            formula = f"=REGEX({pr_letter}{row},\"(v[0-9]+)$\",\"\",\"g\")"
            self.ws.cell(row=row, column=delimit_col_idx).value = formula
        
        # Column for PR as numeric
        numeric_col_idx = delimit_col_idx + 1
        numeric_col_letter = get_column_letter(numeric_col_idx)
        
        # Add header
        self.ws.cell(row=1, column=numeric_col_idx).value = OUTPUT_COLUMNS['pr_ref_numeric']
        
        # Add formula to convert to numeric
        for row in range(2, self.ws.max_row + 1):
            formula = f"=VALUE({delimit_col_letter}{row})"
            self.ws.cell(row=row, column=numeric_col_idx).value = formula
        
        return self
    
    def _get_column_index(self, column_name: str) -> int:
        """Get column index (1-based) from column name in header row"""
        for idx, cell in enumerate(self.ws[1], start=1):
            if cell.value == column_name:
                return idx
        raise ValueError(f"Column '{column_name}' not found in row 1")


class ZMMConsolidator:
    """Consolidator for multiple ZMM files"""
    
    @staticmethod
    def consolidate_zmm_files(file_paths):
        """
        Consolidate multiple ZMM files into one
        
        Args:
            file_paths: list of file paths to consolidate
            
        Returns:
            Consolidated DataFrame
        """
        dfs = []
        headers_verified = False
        reference_columns = None
        
        for filepath in file_paths:
            df = pd.read_excel(filepath)
            
            if not headers_verified:
                reference_columns = df.columns.tolist()
                headers_verified = True
            else:
                # Verify headers match
                if df.columns.tolist() != reference_columns:
                    # Try to align columns
                    df = df[reference_columns]
            
            dfs.append(df)
        
        # Concatenate all dataframes
        consolidated = pd.concat(dfs, ignore_index=True)
        
        return consolidated
    
    @staticmethod
    def validate_headers(file_paths):
        """
        Validate that all ZMM files have same headers
        
        Args:
            file_paths: list of file paths to validate
            
        Returns:
            Tuple of (headers_match: bool, differences: list)
        """
        if not file_paths:
            return True, []
        
        first_df = pd.read_excel(file_paths[0])
        reference_headers = first_df.columns.tolist()
        
        differences = []
        
        for i, filepath in enumerate(file_paths[1:], 1):
            df = pd.read_excel(filepath)
            current_headers = df.columns.tolist()
            
            if current_headers != reference_headers:
                differences.append({
                    'file': filepath,
                    'file_index': i,
                    'missing_cols': set(reference_headers) - set(current_headers),
                    'extra_cols': set(current_headers) - set(reference_headers)
                })
        
        return len(differences) == 0, differences
