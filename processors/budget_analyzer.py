"""
WP LOA BUDGET Sheet Analyzer
Helps diagnose why VLOOKUP formulas return N/A
"""

import pandas as pd
from pathlib import Path


def analyze_budget_sheet(file_path: str) -> None:
    """
    Analyze BUDGET sheet structure and display for debugging
    
    Helps identify:
    - What columns exist
    - What data is in lookup columns
    - Why VLOOKUP might fail
    
    Args:
        file_path: Path to WP LOA Report file
    """
    try:
        df = pd.read_excel(file_path, sheet_name='BUDGET')
        
        print("\n=" * 80)
        print("BUDGET SHEET ANALYSIS")
        print("=" * 80)
        print(f"\nTotal rows: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        
        print("\nColumn Headers (A through AL):")
        for idx, col in enumerate(df.columns, start=1):
            print(f"  Column {idx:2d} ({chr(64+idx)}): {col}")
        
        print("\nFirst 5 rows of data:")
        print(df.head().to_string())
        
        print("\n\nCritical columns for VLOOKUP:")
        print("-" * 80)
        
        # Check column A (should be L1 WBS for lookup)
        if len(df.columns) >= 1:
            col_a = df.columns[0]
            print(f"\nColumn A ({col_a}):")
            print(f"  Sample values: {list(df.iloc[:5, 0])}")
            print(f"  Unique values: {df.iloc[:, 0].nunique()}")
        
        # Check if columns exist for VLOOKUP returns
        required_cols = {
            4: 'CFU Sponsor (for column U)',
            6: 'Department (for column S)',
            7: 'Division (for column R)',
            10: 'Program/Budget Owner (for column Q)',
            11: 'Project Name (for column Z)',
            12: 'Sub-project Name (for column AA)',
            13: 'Funding Source (for column T)'
        }
        
        print("\nVLOOKUP Return Columns:")
        for col_num, description in sorted(required_cols.items()):
            if col_num <= len(df.columns):
                col_name = df.columns[col_num - 1]
                print(f"  Column {col_num} ({chr(64+col_num)}): {col_name}")
                print(f"    Description: {description}")
                print(f"    Sample: {list(df.iloc[:2, col_num-1])}")
            else:
                print(f"  Column {col_num}: ⚠️ MISSING (only {len(df.columns)} columns exist)")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"Error analyzing BUDGET sheet: {str(e)}")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        analyze_budget_sheet(sys.argv[1])
    else:
        print("Usage: python budget_analyzer.py <path_to_wp_loa_file>")
