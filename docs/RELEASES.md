# Release History - CAPEX Reporting Tool

All notable changes to the CAPEX Reporting Tool will be documented in this file.

## Installation & Distribution

**For Windows Users:**
1. Download `CAPEX_Reporting_Tool.exe` from GitHub Releases
2. Double-click to run
3. App automatically checks for updates
4. Updates install silently on next restart

**For macOS Users:**
1. Download `CAPEX_Reporting_Tool.app.zip` from GitHub Releases
2. Unzip to get `CAPEX_Reporting_Tool.app`
3. Double-click to run (may need to allow in Security settings)
4. App automatically checks for updates
5. Updates install silently on next restart

**For Developers:**
- Update `config/version.py` with new version number
- Build Windows: `python -m PyInstaller build-scripts/CAPEX_Reporting_Tool.spec`
- Build macOS: `python -m PyInstaller build-scripts/CAPEX_Reporting_Tool_macOS.spec`
- Create GitHub release with tag `v{VERSION}`
- Upload both executables to release
- Update `version.json` with platform-specific download URLs

---

## [1.0.1] - 2026-02-25

### Added - Cross-Platform Support
- ✓ **macOS Support** - Full application support for Apple macOS
  - App bundle (.app) for native macOS experience
  - Compressed ZIP distribution (~80 MB)
  - Auto-updater detects macOS and downloads correct version
  - Shell script installation (equivalent to Windows batch approach)
  - Same features as Windows version

- ✓ **Platform Detection** - Auto-updater automatically:
  - Detects Windows vs macOS
  - Downloads correct executable version
  - Uses OS-specific installation method
  - Maintains single version.json for both platforms

- ✓ **Dual Build Configuration** - PyInstaller specs for both:
  - Windows: `CAPEX_Reporting_Tool.spec` → .exe (54 MB)
  - macOS: `CAPEX_Reporting_Tool_macOS.spec` → .app bundle

- ✓ **Auto-Update System** - Cross-platform version:
  - Windows: Uses batch file replacement
  - macOS: Uses shell script replacement
  - Same transparent user experience on both platforms
  - Graceful handling of offline mode on both OS

### Features (from previous work)
- ✓ **18 Formula Columns (K-AB)** in WP LOA processor including:
  - K-N: PID extraction formulas
  - O-P: L1/L2 concatenation
  - Q-U: BUDGET lookups (Program MBR, DIV, DEP, FUNDING, CFU SPONSOR)
  - V-X: AVAILMENT TRACKER, PROPONENT lookups
  - Y: DIV IN REPORT (nested IF mapping)
  - **Z: PROGRAM IN REPORT** (Program name from BUDGET)
  - AA-AB: Project and Subproject names

- ✓ **Flexible File Detection** - Auto-detection handles naming variations:
  - Matches "2026 CAPEX AVAILMENT_as of FEB 23" ✓
  - Matches "Feb 16 AVAILMENT" ✓
  - Matches "LOA_CURRENT_APPROVER (Auto Email)" ✓
  - Uses keyword-based matching (3+ keywords per file type)

- ✓ **Formula-Based Processing** - All formulas written to Excel, not calculated values
  - Formulas remain editable in Excel
  - IFERROR wrapping for safe lookups
  - Dynamic filename insertion in VLOOKUP

- ✓ **Multiple Processors:**
  - CJI5 & CJI3 processors (currency conversion)
  - RFP Reclass processor
  - ZMM processor with consolidation
  - WP LOA processor with formula generation

### Fixed
- ✓ VLOOKUP returning "N/A" errors (wrong range and key)
- ✓ Excessive code comments (cleaned up docstrings)
- ✓ Missing column headers K, L, M, N
- ✓ Strict file name requirements (now flexible)

### Structure
```
capex-reporting-app/
├── config/
│   ├── version.py         (NEW: Version tracking)
│   ├── config.py
│   └── __init__.py
├── utils/
│   ├── auto_updater.py    (NEW: Auto-update logic)
│   ├── file_detector.py
│   └── validators.py
├── src/
│   └── app_desktop.py     (UPDATED: Integratedp auto-updater)
├── processors/
│   ├── wp_loa_formula.py
│   ├── wp_loa.py
│   └── ...
├── logs/                   (NEW: Auto-created for update logs)
├── version.json            (NEW: GitHub release metadata)
├── RELEASES.md             (NEW: This file)
└── README.md
```

### Technical Details

**Auto-Updater Features:**
- Background thread (doesn't block app)
- Timeout handling (5s for version check, 60s for download)
- Graceful offline fallback
- Full logging to `logs/update.log`
- Batch file replacement (replaces exe after app closes)
- Version comparison using tuple sorting

**Update Flow:**
1. App starts → `check_updates_on_startup()` called
2. Background thread starts (doesn't block UI)
3. Connects to `version.json` on GitHub main branch
4. Compares versions
5. If newer available:
   - Downloads new exe (with 60s timeout)
   - Creates `update_installer.bat`
   - Schedules bat file to run
   - On next restart, bat replaces exe and restarts app
6. If offline or error: Silently continues with current version

**Deployment Checklist:**
- [x] Version config in `config/version.py`
- [x] AutoUpdater class in `utils/auto_updater.py`
- [x] App integration in `src/app_desktop.py`
- [x] Release metadata in `version.json`
- [x] Release documentation in `RELEASES.md`
- [ ] Build exe with PyInstaller
- [ ] Create GitHub release v1.0.1
- [ ] Upload exe to GitHub release
- [ ] Test auto-update workflow
- [ ] Distribute exe link to users

### Known Limitations
- Currently Windows-only (uses `os.startfile()` and batch files)
- Requires internet connection for updates (app works offline)
- Updates install on **next restart** (not immediate)
- Batch file approach works for compiled exe only

---

## Planned for Future Releases

### v1.0.2 (Planned)
- [ ] Improved UI with update notification
- [ ] Option to manually check for updates from GUI
- [ ] Update progress indicator
- [ ] macOS/Linux support for auto-updater
- [ ] Self-extracting installer option

### v1.1.0 (Planned)
- [ ] Advanced filtering options
- [ ] Custom Excel template support
- [ ] Batch processing multiple files
- [ ] Real-time formula preview
- [ ] Dark mode UI

### v2.0.0 (Planned - Major refactor)
- [ ] Web-based app (Flask/FastAPI)
- [ ] Cloud storage integration
- [ ] Multi-user collaboration
- [ ] REST API
- [ ] Advanced reporting dashboards

---

## How to Use This Document

**For Users:**
- Check the "Added" and "Fixed" sections to see what's new
- Follow "Installation & Distribution" section to get the app

**For Developers:**
- Check "Technical Details" for implementation notes
- Use "Deployment Checklist" before each release
- Update this file with each new release
- Keep version number in sync with `config/version.py`

---

## Version Numbering Scheme

Follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.0.1)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes only

Example:
- 1.0.0 → 1.0.1 = bug fix
- 1.0.1 → 1.1.0 = new feature
- 1.1.0 → 2.0.0 = breaking change

---

## Support

For issues or questions:
1. Check existing GitHub issues
2. Review logs in `logs/update.log`
3. Contact developer

---

**Last Updated:** 2026-02-24
**Current Version:** 1.0.1
