# Auto-Update System Setup Guide

This guide explains how to set up and deploy the CAPEX Reporting Tool with automatic updates.

---

## Quick Overview

**User Experience:**
1. Download `CAPEX_Reporting_Tool.exe` once
2. Double-click to run
3. Creates own shortcut
4. Automatic updates happen in background
5. User never thinks about updates

**Developer Workflow:**
1. Fix bugs / add features locally
2. Test thoroughly
3. Update `config/version.py` with new version
4. Build exe with PyInstaller
5. Upload to GitHub release
6. Update `version.json` with new URL
7. Done! Users auto-update next time they open the app

---

## Step-by-Step Setup

### Step 1: Initial Development Environment

```bash
# Clone repository (already done)
git clone https://github.com/ludreinsalvador/capex-reporting-app.git
cd capex-reporting-app

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Test Auto-Update Code Locally

```bash
# Run app from Python (auto-update will work in background)
cd src
python app_desktop.py

# Check logs
cat ../logs/update.log
```

### Step 3: Build Executable with PyInstaller

```bash
# Build from workspace root
pyinstaller CAPEX_Reporting_Tool.spec

# Exe will be in dist/CAPEX_Reporting_Tool.exe
ls dist/
```

### Step 4: Create GitHub Release

#### Option A: Using GitHub Web Interface (Recommended)

1. Go to https://github.com/ludreinsalvador/capex-reporting-app/releases/new
2. Click "Draft a new release"
3. **Tag version:** `v1.0.1` (must match `config/version.py`)
4. **Release title:** `CAPEX Reporting Tool v1.0.1`
5. **Description:** Copy from `RELEASES.md`
6. **Attach exe:** Drag and drop `dist/CAPEX_Reporting_Tool.exe`
7. Click "Publish release"

#### Option B: Using Git Command Line

```bash
# Create tag
git tag -a v1.0.1 -m "Release 1.0.1 - Initial release with auto-update"
git push origin v1.0.1

# On GitHub, manually create release from tag and upload exe
```

### Step 5: Update version.json

After uploading exe to GitHub release:

```bash
# Edit version.json in repo root
# Update download_url to match new release

example:
{
  "version": "1.0.1",
  "download_url": "https://github.com/ludreinsalvador/capex-reporting-app/releases/download/v1.0.1/CAPEX_Reporting_Tool.exe",
  "release_date": "2026-02-24",
  ...
}

git add version.json
git commit -m "Update version.json for v1.0.1"
git push origin main
```

### Step 6: Distribute to User

Send her a link:
```
https://github.com/ludreinsalvador/capex-reporting-app/releases/tag/v1.0.1
```

Or send directly:
```
https://github.com/ludreinsalvador/capex-reporting-app/releases/download/v1.0.1/CAPEX_Reporting_Tool.exe
```

She:
1. Clicks link and downloads exe
2. Creates shortcut on Desktop
3. Runs it
4. Done! Updates happen automatically

---

## File Structure

```
capex-reporting-app/
├── config/
│   ├── version.py              ← UPDATE VERSION HERE FOR EACH RELEASE
│   ├── config.py
│   └── __init__.py
├── utils/
│   ├── auto_updater.py         ← Auto-update logic (don't modify)
│   ├── file_detector.py
│   └── validators.py
├── src/
│   └── app_desktop.py          ← Integrated auto-updatercall
├── processors/
│   └── ... (all processors)
├── VERSION_JSON_LOCATION
│   └── version.json            ← UPDATE DOWNLOAD_URL HERE FOR EACH RELEASE
├── RELEASES.md                 ← Version history
├── SETUP.md                    ← This file
├── requirements.txt            ← pip dependencies
├── CAPEX_Reporting_Tool.spec   ← PyInstaller config
└── .gitignore
```

---

## How to Release a New Version

### Quick Checklist (5 minutes)

```
1. [ ] Make code changes and test
2. [ ] Update config/version.py: VERSION = "1.0.2"
3. [ ] Build exe: pyinstaller CAPEX_Reporting_Tool.spec
4. [ ] Create GitHub release v1.0.2 and upload exe
5. [ ] Update version.json download_url to new release
6. [ ] Commit and push version.json
7. [ ] Done! Users auto-update on next app open
```

### Detailed Workflow Example

Releasing v1.0.2 with a bug fix:

```bash
# 1. Make and test fix
git add src/app_desktop.py
git commit -m "Fix: Improved error handling"

# 2. Update version
# Edit config/version.py: VERSION = "1.0.2"
git add config/version.py
git commit -m "Bump version to 1.0.2"

# 3. Build exe
pyinstaller CAPEX_Reporting_Tool.spec
# Output: dist/CAPEX_Reporting_Tool.exe

# 4. Create release on GitHub (web interface)
# - Tag: v1.0.2
# - Upload exe from dist/

# 5. Update version.json
# Edit version.json:
{
  "version": "1.0.2",
  "download_url": "https://github.com/ludreinsalvador/capex-reporting-app/releases/download/v1.0.2/CAPEX_Reporting_Tool.exe",
  "release_date": "2026-02-25",
  "notes": "Fixed error handling in import dialogs"
}

git add version.json
git commit -m "Update version.json for v1.0.2"
git push origin main

# 6. Test and notify
# Tell user: "New version 1.0.2 available - auto-update will download on next restart"
```

### What Happens Next

When user opens app:
1. App starts
2. `check_updates_on_startup()` called
3. Background thread checks GitHub version.json
4. Sees v1.0.2 > v1.0.1
5. Downloads new exe
6. Creates update batch file
7. Next time she restarts app → update installs
8. User doesn't know anything happened ✓

---

## Update Flow Diagram

```
Developer                              User
    |                                  |
    ├─1. Code fix ──────────────────.. |
    │                                  |
    ├─2. Build exe with PyInstaller    |
    │                                  |
    ├─3. Create GitHub release         |
    │    └─ Upload exe                 |
    │                                  |
    ├─4. Update version.json           |
    │    └─ Commit & push              |
    │                                  |
    └─────────────────────────────────>├─ Opens app
                                       │
                                       ├─ Auto-checks version.json
                                       │
                                       ├─ Downloads new exe if available
                                       │
                                       ├─ Schedules update
                                       │
                    (User closes app) <─┤
                                       │
                    (Update installs)  │
                                       │
                    (App restarts)    ─┤
                                       │
                    (New version v1.0.2) ✓
```

---

## Troubleshooting

### Update Check Failed (Offline)
- User's laptop doesn't have internet
- App continues with current version
- On next internet connection, update will download

### Update Downloaded But Not Installing
- Batch file might not have permissions
- Try running as Administrator
- Check `logs/update.log` for errors

### Manual Version Check
```python
# For testing, run this in Python:
from utils.auto_updater import AutoUpdater
from config.version import VERSION, VERSION_CHECK_URL

updater = AutoUpdater(VERSION, VERSION_CHECK_URL)
has_update, new_version, url = updater.check_for_updates()
print(f"Current: {VERSION}, Latest: {new_version}, Update available: {has_update}")
```

### Check Update Logs
```bash
# After running app, check:
cat logs/update.log

# Shows all version checks and downloads
```

---

## Testing Auto-Update Locally

### Simulate New Version Available

```python
# Edit version.json temporarily:
{
  "version": "1.0.2",  # Bump to simulate new version
  ...
}

# Run app - should see update check in logs/update.log
python src/app_desktop.py

# Check logs:
cat logs/update.log
```

### Test Download & Installation

Create a test release on GitHub:
1. Upload dummy exe as v1.0.2
2. Update version.json
3. Run app
4. Monitor logs

The batch file will try to replace exe - if download URL is valid, it will work even if exe is test file.

---

## Deployment Checklist

Before each release:

- [ ] All features tested locally
- [ ] No syntax errors (`pylance` check)
- [ ] version.py updated with new version
- [ ] RELEASES.md updated with changelog
- [ ] requirements.txt has all dependencies
- [ ] PyInstaller spec file up to date
- [ ] Built exe exists in dist/
- [ ] GitHub release created with exe uploaded
- [ ] version.json updated with new download URL
- [ ] version.json committed and pushed
- [ ] Release notification sent to user

---

## FAQ

**Q: How do I know if an update is available?**
A: Check `logs/update.log` or look at version in window title.

**Q: Can I skip an update?**
A: Updates install automatically on next restart. Can't skip.

**Q: What if update fails?**
A: App continues with old version. Next restart tries again.

**Q: Can user revert to old version?**
A: Only by downloading old exe from GitHub releases manually.

**Q: Is there a way to force all users to update?**
A: Currently no. All versions work indefinitely. Could add "forced update" in future.

**Q: Can I update the app while user has it running?**
A: No. Update installs after app closes. Safe to update while running.

**Q: How big is the exe?**
A: Roughly 50-100 MB depending on dependencies.

---

## Next Steps

1. ✅ You've implemented auto-update system
2. ✅ All code reviewed and validated
3. Next:
   - Build exe with PyInstaller
   - Create first GitHub release v1.0.1
   - Update version.json
   - Send exe link to user
   - Monitor logs to confirm first update check works
   - That's it! System is automated from here

---

**Last Updated:** 2026-02-24
**Current Version:** 1.0.1
