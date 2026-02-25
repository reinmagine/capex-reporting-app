# Cross-Platform Build Guide

Build CAPEX Reporting Tool for Windows and macOS

---

## 📋 Prerequisites

### Windows
- Python 3.8+ installed
- PyInstaller: `pip install pyinstaller`
- All dependencies: `pip install -r requirements.txt`
- Workspace: `c:\Users\[YOUR_USER]\Downloads\capex-reporting-app`

### macOS
- Python 3.8+ installed (via Homebrew: `brew install python@3.9`)
- PyInstaller: `pip install pyinstaller`
- All dependencies: `pip install -r requirements.txt`
- Xcode Command Line Tools: `xcode-select --install`

---

## 🪟 BUILD FOR WINDOWS

### Step 1: Clean Previous Build
```bash
rmdir /s /q dist build
```

### Step 2: Build Executable
```bash
python -m PyInstaller build-scripts/CAPEX_Reporting_Tool.spec
```

**Output:** `dist/CAPEX_Reporting_Tool.exe` (~54 MB)

### Step 3: Verify Build
```bash
# Test exe runs
.\dist\CAPEX_Reporting_Tool.exe

# Check logs created
type logs\update.log
```

### Step 4: Upload to GitHub
1. Go to: https://github.com/ludreinsalvador/capex-reporting-app/releases/v1.0.1
2. Click Edit
3. Delete old Windows exe
4. Upload new exe from `dist/CAPEX_Reporting_Tool.exe`
5. Save changes

---

## 🍎 BUILD FOR MACOS

### Step 1: Clone Repo on macOS
```bash
git clone https://github.com/ludreinsalvador/capex-reporting-app.git
cd capex-reporting-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Build App Bundle
```bash
python -m PyInstaller build-scripts/CAPEX_Reporting_Tool_macOS.spec
```

**Output:** `dist/CAPEX_Reporting_Tool.app/` (directory)

### Step 3: Verify Build
```bash
# Test app runs
open dist/CAPEX_Reporting_Tool.app

# Give it execute permission if needed
chmod +x dist/CAPEX_Reporting_Tool.app/Contents/MacOS/CAPEX_Reporting_Tool
```

### Step 4: Create DMG (Optional but Recommended)
```bash
# Create DMG for easier distribution
hdiutil create -volname CAPEX_Reporting_Tool -srcfolder dist/CAPEX_Reporting_Tool.app -ov -format UDZO dist/CAPEX_Reporting_Tool.dmg

# Result: dist/CAPEX_Reporting_Tool.dmg (~80-100 MB)
```

### Step 5: Upload to GitHub
1. Go to: https://github.com/ludreinsalvador/capex-reporting-app/releases/v1.0.1
2. Click Edit
3. Upload either:
   - `dist/CAPEX_Reporting_Tool.app.zip` (zipped app)
   - `dist/CAPEX_Reporting_Tool.dmg` (disk image)
4. Save changes

---

## 📦 CREATE PLATFORM PACKAGES

### For macOS: Compress App to ZIP
```bash
cd dist
zip -r CAPEX_Reporting_Tool.app.zip CAPEX_Reporting_Tool.app
# Result: CAPEX_Reporting_Tool.app.zip (~80 MB)
```

### For Windows: Already Single File
- No compression needed
- `CAPEX_Reporting_Tool.exe` is ready to distribute

---

## 📝 UPDATE VERSION.JSON

After uploading both versions to GitHub releases:

```json
{
  "version": "1.0.1",
  "downloads": {
    "windows": "https://github.com/ludreinsalvador/capex-reporting-app/releases/download/v1.0.1/CAPEX_Reporting_Tool.exe",
    "darwin": "https://github.com/ludreinsalvador/capex-reporting-app/releases/download/v1.0.1/CAPEX_Reporting_Tool.app.zip"
  }
}
```

Then commit and push:
```bash
git add version.json
git commit -m "Update version.json for v1.0.1 with cross-platform support"
git push origin main
```

---

## 🔍 BUILD VERIFICATION CHECKLIST

### Windows Build
- [ ] `dist/CAPEX_Reporting_Tool.exe` exists (~54 MB)
- [ ] Single file (no _internal folder)
- [ ] Runs without errors
- [ ] Auto-updater logs created in `logs/update.log`
- [ ] Uploaded to GitHub release
- [ ] Download link tested

### macOS Build
- [ ] `dist/CAPEX_Reporting_Tool.app` directory exists
- [ ] App runs when double-clicked
- [ ] No code signing errors (if on Big Sur+, might need to bypass gatekeeper)
- [ ] Compressed to ZIP (~80 MB)
- [ ] Uploaded to GitHub release
- [ ] Download link tested

---

## ⚙️ BUILD FILE SIZES

| Platform | Build Type | Size | Time |
|----------|-----------|------|------|
| Windows | Single-file exe | ~54 MB | 3-5 min |
| macOS | app bundle (uncompressed) | ~500 MB | 5-7 min |
| macOS | app bundle (compressed ZIP) | ~80 MB | - |
| macOS | DMG installer | ~80 MB | - |

---

## 🚀 DISTRIBUTION LINKS

### Windows Users Download From:
```
https://github.com/ludreinsalvador/capex-reporting-app/releases/download/v1.0.1/CAPEX_Reporting_Tool.exe
```

### macOS Users Download From:
```
https://github.com/ludreinsalvador/capex-reporting-app/releases/download/v1.0.1/CAPEX_Reporting_Tool.app.zip
```

Or for DMG:
```
https://github.com/ludreinsalvador/capex-reporting-app/releases/download/v1.0.1/CAPEX_Reporting_Tool.dmg
```

---

## 🔧 TROUBLESHOOTING

### Windows: "Python DLL not found"
- **Cause:** Multi-file build (spec file has `exclude_binaries=True`)
- **Fix:** Use single-file spec (current spec file is correct)

### macOS:  "App is damaged or can't be opened"
- **Cause:** Gatekeeper restrictions on unsigned app
- **Fix:** 
  ```bash
  # Allow app to open (one-time)
  xattr -d com.apple.quarantine /Applications/CAPEX_Reporting_Tool.app
  ```

### macOS: "Python not found"
- **Cause:** Spec file doesn't include Python runtime
- **Fix:** Use macOS spec file (includes all dependencies)

### Build Takes Too Long (>10 min)
- **Cause:** Collecting dependencies
- **Fix:** Normal for first build. Subsequent builds faster (~2 min)

---

## 🔄 AUTOMATION (Advanced)

### GitHub Actions Workflow
You can automate this with GitHub Actions to build both platforms on every release:

```yaml
# .github/workflows/build.yml
name: Build Executables

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python -m PyInstaller build-scripts/CAPEX_Reporting_Tool.spec
      - uses: actions/upload-artifact@v2
        with:
          name: Windows-Exe
          path: dist/CAPEX_Reporting_Tool.exe

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python -m PyInstaller build-scripts/CAPEX_Reporting_Tool_macOS.spec
      - run: cd dist && zip -r CAPEX_Reporting_Tool.app.zip CAPEX_Reporting_Tool.app
      - uses: actions/upload-artifact@v2
        with:
          name: macOS-App
          path: dist/CAPEX_Reporting_Tool.app.zip
```

Then both executables auto-upload to release with every tag push!

---

## 📚 RELATED DOCUMENTATION

- `docs/RELEASES.md` - Version history
- `docs/QUICK_REFERENCE.md` - Quick commands
- `docs/BUILD_CHECKLIST.md` - Pre-release checklist
- `config/version.py` - Version configuration
- `utils/auto_updater.py` - Auto-update engine

---

**Version:** 1.0.1  
**Last Updated:** 2026-02-25  
**Supported Platforms:** Windows 7+, macOS 10.13+
