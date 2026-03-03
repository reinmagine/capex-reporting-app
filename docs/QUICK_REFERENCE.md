# Quick Start - Auto-Update System

## ⚡ TL;DR

Your CAPEX Reporting Tool now has automatic updates built-in. Here's what to do:

### For You (Developer)

**To Release a New Version (5 minutes):**

```bash
# 1. Update version number
# Edit: config/version.py
# Change: VERSION = "1.0.2"  (increase from 1.0.1)

# 2. Build executable
pyinstaller CAPEX_Reporting_Tool.spec
# Result: dist/CAPEX_Reporting_Tool.exe

# 3. Create GitHub release
# Go to: https://github.com/ludreinsalvador/capex-reporting-app/releases/new
# Tag: v1.0.2
# Upload: dist/CAPEX_Reporting_Tool.exe

# 4. Update version.json
# Edit: version.json
# Change download_url to: https://github.com/.../download/v1.0.2/CAPEX_Reporting_Tool.exe
git add version.json
git commit -m "Update version.json for v1.0.2"
git push origin main

# Done! Users auto-update on next restart
```

### For Your User

**First Time:**
1. Download `CAPEX_Reporting_Tool.exe`
2. Double-click → App runs
3. Done! ✓

**Every Time After:**
- App checks for updates in background automatically
- If new version available, downloads silently
- Installs on next restart
- Zero user interaction

---

## 📁 Files Added

| File | Purpose | Location |
|------|---------|----------|
| `version.py` | Version configuration | `config/` |
| `auto_updater.py` | Update logic | `utils/` |
| `version.json` | GitHub release metadata | Root |
| `RELEASES.md` | Version history | Root |
| `SETUP.md` | Deployment guide | Root |
| `IMPLEMENTATION_SUMMARY.md` | What was done | Root |
| `.gitignore` | Git ignore rules | Root |
| `logs/.gitkeep` | Log directory | `logs/` |

---

## 🔍 Key Files to Know

| File | Edit? | Purpose |
|------|-------|---------|
| `config/version.py` | ✅ YES | Update VERSION with each release |
| `version.json` | ✅ YES | Update download_url after GitHub release |
| `utils/auto_updater.py` | ❌ NO | Don't modify - it's the update engine |
| `src/app_desktop.py` | ❌ NO | Already integrated |
| `RELEASES.md` | ✅ YES | Document changes each release |

---

## 📋 Release Checklist

### Before Release
- [ ] Code tested and working
- [ ] No syntax errors
- [ ] Features documented

### During Release
- [ ] Update `config/version.py` with new version
- [ ] Build exe: `pyinstaller CAPEX_Reporting_Tool.spec`
- [ ] Create GitHub release with tag `v1.0.X`
- [ ] Upload exe from `dist/`
- [ ] Update `version.json` with new download URL
- [ ] Commit and push

### After Release
- [ ] Test by downloading exe
- [ ] Send update notification to user
- [ ] Monitor `logs/update.log` for issues

---

## 🧪 Testing Auto-Update

```bash
# 1. Run app and check logs
python src/app_desktop.py

# 2. View update logs
type logs/update.log

# 3. Manual version check in Python
python -c "from config.version import VERSION; print(f'Version: {VERSION}')"
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Update check failed" | User offline - app continues, tries again next time |
| "Can't write to file" | Run as admin, check file permissions |
| "Excel file locked" | Close Excel first, then run app |
| Want to see what's happening? | Check `logs/update.log` |

---

## 📊 Version Numbers

```
Format: MAJOR.MINOR.PATCH

1.0.1  →  1.0.2  = Bug fix (patch)
1.0.1  →  1.1.0  = New feature (minor)
1.0.1  →  2.0.0  = Breaking change (major)
```

---

## 🚀 Deployment Workflow

```
CODE FIX → UPDATE VERSION → BUILD EXE → 
CREATE RELEASE → UPDATE version.json → 
PUSH TO GITHUB → ✓ DONE!

Users auto-update automatically next time they open app
```

---

## 📞 Need Help?

1. **Setup questions:** See `SETUP.md`
2. **Release history:** See `RELEASES.md`
3. **What was implemented:** See `IMPLEMENTATION_SUMMARY.md`
4. **Update logs:** Check `logs/update.log`
5. **Code details:** See `utils/auto_updater.py`

---

## ✅ What's Working

- ✅ Version tracking
- ✅ Auto-update checking
- ✅ Silent background downloads
- ✅ Graceful offline handling
- ✅ Automatic installation
- ✅ Full logging
- ✅ GitHub integration
- ✅ App window version display

---

## 🎯 Current Status

**Version:** 1.0.1  
**Status:** Ready for production ✅  
**User Experience:** Automatic updates, zero interaction  
**Developer Effort:** 5 minutes per release

---

## 📝 Quick Command Reference

```bash
# Build exe
pyinstaller CAPEX_Reporting_Tool.spec

# Run app from Python
python src/app_desktop.py

# Check update logs
type logs\update.log  # Windows
cat logs/update.log   # Mac/Linux

# View current version
python -c "from config.version import VERSION; print(VERSION)"

# Git commands for release
git add config/version.py version.json
git commit -m "Release v1.0.2"
git push origin main
```

---

## 📚 Documentation Location

Moved to `docs/` folder for organization:
- `docs/SETUP.md` - Detailed deployment guide
- `docs/BUILD_CHECKLIST.md` - Release checklist
- `docs/IMPLEMENTATION_SUMMARY.md` - What was implemented
- `docs/RELEASES.md` - Release version history

---

**Version:** 1.0.1  
**Last Updated:** 2026-02-24  
**Ready to Deploy:** YES ✅
