"""
WP LOA Report Processor - Formula-based Version
Creates Excel formulas instead of calculated values
Generates new columns from K onwards with proper headers
"""

import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil
import sys

# Add utils to path for file detector import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.file_detector import FileDetector


class WPLOAFormulaProcessor:
    """WP LOA Report processor using Excel formulas. Adds columns K-AA with extraction and VLOOKUP formulas."""
    
    # Column headers for K-AB
    NEW_COLUMN_HEADERS = [
        'PID (Mother and Sub)', '1', 'YEAR', '3', 'L1', 'L2',
        'PROGRAM MBR', 'DIV', 'DEP', 'FUNDING', 'CFU SPONSOR',
        'AVAILMENT TRACKER', 'PROPONENT', 'PROPONENT 1', 'DIV IN REPORT', 'PROGRAM IN REPORT',
        'PROJ', 'SUBPROJ'
    ]
    
    # Column positions for reference
    COLUMNS = {
        'WP_LOA': 1, 'CHANGE_DATE': 2, 'CHANGE_TIME': 3, 'BOQ_PR': 4, 'PROGRAM': 5,
        'PROJECT': 6, 'DESCRIPTION': 7, 'PID': 8, 'AMOUNT_USD': 9, 'STATUS': 10,
        'PID_COPY': 11, 'L1_PART1': 12, 'YEAR': 13, 'L1_PART3': 14, 'L1': 15,
        'L2': 16, 'PROGRAM_MBR': 17, 'DIV': 18, 'DEP': 19, 'FUNDING': 20,
        'CFU_SPONSOR': 21, 'AVAILMENT_TRACKER': 22, 'PROPONENT': 23,
        'PROPONENT_1': 24, 'DIV_IN_REPORT': 25, 'PROGRAM_IN_REPORT': 26,
        'PROJ': 27, 'SUBPROJ': 28
    }
    
    def __init__(self, file_path: str):
        """Initialize processor with file path."""
        self.file_path = file_path
        self.wb = None
        self.ws = None
        self.df = None
        self.budget_df = None
        self.detected_files = {}  # Cache for auto-detected files
        
    def auto_detect_external_files(self, search_directory: Optional[str] = None) -> Dict[str, Optional[str]]:
        """
        Auto-detect external files based on keywords
        
        Args:
            search_directory: Directory to search in (default: same directory as WP LOA file)
            
        Returns:
            Dictionary with detected file paths
        """
        if search_directory is None:
            search_directory = str(Path(self.file_path).parent)
        
        # Use FileDetector to find files
        detected = FileDetector.auto_detect_all_files(search_directory)
        self.detected_files = detected
        
        print("Auto-detected files:")
        for file_type, file_path in detected.items():
            if file_path:
                print(f"  ✓ {file_type}: {Path(file_path).name}")
            else:
                print(f"  ✗ {file_type}: NOT FOUND")
        
        return detected
        
    def load_file(self) -> bool:
        """Load WP LOA workbook and BUDGET sheet. Returns True if successful."""
        try:
            self.wb = openpyxl.load_workbook(self.file_path)
            self.ws = self.wb['page']
            self.df = pd.read_excel(self.file_path, sheet_name='page')
            
            try:
                self.budget_df = pd.read_excel(self.file_path, sheet_name='BUDGET')
            except:
                print("Warning: BUDGET sheet not found")
                self.budget_df = None
            
            return True
        except Exception as e:
            raise Exception(f"Error loading WP LOA file: {str(e)}")
    
    def create_formulas(self, availment_file: Optional[str] = None,
                       loa_approver_file: Optional[str] = None) -> None:
        """
        Create all formulas and headers in columns K-AB.
        
        Supports auto-detection of external files or uses provided paths
        
        Column breakdown:
        - K-N: Extract PID parts from column H (e.g., "I-BSRF-26-SA" → K=I, L=BSRF, M=26, N=SA)
        - O: L1 = concatenate K-L-M
        - P: L2 = copy of H (full PID)
        - Q-U: BUDGET VLOOKUP formulas
        - V: AVAILMENT TRACKER = check if BOQ PR exists
        - W-X: PROPONENT lookups and formatting
        - Y: DIV IN REPORT mapping
        - Z: PROGRAM IN REPORT = Program name from BUDGET
        - AA-AB: BUDGET VLOOKUP formulas (Project and Subproject names)
        
        Args:
            availment_file: Path to CAPEX AVAILMENT file (auto-detected if None)
            loa_approver_file: Path to LOA CURRENT APPROVER file (auto-detected if None)
        """
        
        # Auto-detect files if not provided
        if availment_file is None or loa_approver_file is None:
            detected = self.auto_detect_external_files()
            if availment_file is None:
                availment_file = detected.get('capex_availment') or '2026 CAPEX AVAILMENT_as of Feb 16.xlsx'
            if loa_approver_file is None:
                loa_approver_file = detected.get('loa_approver') or 'LOA_CURRENT_APPROVER (Auto Email).xlsx'
        
        # Extract just the filenames (Excel formulas use filenames, not full paths)
        availment_filename = Path(availment_file).name
        loa_approver_filename = Path(loa_approver_file).name
        
        # STEP 1: Add column headers in row 1 (columns K-AB)
        # Headers for columns K through AB
        column_headers = [
            'PID (Mother and Sub)',  # K - Column 11
            '1',                      # L - Column 12
            'YEAR',                  # M - Column 13
            '3',                      # N - Column 14
            'L1',                      # O - Column 15
            'L2',                      # P - Column 16
            'PROGRAM MBR',           # Q - Column 17
            'DIV',                    # R - Column 18
            'DEP',                    # S - Column 19
            'FUNDING',               # T - Column 20
            'CFU SPONSOR',           # U - Column 21
            'AVAILMENT TRACKER',     # V - Column 22
            'PROPONENT',             # W - Column 23
            'PROPONENT 1',           # X - Column 24
            'DIV IN REPORT',         # Y - Column 25
            'PROGRAM IN REPORT',     # Z - Column 26 (NEW)
            'PROJ',                  # AA - Column 27
            'SUBPROJ'                # AB - Column 28
        ]
        
        # Write headers to row 1
        for col_idx, header in enumerate(column_headers, start=11):
            self.ws.cell(row=1, column=col_idx).value = header
        
        # STEP 2: Add formulas in rows 2 onwards
        last_row = self.ws.max_row
        
        for row in range(2, last_row + 1):
            # Extract PID parts from H column
            self.ws[f'K{row}'].value = f'=LEFT(H{row},FIND("-",H{row})-1)'
            self.ws[f'L{row}'].value = f'=TRIM(MID(SUBSTITUTE(H{row},"-",REPT(" ",100)),100,100))'
            self.ws[f'M{row}'].value = f'=TRIM(MID(SUBSTITUTE(H{row},"-",REPT(" ",100)),200,100))'
            self.ws[f'N{row}'].value = f'=TRIM(MID(SUBSTITUTE(H{row},"-",REPT(" ",100)),300,100))'
            
            # Derived columns
            self.ws[f'O{row}'].value = f'=K{row}&"-"&L{row}&"-"&M{row}'  # L1: concatenate parts
            self.ws[f'P{row}'].value = f'=H{row}'  # L2: copy full PID
            
            # BUDGET lookups (range B:N, base lookup key is P)
            self.ws[f'Q{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,9,0),"N/A")'
            self.ws[f'R{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,6,0),"N/A")'
            self.ws[f'S{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,5,0),"N/A")'
            self.ws[f'T{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,12,0),"N/A")'
            self.ws[f'U{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,3,0),"N/A")'
            
            # AVAILMENT TRACKER: return D value if found, else fallback message
            # Uses detected or provided filename
            self.ws[f'V{row}'].value = f"=IF(COUNTIF('[{availment_filename}]data_2026'!$C:$C,D{row})>0,D{row},\"For Ariba PR Translation\")"
            
            # PROPONENT lookups
            # Uses detected or provided filename
            self.ws[f'W{row}'].value = f"=IFERROR(PROPER(VLOOKUP(A{row},'[{loa_approver_filename}]page'!$A:$I,9,0)),\"N/A\")"
            
            # Format PROPONENT (convert "Last, First" to "First Last" if needed)
            proponent1_formula = (
                f"=IF(ISERROR(FIND(\",\",W{row})),"
                f"W{row},"
                f"PROPER(TRIM(MID(W{row},FIND(\",\",W{row})+2,LEN(W{row}))&\" \"&LEFT(W{row},FIND(\",\",W{row})-1))))"
            )
            self.ws[f'X{row}'].value = proponent1_formula
            
            # Division mapping
            div_formula = (
                f'=IF(R{row}="B&D","B&D",'
                f'IF(R{row}="CIPE","CIPE/Ting",'
                f'IF(R{row}="NAI","NAI/Raymond",'
                f'IF(R{row}="ND","ND/Dennis",'
                f'IF(R{row}="NOA","NOA/Cris",'
                f'IF(R{row}="Non-NTG","NTG Pool",'
                f'IF(R{row}="NTG","NTG / Manpower",'
                f'IF(R{row}="SPE","SPE/Joel",'
                f'IF(R{row}="SPP","SPP/Helen",'
                f'IF(R{row}="SS","SS/Marge",""'
                f'))))))))))'
            )
            self.ws[f'Y{row}'].value = div_formula
            
            # PROGRAM IN REPORT: VLOOKUP to get Program name
            self.ws[f'Z{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,9,0),"N/A")'
            
            # More BUDGET lookups (shifted to AA and AB)
            self.ws[f'AA{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,10,0),"N/A")'
            self.ws[f'AB{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,11,0),"N/A")'
    
    def add_external_file_support(self, availment_file: Optional[str] = None,
                                  loa_approver_file: Optional[str] = None) -> None:
        """Placeholder for external file support (currently disabled)."""
        return
    
    def save(self, output_path: str) -> bool:
        """Save workbook with formulas. Returns True if successful."""
        try:
            self.wb.save(output_path)
            return True
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return False
    
    def process_and_save(self, output_path: str, 
                        availment_file: Optional[str] = None,
                        loa_approver_file: Optional[str] = None) -> bool:
        """
        Complete processing pipeline: load, create formulas, save.
        
        Automatically detects external files if not provided.
        
        Args:
            output_path: Path to save output file
            availment_file: Optional path to CAPEX AVAILMENT file (auto-detected if None)
            loa_approver_file: Optional path to LOA APPROVER file (auto-detected if None)
        """
        try:
            self.load_file()
            self.create_formulas(availment_file, loa_approver_file)
            self.add_external_file_support(availment_file, loa_approver_file)
            self.save(output_path)
            return True
        except Exception as e:
            print(f"Error in processing: {str(e)}")
            return False
    
    def process_loa_current_approver(self, loa_current_approver_path: str, 
                                     budget_file_path: Optional[str] = None) -> bool:
        """
        Process LOA CURRENT APPROVER file and add formula columns + Network Classification + Current Approver 1
        
        This method:
        1. Loads LOA CURRENT APPROVER file (existing columns A-K)
        2. Adds WP LOA formula columns (L-AB): PID, 1, 2, 3, L1, L2, PROGRAM MBR, DIV, DEP, FUNDING, etc.
        3. Inserts Network Classif column (X) from BUDGET sheet
        4. Adds Current Approver 1 column (AD) with formatted name
        
        Final structure:
        A-K: Original LOA CURRENT APPROVER data
        L-AB: Formula columns from WP LOA
        X: Network Classif (inserted between FUNDING and PROPONENT)
        AD: Current Approver 1 (formatted name)
        
        Args:
            loa_current_approver_path: Path to LOA CURRENT APPROVER file
            budget_file_path: Path to BUDGET file with Network Classification data
        """
        try:
            from openpyxl.utils import get_column_letter
            
            # Load LOA CURRENT APPROVER workbook
            loa_wb = openpyxl.load_workbook(loa_current_approver_path)
            loa_ws = loa_wb.active
            
            # Load LOA CURRENT APPROVER data
            loa_df = pd.read_excel(loa_current_approver_path)
            
            # Identify column positions in LOA file
            # Expected: A=LOA#, B=Subject, C=Total Amount, D=STATUS, E=Current Approver, F-K=other data
            
            last_row = loa_ws.max_row
            
            # Add formula columns starting at column L (column 12)
            # K→L (12), L→M (13), M→N (14), etc.
            
            # Column headers for the new columns (L onwards)
            new_headers = [
                'PID (Mother and Sub)',  # L (12)
                '1', 'YEAR', '3', 'L1', 'L2',  # M-Q (13-17)
                'PROGRAM MBR', 'DIV', 'DEP', 'FUNDING'  # R-W (18-23)
            ]
            
            # Write headers starting at column L
            for col_idx, header in enumerate(new_headers, start=12):
                loa_ws.cell(row=1, column=col_idx).value = header
            
            # Add "Network Classif" header at column X (24)
            loa_ws.cell(row=1, column=24).value = 'Network Classif'
            
            # Add PROPONENT and remaining headers
            remaining_headers = [
                'PROPONENT',  # Y (25)
                'DIV IN REPORT',  # Z (26)
                'PROGRAM IN REPORT',  # AA (27)
                'PROJ',  # AB (28)
                'SUBPROJ'  # AC (29)
            ]
            
            for col_idx, header in enumerate(remaining_headers, start=25):
                loa_ws.cell(row=1, column=col_idx).value = header
            
            # Add "Current Approver 1" header at column AD (30)
            loa_ws.cell(row=1, column=30).value = 'Current Approver 1'
            
            # Add formulas for each data row
            for row in range(2, last_row + 1):
                # Column L: PID (Mother and Sub) - empty for now (will reference if available)
                loa_ws[f'L{row}'].value = ''
                
                # Columns M-W: Extract and formula columns
                # M: '1' (user input)
                loa_ws[f'M{row}'].value = ''
                
                # N: YEAR (user input)
                loa_ws[f'N{row}'].value = ''
                
                # O: '3' (user input)
                loa_ws[f'O{row}'].value = ''
                
                # P: L1 (user input)
                loa_ws[f'P{row}'].value = ''
                
                # Q: L2 (user input)
                loa_ws[f'Q{row}'].value = ''
                
                # R-W: VLOOKUP formulas referencing BUDGET sheet
                # Assuming budget lookup using PID (column L) as key
                loa_ws[f'R{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,9,0),"N/A")'  # PROGRAM MBR
                loa_ws[f'S{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,6,0),"N/A")'  # DIV
                loa_ws[f'T{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,5,0),"N/A")'  # DEP
                loa_ws[f'U{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,12,0),"N/A")'  # FUNDING
                
                # Column X: Network Classif from BUDGET column C using LOA# (column A) as lookup key
                # Lookup in BUDGET sheet using column A (LOA#)
                loa_ws[f'X{row}'].value = f'=IFERROR(VLOOKUP($A{row},BUDGET!$A:$C,3,0),"N/A")'
                
                # Columns Y-AC: Remaining formula columns
                loa_ws[f'Y{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,9,0),"N/A")'  # PROPONENT
                loa_ws[f'Z{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,6,0),"N/A")'  # DIV IN REPORT
                loa_ws[f'AA{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,9,0),"N/A")'  # PROGRAM IN REPORT
                loa_ws[f'AB{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,10,0),"N/A")'  # PROJ
                loa_ws[f'AC{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,11,0),"N/A")'  # SUBPROJ
                
                # Column AD: Current Approver 1 - Format name from column E
                # Convert "LAST NAME, First Name" to "First Name Last Name"
                format_name_formula = (
                    f"=IF(ISERROR(FIND(\",\",E{row})),"
                    f"E{row},"
                    f"PROPER(TRIM(MID(E{row},FIND(\",\",E{row})+2,LEN(E{row}))&\" \"&LEFT(E{row},FIND(\",\",E{row})-1))))"
                )
                loa_ws[f'AD{row}'].value = format_name_formula
            
            # Save the workbook
            loa_wb.save(loa_current_approver_path)
            return True
            
        except Exception as e:
            print(f"Error processing LOA CURRENT APPROVER: {str(e)}")
            return False
    
    def get_summary(self) -> Dict:
        """Get processing summary."""
        return {
            'total_rows': self.ws.max_row - 1,
            'columns_added': 18,
            'output_type': 'Excel Formulas',
            'column_range': 'K:AB',
            'columns_created': [
                'PID (Mother and Sub)', '1', 'YEAR', '3', 'L1', 'L2',
                'PROGRAM_MBR', 'DIV', 'DEP', 'FUNDING', 'CFU_SPONSOR',
                'AVAILMENT_TRACKER', 'PROPONENT', 'PROPONENT_1',
                'DIV_IN_REPORT', 'PROGRAM_IN_REPORT', 'PROJ', 'SUBPROJ'
            ]
        }
