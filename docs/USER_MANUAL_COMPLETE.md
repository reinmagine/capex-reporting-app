# CAPEX Reporting Tool - Complete User Manual

---

## TABLE OF CONTENTS

1. Overview and Introduction
2. System Requirements
3. Installation Guide (Windows)
4. Installation Guide (macOS)
5. First-Time Setup
6. Application Interface Overview
7. How to Use Each Feature
8. Troubleshooting and FAQ
9. Tips and Best Practices
10. Quick Reference Guide

---

## 1. OVERVIEW AND INTRODUCTION

### What is the CAPEX Reporting Tool?

The CAPEX Reporting Tool is a desktop application designed to help you process and manage capital expenditure (CAPEX) data efficiently. The tool automatically converts and formats financial data into standardized Excel files with embedded formulas for easy calculation and modification.

### Who Should Use This Tool?

- Finance teams managing CAPEX reporting
- Personnel processing procurement and financial data
- Anyone working with CJI, RFP, Reclass, ZMM, or WP LOA reports
- Excel and financial data management professionals

### Key Benefits

- Fast processing: Converts large files in seconds instead of minutes
- Formula retention: Output files contain editable Excel formulas, not static values
- Multiple file formats supported: Works with CJI5, CJI3, RFP, Reclass, ZMM, and WP LOA files
- Cross-platform: Available for both Windows and macOS
- Manual updates: Receive new versions when notified by your IT department
- Data validation: Checks files before processing to ensure compatibility

### Application Features

The tool supports processing and conversion for six different file types, each with specific functions:

- WP LOA Report: Handles work package level of assurance data
- CJI5: Processes CJI version 5 financial reference documents
- CJI3: Processes CJI version 3 financial reference documents
- RFP: Manages request for proposal financial data
- Reclass: Reclassifies financial entries between categories
- ZMM: Handles procurement and PR (Purchase Requisition) reference data

---

## 2. SYSTEM REQUIREMENTS

### For Windows Users

- Operating System: Windows 10 or Windows 11
- Processor: Intel or AMD processor (any recent model)
- RAM: 4 GB minimum (8 GB recommended)
- Storage Space: 200 MB free space
- Internet Connection: Required only for initial download (not needed for general use)
- Excel or Spreadsheet Application: Excel 2016 or newer (to open processed files)

### For macOS Users

- Operating System: macOS 10.14 (Mojave) or newer
- Processor: Intel or Apple Silicon (M1/M2/M3)
- RAM: 4 GB minimum (8 GB recommended)
- Storage Space: 200 MB free space
- Internet Connection: Required only for initial download (not needed for general use)
- Excel or Spreadsheet Application: Excel 2016 for Mac or newer (to open processed files)

### General Requirements

- Internet connection only needed for initial download
- Excel, Numbers, or any spreadsheet application to work with output files
- Basic computer skills (file selection, button clicking)

---

## 3. INSTALLATION GUIDE - WINDOWS

### Step 1: Download the Application

1. You should have received a download link to the Google Drive folder from your IT team or manager
2. Click the Google Drive folder link (or paste it in your browser)
3. Look for the file named "CAPEX_Reporting_Tool.exe" (approximately 50-60 MB)
4. Right-click on the file and select "Download"
5. The file begins downloading to your computer
6. Wait for download to complete (approximately 1-3 minutes depending on internet speed)
7. The file will be in your Downloads folder by default

Alternative if you have trouble downloading:
- Click the three-dot menu next to the file
- Select "Make a copy" or "Download"
- Save to your computer

[Screenshot Placeholder: Google Drive folder showing CAPEX_Reporting_Tool.exe]

### Step 2: Install the Application

1. Open your Downloads folder or the location where you saved the file
2. Find "CAPEX_Reporting_Tool.exe"
3. Double-click the file
4. Windows may show a "User Account Control" dialog asking for permission - click "Yes"
5. An installer window appears showing installation progress
6. Wait until installation completes (approximately 30-60 seconds)
7. Click "Finish" when the installation window closes
8. A shortcut may be created on your desktop

[Screenshot Placeholder: Installation wizard showing progress]

### Step 3: Run the Application

1. Double-click the "CAPEX Reporting Tool" shortcut on your desktop, OR
2. Use Windows Start Menu:
   - Click the Start button (Windows logo in lower left)
   - Type "CAPEX Reporting Tool"
   - Click the application name when it appears
3. The application window opens and is ready to use

[Screenshot Placeholder: Application main window on Windows]

### Step 4: Getting New Versions

When your organization has updates:

1. Your IT department will notify you that a new version is available
2. Go to the same Google Drive folder
3. Download the new version file (CAPEX_Reporting_Tool.exe)
4. Run the new installer file (it automatically replaces the old version)
5. You now have the latest version installed

---

## 4. INSTALLATION GUIDE - MACOS

### Step 1: Download the Application

1. You should have received a download link to the Google Drive folder from your IT team or manager
2. Click the Google Drive folder link (or paste it in your browser)
3. Look for the file named "CAPEX_Reporting_Tool.app.zip" (approximately 70-80 MB)
4. Right-click on the file and select "Download"
5. Or click the three-dot menu next to the file and select "Download"
6. The file begins downloading to your computer
7. Wait for download to complete (approximately 2-4 minutes depending on internet speed)
8. The file will be in your Downloads folder by default

[Screenshot Placeholder: Google Drive folder showing CAPEX_Reporting_Tool.app.zip on macOS]

### Step 2: Extract the Application

Method 1: Automatic (Recommended)

1. Open Finder (the blue face icon in the dock)
2. Click "Downloads" in the sidebar
3. Find "CAPEX_Reporting_Tool.app.zip" in the Downloads folder
4. Double-click the file
5. macOS automatically extracts the file
6. You now have "CAPEX_Reporting_Tool.app" in your Downloads folder

Method 2: Manual

1. Open Terminal (Launchpad > Other > Terminal, or Spotlight search for Terminal)
2. Copy and paste this command, then press Enter:
   cd ~/Downloads && unzip CAPEX_Reporting_Tool.app.zip

Screenshot Placeholder: [Finder showing Downloads with extracted app]

### Step 3: Run the Application (First Time)

Important: macOS requires approval before running the application.

1. Open Finder and go to Downloads folder
2. Find "CAPEX_Reporting_Tool.app"
3. Right-click (or Control+click) on the app
4. Select "Open" from the menu
5. A security dialog appears saying "macOS cannot verify the developer"
6. Click the "Open" button in this dialog
7. The application window opens and runs successfully

Screenshot Placeholder: [macOS security dialog and app opening]

### Step 4: Run the Application (Subsequent Times)

After the first launch, you can open the application normally:

1. Open Finder and go to Downloads folder
2. Double-click "CAPEX_Reporting_Tool.app", OR
3. Drag the app to Applications folder and double-click from there

### Troubleshooting: App Won't Open

If you see an error message like "CAPEX_Reporting_Tool cannot be opened because Apple cannot check it for malicious software," follow these steps:

Solution 1: Use Terminal Command (Fastest)

1. Open Terminal (Spotlight search for Terminal)
2. Copy and paste this entire line:
   xattr -d com.apple.quarantine ~/Downloads/CAPEX_Reporting_Tool.app
3. Press Enter and wait for completion
4. Double-click the app to open it normally

Solution 2: System Settings

1. Try to open the app (security dialog appears)
2. Go to System Settings > Privacy & Security
3. Find CAPEX_Reporting_Tool in the list
4. Click "Open Anyway"
5. The app now opens

Screenshot Placeholder: [Terminal command execution or System Settings screen]

### Step 5: Getting New Versions

When your organization has updates:

1. Your IT department will notify you that a new version is available
2. Go to the same Google Drive folder
3. Download the new version file (CAPEX_Reporting_Tool.app.zip)
4. Extract the new .app.zip file (same process as Step 2)
5. Replace the old CAPEX_Reporting_Tool.app with the new version
6. You now have the latest version installed

---

## 5. FIRST-TIME SETUP

### Application Settings

When you first open the application, the default settings are already configured:

- Currency Conversion Rates: PHP to USD (Rate: 57), SGD to USD (Rate: 1.34)
- File validation: Enabled by default
- Updates: Manual updates only (will be notified by IT when new versions available)

### Creating a Working Directory (Optional but Recommended)

1. Create a folder on your computer where you will keep your Excel files
2. Example folder names:
   - CAPEX Reports
   - Financial Data
   - Processing Files
   - CAPEX Work
3. Keep both your original files and processed files in this location for easy access

### Setting Up File Organization

Recommended folder structure:

```
CAPEX Reports/
├── Original Files/
│   ├── CJI5 files
│   ├── RFP files
│   └── ZMM files
├── Processed Files/
│   ├── CJI5 Output
│   ├── RFP Output
│   └── ZMM Output
└── Reference/
    └── File templates
```

### Gathering Your Files

Before using the application, prepare your Excel files:

1. Locate the Excel files you need to process
2. Check that files are in proper Excel format (.xlsx or .xls)
3. Ensure you have the necessary access permissions to read the files
4. Keep a backup copy of original files before processing

---

## 6. APPLICATION INTERFACE OVERVIEW

### Main Window Layout

When you open the application, you see the main window with several components:

#### Top Section: Title Bar
- Shows "CAPEX Reporting Tool v1.0" and version number
- Application name

#### Left Panel: Feature Tabs
Six tabs are available for different functions:
- WP LOA Report
- CJI5
- CJI3
- RFP
- Reclass
- ZMM

Each tab contains specific processing features for that file type.

#### Center Panel: Main Work Area
- File selection section
- Processing options
- Status display
- Process button

#### Bottom Section: Status Bar
- Shows current status or processing information
- Displays file size and row count after processing

Screenshot Placeholder: [Complete application main window with all sections labeled]

### Menu and Button Locations

File Selection Button
- Location: Top of main work area
- Function: Click to browse and select your Excel file
- Label: "Choose File" or "Browse"

Process Button
- Location: Below file selection area
- Function: Starts processing the selected file
- Color: Blue with white text
- Label: "Process File"

Settings or Options
- Location: Varies by tab
- Function: Allows customization for specific file types

Status Display
- Location: Bottom of window
- Function: Shows current operation status and results

Screenshot Placeholder: [Main buttons and interface elements highlighted]

---

## 7. HOW TO USE EACH FEATURE

### General Processing Steps (All File Types)

Every file type follows the same basic workflow:

1. Click on the appropriate tab (WP LOA, CJI5, CJI3, RFP, Reclass, or ZMM)
2. Click the "Choose File" button to select your Excel file
3. Review any available options for that file type
4. Click the "Process File" button
5. Select where to save the processed file
6. Wait for processing to complete
7. Processed file is ready to download

---

### Feature 1: WP LOA Report Processing

#### What is WP LOA?
Work Package Level of Assurance report. Used for managing and documenting equipment and project approval levels.

#### When to Use
Use this feature when you have a WP LOA Excel file that needs to be processed or validated.

#### Step-by-Step Instructions

1. Open the CAPEX Reporting Tool application
2. Click on the "WP LOA Report" tab
3. Click the "Choose File" button
4. Browse to your WP LOA Excel file
5. Select the file and click "Open"
6. The file name appears in the application
7. Click the "Process File" button
8. A save dialog opens
9. Choose a location where you want to save the processed file
10. Enter a name for the output file (or accept the default)
11. Click "Save"
12. Processing begins (status bar shows progress)
13. Processing completes (seconds to minutes depending on file size)
14. Success message appears showing processed file name and row count

#### Output Format
- New Excel file with "WP_LOA_Processed" in the filename
- Original data with added formulas for calculations
- Formulas allow for recalculation and modification in Excel
- All data validation maintained from original file

#### Example Workflow
[Screenshot Placeholder: WP LOA tab, file selection, processing]
[Screenshot Placeholder: Processing complete with success message]
[Screenshot Placeholder: Processed file open in Excel showing formulas]

---

### Feature 2: CJI5 Processing

#### What is CJI5?
CJI5 is a version 5 financial reference document containing transaction data with currency information.

#### When to Use
Use this feature when you need to convert CJI5 data and apply currency conversion formulas (PHP and SGD to USD).

#### File Requirements
Your CJI5 file must contain these columns:
- Reference Document number
- Transaction Currency (PHP, SGD, USD, or other)
- Value/Amount field
- Additional reference information

#### Step-by-Step Instructions

1. Open the CAPEX Reporting Tool application
2. Click on the "CJI5" tab
3. Click the "Choose File" button
4. Select your CJI5 Excel file
5. Click "Open"
6. Verify the file is recognized (file name appears in the application)
7. Review any available options on the CJI5 tab
8. Click the "Process File" button
9. In the save dialog:
   - Choose where to save the file
   - Enter a filename or use the default "CJI5_Processed_[date]"
10. Click "Save"
11. Processing starts (this is now very fast - usually 1-2 seconds)
12. Processing complete message appears showing:
    - Output filename
    - File size in MB
    - Number of rows processed
    - Confirmation that formulas are retained

#### What the Processing Does
- Validates all reference documents are in correct format
- Adds new column: Amount in USD
- Creates formula: Converts currency to USD using rates (PHP: 57, SGD: 1.34)
- Formula allows users to modify amounts and recalculate automatically in Excel
- Preserves all original data

#### Currency Conversion Formula
The formula used in the output:
IF(Currency = "PHP", Amount / 57, IF(Currency = "SGD", Amount / 1.34, Amount))

This means:
- If currency is PHP: divide amount by 57 to get USD
- If currency is SGD: divide amount by 1.34 to get USD  
- If currency is USD or other: keep amount as is

#### Output Format
- File named: CJI5_Processed_[date]_[time].xlsx
- Contains original data plus new USD Amount column
- All formulas editable in Excel
- Ready for further analysis or reporting

#### Example Workflow
[Screenshot Placeholder: CJI5 tab interface]
[Screenshot Placeholder: File selection dialog]
[Screenshot Placeholder: Processing progress]
[Screenshot Placeholder: Success message with file details]
[Screenshot Placeholder: Processed file open in Excel with formula visible in formula bar]

#### Common Scenarios

Scenario 1: Mixed Currency File
- File contains PHP, SGD, and USD amounts
- Processor automatically converts PHP and SGD to USD
- USD amounts remain unchanged
- Result: All amounts normalized to USD

Scenario 2: Large File (50,000+ rows)
- Old processing: 5-10 minutes
- New formula processing: 1-2 seconds
- File size: May be slightly larger (contains formulas, not just values)
- Processing speed: Drastically improved

---

### Feature 3: CJI3 Processing

#### What is CJI3?
CJI3 is a version 3 financial reference document, similar to CJI5 but with different structure or data format.

#### Differences from CJI5
- CJI3 uses different column names or data structure
- Processing logic adapted for CJI3 format
- Both use similar currency conversion and reference formatting
- Output format and benefits are identical to CJI5

#### When to Use
Use this feature specifically for CJI3 formatted files. Do not use CJI5 processor for CJI3 files, as column names may not match.

#### Step-by-Step Instructions

The process is identical to CJI5:

1. Open CAPEX Reporting Tool
2. Click "CJI3" tab (not CJI5)
3. Click "Choose File"
4. Select your CJI3 Excel file
5. Click "Open"
6. Click "Process File"
7. Choose save location and filename
8. Click "Save"
9. Processing completes in 1-2 seconds
10. Success message displays results

#### File Requirements for CJI3
Your CJI3 file must contain these exact columns:
- Purchase Document field
- Transaction Currency
- Value/Amount field
- Additional transaction data

#### Output Format
- File named: CJI3_Processed_[date]_[time].xlsx
- Structure identical to CJI5 output
- All formulas editable
- Ready for use

#### Important Note
Do not mix CJI5 and CJI3 files. Use the correct processor tab for your file type. If you're unsure which version your file is, check the file name or ask your team lead.

#### Example Workflow
[Screenshot Placeholder: CJI3 tab selection]
[Screenshot Placeholder: Processed CJI3 file results]

---

### Feature 4: RFP Processing

#### What is RFP?
RFP (Request for Proposal) files contain procurement and financial data for proposal requests and approvals.

#### When to Use
Use this feature when you need to process RFP files and apply currency conversion.

#### File Requirements
Your RFP file must contain:
- Proposal Reference number
- Transaction Currency
- Amount/Value field
- Proposal details or descriptions

#### Step-by-Step Instructions

1. Open CAPEX Reporting Tool
2. Click on the "RFP" tab
3. Click "Choose File"
4. Select your RFP Excel file
5. Click "Open"
6. Note: You may see an option "Remove M-CBIP-25 entries" (optional checkbox)
   - If checked: removes entries marked as M-CBIP-25 category
   - If unchecked: keeps all entries
   - Leave unchecked unless specifically instructed to remove these entries
7. Click "Process File"
8. Save dialog opens
9. Choose save location
10. Enter filename or use default "RFP_Processed_[date]_[time]"
11. Click "Save"
12. Processing completes (1-2 seconds)
13. Success message appears with file information

#### What the Processing Does
- Validates RFP data structure
- Adds USD Amount column with conversion formula
- Optionally removes M-CBIP-25 entries if selected
- Calculates total amount (all entries summed)
- Total appears in processed file
- All formulas editable

#### The M-CBIP-25 Option
- CBIP entries are a specific category in RFP files
- By default, the processor keeps all entries (checkbox unchecked)
- Some workflows require removing CBIP entries
- Only check this box if instructed by your manager or documentation

#### Output Format
- File named: RFP_Processed_[date]_[time].xlsx
- Contains all RFP data with USD conversion formulas
- Total amount row included at bottom
- All amounts in USD (converted using same rates as CJI)
- Ready for proposal review and approval

#### Example Workflow
[Screenshot Placeholder: RFP tab with M-CBIP option]
[Screenshot Placeholder: File processing]
[Screenshot Placeholder: Processed file with total row visible]

---

### Feature 5: Reclass Processing

#### What is Reclass?
Reclass (Reclassification) files contain financial data that needs to be reclassified or reorganized into different categories or cost centers.

#### When to Use
Use this feature when financial entries need to be moved between categories or when you need to reorganize financial data structure.

#### File Requirements
Your Reclass file must contain:
- Current Classification code
- Financial Amount or Value
- Target Classification (where it should move to)
- Optional: Description or reason for reclassification

#### Step-by-Step Instructions

1. Open CAPEX Reporting Tool
2. Click on the "Reclass" tab
3. Click "Choose File"
4. Select your Reclass Excel file
5. Click "Open"
6. Review the "Remove M-CBIP-25 entries" option if visible
   - Set as needed for your workflow
7. Click "Process File"
8. Save dialog opens
9. Choose location and enter filename
10. Click "Save"
11. Processing runs (1-2 seconds)
12. Success message shows results

#### What the Processing Does
- Validates reclassification structure
- Adds USD Amount column with currency conversion
- Applies reclassification logic to entries
- Cross-references original and new categories
- Creates audit trail of changes
- Totals calculated for verification
- All formulas included for future modifications

#### Output Format
- File named: Reclass_Processed_[date]_[time].xlsx
- Shows original classification and new classification
- All amounts converted to USD
- Totals by category included
- Ready for accounting/finance team review

#### When Results Are Used
- Finance review and approval
- Cost center transfer documentation
- Accounting records update
- Budget reallocation tracking

#### Example Workflow
[Screenshot Placeholder: Reclass tab interface]
[Screenshot Placeholder: Original vs. reclassified data]
[Screenshot Placeholder: Totals by category]

---

### Feature 6: ZMM Processing

#### What is ZMM?
ZMM files handle procurement and Purchase Requisition (PR) reference data from the materials management system.

#### When to Use
Use this feature when you need to clean up PR numbers and reference data.

#### File Requirements
Your ZMM file must contain:
- Ariba PR Reference number (main identifier)
- PR contains version numbers (v1, v2, v3, etc.) that need to be removed
- Additional purchase or vendor information

#### Step-by-Step Instructions

1. Open CAPEX Reporting Tool
2. Click on the "ZMM" tab
3. Click "Choose File"
4. Select your ZMM Excel file
5. Click "Open"
6. File is validated automatically
7. Click "Process File"
8. Save dialog opens
9. Choose save location and filename
10. Click "Save"
11. Processing completes (1-2 seconds)
12. Success message displays results

#### What the Processing Does
- Extracts PR numbers from Ariba references
- Removes version suffixes (v1, v2, v3, etc.) using formula
  Example: "PRN123456v2" becomes "PRN123456"
- Creates new column with cleaned PR number
- Converts cleaned PR to numeric format for sorting/analysis
- Creates duplicate column for reference
- Copies PO (Purchase Order) number if available
- Copies Vendor information if available
- All processing uses formulas (editable)

#### Output Structure
The processed file includes these new columns:
- PR Reference Delimited: PR number with version removed (text format)
- PR Reference Numeric: PR number converted to number format
- PR Reference Copy: Duplicate of cleaned PR
- PO Copy: Duplicate of PO number (if exists)
- Vendor Copy: Duplicate of vendor name (if exists)

#### Example Data
Original: "P-123456v3"
After Processing:
- Delimited: "P-123456"
- Numeric: 123456 (can be sorted as number)

#### Output Format
- File named: ZMM_Processed_[date]_[time].xlsx
- Contains all original data plus new columns
- All new columns contain formulas
- Ready for consolidation or analysis
- PR numbers now standardized and sortable

#### Use Cases
- Consolidating multiple PR references
- Finding duplicate PRs with different versions
- Sorting POs by numeric PR number
- Vendor analysis and reporting

#### Example Workflow
[Screenshot Placeholder: ZMM tab interface]
[Screenshot Placeholder: Original PR numbers with versions]
[Screenshot Placeholder: Processed file with cleaned PR numbers]
[Screenshot Placeholder: Multiple version numbers removed]

---

## 8. TROUBLESHOOTING AND FAQ

### Common Issues and Solutions

#### Issue 1: File Selection Not Working

Problem: Clicking "Choose File" button does nothing, or window closes unexpectedly.

Solutions:

1. Make sure you have file selection permission:
   - Windows: Run as Administrator if prompted
   - macOS: Check System Preferences > Security & Privacy

2. Try using a different folder:
   - Don't select from restricted locations (Desktop sometimes has permission issues)
   - Save your file to Documents or a custom folder first

3. Restart the application:
   - Close completely
   - Wait 10 seconds
   - Reopen and try again

#### Issue 2: File Validation Error

Problem: After selecting file, you get an error message like "Invalid file structure" or "Missing columns."

Solutions:

1. Verify correct file type:
   - Are you using CJI5 for a CJI3 file? (use correct tab)
   - Check the file name for version information

2. Verify file format:
   - File must be .xlsx or .xls (Excel format)
   - Not .csv or .txt or other formats
   - Not corrupted or damaged

3. Check file contents:
   - Open file in Excel first
   - Verify all required columns exist
   - Check column headers exactly match expected names
   - Delete empty rows or columns at top

4. Save file properly:
   - Open file in Excel
   - Use File > Save As > Excel format (.xlsx)
   - Close file
   - Try processing again

#### Issue 3: Processing Takes Very Long

Problem: After clicking "Process File," the application appears to freeze or just shows loading screen for many minutes.

Solutions:

1. Wait a bit longer:
   - Formula-based processing is fast (1-2 seconds typically)
   - If it's been less than 1 minute, wait a bit more
   - Very large files (1M+ rows) may need 5-10 seconds

2. Restart if frozen more than 5 minutes:
   - Force close the application
   - Windows: Use Ctrl+Alt+Delete, select Task Manager
   - macOS: Use Command+Q or Force Quit (Command+Option+Esc)

3. Reduce file size and try again:
   - If file has millions of rows, split into smaller files
   - Process one piece at a time

#### Issue 4: Cannot Find Processed File

Problem: Processing completes but cannot locate the saved file.

Solutions:

1. Check save location:
   - During save dialog, notice which folder is shown
   - That's where your file saved (usually Documents or last folder used)

2. Windows file search:
   - Click Start menu
   - Type filename or "CJI5_Processed"
   - Files menu shows all matches
   - Double-click to open

3. macOS file search:
   - Click Spotlight (magnifying glass, upper right)
   - Type filename
   - Click on file in results
   - Opens folder showing file

4. Default locations to check:
   - Windows: C:\Users\[YourName]\Documents\
   - macOS: Users > [YourName] > Downloads

#### Issue 5: Cannot Open Processed File in Excel

Problem: Processed file opens but shows errors or formulas don't calculate.

Solutions:

1. Enable formulas in Excel:
   - Open file in Excel
   - If dialog appears asking about formulas, click "Enable"
   - Excel processes all formulas automatically

2. Check Excel version:
   - File requires Excel 2016 or newer
   - Older versions may not support all formulas
   - Try opening in newer Excel or LibreOffice/Google Sheets

3. File is corrupted:
   - Delete the file
   - Reprocess original file
   - Try again

#### Issue 6: Wrong Data in Output

Problem: Processed file contains incorrect data, wrong calculations, or missing entries.

Solutions:

1. Verify input file is correct:
   - Is this the right original file?
   - Does file contain the data you expected?
   - Are column names spelled correctly?

2. Check for hidden rows/columns:
   - Open original file in Excel
   - Unhide any hidden rows (right-click row numbers, select Unhide)
   - Unhide any hidden columns

3. Re-process the file:
   - Verify file format is .xlsx
   - Verify all required columns exist
   - Process again

#### Issue 7: Application Won't Open

Problem: Double-clicking the application does nothing, or crashes immediately.

Windows Solutions:

1. Restart your computer:
   - May resolve temporary issues

2. Reinstall the application:
   - Uninstall: Programs > Programs and Features > Uninstall
   - Delete any shortcuts
   - Redownload from GitHub releases
   - Install fresh

3. Run as Administrator:
   - Right-click the application shortcut
   - Select "Run as Administrator"

macOS Solutions:

1. Use Terminal command:
   xattr -d com.apple.quarantine ~/Downloads/CAPEX_Reporting_Tool.app
   
2. Try from different location:
   - Move app from Downloads to Applications folder
   - Try running from Applications

3. Restart your Mac:
   - Close all applications
   - Restart computer
   - Try opening app again

#### Issue 8: Update Failed or Stuck on Old Version

Problem: Application doesn't update to newest version, or update process seems stuck.

Solutions:

1. Manual update:
   - Delete current application
   - Download latest version from GitHub releases
   - Install fresh

2. Clear update cache:
   - Windows: Delete %AppData%\CAPEX folder if exists
   - macOS: Delete ~/Library/Application Support/CAPEX folder if exists

3. Disable and re-enable auto-update:
   - Close application
   - Restart application (should fetch latest version)

#### Issue 9: Formulas Show as Text Instead of Calculating

Problem: Processed file shows formulas as text (e.g., "=IF(A1..." visible) instead of calculated values.

Solutions:

1. Format column as number:
   - Select the column
   - Right-click > Format Cells
   - Click "Number" tab
   - Change format to "Number"

2. Recalculate formulas:
   - Press Ctrl+Shift+F9 (Windows) or Cmd+Shift+F9 (macOS)
   - Excel recalculates all formulas

3. Check Excel settings:
   - File > Options > Formulas
   - Make sure "Show formulas" is NOT checked
   - Click OK

#### Issue 10: File Size Seems Too Large

Problem: Processed file is much larger than expected, takes long to open.

Explanation: This is normal and expected:
- Original file: What you started with
- Processed file: Original data + new formula columns
- Formulas add size to file
- Larger file = more comprehensive processing
- Still opens quickly once formulas calculate

Solution: File size is not a problem. This is normal operation.

---

### Frequently Asked Questions (FAQ)

Q1: Why do I need to use this tool instead of opening files directly in Excel?

A: The tool automatically:
- Validates data structure before processing
- Converts currency values to USD using correct rates
- Adds calculated columns with embedded formulas
- Ensures consistency across all files
- Fast processing (seconds instead of minutes)
- Maintains formula editing capability

Q2: Can I edit the formulas in the processed file?

A: Yes, absolutely! The entire point is to preserve formulas so you can:
- Edit amounts and watch calculations update automatically
- Change currency conversion rates if needed
- Copy formulas to other rows
- Analyze different scenarios

Q3: What if my exchange rates are different from the default (PHP 57, SGD 1.34)?

A: Currently, the default rates are hardcoded:
- PHP to USD: 57
- SGD to USD: 1.34

If you need different rates, you can edit the processed file's formulas manually in Excel. Or contact the development team about custom rate options.

Q4: Can I process multiple files at once?

A: Not in the current version. Process one file at a time:
1. Process first file
2. Save result
3. Process next file
4. Save result

Q5: How long does processing take?

A: Processing is very fast now (roughly):
- Small files (under 10,000 rows): 1-2 seconds
- Medium files (10,000-50,000 rows): 2-5 seconds
- Large files (50,000-100,000 rows): 5-10 seconds
- Very large files (100,000+ rows): 10-30 seconds

Q6: What file formats are supported?

A: Input files must be:
- .xlsx (Excel 2007 and newer)
- .xls (Excel 97-2003, though older format)

Output files are always: .xlsx (Excel format)

Q7: Do I need internet connection while processing files?

A: No. Internet is only needed:
- During initial download and installation of the application
- After installation, app works completely offline
- No periodic update checks or background downloads

Q8: Is my data safe? Does the tool upload files anywhere?

A: Yes, completely safe:
- All processing happens on your local computer
- Files never sent to internet or cloud
- No data collection or tracking
- Files remain on your computer

Q9: Can I use the processed files directly in reports?

A: Absolutely. Processed files are ready to use:
- Open in Excel
- Copy data to reports or documents
- Formulas work in reports too
- Can be emailed to others

Q10: What if I accidentally close the app during processing?

A: The output file may not be saved complete:
- Reprocess the original file
- No data loss to original file (only processed outputs affected)

Q11: Does the app support Mac and Windows equally?

A: Yes, as much as possible:
- App works identically on both platforms
- Processing speed same
- File handling same
- Only differences are installation steps

Q12: Can I move the application after installation?

A: Windows: No, leave in Program Files
macOS: Yes, you can move the .app file to Applications folder

Q13: What should I do with the original file after processing?

A: Keep your original file:
- Don't delete it
- Keep as backup
- Helps verify results
- Can reprocess if needed

Q14: How do I know if the processing was successful?

A: Success indicators:
- No error messages appear
- Success notification shows filename and row count
- Processed file opens without errors
- Formulas are visible in formula bar (top of Excel)

Q15: Can I process the same file twice?

A: Yes, but:
- Creates separate output files each time (different timestamps)
- Both contain correct data and formulas
- Both can be used
- Combine results only if needed, not automatically

---

## 9. TIPS AND BEST PRACTICES

### Before You Start Processing

Tip 1: Keep Original Files Safe
- Always keep backup copies of original files
- Don't delete original files after processing
- Store originals in separate "Original Files" folder
- This lets you reprocess if needed

Tip 2: Name Your Files Clearly
- Use descriptive names: "CJI5_February_2024" instead of "Data1"
- Include dates in filename
- Use consistent naming across all files
- Makes finding files easier later

Tip 3: Check File Format First
- Before processing, open file in Excel
- Verify structure looks correct
- Check columns exist and have correct headers
- Delete any test rows or empty sections
- Close file properly

Tip 4: Create a Processing Checklist
Create a simple list:
- [ ] Original file saved and backed up
- [ ] File opened in Excel to verify
- [ ] Correct processor tab selected
- [ ] File processed
- [ ] Output file saved
- [ ] Output file verified in Excel
- [ ] Formulas working correctly

### During Processing

Tip 5: Use Consistent File Location
- Always use same folder (Documents or CAPEX Reports)
- Don't scatter files across computer
- Makes consolidation easier
- Easier to find later

Tip 6: Monitor Processing Speed
- Note how long processing takes
- If suddenly slow, may indicate computer issue
- Restart if needed
- Large files slower is normal

Tip 7: Save Output with Clear Name
- Use default name (includes timestamp) for easy tracking
- Or manually name: "[Type]_[Month]_[Year]_[Version]"
- Example: "CJI5_February_2024_v1"
- Include version number if reprocessing

### After Processing

Tip 8: Review Output File Immediately
- Open processed file in Excel right after saving
- Spot-check data looks correct
- Click on formula cells to verify formula exists (not just values)
- Check totals or key numbers seem reasonable

Tip 9: Verify Formulas Are Working
- In Excel, select a cell with formula
- Look at formula bar at top (shows formula, not value)
- Should see formula like: =IF(A1="PHP",B1/57,...)
- Click cell in another row with formula
- Should see formula adjust (different row numbers)

Tip 10: Test Formula Editing (Optional)
- In processed file, find a formula cell
- Edit the formula or the input value
- Press Enter
- Watch result recalculate automatically
- Verify it calculates correctly
- Undo (Ctrl+Z) to restore if testing

Tip 11: Keep Organized Records
- Keep spreadsheet tracking:
  - Date processed
  - File type (CJI5, RFP, etc.)
  - Input filename
  - Output filename
  - Row count
  - Any notes about processing
- Easier to track if you need to re-process

Tip 12: Consolidate Multiple Processed Files
- If processing many files of same type
- Save all to same folder
- Later can consolidate or compare
- Excel lets you copy columns between files

### Managing Your Processed Files

Tip 13: Backup Processed Files
- After processing important files, backup the output
- Copy to external drive or cloud storage
- Protects against accidental deletion
- Timestamps in filename help identify versions

Tip 14: Use Consistent Date Format
- If using dates in filename, be consistent
- Use YYYYMMDD format (2024-02-15)
- This sorts alphabetically by date automatically
- Example: "CJI5_20240215_v1"

Tip 15: Share Processed Files Carefully
- Processed files have formulas (editable)
- If sharing, consider if formulas should be locked
- Can email .xlsx file directly
- Include note that formulas are recalculated on recipient's Excel

### Performance Optimization

Tip 16: Keep Computer Running Well
- Close unnecessary applications before processing
- Lots of running programs may slow processing
- Restart computer occasionally
- Keeps system running smoothly

Tip 17: Don't Process Too Many Files at Once
- Process one file at a time
- Don't try to select multiple files
- Open, process, save one file completely before next
- More reliable and organized

Tip 18: Monitor Storage Space
- Processed files take disk space
- If running low on space, delete old temporary files
- Keep only current versions of important files
- Archive old files to external storage

### Documentation and Records

Tip 19: Keep Processing Log
Simple spreadsheet or document tracking:

Date | File Type | Input File | Output File | Row Count | Status | Notes
-----|-----------|-----------|-----------|-----------|--------|------
2024-02-15 | CJI5 | CJI5_Feb | CJI5_20240215 | 5,234 | OK | Normal processing
2024-02-15 | RFP | RFP_Feb | RFP_20240215 | 2,105 | OK | Removed CBIP entries

Tip 20: Document Your Workflow
- Create written procedure for your team:
  1. Where files come from
  2. Which processor to use for each type
  3. Where to save outputs
  4. Who reviews the results
  5. Next steps after processing
- Helps consistency across team

### Troubleshooting Best Practices

Tip 21: Try Simple Fix First
- Restart application before complex troubleshooting
- Restart computer if still having issues
- Usually resolves temporary glitches

Tip 22: Keep Error Messages
- Take screenshot of any errors
- Copy error text (if possible)
- Write down what you were doing
- Helps troubleshoot if problem continues

Tip 23: Test with Sample File
- Keep small test file for each type
- Use to verify processing working
- If test works but real file doesn't, problem is with real file
- Use test during application startup to verify working

Tip 24: Know When to Ask for Help
- If can't resolve after 30 minutes
- Keep record of what you tried
- Contact your IT support or team lead
- Provide error message and file details

---

## 10. QUICK REFERENCE GUIDE

### File Type Quick Reference

| File Type | Use For | Key Processing | Output Includes |
|-----------|---------|-----------------|-----------------|
| WP LOA | Level of assurance documentation | Data validation and formula setup | Validated data with formulas |
| CJI5 | CJI version 5 financial data | Currency conversion, Reference validation | Data + USD Amount formula |
| CJI3 | CJI version 3 financial data | Currency conversion, Reference validation | Data + USD Amount formula |
| RFP | Proposal request data | Currency conversion, Optional CBIP removal | Data + USD Amount + Total |
| Reclass | Reclassification data | Category mapping, Currency conversion | Data + USD Amount + Classification |
| ZMM | Purchase requisition data | PR number cleaning, Version removal | Data + Cleaned PR + Numeric PR |

### Keyboard Shortcuts

Windows:
- Ctrl+O: Open file (in some screens)
- Ctrl+S: Save file (in Excel or after processing)
- Ctrl+V: Paste
- Ctrl+C: Copy

macOS:
- Command+O: Open file
- Command+S: Save file
- Command+V: Paste
- Command+C: Copy

Application:
- Tab key: Move between buttons and fields
- Enter: Activate button or confirm selection
- Escape: Cancel dialog or action

### Default Exchange Rates

PHP to USD: 57 (divide PHP amount by 57 to get USD)
SGD to USD: 1.34 (divide SGD amount by 1.34 to get USD)

### File Organization Example

Recommended folder structure for optimal workflow:

```
My CAPEX Reports
├── 2024 February
│   ├── Original Files
│   │   ├── CJI5_February.xlsx
│   │   ├── RFP_February.xlsx
│   │   ├── ZMM_February.xlsx
│   └── Processed Output
│       ├── CJI5_20240215_v1.xlsx
│       ├── RFP_20240215_v1.xlsx
│       ├── ZMM_20240215_v1.xlsx
├── 2024 January
│   ├── Original Files
│   └── Processed Output
└── Archive
    ├── 2023 Files
    └── 2022 Files
```

### Processing Workflow Flowchart

Start
  ↓
Open CAPEX Reporting Tool
  ↓
Select correct tab (CJI5, RFP, ZMM, etc.)
  ↓
Click "Choose File"
  ↓
Select your Excel file
  ↓
Review any options (e.g., Remove CBIP?)
  ↓
Click "Process File"
  ↓
Choose save location and filename
  ↓
Click "Save"
  ↓
Processing occurs (1-30 seconds typically)
  ↓
Success message appears
  ↓
Processed file saved to your location
  ↓
Click filename in message to verify
  ↓
Open in Excel to confirm formulas working
  ↓
Ready to use or share file
  ↓
End

### Common File Locations

Windows:
- Downloads: C:\Users\[Your Name]\Downloads
- Documents: C:\Users\[Your Name]\Documents
- Desktop: C:\Users\[Your Name]\Desktop
- Program Files: C:\Program Files\CAPEX Reporting Tool

macOS:
- Downloads: /Users/[Your Name]/Downloads
- Documents: /Users/[Your Name]/Documents
- Applications: /Applications/CAPEX_Reporting_Tool.app
- Desktop: /Users/[Your Name]/Desktop

### What Column Names the App Looks For

CJI5 Processor expects:
- "Reference Document"
- "Transaction Currency"
- "Value/Amount" or similar

CJI3 Processor expects:
- "Purchase Document"
- "Transaction Currency"
- "Value/Amount" or similar

RFP/Reclass Processor expects:
- "Transaction Currency"
- "Value/Amount"
- "Description" or "Category"

ZMM Processor expects:
- "Ariba PR Reference"
- "PO Number"
- "Vendor"

Note: Column names must match exactly (spelling and spacing matter)

### Troubleshooting Quick Decision Tree

Processing won't start?
→ Restart application
→ Restart computer
→ Reinstall application

File validation fails?
→ Check file format (.xlsx required)
→ Verify column names match exactly
→ Open file in Excel to verify data
→ Try processing different file

Processing takes too long?
→ Wait a bit longer (very large files take time)
→ Close other applications
→ Restart computer
→ Try smaller file

Output file won't open?
→ Check it saved properly
→ Try opening in different Excel version
→ Delete file and reprocess
→ Contact IT support

Formulas not calculating?
→ Click formula cell and check formula bar
→ Press Ctrl+Shift+F9 to recalculate
→ Check Excel is not in "Show Formulas" mode
→ Try in newer Excel version

### Contact Information for Support

For technical issues:
- Contact your IT department
- Provide: error message, file name, what you were doing

For processing questions:
- Ask your direct supervisor or team lead
- Check this manual sections 7 and 8
- Refer to your team's processing procedures

For feature requests or bugs:
- Report to development team
- Include: description of issue, steps to reproduce, screenshot if possible

---

## APPENDIX: GLOSSARY OF TERMS

Currency Conversion: Changing amount from one currency (PHP, SGD) to another (USD) using exchange rate

Exchange Rate: How much one currency is worth compared to another (PHP 57 = USD 1)

Formula: Excel calculation that automatically updates when values change (example: =A1*2)

CBIP: A specific category classification in some files (M-CBIP-25 is the standard code)

CJI: Financial reference classification system (version 3 and 5 available)

CSV: Comma Separated Values - text file format (not supported, use .xlsx instead)

Delimit: Remove or separate specific text patterns

Process: Action of converting/transforming file using the application

Reclass: Reclassification - moving entries to different categories

RFP: Request for Proposal - procurement document

Validation: Checking that file structure and data are correct before processing

WP LOA: Work Package Level of Assurance - approval/authorization document

XLS/XLSX: Excel file formats (.xlsx is newer preferred format)

ZMM: Materials Management system - handles purchase requisitions

---

## APPENDIX: KEYBOARD AND MOUSE GUIDE FOR BEGINNERS

### Using the Mouse
- Click: Press left mouse button once
- Double-click: Press left mouse button twice quickly
- Right-click: Press right mouse button once (shows menu)
- Drag: Press and hold button while moving mouse

### Basic Computer Concepts
- File: Document or piece of data stored on computer
- Folder: Container that holds files (like drawer holds papers)
- Download: Copying file from internet to your computer
- Extension: Suffix on filename (.xlsx, .txt, .exe indicate file type)
- Dialog Box: Small window asking for information or confirmation

### Button Types
- Rectangular button: Click to activate (like "Process File")
- Checkbox: Click to check or uncheck
- Radio button: Click to select one option from many
- Dropdown: Click arrow to see list of options

### Common Screen Elements
- Menu bar: Top of window with options
- Toolbar: Row of buttons below menu
- Status bar: Bottom of window showing information
- Title bar: Top shows window name

---

End of Complete User Manual

