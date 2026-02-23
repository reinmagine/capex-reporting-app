# WP LOA Report Processing Automation

## Overview

The WP LOA (Work Package Letter of Authority) Report processing automation provides an integrated solution for automating data enrichment, filtering, and VLOOKUP operations across multiple Excel workbooks. This feature eliminates manual data entry and ensures consistency across the WP LOA reporting workflow.

## Architecture

### Core Components

#### 1. **WPLOAProcessor** (`processors/wp_loa.py`)
Main processor class handling:
- Loading and validating WP LOA workbook structure
- Filtering PR numbers and years
- Creating derived columns through VLOOKUP and concatenation
- Interfacing with external reference files

**Key Methods:**
- `load_file(file_path)` - Load main WP LOA workbook
- `load_external_files(availment_file, loa_approver_file)` - Load reference workbooks
- `filter_boq_pr()` - Filter for MGA/MIA PR numbers
- `filter_year_2026()` - Exclude year 2026 rows
- `process_full()` - Execute complete processing pipeline
- `save(output_path)` - Save processed results

#### 2. **VLookupHelper** (`utils/vlookup.py`)
Utility class providing Excel-like VLOOKUP operations:
- `vlookup()` - Single value VLOOKUP
- `vlookup_column()` - Column-wise VLOOKUP application

#### 3. **ExternalFileLookup** (`utils/vlookup.py`)
Manages external file loading and lookups with built-in caching:
- `load_external_file()` - Load and cache external workbooks
- `vlookup_external()` - VLOOKUP on external files
- `clear_cache()` - Reset file cache

#### 4. **NameFormatter** (`utils/vlookup.py`)
Helper for name transformations:
- `reform_name()` - Convert "Last, First" to "First Last" format

### Data Flow

```
Input: WP LOA Report (main file + optional external files)
  ↓
Load & Validate Structure
  ↓
Filter Rows (MGA/MIA, Year 26)
  ↓
Create Derived Columns:
  ├── L1: Concatenate PID-L1Base-YEAR
  ├── L2: Copy of PID
  ├── PROGRAM_MBR: VLOOKUP(L2 → BUDGET[9])
  ├── DIV: VLOOKUP(L2 → BUDGET[7])
  ├── DEP: VLOOKUP(L2 → BUDGET[6])
  ├── FUNDING: VLOOKUP(L2 → BUDGET[13])
  ├── CFU_SPONSOR: VLOOKUP(L2 → BUDGET[4])
  ├── AVAILMENT_TRACKER: VLOOKUP(BOQ PR → AVAILMENT)
  ├── PROPONENT: VLOOKUP(WP LOA → LOA_APPROVER)
  ├── PROPONENT_1: Format PROPONENT name
  ├── DIV_IN_REPORT: Lookup from AVAILMENT
  ├── PROJ: VLOOKUP(L2 → BUDGET[11])
  └── SUBPROJ: VLOOKUP(L2 → BUDGET[12])
  ↓
Output: Processed Excel file
```

## Input File Requirements

### Main WP LOA Report File
**Sheet Name:** `page`

**Required Columns:**
- WP LOA
- BOQ PR (Pending no Ariba PR Only(
- YEAR
- PID (Mother and Sub)
- Amount (USD)
- 1 (L1 value column)
- And others as per standard template

**Internal Reference Sheet:**
- Sheet Name: `BUDGET`
- Columns: A-AL with standard structure
  - Column B: L1 WBS (lookup key)
  - Column 4: CFU Sponsor
  - Column 5: CAPEX Type / Department
  - Column 6: Dept
  - Column 7: Div
  - Column 9: Budget Owner SPOC / Program Name
  - Column 11: Project Name
  - Column 12: Sub-project Name
  - Column 13: Funding Source

### Optional External Files

#### 2026 CAPEX AVAILMENT File
**File Name:** `2026 CAPEX AVAILMENT_as of Feb 16.xlsx` (or similar)
**Sheet Name:** `data_2026`

**Key Columns:**
- A: PRReferenceNumber (lookup key for DIV IN REPORT)
- B: System
- C: WP LOA Reference (lookup for AVAILMENT TRACKER)
- D: ERP Reference
- ... (other columns)

**Used For:**
- AVAILMENT TRACKER column (lookup by BOQ PR)
- DIV IN REPORT column (lookup by PR Reference Number)

#### LOA Current Approver File
**File Name:** `LOA_CURRENT_APPROVER (Auto Email).xlsx`
**Sheet Name:** `page`

**Key Columns:**
- A: LOA# (lookup key)
- B-D: Metadata
- E: Current Approver (return value for PROPONENT)

**Used For:**
- PROPONENT column
- PROPONENT 1 column (formatted version)

## Processing Steps

### Step 1: Filter PR Numbers
Keeps only rows with BOQ PR containing "MGA" or "MIA"
- Example: MIA1029963, MGA1075573
- Removes: Other PR formats or empty values

### Step 2: Filter by Year
Option to exclude rows with YEAR = 26
- Can be toggled in GUI
- Preserves rows with other year values

### Step 3: Create L1 Column
Concatenates three columns with "-" separator:
```
L1 = PID + "-" + 1_value + "-" + YEAR
Example: I-BSRF-26
```

### Step 4: Create L2 Column
Uses full PID string as lookup key:
```
L2 = PID (Mother and Sub)
Example: I-BSRF-26-SA
```

### Step 5: VLOOKUP to BUDGET Tab
Performs multiple lookups using L2 as key:

| Column | VLOOKUP Col | Return Col | Usage |
|--------|-------------|-----------|-------|
| PROGRAM_MBR | L2 | 9 | Program/Budget Owner |
| DIV | L2 | 7 | Division |
| DEP | L2 | 6 | Department |
| FUNDING | L2 | 13 | Funding Source |
| CFU_SPONSOR | L2 | 4 | CFU Sponsor |
| PROJ | L2 | 11 | Project Name |
| SUBPROJ | L2 | 12 | Sub-project Name |

### Step 6: VLOOKUP to External Files

**AVAILMENT TRACKER:**
- Lookup: BOQ PR value in AVAILMENT file
- Return: Status or "For Ariba PR Translation"

**PROPONENT:**
- Lookup: WP LOA number in LOA_CURRENT_APPROVER file
- Return: Current Approver name
- Format: Apply PROPER case formatting

**PROPONENT_1:**
- Source: PROPONENT column
- Format: Convert "Last, First" to "First Last"
- Example: "Padilla, Danross S." → "Danross Padilla"

**DIV_IN_REPORT:**
- Lookup: BOQ PR in AVAILMENT file
- Return: Division/Department assignment
- Example: "SPE/Joel", "CIPE/Ting"

## Configuration

All column mappings and processing rules are configured in `config.py` under `WP_LOA_CONFIG`:

```python
WP_LOA_CONFIG = {
    'required_columns': [...],  # Validation list
    'budget_tab_name': 'BUDGET',  # Internal reference sheet
    'page_tab_name': 'page',  # Main data sheet
    'external_lookup_columns': {...},  # External file references
    'derived_columns': {...}  # Column creation rules
}
```

## GUI Usage

### Step 1: Select Main File
1. Click "Browse..." button under "Step 1"
2. Select your WP LOA Report Excel file
3. File path will display in the text field

### Step 2: Load Optional External Files
1. **For AVAILMENT TRACKER and DIV IN REPORT:**
   - Click "Browse" under CAPEX AVAILMENT
   - Select "2026 CAPEX AVAILMENT_as of Feb 16.xlsx"
   
2. **For PROPONENT lookup:**
   - Click "Browse" under LOA Current Approver
   - Select "LOA_CURRENT_APPROVER (Auto Email).xlsx"

3. Both files are optional. Without them:
   - AVAILMENT TRACKER → "For Ariba PR Translation"
   - PROPONENT → "N/A"
   - DIV IN REPORT → Empty

### Step 3: Configure Options
- ✓ **Filter for MGA/MIA PR numbers** (default: checked)
  - Only includes rows with MGA or MIA in BOQ PR column
  
- ✓ **Filter out year 2026** (default: checked)
  - Excludes rows where YEAR = 26

### Step 4: Process
1. Click "Process WP LOA Report" button
2. Tool will show progress indicator
3. When complete, choose save location
4. File saves with timestamp in filename

### Clear Form
- Click "Clear All" to reset all selections

## Error Handling

### Missing Required Columns
```
Validation Error: Missing required columns
- YEAR
- PID (Mother and Sub)
```
**Solution:** Ensure your file has the exact column names as required

### External File Not Found
```
Error: File not found: path/to/file.xlsx
```
**Solution:** Verify the file path and location are correct

### Sheet Not Found
```
Error loading sheet 'data_2026' from ...
```
**Solution:** Check sheet name in external file matches expected name

## Performance Considerations

### File Caching
- External files are cached after first load
- Subsequent lookups use cached data (faster)
- Cache cleared when application closes
- Manual cache clear: `ExternalFileLookup.clear_cache()`

### Processing Speed
- 100 rows: ~2-3 seconds
- 1,000 rows: ~10-15 seconds
- 10,000 rows: ~60-90 seconds
- Depends on number of VLOOKUP operations and external file size

### Optimization Tips
1. Use smaller external files if possible
2. Filter data before processing
3. Process in batches if dataset is very large
4. Load external files once (reuse for multiple files)

## Advanced Usage

### Programmatic Usage

```python
from processors.wp_loa import WPLOAProcessor

# Create processor
processor = WPLOAProcessor()

# Load main file
processor.load_file('WP_LOA_Report.xlsx')

# Load external files (optional)
processor.load_external_files(
    availment_file='2026 CAPEX AVAILMENT.xlsx',
    loa_approver_file='LOA_CURRENT_APPROVER.xlsx'
)

# Process
result_df = processor.process_full()

# Save
processor.save('WP_LOA_Processed.xlsx')

# Get statistics
summary = processor.get_summary()
print(f"Processed {summary['total_rows']} rows")
```

### Custom Lookups

```python
from utils.vlookup import VLookupHelper, ExternalFileLookup

# Load external file
df = ExternalFileLookup.load_external_file(
    'file.xlsx', 
    'sheet_name'
)

# Perform VLOOKUP
result = VLookupHelper.vlookup(
    lookup_value='MIA1029963',
    table_array=df,
    col_index=3,
    not_found_value='Not Found'
)
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "No columns found" | Column name mismatch | Check exact column names in source file |
| VLOOKUP returns "N/A" | No matching value in lookup table | Verify lookup value exists in external file |
| Processing hangs | Large file with many lookups | Check external file is not corrupted; try smaller file |
| External file error | Wrong sheet name | Verify sheet name matches expected (e.g., 'data_2026') |
| Name formatting doesn't work | Unexpected name format | Review actual format in PROPONENT column |

## Future Enhancements

- [ ] Batch processing for multiple WP LOA files
- [ ] Custom formula mapping interface
- [ ] Advanced filtering options (date ranges, amount ranges)
- [ ] Data validation and quality checks
- [ ] Report generation with statistics
- [ ] Direct database connectivity (instead of Excel)
- [ ] Batch external file loading

## Related Files

- **Main Processor:** `processors/wp_loa.py`
- **Utilities:** `utils/vlookup.py`
- **Configuration:** `config.py` (WP_LOA_CONFIG section)
- **GUI Integration:** `app_desktop.py` (create_wp_loa_tab method)

## Support

For issues or enhancements:
1. Check configuration in `config.py`
2. Validate input file structure
3. Review error messages in status bar
4. Check application logs for detailed error traces

## Example Workflow

```
1. Start application
2. Click "WP LOA Report Processing" tab
3. Select main WP LOA Report file
4. (Optional) Select CAPEX AVAILMENT file
5. (Optional) Select LOA CURRENT APPROVER file
6. Ensure filter options are set as needed
7. Click "Process WP LOA Report"
8. Wait for completion notification
9. Choose save location and filename
10. File saved with all derived columns populated
```

## Technical Details

### Column Index Mapping (BUDGET Tab)
- Column 1 (A): L1 WBS (lookup key)
- Column 4 (D): CFU Sponsor
- Column 5 (E): CAPEX Type
- Column 6 (F): Dept
- Column 7 (G): Div
- Column 9 (I): Budget Owner SPOC / Program Name
- Column 11 (K): Project Name
- Column 12 (L): Sub-project Name
- Column 13 (M): Funding Source

### Data Type Handling
- All values converted to string for comparison
- Empty cells handled as "N/A" or empty string
- Currency values preserved as-is
- Date values kept in original format

### Name Formatting Logic
```
Input: "Padilla, Danross S."
Processing:
  1. Split by comma: ["Padilla", "Danross S."]
  2. Extract first word of first name: "Danross"
  3. Format: "{FirstName} {LastName}"
Output: "Danross Padilla"
```
