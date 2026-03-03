# CAPEX Reporting Tool - Rebuild & Deploy Guide
**After GitHub Pull**  
**Last Updated**: March 3, 2026

---

## 📋 Quick Checklist

- [ ] **Step 1**: Pull latest from GitHub
- [ ] **Step 2**: Verify changes locally
- [ ] **Step 3**: Clean old builds
- [ ] **Step 4**: Rebuild Windows executable
- [ ] **Step 5**: Test Windows version
- [ ] **Step 6**: Build macOS version (if available)
- [ ] **Step 7**: Test macOS version
- [ ] **Step 8**: Organize outputs
- [ ] **Step 9**: Distribute to team

---

## 🔄 STEP 1: Pull Latest from GitHub

### 1a. Open PowerShell in Your Workspace
```powershell
cd c:\Users\ludrein.salvador_glo\Downloads\capex-reporting-app
```

### 1b. Check Current Branch
```powershell
git status
git branch
```

**Expected Output**: Should show `main` or your working branch

### 1c. Pull Latest Changes
```powershell
git pull origin main
```

**Expected Output**:
```
Already up to date.
```
or
```
Updating abc1234..def5678
Fast-forward
 processors/cji.py                     | 25 ++-
 processors/rfp_reclass.py            | 18 ++-
 processors/zmm.py                    | 12 ++-
 IMPLEMENTATION_STATUS.md             |  1 +
 ...
 X files changed, XX insertions(+), YY deletions(-)
```

### ⚠️ If Conflicts Occur:
```powershell
git status  # See which files have conflicts
git diff processors/cji.py  # Review conflicts
git merge --abort  # Cancel if needed, then contact repo maintainer
```

---

## ✅ STEP 2: Verify Changes Locally

### 2a. Check What Changed
```powershell
git log --oneline -5
```

### 2b. Review Specific Files Changed
```powershell
git diff HEAD~1 processors/cji.py
git diff HEAD~1 processors/rfp_reclass.py
git diff HEAD~1 processors/zmm.py
```

### 2c. Run Quick Syntax Check (Python)
```powershell
python -m py_compile processors/cji.py
python -m py_compile processors/rfp_reclass.py
python -m py_compile processors/zmm.py
python -m py_compile processors/wp_loa_formula.py
python -m py_compile app_desktop.py
```

**Expected**: No output = success ✅  
**If Error**: Shows syntax issues that need fixing before build

---

## 🧹 STEP 3: Clean Old Builds

### 3a. Remove Old Build Artifacts
```powershell
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "*.egg-info" -Recurse -Force -ErrorAction SilentlyContinue
```

**Why**: Old builds can have stale code cached

### 3b. Verify Cleanup
```powershell
Get-ChildItem -Path . | Select-Object Name, PSIsContainer
```

**Expected**: No `dist` or `build` folders

---

## 🔨 STEP 4: Rebuild Windows Executable

### 4a. Verify PyInstaller & Dependencies
```powershell
pip list | Select-String "pyinstaller|pandas|openpyxl"
```

**Expected Output**:
```
pyinstaller    6.x.x
pandas         2.x.x
openpyxl       3.x.x
```

**If Missing Any**:
```powershell
pip install pyinstaller pandas openpyxl requests
```

### 4b. Run PyInstaller Build
```powershell
python -m PyInstaller build-scripts/CAPEX_Reporting_Tool.spec
```

**Build will take 2-5 minutes. Expected Output**:
```
...
building 'CAPEX_Reporting_Tool' exe
...
building COLLECT CAPEX_Reporting_Tool
...
completed successfully.
100 INFO: checked 847 modules and 93 dll files
```

⚠️ **Expected Warnings** (these are normal, not errors):
```
WARNING: OPTIONAL DEPENDENCY dataclasses NOT FOUND
WARNING: OPTIONAL DEPENDENCY fiona NOT FOUND
```

### ⛔ If Build Fails:
```powershell
# Try these troubleshooting steps:

# 1. Check if spec file exists
Test-Path build-scripts/CAPEX_Reporting_Tool.spec

# 2. Try verbose mode to see error details
python -m PyInstaller --debug=all build-scripts/CAPEX_Reporting_Tool.spec

# 3. Rebuild spec from scratch (last resort)
python -m PyInstaller --onefile --windowed --icon=icon.ico ^
  --name=CAPEX_Reporting_Tool app_desktop.py
```

### 4c. Verify Build Output
```powershell
Get-ChildItem -Path "dist" -Recurse | Select-Object Name
```

**Expected**: 
- `dist/CAPEX_Reporting_Tool/` folder (contains exe and all dependencies)
- `dist/CAPEX_Reporting_Tool.exe` (standalone executable in some configs)

### 4d. Check Executable Size
```powershell
(Get-Item "dist/CAPEX_Reporting_Tool/CAPEX_Reporting_Tool.exe").Length / 1MB
```

**Expected**: 100-200 MB  
**If <50 MB**: Something went wrong (missing dependencies)  
**If >300 MB**: Might have included unnecessary files

---

## 🧪 STEP 5: Test Windows Version

### 5a. Run Desktop App (Do Not Use PyInstaller version yet)
```powershell
cd c:\Users\ludrein.salvador_glo\Downloads\capex-reporting-app
python app_desktop.py
```

**Expected**:
- Window opens with "CAPEX Reporting Tool v[version]"
- Tabs visible: Basic Processing, Advanced, Consolidation, WP LOA Report
- No error messages

**Test These Features**:

1. **File Selection**:
   - Click "Browse File" in Basic Processing tab
   - Select a test CJI5 Excel file
   - Status bar shows: "File selected: [filename]"

2. **Process Button**:
   - "Process File" button becomes enabled (blue, clickable)
   - Click it → loading bar appears, says "Processing..."

3. **File Processing** (with small test file):
   - Processing completes in 1-2 seconds
   - Save file dialog appears
   - Save to `processed/` folder
   - ✅ File saved successfully

4. **Verify Output**:
   ```powershell
   $file = "processed\[filename].xlsx"
   $excel = New-Object -ComObject Excel.Application
   $workbook = $excel.Workbooks.Open((Resolve-Path $file).Path)
   $sheet = $workbook.Sheets(1)
   $cell = $sheet.Cells(2, 12)  # Sample cell with formula
   Write-Host "Cell Formula: $($cell.Formula)"
   Write-Host "Cell Value: $($cell.Value)"
   $workbook.Close()
   $excel.Quit()
   ```
   
   **Expected**: 
   - If Amount_USD column: `=IF(UPPER(...` (shows formula, not just number)
   - If ZMM: `=IFERROR(LEFT...` (PR cleanup formula)

### 5b. Test All Tabs
- **Basic Tab**: Each file type (CJI5, CJI3, RFP, Reclass, ZMM)
- **Advanced Tab**: Pivot processing, car plan filtering, CBIP removal
- **Consolidation Tab**: ZMM consolidation
- **WP LOA Tab**: File selection (app shouldn't crash)

### 5c. Close App
```powershell
# Close the window or press Ctrl+C in PowerShell
```

### 5d. Test Packaged Executable (Next Day/After Verification)
```powershell
# Once you're confident about the code:
& "dist\CAPEX_Reporting_Tool\CAPEX_Reporting_Tool.exe"
```

**Expected**: Same behavior as `python app_desktop.py`

---

## 🍎 STEP 6: Build macOS Version

### ⚠️ Prerequisites for macOS Build
You have **three options**:

#### Option A: Build on macOS Device (Recommended)
Requires: Mac with Python 3.9+, same repository cloned

#### Option B: Cross-Compile from Windows (Not Recommended)
```powershell
# Generally doesn't work well - OS-specific binaries needed
# Not recommended for production
```

#### Option C: Use macOS CI/CD Pipeline
If your GitHub repo has Actions configured:
- Push to a `macos-build` branch
- GitHub Actions builds automatically
- Download artifact (CAPEX_Reporting_Tool.dmg or .app)

### 6a. Build on macOS (if available)

**On Mac Terminal**:
```bash
cd ~/Downloads/capex-reporting-app

# Pull latest
git pull origin main

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Clean old builds
rm -rf dist build *.egg-info

# Build for macOS
pyinstaller build-scripts/CAPEX_Reporting_Tool.spec --onedir
# or create an app bundle:
# pyinstaller --onefile --windowed --name=CAPEX_Reporting_Tool app_desktop.py

# Test locally
python app_desktop.py
```

**Expected macOS Output**:
- `dist/CAPEX_Reporting_Tool.app/`
- `dist/CAPEX_Reporting_Tool` (executable)

### 6b. Create DMG Installer (macOS)
```bash
# Optional: Create distributable DMG file
hdiutil create -volname "CAPEX Reporting Tool" \
  -srcfolder dist/CAPEX_Reporting_Tool.app \
  -ov -format UDZO \
  "CAPEX_Reporting_Tool_MacOS.dmg"
```

---

## 🧪 STEP 7: Test macOS Version

Same as Windows testing (Step 5), but on Mac:

```bash
# Direct Python test
python app_desktop.py

# Or run the built app
open dist/CAPEX_Reporting_Tool.app

# Or run DMG
hdiutil mount CAPEX_Reporting_Tool_MacOS.dmg
# Then open the .app from the mounted volume
```

---

## 📦 STEP 8: Organize Outputs

### 8a. Create Release Folder Structure
```powershell
$date = Get-Date -Format "yyyyMMdd"
New-Item -ItemType Directory -Path "releases\v$date" -Force
New-Item -ItemType Directory -Path "releases\v$date\Windows" -Force
New-Item -ItemType Directory -Path "releases\v$date\MacOS" -Force
```

### 8b. Copy Windows Build
```powershell
Copy-Item -Path "dist\CAPEX_Reporting_Tool" `
  -Destination "releases\v$date\Windows\" -Recurse -Force

# Also create ZIP for easy distribution
Compress-Archive -Path "releases\v$date\Windows\CAPEX_Reporting_Tool" `
  -DestinationPath "releases\v$date\Windows\CAPEX_Reporting_Tool_Windows.zip"
```

### 8c. Copy macOS Build (from Mac)
```bash
# On Mac, if you built DMG:
cp CAPEX_Reporting_Tool_MacOS.dmg /path/to/releases/v[date]/MacOS/
```

### 8d. Create Version File
```powershell
$versionInfo = @"
# CAPEX Reporting Tool - Build Information
Build Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Version: [Insert version from config/version.py]
Windows Build: CAPEX_Reporting_Tool_Windows.zip
MacOS Build: CAPEX_Reporting_Tool_MacOS.dmg
Python Version: $(python --version)
PyInstaller Version: $(pip show pyinstaller | Select-String Version)
"@

$versionInfo | Out-File "releases\v$date\BUILD_INFO.txt"
```

### 8e. Folder Structure Result
```
releases/
├── v20260303/
│   ├── BUILD_INFO.txt
│   ├── Windows/
│   │   ├── CAPEX_Reporting_Tool/
│   │   │   ├── CAPEX_Reporting_Tool.exe
│   │   │   ├── python313.dll
│   │   │   └── ... (all dependencies)
│   │   └── CAPEX_Reporting_Tool_Windows.zip
│   └── MacOS/
│       └── CAPEX_Reporting_Tool_MacOS.dmg
```

---

## 📤 STEP 9: Distribute to Team

### Option A: Email Distribution
```powershell
# Create a nice summary
$summary = @"
CAPEX Reporting Tool - Version [X.X.X]
Built: $(Get-Date -Format "MMMM dd, yyyy")

WHAT'S NEW:
✅ Fixed formula-based processing (data rows now have formulas, not values)
✅ Fixed ZMM PR number cleanup (now uses LEFT+FIND, compatible with all Excel versions)
✅ Fixed RFP/Reclass subtotal row handling (empty rows stay empty)
✅ Added case-insensitive currency matching (PHP/Php/php all work)

DOWNLOAD:
📥 Windows: CAPEX_Reporting_Tool_Windows.zip (unzip and run .exe)
🍎 macOS: CAPEX_Reporting_Tool_MacOS.dmg (mount and run .app)

TESTING CHECKLIST:
- Process a CJI5 file, check that Amount_USD column shows formulas in formula bar
- Process a ZMM file, verify PR numbers are cleaned (v1/v2 removed)
- Load an RFP/Reclass file, ensure subtotal rows (yellow) are empty after processing

SUPPORT:
If you encounter issues, please provide:
1. File name (anonymized or dummy file)
2. Error message (screenshot or copy/paste)
3. Windows/macOS version
"@

Write-Host $summary
# Then email this + attachment: releases\v[date]\Windows\CAPEX_Reporting_Tool_Windows.zip
```

### Option B: Share Via Google Drive (Recommended)
```powershell
# Upload releases folder to Google Drive
# Share link with team
# Include same summary as Option A
```

### Option C: GitHub Release
```powershell
# Create GitHub Release (if configured)
# Upload both Windows.zip and MacOS.dmg as assets
# Include release notes in description
```

---

## 🔍 Troubleshooting Reference

### Issue: "ModuleNotFoundError: No module named 'processors'"
**Cause**: Python path not set correctly  
**Fix**:
```powershell
$env:PYTHONPATH = "c:\Users\ludrein.salvador_glo\Downloads\capex-reporting-app"
python app_desktop.py
```

### Issue: PyInstaller Build Fails
**Cause**: Missing dependencies or corrupted cache  
**Fix**:
```powershell
pip install --upgrade pyinstaller
pip install --upgrade -r requirements.txt
Remove-Item -Path "build" -Recurse -Force
python -m PyInstaller build-scripts/CAPEX_Reporting_Tool.spec
```

### Issue: Processing Hangs or is Slow
**Cause**: Large file or formula evaluation  
**Fix**:
- Test with smaller file first (100-500 rows)
- Wait 30+ seconds for large files (formulas take time on first open)
- Check if Excel is already open (can cause conflicts)

### Issue: Formulas Show as Values in Output
**Cause**: Old code or didn't rebuild properly  
**Fix**:
```powershell
# Verify you're running new version
Remove-Item "dist" -Recurse -Force
python -m PyInstaller build-scripts/CAPEX_Reporting_Tool.spec
# Then test with fresh build
```

### Issue: Windows Defender/Antivirus Flags Executable
**Cause**: New executable is unsigned  
**Fix**:
- Add to antivirus whitelist/exceptions
- Windows Defender SmartScreen → "Run Anyway"
- (Consider code signing in future for production release)

---

## 📋 Command Cheat Sheet

### All-In-One Rebuild Script
```powershell
# Copy this entire block and run in PowerShell

cd c:\Users\ludrein.salvador_glo\Downloads\capex-reporting-app

# 1. Pull latest
Write-Host "Pulling from GitHub..." -ForegroundColor Green
git pull origin main

# 2. Clean old builds
Write-Host "Cleaning old builds..." -ForegroundColor Green
Remove-Item -Path "dist", "build" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Rebuild
Write-Host "Rebuilding for Windows..." -ForegroundColor Green
python -m PyInstaller build-scripts/CAPEX_Reporting_Tool.spec

# 4. Verify
Write-Host "Verifying build..." -ForegroundColor Green
if (Test-Path "dist\CAPEX_Reporting_Tool\CAPEX_Reporting_Tool.exe") {
    $size = (Get-Item "dist\CAPEX_Reporting_Tool\CAPEX_Reporting_Tool.exe").Length / 1MB
    Write-Host "✅ Build successful! Executable size: $([Math]::Round($size, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "❌ Build failed - executable not found" -ForegroundColor Red
}
```

### Quick Test Script
```powershell
# Run this to test the built version
$exePath = "dist\CAPEX_Reporting_Tool\CAPEX_Reporting_Tool.exe"
if (Test-Path $exePath) {
    & $exePath
} else {
    Write-Host "Executable not found. Run rebuild script first."
}
```

---

## ✅ Final Checklist Before Distribution

- [ ] Git pull completed successfully
- [ ] No syntax errors in Python files
- [ ] Old builds cleaned
- [ ] PyInstaller build completed with no fatal errors
- [ ] Tested file processing (actual CJI/RFP file)
- [ ] Verified formulas in output (not values)
- [ ] All tabs accessible, no crashes
- [ ] Windows executable created and runs
- [ ] macOS build created (if applicable)
- [ ] Version number updated in `config/version.py`
- [ ] Release folder organized
- [ ] Distribution ready
- [ ] Team notified

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Pull Latest | `git pull origin main` |
| Run from Python | `python app_desktop.py` |
| Clean Builds | `Remove-Item dist, build -Recurse -Force` |
| Rebuild Windows | `python -m PyInstaller build-scripts/CAPEX_Reporting_Tool.spec` |
| Test Executable | `& "dist\CAPEX_Reporting_Tool\CAPEX_Reporting_Tool.exe"` |
| Check Dependencies | `pip list \| Select-String "pyinstaller\|pandas"` |
| Syntax Check | `python -m py_compile processors/cji.py` |

