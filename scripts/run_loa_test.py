"""
Small runner to process LOA CURRENT APPROVER file.

Usage:
  python scripts/run_loa_test.py path/to/YourLOAFile.xlsx

If no path is provided, it will look for a file in `uploads/`.
"""

import sys
from pathlib import Path

from processors.wp_loa_formula import WPLOAFormulaProcessor

input_path = sys.argv[1] if len(sys.argv) > 1 else 'uploads/YourLOAFile.xlsx'

p = Path(input_path)
if not p.exists():
    print(f"ERROR: Input file not found: {input_path}")
    print("Place your LOA CURRENT APPROVER Excel file in the 'uploads' folder or provide a full path.")
    sys.exit(2)

print(f"Using input file: {input_path}")

processor = WPLOAFormulaProcessor(str(input_path))
ok, result = processor.process_loa_current_approver(str(input_path))
print("Result:", ok, result)
