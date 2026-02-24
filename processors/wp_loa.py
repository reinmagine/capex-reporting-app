"""
WP LOA Report Processor
Handles processing of WP LOA Report workbook with multi-sheet lookups
Implements VLOOKUP operations across internal tabs and external workbooks
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from utils.vlookup import VLookupHelper, ExternalFileLookup, NameFormatter
from utils.column_mapper import ColumnMapper


class WPLOAProcessor:
    """
    Processor for WP LOA Report automation
    
    Handles:
    - Loading and validating WP LOA workbook
    - Filtering MGA/MIA PR numbers
    - Filtering by year
    - VLOOKUP operations to BUDGET tab
    - VLOOKUP operations to external files
    - Deriving calculated columns (L1, L2, etc.)
    - Name formatting
    """
    
    def __init__(self):
        """Initialize processor"""
        self.df = None
        self.budget_df = None
        self.availment_df = None
        self.loa_current_approver_df = None
        self.file_path = None
        self.external_files = {}  # Cache for external files
        
    def load_file(self, file_path: str) -> bool:
        """
        Load WP LOA Report workbook
        
        Args:
            file_path: Path to WP LOA Report Excel file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.file_path = file_path
            
            # Load main "page" sheet
            self.df = pd.read_excel(file_path, sheet_name='page')
            
            # Load BUDGET sheet for lookups
            try:
                self.budget_df = pd.read_excel(file_path, sheet_name='BUDGET')
            except:
                print("Warning: Could not load BUDGET sheet")
                self.budget_df = None
            
            return True
        except Exception as e:
            raise Exception(f"Error loading WP LOA file: {str(e)}")
    
    def load_external_files(self, availment_file: Optional[str] = None,
                           loa_approver_file: Optional[str] = None) -> Dict[str, bool]:
        """
        Load external reference files
        
        Args:
            availment_file: Path to "2026 CAPEX AVAILMENT_as of Feb 16.xlsx"
            loa_approver_file: Path to "LOA_CURRENT_APPROVER (Auto Email).xlsx"
            
        Returns:
            Dictionary with load status for each file
        """
        results = {}
        
        # Load CAPEX AVAILMENT file
        if availment_file:
            try:
                self.availment_df = pd.read_excel(availment_file, sheet_name='data_2026', dtype=str)
                results['availment'] = True
            except Exception as e:
                print(f"Warning: Could not load CAPEX AVAILMENT file: {str(e)}")
                results['availment'] = False
        else:
            results['availment'] = False
        
        # Load LOA Current Approver file
        if loa_approver_file:
            try:
                self.loa_current_approver_df = pd.read_excel(loa_approver_file, 
                                                             sheet_name='page', dtype=str)
                results['loa_approver'] = True
            except Exception as e:
                print(f"Warning: Could not load LOA Current Approver file: {str(e)}")
                results['loa_approver'] = False
        else:
            results['loa_approver'] = False
        
        return results
    
    def validate_structure(self) -> Tuple[bool, List[str]]:
        """
        Validate that main dataframe has required columns
        
        Returns:
            Tuple of (is_valid, missing_columns)
        """
        required_cols = [
            'WP LOA', 'BOQ PR (Pending no Ariba PR Only(', 'YEAR',
            'PID (Mother and Sub)', 'Amount (USD)'
        ]
        
        missing = []
        for col in required_cols:
            if col not in self.df.columns:
                missing.append(col)
        
        return len(missing) == 0, missing
    
    def filter_boq_pr(self) -> 'WPLOAProcessor':
        """
        Filter to include only MGA and MIA PR numbers
        
        STEP: Filter BOQ PR column for rows containing "MGA" or "MIA"
        
        Returns:
            Self for chaining
        """
        boq_col = 'BOQ PR (Pending no Ariba PR Only('
        
        # Filter for MGA or MIA (convert to string to handle mixed types)
        try:
            mask = self.df[boq_col].astype(str).str.contains('MGA|MIA', case=False, na=False)
            self.df = self.df[mask].copy()
        except Exception as e:
            print(f"Warning: Could not filter BOQ PR: {str(e)}")
        
        return self
    
    def filter_year_2026(self) -> 'WPLOAProcessor':
        """
        Filter to exclude year 26 rows
        
        STEP: In YEAR column, exclude year 26
        
        Returns:
            Self for chaining
        """
        year_col = 'YEAR'
        
        # Filter out 26 (keep only where YEAR != 26), handle non-numeric values
        if year_col in self.df.columns:
            try:
                # Convert to numeric, handling non-numeric values
                year_numeric = pd.to_numeric(self.df[year_col], errors='coerce')
                mask = year_numeric != 26
                self.df = self.df[mask].copy()
            except Exception as e:
                print(f"Warning: Could not filter YEAR column: {str(e)}")
        
        return self
    
    def add_l1_column(self) -> 'WPLOAProcessor':
        """
        Create L1 column: PID - 1 - YEAR
        
        Formula: =K&"-"&L&"-"&M where K=PID, L=1 value, M=YEAR
        Example: I-BSRF-26
        
        Returns:
            Self for chaining
        """
        # Find the PID column (could be named "PID (Mother and Sub)" or variations)
        pid_col = self._find_column(['PID (Mother and Sub)', 'PID'])
        year_col = self._find_column(['YEAR', '3'])
        l1_base_col = self._find_column(['1'])  # The "1" column
        
        if all([pid_col, year_col, l1_base_col]):
            self.df['L1'] = (
                self.df[pid_col].astype(str).str.strip() + '-' +
                self.df[l1_base_col].astype(str).str.strip() + '-' +
                self.df[year_col].astype(str).str.strip()
            )
        else:
            print("Warning: Could not create L1 column - missing source columns")
        
        return self
    
    def add_l2_column(self) -> 'WPLOAProcessor':
        """
        Create L2 column: PID with Subproject code
        
        Formula: Based on L1 column (which contains the full PID string)
        Essentially copies the combined PID-L1Base-YEAR-Subproject
        
        Returns:
            Self for chaining
        """
        # L2 appears to be the full PID string from column H (PID (Mother and Sub))
        pid_col = self._find_column(['PID (Mother and Sub)', 'PID'])
        
        if pid_col and 'L1' in self.df.columns:
            # Based on example data, L2 = L1 + Subproject code
            # Need to extract subproject from the full PID field
            # From examples: I-BSRF-26-SA where "SA" is the subproject
            
            # For now, use the full H column value if available
            self.df['L2'] = self.df[pid_col].astype(str).str.strip()
        else:
            print("Warning: Could not create L2 column")
        
        return self
    
    def add_program_mbr_column(self) -> 'WPLOAProcessor':
        """
        Create PROGRAM MBR column via VLOOKUP
        
        Formula: =VLOOKUP(L2, BUDGET!$B:$N, 9, 0)
        Looks up L2 value in BUDGET tab columns B:N, returns column 9
        
        Returns:
            Self for chaining
        """
        if self.budget_df is None or 'L2' not in self.df.columns:
            print("Warning: Cannot create PROGRAM MBR column")
            return self
        
        # Get all L2 values and perform VLOOKUP
        l2_values = self.df['L2'].tolist()
        self.df['PROGRAM MBR'] = VLookupHelper.vlookup_column(
            l2_values, self.budget_df, col_index=9, not_found_value="N/A"
        )
        
        return self
    
    def add_div_column(self) -> 'WPLOAProcessor':
        """
        Create DIV column via VLOOKUP
        
        Formula: =VLOOKUP(L2, BUDGET!$B:$N, 6, 0)
        
        Returns:
            Self for chaining
        """
        if self.budget_df is None or 'L2' not in self.df.columns:
            print("Warning: Cannot create DIV column")
            return self
        
        l2_values = self.df['L2'].tolist()
        self.df['DIV'] = VLookupHelper.vlookup_column(
            l2_values, self.budget_df, col_index=7, not_found_value="N/A"  # Column 7 is DIV
        )
        
        return self
    
    def add_dep_column(self) -> 'WPLOAProcessor':
        """
        Create DEP column via VLOOKUP
        
        Formula: =VLOOKUP(L2, BUDGET!$B:$N, 5, 0)
        
        Returns:
            Self for chaining
        """
        if self.budget_df is None or 'L2' not in self.df.columns:
            print("Warning: Cannot create DEP column")
            return self
        
        l2_values = self.df['L2'].tolist()
        self.df['DEP'] = VLookupHelper.vlookup_column(
            l2_values, self.budget_df, col_index=6, not_found_value="N/A"  # Column 6 is DEPT
        )
        
        return self
    
    def add_funding_column(self) -> 'WPLOAProcessor':
        """
        Create FUNDING column via VLOOKUP
        
        Formula: =VLOOKUP(L2, BUDGET!$B:$N, 12, 0)
        
        Returns:
            Self for chaining
        """
        if self.budget_df is None or 'L2' not in self.df.columns:
            print("Warning: Cannot create FUNDING column")
            return self
        
        l2_values = self.df['L2'].tolist()
        self.df['FUNDING'] = VLookupHelper.vlookup_column(
            l2_values, self.budget_df, col_index=13, not_found_value="N/A"  # Column 13 is Funding Source
        )
        
        return self
    
    def add_cfu_sponsor_column(self) -> 'WPLOAProcessor':
        """
        Create CFU SPONSOR column via VLOOKUP
        
        Formula: =VLOOKUP(L2, BUDGET!$B:$N, 3, 0)
        
        Returns:
            Self for chaining
        """
        if self.budget_df is None or 'L2' not in self.df.columns:
            print("Warning: Cannot create CFU SPONSOR column")
            return self
        
        l2_values = self.df['L2'].tolist()
        self.df['CFU SPONSOR'] = VLookupHelper.vlookup_column(
            l2_values, self.budget_df, col_index=4, not_found_value="N/A"  # Column 4 is CFU Sponsor
        )
        
        return self
    
    def add_availment_tracker_column(self) -> 'WPLOAProcessor':
        """
        Create AVAILMENT TRACKER column via VLOOKUP to external file
        
        Formula: =IFNA(VLOOKUP(D, 'path'![sheet]!$C:$C, 1, 0), "For Ariba PR Translation")
        Looks up in 2026 CAPEX AVAILMENT_as of Feb 16 workbook, data_2026 sheet
        
        Returns:
            Self for chaining
        """
        if self.availment_df is None:
            # Set default value if external file not loaded
            self.df['AVAILMENT TRACKER'] = "For Ariba PR Translation"
            return self
        
        # Column D is BOQ PR
        boq_col = self._find_column(['BOQ PR (Pending no Ariba PR Only(', 'BOQ PR'])
        
        if boq_col:
            boq_values = self.df[boq_col].tolist()
            
            # Lookup in WP LOA Reference column (column D in availment)
            # Return matching row or "For Ariba PR Translation"
            results = []
            for boq_val in boq_values:
                # Look for match in WP LOA Reference column
                if boq_val and pd.notna(boq_val):
                    # Search in the availment dataframe
                    wploa_col = self._find_column_in_df(self.availment_df, ['WP LOA Reference', 'WP LOA'])
                    if wploa_col:
                        matches = self.availment_df[wploa_col] == str(boq_val)
                        if matches.any():
                            results.append(self.availment_df.iloc[matches.idxmax(), 0])
                        else:
                            results.append("For Ariba PR Translation")
                    else:
                        results.append("For Ariba PR Translation")
                else:
                    results.append("For Ariba PR Translation")
            
            self.df['AVAILMENT TRACKER'] = results
        else:
            self.df['AVAILMENT TRACKER'] = "For Ariba PR Translation"
        
        return self
    
    def add_proponent_column(self) -> 'WPLOAProcessor':
        """
        Create PROPONENT column via VLOOKUP to external file
        
        Formula: =PROPER(VLOOKUP(A, 'path'![sheet]!$A:$I, 9, 0))
        Looks up in LOA_CURRENT_APPROVER (Auto Email) workbook, page sheet
        
        Returns:
            Self for chaining
        """
        if self.loa_current_approver_df is None:
            self.df['PROPONENT'] = "N/A"
            return self
        
        # Column A is WP LOA
        wploa_col = self._find_column(['WP LOA'])
        
        if wploa_col:
            wploa_values = self.df[wploa_col].tolist()
            
            # Lookup in LOA # column (column A in LOA file)
            results = []
            for wploa_val in wploa_values:
                if wploa_val and pd.notna(wploa_val):
                    # Look for match in first column
                    loa_num_col = self._find_column_in_df(self.loa_current_approver_df, ['LOA#', 'LOA'])
                    if loa_num_col:
                        matches = self.loa_current_approver_df[loa_num_col] == str(wploa_val)
                        if matches.any():
                            # Get column 9 (Current Approver, which is column I)
                            result = self.loa_current_approver_df.iloc[matches.idxmax(), 4]  # Column 5 (0-indexed) = Current Approver
                            results.append(str(result).title() if pd.notna(result) else "N/A")
                        else:
                            results.append("N/A")
                    else:
                        results.append("N/A")
                else:
                    results.append("N/A")
            
            self.df['PROPONENT'] = results
        else:
            self.df['PROPONENT'] = "N/A"
        
        return self
    
    def add_proponent_1_column(self) -> 'WPLOAProcessor':
        """
        Create PROPONENT 1 column: Reformat PROPONENT name
        
        Converts "Last, First" format to "First Last" format
        Example: "Padilla, Danross S." -> "Danross Padilla"
        
        Returns:
            Self for chaining
        """
        if 'PROPONENT' not in self.df.columns:
            self.df['PROPONENT 1'] = ""
            return self
        
        self.df['PROPONENT 1'] = self.df['PROPONENT'].apply(NameFormatter.reform_name)
        
        return self
    
    def add_div_in_report_column(self) -> 'WPLOAProcessor':
        """
        Create DIV IN REPORT column via lookup to external file
        
        Looks up from 2026 CAPEX AVAILMENT (data_2026 sheet)
        Column shows Department/Division assignment
        
        Returns:
            Self for chaining
        """
        if self.availment_df is None:
            self.df['DIV IN REPORT'] = ""
            return self
        
        # This is typically manual data, but we can try to populate from Division column
        boq_col = self._find_column(['BOQ PR (Pending no Ariba PR Only(', 'BOQ PR'])
        
        if boq_col:
            boq_values = self.df[boq_col].tolist()
            results = []
            
            for boq_val in boq_values:
                if boq_val and pd.notna(boq_val):
                    # Search for PR Reference in availment file
                    pr_col = self._find_column_in_df(self.availment_df, ['PRReferenceNumber', 'PR'])
                    div_col = self._find_column_in_df(self.availment_df, ['Division', 'Div'])
                    
                    if pr_col and div_col:
                        matches = self.availment_df[pr_col] == str(boq_val)
                        if matches.any():
                            results.append(str(self.availment_df.iloc[matches.idxmax()][div_col]))
                        else:
                            results.append("")
                    else:
                        results.append("")
                else:
                    results.append("")
            
            self.df['DIV IN REPORT'] = results
        else:
            self.df['DIV IN REPORT'] = ""
        
        return self
    
    def add_proj_column(self) -> 'WPLOAProcessor':
        """
        Create PROJ column via VLOOKUP
        
        Formula: =VLOOKUP(L2, BUDGET!$B:$N, 10, 0)
        
        Returns:
            Self for chaining
        """
        if self.budget_df is None or 'L2' not in self.df.columns:
            print("Warning: Cannot create PROJ column")
            return self
        
        l2_values = self.df['L2'].tolist()
        self.df['PROJ'] = VLookupHelper.vlookup_column(
            l2_values, self.budget_df, col_index=11, not_found_value="N/A"  # Column 11 is Project Name
        )
        
        return self
    
    def add_subproj_column(self) -> 'WPLOAProcessor':
        """
        Create SUBPROJ column via VLOOKUP
        
        Formula: =VLOOKUP(L2, BUDGET!$B:$N, 11, 0)
        
        Returns:
            Self for chaining
        """
        if self.budget_df is None or 'L2' not in self.df.columns:
            print("Warning: Cannot create SUBPROJ column")
            return self
        
        l2_values = self.df['L2'].tolist()
        self.df['SUBPROJ'] = VLookupHelper.vlookup_column(
            l2_values, self.budget_df, col_index=12, not_found_value="N/A"  # Column 12 is Sub-project Name
        )
        
        return self
    
    def process_full(self, availment_file: Optional[str] = None,
                    loa_approver_file: Optional[str] = None) -> pd.DataFrame:
        """
        Execute full WP LOA processing pipeline
        
        Args:
            availment_file: Path to CAPEX AVAILMENT external file (optional)
            loa_approver_file: Path to LOA_CURRENT_APPROVER external file (optional)
            
        Returns:
            Processed DataFrame
        """
        # Load external files
        self.load_external_files(availment_file, loa_approver_file)
        
        # Execute processing steps
        self.filter_boq_pr()
        self.filter_year_2026()
        self.add_l1_column()
        self.add_l2_column()
        self.add_program_mbr_column()
        self.add_div_column()
        self.add_dep_column()
        self.add_funding_column()
        self.add_cfu_sponsor_column()
        self.add_availment_tracker_column()
        self.add_proponent_column()
        self.add_proponent_1_column()
        self.add_div_in_report_column()
        self.add_proj_column()
        self.add_subproj_column()
        
        return self.df
    
    def save(self, output_path: str) -> bool:
        """
        Save processed data to Excel
        
        Args:
            output_path: Path to save processed file
            
        Returns:
            True if successful
        """
        try:
            self.df.to_excel(output_path, sheet_name='page', index=False)
            return True
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return False
    
    def _find_column(self, possible_names: List[str]) -> Optional[str]:
        """Find column by list of possible names (case-insensitive)"""
        if self.df is None:
            return None
        
        cols_lower = {str(col).lower(): col for col in self.df.columns}
        
        for name in possible_names:
            if name.lower() in cols_lower:
                return cols_lower[name.lower()]
        
        return None
    
    def _find_column_in_df(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find column in a dataframe by list of possible names"""
        if df is None or df.empty:
            return None
        
        cols_lower = {str(col).lower(): col for col in df.columns}
        
        for name in possible_names:
            if name.lower() in cols_lower:
                return cols_lower[name.lower()]
        
        return None
    
    def get_summary(self) -> Dict[str, any]:
        """Get processing summary statistics"""
        return {
            'total_rows': len(self.df),
            'mga_mia_filtered': len(self.df[self.df['BOQ PR (Pending no Ariba PR Only('].str.contains('MGA|MIA', na=False)]),
            'year_26_filtered': len(self.df[self.df['YEAR'] == 26]),
            'columns_added': ['L1', 'L2', 'PROGRAM MBR', 'DIV', 'DEP', 'FUNDING', 
                             'CFU SPONSOR', 'AVAILMENT TRACKER', 'PROPONENT', 'PROPONENT 1',
                             'DIV IN REPORT', 'PROJ', 'SUBPROJ'],
            'external_files_loaded': {
                'availment': self.availment_df is not None,
                'loa_approver': self.loa_current_approver_df is not None
            }
        }
