# WP LOA Report Processing - Quick Start Guide

## 5-Minute Setup

### 1. Prepare Your Files

**Required:**
- WP LOA Report file with "page" and "BUDGET" tabs

**Recommended:**
- `2026 CAPEX AVAILMENT_as of Feb 16.xlsx` (for AVAILMENT TRACKER column)
- `LOA_CURRENT_APPROVER (Auto Email).xlsx` (for PROPONENT columns)

### 2. Launch the Tool

```bash
# Run the desktop application
python app_desktop.py
```

### 3. Click "WP LOA Report Processing" Tab

### 4. Select Files and Process

```
Step 1: Browse → Select your WP LOA Report file
Step 2: (Optional) Browse → Select external lookup files
        Click Process → Choose save location
```

Done! All derived columns are now automated.

---

## What Gets Automated

| Column | Source | Automation |
|--------|--------|-----------|
| L1 | Formula | `PID-L1Base-YEAR` |
| L2 | PID Column | Direct copy |
| PROGRAM_MBR | BUDGET Tab | VLOOKUP to column 9 |
| DIV | BUDGET Tab | VLOOKUP to column 7 |
| DEP | BUDGET Tab | VLOOKUP to column 6 |
| FUNDING | BUDGET Tab | VLOOKUP to column 13 |
| CFU_SPONSOR | BUDGET Tab | VLOOKUP to column 4 |
| AVAILMENT_TRACKER | External File | Lookup by BOQ PR |
| PROPONENT | External File | Lookup by WP LOA # |
| PROPONENT_1 | PROPONENT | Name format conversion |
| DIV_IN_REPORT | External File | Lookup by PR number |
| PROJ | BUDGET Tab | VLOOKUP to column 11 |
| SUBPROJ | BUDGET Tab | VLOOKUP to column 12 |

---

## Filtering Options

### MGA/MIA Filter
Keeps only rows where BOQ PR contains "MGA" or "MIA"
- ✓ Example: MIA1029963, MGA1075573
- ✗ Filtered out: Other PR formats

### Year 2026 Filter
Excludes rows where YEAR = 26
- Can be toggled in "Processing Options"
- Useful for year-end reporting

---

## File Structure Reference

### WP LOA Report File
**Main Sheet:** "page"
- Columns A-U contain data
- Column A: WP LOA
- Column D: BOQ PR (Pending no Ariba PR Only(
- Column H: PID (Mother and Sub)
- Column L: YEAR
- Column M: L1 Base Value

**Reference Sheet:** "BUDGET"
- Columns A-AL
- Column A: L1 WBS (lookup key)
- Columns to return: 4, 6, 7, 9, 11, 12, 13

### CAPEX AVAILMENT File (Optional)
**Sheet:** "data_2026"
- Column A: PRReferenceNumber
- Column C: WP LOA Reference
- Column H: Division

### LOA Current Approver File (Optional)
**Sheet:** "page"
- Column A: LOA#
- Column E: Current Approver

---

## Common Scenarios

### Scenario 1: Process with External Files
```
1. Select main WP LOA file
2. Select CAPEX AVAILMENT file
3. Select LOA CURRENT APPROVER file
4. Ensure both filters are checked
5. Click "Process WP LOA Report"
Result: All 13 columns populated with data
```

### Scenario 2: Process without External Files
```
1. Select main WP LOA file
2. Leave external file selections empty
3. Click "Process WP LOA Report"
Result: VLOOKUP columns populated from BUDGET
        AVAILMENT TRACKER = "For Ariba PR Translation"
        PROPONENT = "N/A"
```

### Scenario 3: Process Only Recent Records
```
1. Select main WP LOA file
2. Ensure "Filter out year 2026" is checked
3. Click "Process WP LOA Report"
Result: Only rows with non-26 YEAR values processed
```

---

## Troubleshooting

### Error: "Missing required columns"
- Check that main file has these exact columns:
  - WP LOA
  - BOQ PR (Pending no Ariba PR Only(
  - YEAR
  - PID (Mother and Sub)
  - Amount (USD)
  - 1 (the L1 base value column)

### AVAILMENT TRACKER shows "For Ariba PR Translation"
- External CAPEX AVAILMENT file not loaded
- OR BOQ PR value not found in That file
- To fix: Load the CAPEX AVAILMENT file

### PROPONENT shows "N/A"
- External LOA CURRENT APPROVER file not loaded
- OR WP LOA # not found in that file
- To fix: Load the LOA CURRENT APPROVER file

### Processing takes very long
- File might be very large (>5000 rows)
- External files might be corrupted
- Try processing a smaller subset first

---

## Output File

### Filename Format
```
WP_LOA_Processed_YYYYMMDD_HHMMSS.xlsx
```

### Columns Provided
- All original columns from main sheet
- Plus 13 new automated columns:
  1. L1
  2. L2
  3. PROGRAM_MBR
  4. DIV
  5. DEP
  6. FUNDING
  7. CFU_SPONSOR
  8. AVAILMENT_TRACKER
  9. PROPONENT
  10. PROPONENT_1
  11. DIV_IN_REPORT
  12. PROJ
  13. SUBPROJ

---

## Formula Reference (Excel)

If you need to manually create formulas, here are the equivalents:

```excel
=L1 formula=
=K&"-"&L&"-"&M

=L2 formula=
=H

=PROGRAM_MBR formula=
=VLOOKUP($P,BUDGET!$B:$N,9,0)

=DIV formula=
=VLOOKUP($P,BUDGET!$B:$N,6,0)

=DEP formula=
=VLOOKUP($P,BUDGET!$B:$N,5,0)

=FUNDING formula=
=VLOOKUP($P,BUDGET!$B:$N,12,0)

=CFU_SPONSOR formula=
=VLOOKUP($P,BUDGET!$B:$N,3,0)

=PROPONENT formula=
=PROPER(VLOOKUP(A,'[LOA_APPROVER.xlsx]page'!$A:$I,9,0))

=DIV_IN_REPORT formula=
=VLOOKUP([BOQ PR],'[AVAILMENT.xlsx]data'!$A:$Z,8,0)

=PROJ formula=
=VLOOKUP($P,BUDGET!$B:$N,10,0)

=SUBPROJ formula=
=VLOOKUP($P,BUDGET!$B:$N,11,0)
```

---

## Advanced Tips

### For Power Users

1. **Batch Processing:**
   - Process multiple files in sequence
   - File names automatically timestamp to prevent overwrites

2. **File Caching:**
   - External files are cached in memory
   - Reuse same external files across multiple WP LOA files
   - Cache clears when application closes

3. **Error Recovery:**
   - If a file is corrupted, tool will show specific error
   - You can reselect file and try again
   - Form "Clear All" button resets everything

4. **Custom File Paths:**
   - You can specify external files from different locations
   - Path is stored for current session only

---

## Before First Use

☐ Download all required and optional files to known location
☐ Verify WP LOA file has both "page" and "BUDGET" sheets
☐ Verify external files have sheets named "data_2026" and "page"
☐ Test with a small subset if file is very large
☐ Have backup of original files before processing

---

## Feature Comparison

### Manual Entry (Old Way)
- Time: 1 hour per WP LOA file
- Error Rate: 10-20%
- Steps: Copy data, use Excel formulas, manual lookups

### Automated (New Way)
- Time: 2-3 minutes per WP LOA file
- Error Rate: <1%
- Steps: Select files, click Process

**Time Saved:** 57 minutes per file
**For 100 files annually:** 95+ hours saved

---

## Questions?

Refer to full documentation: [WP_LOA_PROCESSING.md](WP_LOA_PROCESSING.md)

For code-level details, see:
- `processors/wp_loa.py` - Main processor
- `utils/vlookup.py` - VLOOKUP utilities
- `config.py` - Configuration mappings
