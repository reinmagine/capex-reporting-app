# WP LOA Report Automation Guide

## Overview

The WP LOA (Work Plan Level of Authority) Report automation has been completed. It processes Excel files and creates a new version with formulas in columns K through AA.

## File Structure

Your WP LOA Report file should have:

### **Existing Columns (A-J) - System Generated**
- **A**: WP LOA
- **B**: Change Date
- **C**: Change Time
- **D**: BOQ PR
- **E**: Program
- **F**: Project
- **G**: Description
- **H**: PID (Mother and Sub-project)
- **I**: Amount (USD)
- **J**: Status

### **New Columns Created (K-AA) - Formula Based**

| Column | Header | Type | Description |
|--------|--------|------|-------------|
| K | PID (Mother and Sub) | Formula | Copy of column H |
| L | 1 | Manual | First part of L1 WBS (you enter this) |
| M | YEAR | Manual | Year value (you enter this) |
| N | 3 | Manual | Third part of L1 WBS (you enter this) |
| O | L1 | Formula | `=L&"-"&M&"-"&N` (auto-calculated) |
| P | L2 | Formula | Copy of column H |
| Q | PROGRAM MBR | Formula | VLOOKUP to BUDGET tab, column 10 |
| R | DIV | Formula | VLOOKUP to BUDGET tab, column 7 |
| S | DEP | Formula | VLOOKUP to BUDGET tab, column 6 |
| T | FUNDING | Formula | VLOOKUP to BUDGET tab, column 13 |
| U | CFU SPONSOR | Formula | VLOOKUP to BUDGET tab, column 4 |
| V | AVAILMENT TRACKER | Formula/Static | Reference value or external lookup |
| W | PROPONENT | Formula/Static | Default or external lookup |
| X | PROPONENT 1 | Formula/Static | Formatted proponent name |
| Y | DIV IN REPORT | Formula/Static | Division reference |
| Z | PROJ | Formula | VLOOKUP to BUDGET tab, column 11 |
| AA | SUBPROJ | Formula | VLOOKUP to BUDGET tab, column 12 |

## How to Use

### **Option 1: Using the GUI Application**

1. Run the application:
   ```bash
   python app_desktop.py
   ```

2. Click the **"WP LOA Report"** tab

3. Click **"Select WP LOA File"** and choose your main report Excel file

4. (Optional) Select supporting files:
   - CAPEX AVAILMENT file
   - LOA CURRENT APPROVER file

5. Click **"Process WP LOA Report"**

6. Choose where to save the output file

7. The app will create a new file with all formulas in place

### **Option 2: Using Test Script**

1. Place your WP LOA Report file in the `uploads` folder

2. Run the test script:
   ```bash
   python test_wp_loa.py
   ```

3. Open the output file (`output_*.xlsx`) in the `uploads` folder

### **Troubleshooting: VLOOKUP Returns "N/A"**

If VLOOKUP formulas show "N/A" instead of values:

1. **Verify BUDGET sheet exists** in your file

2. **Check BUDGET sheet structure**:
   ```bash
   python test_wp_loa.py analyze <path_to_your_file>
   ```
   This will display:
   - All columns in the BUDGET sheet
   - Sample data from each column
   - Which columns match expected VLOOKUP return columns

3. **Common issues**:
   - BUDGET sheet column order differs from expected
   - Column numbers (4, 6, 7, 10, 11, 12, 13) are incorrect
   - Lookup key (L2 in column P) doesn't match BUDGET column A values

4. **If columns are different**:
   - Note the actual column numbers from the analyzer
   - Update `processors/wp_loa_formula.py` lines in `create_formulas()` method
   - Change the column numbers in VLOOKUP formulas to match BUDGET structure

## File Organization

```
capex-reporting-app/
├── processors/
│   ├── wp_loa_formula.py        (Main processor - creates formulas)
│   ├── budget_analyzer.py       (Diagnostic tool)
│   └── wp_loa.py               (Old value-based processor - unused)
├── app_desktop.py              (GUI application)
├── app.py                      (CLI application)
├── test_wp_loa.py             (Test and diagnostic script)
├── uploads/                    (Put input files here for testing)
└── processed/                  (Output files saved here)
```

## Formula Details

### **L1 Formula (Column O)**
```excel
=L2&"-"&M2&"-"&N2
```
Concatenates the three parts with hyphens. Example: `M-MNA-24-NS`

### **VLOOKUP Formulas (Columns Q, R, S, T, U, Z, AA)**
```excel
=IFERROR(VLOOKUP(P2,BUDGET!$A:$AL,10,FALSE),"N/A")
```
- Looks up value from column P (L2)
- Searches in BUDGET sheet columns A through AL
- Returns specific column (10, 7, 6, 13, 4, 11, or 12)
- Returns "N/A" if not found (wrapped with IFERROR)
- Uses FALSE for exact match

## Expected Workflow

1. **System generates** columns A-J (WP LOA through Status)

2. **User processes** file through automation:
   - Output has new columns K-AA with formulas
   - Columns L, M, N are empty (ready for manual entry)

3. **User enters** values in columns L, M, N:
   - L: First part of L1 (e.g., "M")
   - M: Year (e.g., "MNA")
   - N: Third part (e.g., "24", "NS")

4. **Formulas auto-update**:
   - Column O calculates L1: `L&"-"&M&"-"&N`
   - Column P copies H (PID)
   - Columns Q-AA look up values in BUDGET

5. **Edit as needed** - all formulas remain intact

## Support Files

### **BUDGET Sheet** (Required)
Internal worksheet in main file with lookup table:
- Column A: L1 WBS codes (for lookup key)
- Other columns: Program info, department, etc.

### **CAPEX AVAILMENT File** (Optional)
External file with availability data:
- Used to populate column V (AVAILMENT_TRACKER)
- Lookup sheet name: `data_2026` (or `data_2024` etc.)

### **LOA CURRENT APPROVER File** (Optional)
External file with approver information:
- Used to populate column W (PROPONENT)
- Lookup sheet name: `page`

## Python API

For advanced users, you can use the processor directly:

```python
from processors.wp_loa_formula import WPLOAFormulaProcessor

# Create processor
processor = WPLOAFormulaProcessor('path/to/your/file.xlsx')

# Load workbook
processor.load_file()

# Create formulas
processor.create_formulas()

# Add external file lookups (optional)
processor.add_external_file_support(
    availment_file='path/to/availment.xlsx',
    loa_approver_file='path/to/approver.xlsx'
)

# Save output
processor.save_workbook('path/to/output.xlsx')

# Get summary
summary = processor.get_summary()
print(summary)
```

## Technical Details

### **Processor Class: WPLOAFormulaProcessor**

**Key Methods:**
- `load_file()` - Load Excel workbook using openpyxl
- `create_formulas()` - Add headers in row 1, formulas in rows 2+
- `add_external_file_support()` - Add VLOOKUP to external files
- `save_workbook()` - Write openpyxl workbook to file
- `get_summary()` - Return processing summary

**Key Attributes:**
- `NEW_COLUMN_HEADERS` - List of 17 column headers (K-AA)
- `COLUMNS` - Mapping of column names to positions
- `ws` - Active worksheet (openpyxl)
- `wb` - Workbook object (openpyxl)

### **VLOOKUP Column Mapping**

| VLOOKUP Column | BUDGET Column # | Data Type |
|---|---|---|
| Q (PROGRAM MBR) | 10 | Program name |
| R (DIV) | 7 | Division name |
| S (DEP) | 6 | Department name |
| T (FUNDING) | 13 | Funding source |
| U (CFU SPONSOR) | 4 | Sponsor name |
| Z (PROJ) | 11 | Project name |
| AA (SUBPROJ) | 12 | Sub-project name |

These column numbers are based on standard BUDGET sheet structure. **If your BUDGET sheet has different columns, these numbers will need adjustment.**

## Version History

- **Latest**: Formula-based processor with headers in K-AA, formulas in data rows
- **Previous**: Value-based processor (outdated, still in `wp_loa.py`)

## Next Steps

1. ✅ Test with sample data
2. ✅ Verify VLOOKUP matches BUDGET sheet structure
3. ✅ Enter L1 components in columns L, M, N
4. ✅ Verify all formulas calculate correctly
5. ⏳ Handle external file lookups (when files available)
6. ⏳ Automate L1 component extraction (future enhancement)
