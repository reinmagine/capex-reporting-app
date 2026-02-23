# CAPEX Reporting Tool - Implementation Analysis

## Summary
This document maps the 45 CAPEX Report processing steps against the current codebase implementation, identifying gaps and redundancies.

---

## ✅ STEPS CURRENTLY COVERED

### STEP 5 - Currency Conversion (Partial)
- **Status**: ✅ IMPLEMENTED
- **Location**: Both `app.py` and `app_desktop.py`
- **Coverage**: 
  - Currency conversion to USD for CJI5, CJI3, RFP, Reclass files
  - Uses formulas: `IF(J2="Php",(L2/57),IF(J2="SGD",(L2/1.34),(L2)))`
  - Adds "Amount_USD" column
- **Issue**: Uses hardcoded exchange rates instead of live/dynamic rates

### STEP 4 - Reference/Document Number Conversion
- **Status**: ✅ PARTIALLY IMPLEMENTED
- **Location**: `process_cji5()`, `process_cji3()` functions
- **Coverage**:
  - Converts ERP Reference (CJI5) to numeric format
  - Converts Purchasing Document (CJI3) to numeric format
  - Uses `pd.to_numeric()` with error coercion

### STEP 6 & 7 - Pivot Table Generation
- **Status**: ✅ PARTIALLY IMPLEMENTED
- **Location**: Advanced Features tab, `process_with_pivot()` function
- **Coverage**:
  - CJI5 pivot: Reference Document number (rows) vs Reference Document Category (columns)
  - CJI3 pivot: Purchasing Document number (rows)
  - Both pivot on Amount_USD (sum)
- **Gaps**:
  - STEP 6: No requirement to move "PReq" to 1st column position
  - STEP 7: No check for offsetting/cancellation
  - No validation of equal amounts

### STEP 9 & 10 - Car Plan Filtering (GNT-OTACP-25)
- **Status**: ✅ PARTIALLY IMPLEMENTED
- **Location**: `filter_carplan()` function in `app_desktop.py`
- **Coverage**:
  - Filters GNT-OTACP-25 from WBS/Project column
  - Exports filtered data
- **Gaps**:
  - Does NOT separate car plan PR totals vs PO totals
  - Does NOT update main tracker with totals
  - Does NOT handle lookup of ERP# vs PO#

### STEP 12 & 13 - Reclass & RFP Processing
- **Status**: ✅ PARTIALLY IMPLEMENTED
- **Location**: `process_reclass()`, `process_rfp()` functions
- **Coverage**:
  - Currency conversion to USD
  - Adds "Amount_USD" column
  - Reclass: Calculates total and adds TOTAL row
- **Gaps**:
  - NO filtering for "cell color in transaction currency column" (can't detect colors in pandas)
  - INCOMPLETE M-CBIP-25 removal (`remove_cbip()` function exists but only filters Object column)
  - Does NOT calculate proper subtotals excluding blank Object rows

### STEP 17 - ZMM File Processing
- **Status**: ✅ PARTIALLY IMPLEMENTED
- **Location**: `process_zmm()` function
- **Coverage**:
  - Finds Ariba PR Reference column
  - Delimits PR numbers (removes v1, v2, v3)
  - Converts PR number to numeric format
  - Copies PR Reference and PO columns
- **Gaps**:
  - Does NOT consolidate headers from multiple ZMM files
  - Does NOT copy columns in exact positions (C, E for PR Reference; D for PO)
  - Missing validation of column positions

---

## ❌ STEPS NOT IMPLEMENTED

### STEP 1 - GNT PID Separation & ZMM Consolidation
- **Status**: ❌ NOT IMPLEMENTED
- **Required Actions**:
  - Separate GNT PID for Carplan from CJI5 & CJI3
  - Consolidate multiple ZMM files into one
  - Validate header consistency before consolidation

### STEP 2 - Update Main Tracker with Date
- **Status**: ❌ NOT IMPLEMENTED
- **Required Actions**:
  - Save/update Excel files with current date in title
  - Main tracker file management

### STEP 3 - Conditional CJI3 Filtering
- **Status**: ❌ NOT IMPLEMENTED
- **Required Actions**:
  - Filter CJI3 if GNT not included
  - Skip if GNT already included

### STEP 8 - Duplicate Lookup & Merge
- **Status**: ❌ NOT IMPLEMENTED
- **Required Actions**:
  - Paste CJI5 pivot to CJI3
  - Lookup duplicate Purchasing Doc in CJI5 Ref. Doc
  - Remove duplicates
  - Merge CJI5 & CJI3 data into single table with PO number & amount

### STEP 11 - CAR PLAN CAPCOST LINE
- **Status**: ❌ NOT IMPLEMENTED
- **Required Actions**:
  - Request monthly amount from FBA
  - Update main tracker with capcost amounts
  - Handle monthly tracking

### STEP 14 - CJI5 Without Car Plan Processing
- **Status**: ❌ NOT IMPLEMENTED
- **Required Actions**:
  - Process CJI5 excluding GNT-OTACP-25 (car plan)
  - Apply same currency conversion
  - Note: Current `process_cji5()` includes all rows

### STEP 15-45 - Advanced Tracking & Integration
- **Status**: ❌ NOT IMPLEMENTED
- **These are comprehensive and include**:
  - STEP 15-26: Main tracker updates with PR/PO data
  - STEP 27-29: Main tracker formulas and consolidation
  - STEP 30+: Maximo & Ariba integration, status tracking, LOA reports
  - STEP 31-45: Complex lookup and multi-file processing

---

## 🔴 REDUNDANT / PROBLEMATIC CODE

### 1. **Duplicate Function Implementations**
```
- convert_currency_cji5() - only differs in column name
- convert_currency_cji3() - only differs in column name  
- convert_currency_rfp_reclass() - same logic
```
**Recommendation**: Create a single unified function with column mapping

### 2. **Two Separate Applications**
- `app.py` - Flask web version
- `app_desktop.py` - Tkinter desktop version
- Both contain identical logic with no code reuse

**Recommendation**: 
- Keep Desktop (app_desktop.py) as primary
- Remove Flask app (app.py) or refactor for better DRY principle

### 3. **Hardcoded Column Names**
- Currency column names: 'Transaction Currency', 'Value Trancurr', 'Value TranCurr'
- Reference columns: 'ERP Reference', 'Purchasing Document'
- WBS columns: Multiple variations searched

**Recommendation**: Create a config mapping file with column aliases

### 4. **Limited Exchange Rate Handling**
- Two rate sources: hardcoded defaults and API fetch
- No persistent storage of rates
- No handling of other currencies

**Recommendation**: Create persistent exchange rate manager

### 5. **Missing Error Handling**
- No validation of file structure before processing
- No warnings when expected columns are missing
- Silent failures on column not found

**Recommendation**: Add schema validation step

---

## 📋 FILE-BY-FILE PROCESSING WORKFLOW

### Current Processing Chain (Partial)

```
CJI5 File
├── Convert ERP Reference to number ✅
└── Convert Transaction Currency to USD ✅
    └── Pivot (optional) ✅

CJI3 File
├── Convert Purchasing Document to number ✅
└── Convert Transaction Currency to USD ✅
    └── Pivot (optional) ✅

RFP File
└── Convert Transaction Currency to USD ✅

Reclass File
├── Convert Transaction Currency to USD ✅
└── Calculate Total ✅

ZMM File
├── Find Ariba PR Reference ✅
├── Delimit PR Numbers ✅
└── Copy Columns ⚠️ (Incomplete)
```

### Missing Workflows (STEPS 8-45)
- Duplicate checking and data merge
- Main tracker consolidation
- Car plan extraction and totaling
- Ariba file integration
- Maximo LOA report integration
- Multi-step lookup and status tracking

---

## 🎯 RECOMMENDATIONS BY PRIORITY

### Priority 1: Fix Current Implementations
1. **Unify currency conversion** - Create single function with flexible column mapping
2. **Fix ZMM processing** - Ensure proper column positioning (C, D, E)
3. **File structure validation** - Add checks before processing
4. **Remove CBIP properly** - Handle both RFP and Reclass with subtotals

### Priority 2: Complete Partial Steps
1. **STEP 6-7**: Add pivot validation and formatting
2. **STEP 12-13**: Implement actual color filtering (flag cells needing color checks)
3. **STEP 17**: Fix column positioning and consolidation

### Priority 3: Add Missing Core Steps
1. **STEP 1-3**: Pre-processing and validation
2. **STEP 8**: Duplicate detection and merge logic
3. **STEP 9-14**: Car plan and main file variant processing

### Priority 4: Advanced Steps (STEP 15-45)
- These require main tracker Excel workbook management
- Require Ariba and Maximo file integration
- Would be multi-phase implementation

---

## 🏗️ SUGGESTED CODE STRUCTURE

```
app_desktop.py (Main)
├─ config.py
│  ├─ COLUMN_MAPPINGS (flexible column name aliases)
│  ├─ EXCHANGE_RATES (persistent or API)
│  └─ FILE_TYPES (processing specifications)
│
├─ processors/
│  ├─ base.py (BaseProcessor with validation)
│  ├─ cji.py (CJI5 & CJI3 processing)
│  ├─ rfp_reclass.py (RFP & Reclass processing)
│  └─ zmm.py (ZMM consolidation)
│
├─ utils/
│  ├─ currency.py (unified currency conversion)
│  ├─ validators.py (file structure validation)
│  ├─ column_mapper.py (flexible column finding)
│  └─ excel_helpers.py (Excel operations)
│
└─ ui/
   └─ gui.py (Tkinter UI)

DELETE: app.py (Flask version - redundant)
```

---

## ⚠️ KNOWN ISSUES

1. **No Cell Color Detection** - Pandas cannot detect Excel cell colors
   - STEP 12-13 require filtering by cell color
   - Workaround: Color-coded flag columns or manual marking

2. **Main Tracker Management** - Not implemented
   - STEPS 2, 9-11, 15-29 require main tracker file management
   - Would need workbook reference management

3. **Complex Lookups** - Steps 15-45 require complex multi-file relationships
   - Would need database-like structure or main tracker integration
   - Reference management across CJI5, CJI3, ZMM, Ariba, Maximo files

4. **Hardcoded Exchange Rates**
   - Currently uses 57 for PHP and 1.34 for SGD
   - Should use live API or user-provided rates

5. **No Timestamp Tracking**
   - Steps 25-26 reference "previous report amounts"
   - Would need versioning/historical tracking

---

## 📊 IMPLEMENTATION COVERAGE SUMMARY

| Step Range | Coverage | Status |
|-----------|----------|--------|
| STEP 1-3 | 0% | ❌ Not Started |
| STEP 4-7 | 60% | ⚠️ Partial |
| STEP 8-14 | 20% | ⚠️ Mostly Missing |
| STEP 15-29 | 5% | ❌ Not Started |
| STEP 30-45 | 0% | ❌ Not Started |
| **Overall** | **~20%** | ⚠️ Early Stage |

