# Flexible File Detection System - User Guide

## Overview

The app now **automatically detects files** regardless of their naming variations. No more need to worry about exact file names or dates!

## Supported File Variations

### 1. **CAPEX AVAILMENT Files**
The app will find ANY of these automatically:
- `2026 CAPEX AVAILMENT_as of FEB 23.xlsx`
- `2026 CAPEX AVAILMENT_as of Feb 16.xlsx`
- `2026 CAPEX AVAILMENT_as of Feb 15.xlsx`
- `CAPEX_AVAILMENT_2026.xlsx`
- Any file with "2026", "CAPEX", and "AVAILMENT" in the name

**Detection Rule:** File must contain keywords: `capex`, `availment`, `2026`

---

### 2. **LOA CURRENT APPROVER Files**
The app will find ANY of these automatically:
- `LOA_CURRENT_APPROVER (Auto Email).xlsx`
- `LOA Current Approver - Auto Email.xlsx`
- `LOA_CURRENT_APPROVER.xlsx`
- `LOA APPROVER Email.xlsx`
- Any file with "LOA" and "APPROVER" in the name

**Detection Rule:** File must contain keywords: `loa`, `approver`, `email`

---

### 3. **WP LOA REPORT Files**
The app will find ANY of these automatically:
- `WP LOA Report.xlsx`
- `WP_LOA_Report_2026.xlsx`
- `WP LOA Report - 2026.xlsx`
- `Report_WP_LOA.xlsx`
- Any file with "WP" and "LOA" and "REPORT" in the name

**Detection Rule:** File must contain keywords: `wp`, `loa`, `report`

---

## How It Works

### **Automatic Detection (No User Action Needed)**

When you process a file:

```python
from processors.wp_loa_formula import WPLOAFormulaProcessor

# Initialize with your WP LOA file
processor = WPLOAFormulaProcessor('path/to/WP LOA Report.xlsx')

# Process and save - files are AUTO-DETECTED!
processor.process_and_save('path/to/output.xlsx')

# Output:
# Auto-detected files:
#   ✓ capex_availment: 2026 CAPEX AVAILMENT_as of FEB 23.xlsx
#   ✓ loa_approver: LOA_CURRENT_APPROVER (Auto Email).xlsx
```

---

### **Manual Override (If Needed)**

If auto-detection doesn't find the right file, you can specify it manually:

```python
processor.process_and_save(
    'output.xlsx',
    availment_file='path/to/my_custom_availment_file.xlsx',
    loa_approver_file='path/to/my_custom_approver_file.xlsx'
)
```

---

## File Detection Algorithm

The system uses **keyword matching** (case-insensitive):

1. **Search all files** in the same directory as input file
2. **Check file extension**: Only .xlsx, .xls, .csv files
3. **Match keywords**: ALL keywords must appear in filename
4. **Return first match** found

### Example

For CAPEX AVAILMENT detection:
- `2026 CAPEX AVAILMENT_as of FEB 23.xlsx` ✅ FOUND
  - Contains: `2026`, `capex`, `availment`
  
- `Budget 2026 Data.xlsx` ❌ NOT FOUND
  - Missing: `capex`, `availment`

---

## Using FileDetector Directly

You can also use the `FileDetector` utility independently:

```python
from utils.file_detector import FileDetector

# Find CAPEX AVAILMENT file
availment = FileDetector.find_capex_availment('path/to/directory')
print(availment)  # Returns full path or None

# Find LOA Approver file
loa = FileDetector.find_loa_approver('path/to/directory')
print(loa)  # Returns full path or None

# Auto-detect all files at once
all_files = FileDetector.auto_detect_all_files('path/to/directory')
print(all_files)
# {
#     'wp_loa_report': '/path/to/WP LOA Report.xlsx',
#     'capex_availment': '/path/to/2026 CAPEX AVAILMENT_as of FEB 23.xlsx',
#     'loa_approver': '/path/to/LOA_CURRENT_APPROVER (Auto Email).xlsx',
#     'budget': '/path/to/BUDGET.xlsx'
# }

# Get file info
info = FileDetector.get_file_info(availment)
print(info)
# {
#     'exists': True,
#     'name': '2026 CAPEX AVAILMENT_as of FEB 23.xlsx',
#     'size_mb': 2.5,
#     'path': '/path/to/...'
# }
```

---

## Changes Made

### New Files
- `utils/file_detector.py` - Core file detection utility

### Modified Files
- `processors/wp_loa_formula.py` - Now uses auto-detection
- `processors/wp_loa.py` - Now uses auto-detection

### Key Changes
1. **`create_formulas()`** now accepts optional file paths and auto-detects if not provided
2. **`load_external_files()`** now auto-detects files if paths not provided
3. **`auto_detect_external_files()`** method added to both processors

---

## Benefits

✅ **No more file renaming** - Works with any naming convention  
✅ **Date-agnostic** - Finds files regardless of "FEB 23" vs "Feb 16"  
✅ **Case-insensitive** - "CAPEX", "Capex", "capex" all work  
✅ **Automatic** - Users don't need to browse for files  
✅ **Backwards compatible** - Still accepts manual file paths if needed  

---

## Example Workflow

```
User's Laptop:
├── WP LOA Report - 2026.xlsx          ← Any name with WP, LOA, REPORT
├── 2026 CAPEX AVAILMENT_as of Feb 23  ← Any name with CAPEX, AVAILMENT
├── LOA Current Approver Email.xlsx    ← Any name with LOA, APPROVER
└── App runs...
    → Auto-detects all 3 files ✓
    → Processes correctly ✓
    → No user configuration needed ✓
```

---

## Error Handling

If a file is not found:

```
Auto-detected files:
  ✓ capex_availment: 2026 CAPEX AVAILMENT_as of FEB 23.xlsx
  ✗ loa_approver: NOT FOUND
  ✓ wp_loa_report: WP LOA Report.xlsx

App continues with missing file:
  - LOA lookups will return "N/A" values
  - Processing still completes
  - User gets partial results
```

You can fix by:
1. Renaming file to match keywords (e.g., add "approver" to filename)
2. Moving file to same directory as WP LOA Report
3. Providing manual path in code

---

## Testing

To test file detection:

```python
from utils.file_detector import FileDetector

# List all detected files
detected = FileDetector.auto_detect_all_files('C:/Users/YourName/Documents')

for file_type, path in detected.items():
    if path:
        print(f"✓ Found {file_type}: {path}")
    else:
        print(f"✗ Missing {file_type}")
```

---

## Summary

The app is now **file-naming agnostic**! Users can name files however they want (within reason), and the app will still find and use them automatically.

**No more:** "Error: File not found" message  
**Yes to:** Smart, automatic file detection ✨
