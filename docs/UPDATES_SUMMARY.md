# WP LOA Formula Processor - Updates Summary

## Issues Fixed

### 1. **PID Extraction (Columns K, L, M, N)**

**Problem:** Columns K, L, M, N were empty or incorrectly populated. User needed these to extract parts from the PID.

**Solution:** Added formulas that automatically extract parts from column H using string functions:

```
From: H = "I-BSRF-26-SA"
      ↓
K = "I"      (Part 1)
L = "BSRF"   (Part 2)
M = "26"     (Part 3)
N = "SA"     (Part 4)
```

**Formulas Used:**
- **K:** `=LEFT(H{row},FIND("-",H{row})-1)` → Extracts first part before first hyphen
- **L:** `=TRIM(MID(SUBSTITUTE(H{row},"-",REPT(" ",100)),100,100))` → Extracts second part
- **M:** `=TRIM(MID(SUBSTITUTE(H{row},"-",REPT(" ",100)),200,100))` → Extracts third part
- **N:** `=TRIM(MID(SUBSTITUTE(H{row},"-",REPT(" ",100)),300,100))` → Extracts fourth part

### 2. **L1 Derivation (Column O)**

**Problem:** Previous formula was creating wrong result (e.g., "M-MNA-24-NS-MNA-24.0" instead of "BSRF-26-SA")

**Solution:** Now properly concatenates extracted parts 2, 3, 4 with hyphens:

```
Formula: =L{row}&"-"&M{row}&"-"&N{row}
Result:  BSRF-26-SA
```

### 3. **VLOOKUP to BUDGET Sheet (Columns Q-U, Z-AA)**

**Problem:** VLOOKUP formulas were returning "N/A" because they were looking up the full PID (H) instead of the L1 WBS value.

**Solution:** Changed all VLOOKUP formulas to use column O (the extracted L1 value) as the lookup key:

```
OLD: =IFERROR(VLOOKUP(P{row},BUDGET!$A:$AL,10,FALSE),"N/A")
     └─ Uses P (full PID like "I-BSRF-26-SA")
     
NEW: =IFERROR(VLOOKUP(O{row},BUDGET!$A:$AL,10,FALSE),"N/A")
     └─ Uses O (L1 value like "BSRF-26-SA")
```

**Column Mapping (all now reference O):**
- Q (PROGRAM_MBR):  Column 10 (J - Program Name)
- R (DIV):          Column 7 (G - Division)
- S (DEP):          Column 6 (F - Department)
- T (FUNDING):      Column 13 (M - Funding Source)
- U (CFU_SPONSOR):  Column 4 (D - CFU Sponsor)
- Z (PROJ):         Column 11 (K - Project Name)
- AA (SUBPROJ):     Column 12 (L - Sub-project Name)

### 4. **External File Support (Columns V, W, X)**

**Problem:** External file formulas had hardcoded paths to another user's computer, causing `#NAME?` error.

**Solution:** Completely redesigned external file handling:

**OLD (BROKEN):**
```excel
=IFNA(VLOOKUP(D1058,'C:\Users\paolagarcia-jalbuena\Downloads\...\[2026 CAPEX AVAILMENT.xlsx]data_2026'!$A:$Z,4,FALSE),"...")
```
← Hardcoded path doesn't work on your system

**NEW (WORKING):**
1. When external file is provided, the processor:
   - Loads the external file
   - Copies all its data into a NEW SHEET in your workbook (named `AVAILMENT_DATA` or `LOA_APPROVER_DATA`)
   - Creates formulas that reference these internal sheets

2. Formulas now look like:
```excel
V: =IFERROR(VLOOKUP(D{row},AVAILMENT_DATA!$A:$Z,4,FALSE),"For Ariba PR Translation")
W: =IFERROR(PROPER(VLOOKUP(A{row},LOA_APPROVER_DATA!$A:$I,5,FALSE)),"N/A")
```

**Benefit:** Works on any computer without path issues!

## How to Use

### Method 1: GUI Application

```bash
python app_desktop.py
```

1. Click "WP LOA Report" tab
2. Select your main WP LOA file
3. (Optional) Select external files:
   - CAPEX AVAILMENT file (for column V)
   - LOA CURRENT APPROVER file (for column W)
4. Click "Process WP LOA Report"
5. Save the output file

### Method 2: Quick Test Script

```bash
# Place your file in 'uploads' folder first
python test_wp_loa.py
# Output: uploads/output_your_filename.xlsx
```

#### With External Files

```python
from processors.wp_loa_formula import WPLOAFormulaProcessor

processor = WPLOAFormulaProcessor('path/to/wp_loa_report.xlsx')
processor.load_file()
processor.create_formulas()

# Add external files
processor.add_external_file_support(
    availment_file='path/to/2026 CAPEX AVAILMENT.xlsx',
    loa_approver_file='path/to/LOA_CURRENT_APPROVER.xlsx'
)

processor.save_workbook('output.xlsx')
```

## Expected Results After Processing

### ✅ Your output file should have:

1. **Row 1:** Headers in columns K-AA
2. **K-N:** Extracted PID parts (automatically calculated)
3. **O:** L1 formula result (fully auto-calculated)
4. **P:** L2 value (copy of H)
5. **Q-U, Z-AA:** VLOOKUP results from BUDGET sheet

### ✅ Example row with data "I-BSRF-26-SA" in H:

| Col | Header              | Formula/Value           | Result    |
|-----|---------------------|-------------------------|-----------|
| K   | PID (Mother/Sub)    | =LEFT(...) - extracted  | I         |
| L   | 1                   | =TRIM(MID(...))         | BSRF      |
| M   | YEAR                | =TRIM(MID(...))         | 26        |
| N   | 3                   | =TRIM(MID(...))         | SA        |
| O   | L1                  | =L&"-"&M&"-"&N          | BSRF-26-SA|
| P   | L2                  | =H                      | I-BSRF-26-SA |
| Q   | PROGRAM MBR         | =VLOOKUP(O,...,10,...)  | [from BUDGET] |
| R   | DIV                 | =VLOOKUP(O,...,7,...)   | [from BUDGET] |
| ... | ... (more columns) | ... (more VLOOKUP)      | ... |

## Troubleshooting

### Issue: VLOOKUP still showing "N/A"

**Cause:** L1 WBS value in column O doesn't match anything in BUDGET sheet Column A

**Solution:**
1. Open processed file
2. Check what value is in column O (e.g., "BSRF-26-SA")
3. Open BUDGET sheet
4. See if Column A contains that exact value
5. If not, check column A values to see the correct format

### Issue: External file formulas show #NAME?

**Cause:** Using old formula that referenced external file by path

**Solution:**
- Re-process with the updated processor
- Make sure to provide the external file paths when processing

### Issue: Parts not extracting correctly

**Cause:** PID format in H is different than expected (X-X-X-X pattern)

**Solution:**
- Check the actual PID format in your data
- If format is different, let me know and I can adjust the extraction formulas

## Summary of Technical Changes

### File Modified:
- `processors/wp_loa_formula.py`

### Methods Updated:
1. **`create_formulas()`**
   - K, L, M, N: Now have extraction formulas instead of being empty
   - O: Proper concatenation of extracted parts
   - Q, R, S, T, U, Z, AA: All reference O instead of P for VLOOKUP

2. **`add_external_file_support()`**
   - Loads external files
   - Copies data into internal sheets
   - Creates formulas referencing internal sheets (no paths)

### Backward Compatibility:
- Old files processed with the previous version will still work
- If you re-process, you'll get the fixed formulas

## Next Steps

1. ✅ **Test with your actual data**
   ```bash
   python test_wp_loa.py
   ```

2. ✅ **Verify VLOOKUP values appear** (not "N/A")
   - If still "N/A": Check BUDGET sheet Column A format

3. ✅ **Test with external files (if needed)**
   - Provide file paths and re-process

Let me know if you have any issues!
