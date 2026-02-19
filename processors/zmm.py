"""
ZMM file processor (STEP 17)
Handles PR number delimiting and column copying
"""
import pandas as pd
from processors.base import BaseProcessor
from config import OUTPUT_COLUMNS


class ZMMProcessor(BaseProcessor):
    """Processor for ZMM files"""
    
    def __init__(self):
        super().__init__('zmm')
    
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
