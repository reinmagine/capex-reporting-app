# Build and Deployment Checklist

Use this checklist every time you release a new version.

---

## PRE-RELEASE (Development Phase)

### Code Changes
- [ ] Features implemented and tested locally
- [ ] All bugs fixed and verified
- [ ] No syntax errors (run pylance check)
- [ ] All imports working correctly
- [ ] Functions tested individually
- [ ] Integration tested with full workflow

### Code Quality
- [ ] No unused imports
- [ ] Docstrings updated
- [ ] Comments are clear and helpful
- [ ] No debug print statements left in
- [ ] Code follows project style conventions
- [ ] No hardcoded paths or credentials

### Documentation
- [ ] README.md updated if UI changed
- [ ] Function docstrings updated with parameters
- [ ] Any breaking changes documented
- [ ] Known issues or limitations noted

### Testing
- [ ] Manual testing on Windows (primary platform)
- [ ] Test with sample data files
- [ ] All processors work correctly
- [ ] File detection works as expected
- [ ] Formulas calculate correctly
- [ ] No crashes or errors in logs

---

## VERSION UPDATE

### Update Version Number
- [ ] Edit `config/version.py`
- [ ] Update: `VERSION = "1.0.2"` (increase from current)
- [ ] Verify format is semantic versioning (MAJOR.MINOR.PATCH)
- [ ] Save file

### Update Release Documentation
- [ ] Edit `RELEASES.md`
- [ ] Add section for new version at top
- [ ] Add [Release Date]
- [ ] List features under "### Added"
- [ ] List bug fixes under "### Fixed"
- [ ] List any breaking changes under "### Changed"
- [ ] Add upgrade instructions if needed

---

## BUILD PHASE

### Prepare for Build
- [ ] Close all running Python processes
- [ ] Ensure `dist/` directory doesn't have old files
- [ ] Ensure `CAPEX_Reporting_Tool.spec` is up-to-date
- [ ] Check all dependencies in `requirements.txt`

### Build Executable
- [ ] Open PowerShell in workspace root
- [ ] Run: `pyinstaller CAPEX_Reporting_Tool.spec`
- [ ] Wait for build to complete
- [ ] Verify `dist/CAPEX_Reporting_Tool.exe` exists
- [ ] Check file size is reasonable (~50-100 MB)
- [ ] Test exe by running it once
- [ ] Clean up: delete `build/` directory

### Local Testing
- [ ] Run exe and verify app opens
- [ ] Check window title shows version (v1.0.2)
- [ ] Test main functionality briefly
- [ ] Close app normally
- [ ] Check `logs/update.log` was created
- [ ] Verify no errors in logs

---

## GITHUB RELEASE PHASE

### Create GitHub Release
- [ ] Go to: https://github.com/ludreinsalvador/capex-reporting-app/releases/new
- [ ] Click "Draft a new release"
- [ ] Tag version: `v1.0.2` (must match version.py)
- [ ] Release title: `CAPEX Reporting Tool v1.0.2`
- [ ] Description: Copy from `RELEASES.md` for this version
- [ ] Attach files: Drag and drop `dist/CAPEX_Reporting_Tool.exe`
- [ ] Click "Publish release"
- [ ] Wait for upload to complete
- [ ] Verify exe is downloadable

### Verify GitHub Release
- [ ] Open release page in browser
- [ ] Confirm exe file is listed
- [ ] Click exe download to verify link works
- [ ] Copy download URL for next step

---

## VERSION.JSON UPDATE

### Update version.json
- [ ] Edit `version.json` in repo root
- [ ] Update `"version": "1.0.2"` (must match tag)
- [ ] Update `"download_url"`: Paste GitHub release download link
- [ ] Verify download_url format is correct:
  ```
  https://github.com/ludreinsalvador/capex-reporting-app/releases/download/v1.0.2/CAPEX_Reporting_Tool.exe
  ```
- [ ] Update `"release_date": "2026-02-25"` (today's date)
- [ ] Update `"notes": "Bug fixes and improvements..."` (brief summary)
- [ ] Verify JSON is valid (use JSON validator if unsure)

### Commit version.json
- [ ] Open PowerShell in workspace root
- [ ] Run: `git add version.json`
- [ ] Run: `git commit -m "Update version.json for v1.0.2"`
- [ ] Run: `git push origin main`
- [ ] Verify push succeeded

### Verify GitHub Update
- [ ] Go to GitHub repo main branch
- [ ] Verify `version.json` shows new version
- [ ] Verify `download_url` points to correct release

---

## DISTRIBUTION PHASE

### Prepare for User Distribution
- [ ] Create short release notes (what's new)
- [ ] Collect download URL from GitHub
- [ ] Test download URL one more time
- [ ] Have backup download method if needed

### Notify User
- [ ] Send update notification email/message
- [ ] Include: What changed in this version
- [ ] Include: Download link if first time
- [ ] Include: Instructions if first time: "Just download and run"
- [ ] If just bug fix: "Auto-update available - will install on next restart"

### User Distribution Process
For returning users:
- [ ] User opens app next time
- [ ] Background update check runs
- [ ] New version downloaded
- [ ] Update scheduled for restart
- [ ] On next restart, update installs
- [ ] User opens updated version

For new users:
- [ ] Send exe download link
- [ ] User downloads exe
- [ ] User runs exe (no installation needed)
- [ ] App opens and works
- [ ] From then on, auto-updates apply

---

## POST-RELEASE MONITORING

### First Week
- [ ] Check logs/update.log for errors
- [ ] Verify user received update
- [ ] Ask user: "Did app update automatically?"
- [ ] Monitor for bug reports
- [ ] Have fix prepared if critical bug found

### Ongoing
- [ ] Keep RELEASES.md updated
- [ ] Archive old logs monthly
- [ ] Review update.log for patterns
- [ ] Monitor app performance

---

## ROLLBACK PLAN (If Release Fails)

### If Critical Bug Found
1. [ ] Stop distributing new version immediately
2. [ ] Revert version.json to previous version
3. [ ] Commit and push revert
4. [ ] Wait for users to re-update to previous version
5. [ ] Fix bug in code
6. [ ] Release new patch version (e.g., 1.0.3)

### Manual Rollback Command
```bash
git revert HEAD  # Reverts most recent commit
git push origin main
```

---

## EXAMPLE: Release v1.0.2

### Pre-Release
- [x] Fixed file detection bug
- [x] Tested with 5 sample files
- [x] No syntax errors
- [x] Added docstrings for new functions

### Version Update
- [x] config/version.py: VERSION = "1.0.2"
- [x] RELEASES.md: Added v1.0.2 section with fixes

### Build
- [x] PyInstaller build successful
- [x] Exe is 75 MB
- [x] Local testing passed

### GitHub
- [x] Created release v1.0.2
- [x] Uploaded exe (75 MB)
- [x] Released successfully

### version.json
- [x] Updated with v1.0.2
- [x] Download URL verified
- [x] Committed and pushed

### Distribution
- [x] Sent notification: "Version 1.0.2 with bug fixes"
- [x] Users auto-update on next app open
- [x] Monitor update.log for issues

### Monitoring
- [x] No errors in logs
- [x] User confirmed update worked
- [x] v1.0.2 stable after 1 week

---

## TIME ESTIMATES

| Task | Time |
|------|------|
| Code changes & testing | Varies |
| Update version files | 2 min |
| Build exe | 3-5 min |
| Local test | 2 min |
| Create GitHub release | 3 min |
| Update version.json | 2 min |
| Commit & push | 1 min |
| Notify user | 2 min |
| **TOTAL** | **~20 min** |

---

## COMMON MISTAKES (Avoid These!)

❌ Building exe BEFORE updating version.py  
✅ Always update version.py first

❌ Using wrong tag format in GitHub (use v1.0.2 not 1.0.2)  
✅ Always use "v" prefix for tags

❌ Forgetting to update version.json download_url  
✅ Users won't get the update

❌ Testing exe while old exe running  
✅ Close old exe before testing new one

❌ Committing exe to Git (they're 75 MB)  
✅ Only commit version.json, not exe

---

## USEFUL COMMANDS

```bash
# Check current version
python -c "from config.version import VERSION; print(f'Current: {VERSION}')"

# Build exe
pyinstaller CAPEX_Reporting_Tool.spec

# Clean build artifacts
rmdir /s dist build  # Windows

# View update logs
type logs\update.log  # Windows
cat logs/update.log   # Mac/Linux

# Git log to see releases
git log --oneline | grep -i "release\|version"

# Test version.json JSON syntax
python -c "import json; json.load(open('version.json'))"
```

---

## RELEASE SCHEDULE

### Recommended Practices
- **Patch Releases (1.0.1 → 1.0.2):** Weekly if bugs found
- **Minor Releases (1.0.0 → 1.1.0):** Monthly for new features
- **Major Releases (1.0.0 → 2.0.0):** Quarterly or with breaking changes

### Communication
- Notify user 24 hours before major release
- Automatic notification for patches/bug fixes
- Include "what's new" in release message

---

## NEXT STEPS

1. [ ] Complete this version's development
2. [ ] Update version.py to 1.0.2 (or next version)
3. [ ] Update RELEASES.md with changes
4. [ ] Build exe with PyInstaller
5. [ ] Create GitHub release with exe
6. [ ] Update version.json with new download URL
7. [ ] Commit and push
8. [ ] Notify user of availability
9. [ ] Monitor for updates/issues
10. [ ] Archive logs if needed

---

## REFERENCE DOCUMENTS

- `SETUP.md` - Detailed deployment guide
- `RELEASES.md` - Release version history
- `IMPLEMENTATION_SUMMARY.md` - What was implemented
- `QUICK_REFERENCE.md` - TL;DR quick commands
- `config/version.py` - Current version configuration
- `version.json` - Release metadata

---

**Version:** 1.0.1  
**Last Updated:** 2026-02-24  
**Checklist Status:** Ready to use ✅
