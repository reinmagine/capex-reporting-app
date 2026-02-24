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


class WPLOAFormulaProcessor:
    """
    Processor for WP LOA Report using Excel formulas
    
    Handles:
    - Loading WP LOA workbook (columns A-J)
    - Inserting new columns K onwards with headers
    - Creating VLOOKUP formulas for BUDGET tab lookups
    - Creating derived column formulas
    - Writing formulas to output file (not just values)
    """
    
    # Column headers for new columns K onwards
    NEW_COLUMN_HEADERS = [
        'PID (Mother and Sub)',  # K - Copy of H
        '1',                      # L - First part of L1
        'YEAR',                  # M - Year value
        '3',                      # N - Third part
        'L1',                      # O - Derived: K&"-"&L&"-"&M
        'L2',                      # P - Copy of H (PID)
        'PROGRAM MBR',           # Q - VLOOKUP to BUDGET
        'DIV',                    # R - VLOOKUP to BUDGET
        'DEP',                    # S - VLOOKUP to BUDGET
        'FUNDING',               # T - VLOOKUP to BUDGET
        'CFU SPONSOR',           # U - VLOOKUP to BUDGET
        'AVAILMENT TRACKER',     # V - Default or VLOOKUP
        'PROPONENT',             # W - Default or VLOOKUP
        'PROPONENT 1',           # X - Formatted PROPONENT
        'DIV IN REPORT',         # Y - VLOOKUP
        'PROJ',                  # Z - VLOOKUP to BUDGET
        'SUBPROJ'                # AA - VLOOKUP to BUDGET
    ]
    
    # Column positions (1-indexed for Excel)
    COLUMNS = {
        'WP_LOA': 1,           # A
        'CHANGE_DATE': 2,      # B
        'CHANGE_TIME': 3,      # C
        'BOQ_PR': 4,           # D
        'PROGRAM': 5,          # E
        'PROJECT': 6,          # F
        'DESCRIPTION': 7,      # G
        'PID': 8,              # H
        'AMOUNT_USD': 9,       # I
        'STATUS': 10,          # J
        'PID_COPY': 11,        # K - Copy of PID
        'L1_PART1': 12,        # L - First part (should be extracted or user-entered)
        'YEAR': 13,            # M - Year
        'L1_PART3': 14,        # N - Third part
        'L1': 15,              # O - L1 formula: =L&"-"&M&"-"&N
        'L2': 16,              # P - L2 formula: =H
        'PROGRAM_MBR': 17,     # Q - VLOOKUP to BUDGET
        'DIV': 18,             # R
        'DEP': 19,             # S
        'FUNDING': 20,         # T
        'CFU_SPONSOR': 21,     # U
        'AVAILMENT_TRACKER': 22,  # V
        'PROPONENT': 23,       # W
        'PROPONENT_1': 24,     # X
        'DIV_IN_REPORT': 25,   # Y
        'PROJ': 26,            # Z
        'SUBPROJ': 27          # AA
    }
    
    def __init__(self, file_path: str):
        """
        Initialize processor
        
        Args:
            file_path: Path to WP LOA Report Excel file
        """
        self.file_path = file_path
        self.wb = None
        self.ws = None
        self.df = None
        self.budget_df = None
        
    def load_file(self) -> bool:
        """
        Load WP LOA workbook
        
        Returns:
            True if successful
        """
        try:
            # Load with openpyxl for formula writing
            self.wb = openpyxl.load_workbook(self.file_path)
            self.ws = self.wb['page']
            
            # Also load as dataframe for validation
            self.df = pd.read_excel(self.file_path, sheet_name='page')
            
            # Load BUDGET sheet for reference
            try:
                self.budget_df = pd.read_excel(self.file_path, sheet_name='BUDGET')
            except:
                print("Warning: BUDGET sheet not found")
                self.budget_df = None
            
            return True
        except Exception as e:
            raise Exception(f"Error loading WP LOA file: {str(e)}")
    
    def create_formulas(self) -> None:
        """
        Create all formulas and headers in the worksheet
        
        Step 1: Add headers in row 1 (columns K-AA)
        Step 2: Add formulas in data rows (row 2+)
        
        Formulas created (matching user's manual formulas):
        - K: Part 1 of PID (extracted from H by splitting on hyphens)
        - L: Part 2 of PID (extracted from H)
        - M: Part 3 of PID (extracted from H) - Year
        - N: Part 4 of PID (extracted from H)
        - O: L1 concatenation: =L&"-"&M&"-"&N (parts 2-3-4)
        - P: L2 (full PID copy from H)
        - Q-AA: VLOOKUP formulas using P ($P in absolute ref) as lookup key on BUDGET!$B:$N
        
        Note: All VLOOKUP uses BUDGET!$B:$N range (columns B through N only)
              Lookup key is P (full PID), not O (L1)
        """
        
        # STEP 1: Add headers in row 1 (columns K-AA)
        for col_idx, header in enumerate(self.NEW_COLUMN_HEADERS, start=11):  # Start at K (column 11)
            cell = self.ws.cell(row=1, column=col_idx)
            cell.value = header
        
        # STEP 2: Get last data row and add formulas
        last_row = self.ws.max_row
        
        # Start from row 2 (skip header)
        for row in range(2, last_row + 1):
            # Column K: Part 1 of PID (extract first part before first hyphen)
            # From "I-BSRF-26-SA" → "I"
            self.ws[f'K{row}'].value = f'=LEFT(H{row},FIND("-",H{row})-1)'
            
            # Column L: Part 2 of PID (extract second part)
            # From "I-BSRF-26-SA" → "BSRF"
            self.ws[f'L{row}'].value = f'=TRIM(MID(SUBSTITUTE(H{row},"-",REPT(" ",100)),100,100))'
            
            # Column M: Part 3 of PID (extract third part - Year)
            # From "I-BSRF-26-SA" → "26"
            self.ws[f'M{row}'].value = f'=TRIM(MID(SUBSTITUTE(H{row},"-",REPT(" ",100)),200,100))'
            
            # Column N: Part 4 of PID (extract fourth part)
            # From "I-BSRF-26-SA" → "SA"
            self.ws[f'N{row}'].value = f'=TRIM(MID(SUBSTITUTE(H{row},"-",REPT(" ",100)),300,100))'
            
            # Column O: L1 formula (parts 2-3-4): =L&"-"&M&"-"&N
            # From parts: "BSRF-26-SA"
            self.ws[f'O{row}'].value = f'=L{row}&"-"&M{row}&"-"&N{row}'
            
            # Column P: L2 formula (full PID): =H
            self.ws[f'P{row}'].value = f'=H{row}'
            
            # Column Q: PROGRAM_MBR = VLOOKUP($P, BUDGET!$B:$N, 9, 0)
            # User's formula: =VLOOKUP($P634,BUDGET!$B:$N,9,0)
            # Column 9 in range B:N = Column J (Program Name)
            self.ws[f'Q{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,9,0),"N/A")'
            
            # Column R: DIV = VLOOKUP($P, BUDGET!$B:$N, 6, 0)
            # User's formula: =VLOOKUP($P634,BUDGET!$B:$N,6,0)
            # Column 6 in range B:N = Column G (Division)
            self.ws[f'R{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,6,0),"N/A")'
            
            # Column S: DEP = VLOOKUP($P, BUDGET!$B:$N, 5, 0)
            # User's formula: =VLOOKUP($P634,BUDGET!$B:$N,5,0)
            # Column 5 in range B:N = Column F (Department)
            self.ws[f'S{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,5,0),"N/A")'
            
            # Column T: FUNDING = VLOOKUP($P, BUDGET!$B:$N, 12, 0)
            # User's formula: =VLOOKUP($P634,BUDGET!$B:$N,12,0)
            # Column 12 in range B:N = Column M (Funding Source)
            self.ws[f'T{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,12,0),"N/A")'
            
            # Column U: CFU_SPONSOR = VLOOKUP($P, BUDGET!$B:$N, 3, 0)
            # User's formula: =VLOOKUP($P634,BUDGET!$B:$N,3,0)
            # Column 3 in range B:N = Column D (CFU Sponsor)
            self.ws[f'U{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,3,0),"N/A")'
            
            # Column V: AVAILMENT_TRACKER = VLOOKUP to 2026 CAPEX AVAILMENT workbook
            # Lookup: Column D (BOQ_PR - Ariba reference number)
            # File: 2026 CAPEX AVAILMENT_as of Feb 16.xlsx, sheet 'data_2026'
            # Lookup Range: Column C (MaximoReference)
            # Return: If found and contains "Ariba", return "For Ariba PR Translation"
            # Default: "For Ariba PR Translation" if not found
            self.ws[f'V{row}'].value = f"=IFNA(VLOOKUP(D{row},'[2026 CAPEX AVAILMENT_as of Feb 16.xlsx]data_2026'!$C:$C,1,0),\"For Ariba PR Translation\")"
            
            # Column W: PROPONENT = VLOOKUP from LOA_CURRENT_APPROVER workbook
            # Lookup: Column A (WP LOA number or approver ID)
            # File: LOA_CURRENT_APPROVER (Auto Email).xlsx, sheet 'page'
            # Return: Column 9 (Reported By)
            # Wrapper: PROPER to format the name properly
            self.ws[f'W{row}'].value = f"=IFERROR(PROPER(VLOOKUP(A{row},'[LOA_CURRENT_APPROVER (Auto Email).xlsx]page'!$A:$I,9,0)),\"N/A\")"
            
            # Column X: PROPONENT_1 (formatted name)
            # If PROPONENT (W) already in "First Last" format (no comma), return as-is
            # If PROPONENT in "Last, First" format (has comma), rearrange to "First Last"
            # Example: "Michelle Buga-Ay" → "Michelle Buga-Ay" (no change)
            # Example: "Padilla, Danross S." → "Danross S. Padilla" (rearranged)
            proponent1_formula = (
                f"=IF(ISERROR(FIND(\",\",W{row})),"
                f"W{row},"
                f"PROPER(TRIM(MID(W{row},FIND(\",\",W{row})+2,LEN(W{row}))&\" \"&LEFT(W{row},FIND(\",\",W{row})-1))))"
            )
            self.ws[f'X{row}'].value = proponent1_formula
            
            # Column Y: DIV_IN_REPORT = Nested IF mapping based on Column R (DIV code)
            # Maps DIV codes to formatted division names with responsible person
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
            
            # Column Z: PROJ = VLOOKUP($P, BUDGET!$B:$N, 10, 0)
            # Column 10 in range B:N = Column K (Project Name)
            self.ws[f'Z{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,10,0),"N/A")'
            
            # Column AA: SUBPROJ = VLOOKUP($P, BUDGET!$B:$N, 11, 0)
            # Column 11 in range B:N = Column L (Sub-project Name)
            self.ws[f'AA{row}'].value = f'=IFERROR(VLOOKUP($P{row},BUDGET!$B:$N,11,0),"N/A")'
    
    def add_external_file_support(self, availment_file: Optional[str] = None,
                                  loa_approver_file: Optional[str] = None) -> None:
        """
        External file support is currently disabled.
        Columns V and W use static default values.
        
        This method is kept for future compatibility but doesn't create extra sheets.
        
        Args:
            availment_file: (Not used)
            loa_approver_file: (Not used)
        """
        # All columns V, W, X already have default values from create_formulas()
        # No additional processing needed
        return
    
    
    def save(self, output_path: str) -> bool:
        """
        Save workbook with formulas
        
        Args:
            output_path: Path to save processed file
            
        Returns:
            True if successful
        """
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
        Complete processing pipeline
        
        Args:
            output_path: Path to save processed file
            availment_file: Optional CAPEX AVAILMENT file
            loa_approver_file: Optional LOA CURRENT APPROVER file
            
        Returns:
            True if successful
        """
        try:
            self.load_file()
            self.create_formulas()
            self.add_external_file_support(availment_file, loa_approver_file)
            self.save(output_path)
            return True
        except Exception as e:
            print(f"Error in processing: {str(e)}")
            return False
    
    def get_summary(self) -> Dict:
        """Get processing summary"""
        return {
            'total_rows': self.ws.max_row - 1,  # Exclude header
            'columns_added': 17,  # K through AA
            'output_type': 'Excel Formulas',
            'column_range': 'K:AA',
            'columns_created': [
                'PID (Mother and Sub)', '1', 'YEAR', '3', 'L1', 'L2',
                'PROGRAM_MBR', 'DIV', 'DEP', 'FUNDING', 'CFU_SPONSOR',
                'AVAILMENT_TRACKER', 'PROPONENT', 'PROPONENT_1',
                'DIV_IN_REPORT', 'PROJ', 'SUBPROJ'
            ]
        }
