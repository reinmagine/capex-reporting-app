# CAPEX Reporting Tool

Cross-platform Excel processing application for Windows and macOS with automatic updates.

**Current Version:** 1.0.1  
**Supported Platforms:** Windows 7+, macOS 10.13+  
**Auto-Updates:** Built-in (check every launch)

---

## Quick Start

### For Windows Users
1. **Download:** [CAPEX_Reporting_Tool.exe](https://github.com/ludreinsalvador/capex-reporting-app/releases/download/v1.0.1/CAPEX_Reporting_Tool.exe) (~54 MB)
2. **Run:** Double-click exe
3. **Done!** Updates check automatically

**Full Guide:** [docs/README_WINDOWS.md](docs/README_WINDOWS.md)

### For macOS Users
1. **Download:** [CAPEX_Reporting_Tool.app.zip](https://github.com/ludreinsalvador/capex-reporting-app/releases/download/v1.0.1/CAPEX_Reporting_Tool.app.zip) (~80 MB)
2. **Extract:** Unzip file
3. **Run:** Double-click app (handle security dialog)
4. **Done!** Updates check automatically

**Full Guide:** [docs/README_MACOS.md](docs/README_MACOS.md)

---

## Features

- **Excel Processing:** Process multiple Excel file formats
  - WP LOA Report generation
  - CJI data transformation
  - RFP Reclassification
  - ZMM handling

- **User-Friendly GUI:** Simple Tkinter interface
  - Drag-and-drop file selection
  - Real-time processing feedback
  - Download processed results

- **Cross-Platform:** Single codebase for Windows and macOS
  - Native installers for each OS
  - Consistent interface everywhere
  - Seamless collaboration

- **Automatic Updates:** Silent background updates
  - Check on every launch
  - Download silently
  - Install on next restart
  - No user interaction required

---

## Technical Stack

| Component | Details |
|-----------|---------|
| **Language** | Python 3.13.12 (Windows), 3.9+ (macOS) |
| **GUI Framework** | Tkinter (built-in, cross-platform native) |
| **Data Processing** | Pandas 2.2.0, openpyxl 3.1.2 |
| **Packaging** | PyInstaller 6.18.0+ (single-file executables) |
| **Distribution** | GitHub Releases |
| **Updates** | Custom threaded auto-updater |

---

## Project Structure

```
capex-reporting-app/
├── src/                          # Source code (when run from GitHub)
│   ├── app.py                    # Main application entry
│   ├── app_desktop.py            # Desktop variant launcher
│   └── processors/               # Excel processors
├── utils/
│   ├── auto_updater.py           # Cross-platform update engine
│   └── ...
├── build-scripts/
│   ├── CAPEX_Reporting_Tool.spec     # Windows build config
│   └── CAPEX_Reporting_Tool_macOS.spec  # macOS build config
├── docs/
│   ├── README_WINDOWS.md         # Windows user guide
│   ├── README_MACOS.md           # macOS user guide
│   ├── CROSS_PLATFORM_BUILD.md   # Build instructions for developers
│   ├── RELEASES.md               # Version history
│   └── CROSS_PLATFORM_CHECKLIST.md # Implementation checklist
├── version.json                  # Version metadata with platform-specific URLs
└── requirements.txt              # Python dependencies
```

---

## Installation Methods

### Method 1: Direct Download (Recommended)

**Windows:**
```
Visit releases → Download CAPEX_Reporting_Tool.exe → Double-click
```

**macOS:**
```
Visit releases → Download CAPEX_Reporting_Tool.app.zip → Unzip → Double-click app
```

### Method 2: GitHub Releases Page

Visit: https://github.com/ludreinsalvador/capex-reporting-app/releases

Select latest release and download appropriate binary for your OS.

### Method 3: Developer Source Build

```bash
# Windows & macOS
git clone https://github.com/ludreinsalvador/capex-reporting-app.git
cd capex-reporting-app
pip install -r requirements.txt
python -m src.app  # Run from source
```

For building executables: See [docs/CROSS_PLATFORM_BUILD.md](docs/CROSS_PLATFORM_BUILD.md)

---

## How Automatic Updates Work

1. **On Launch:** App checks version on GitHub (immediate)
2. **If Update Available:**
   - Downloads silently in background
   - Shows no dialogs
   - Doesn't interrupt your work
3. **On Next Restart:** New version runs automatically
4. **You Never Have To:** Check for updates or manually install

**Technical Details:**
- Platform detection uses `platform.system()` (Windows, Darwin, Linux)
- Downloads appropriate binary (`.exe` or `.app.zip`)
- Installs via OS-specific script (batch on Windows, shell on macOS)
- Completely transparent to end user

See [docs/CROSS_PLATFORM_BUILD.md](docs/CROSS_PLATFORM_BUILD.md) for developer details.

---

## For Developers

### Build for Windows

```bash
# Clean
rmdir /s /q dist build

# Build
python -m PyInstaller build-scripts/CAPEX_Reporting_Tool.spec

# Output: dist/CAPEX_Reporting_Tool.exe (~54 MB)
```

### Build for macOS

```bash
# Build
python -m PyInstaller build-scripts/CAPEX_Reporting_Tool_macOS.spec

# Compress for distribution
cd dist
zip -r CAPEX_Reporting_Tool.app.zip CAPEX_Reporting_Tool.app

# Output: CAPEX_Reporting_Tool.app.zip (~80 MB)
```

**Full guide:** [docs/CROSS_PLATFORM_BUILD.md](docs/CROSS_PLATFORM_BUILD.md)

### Release Process

1. Build both Windows and macOS executables
2. Upload to GitHub Release v1.0.1
3. Update `version.json` with newest URLs
4. Users auto-update on next launch

**See:** [docs/RELEASES.md](docs/RELEASES.md)

---

## Troubleshooting

### "Windows Protected Your PC"

Click **"More info"** → **"Run anyway"**

See [docs/README_WINDOWS.md](docs/README_WINDOWS.md) for details.

### macOS: "App Can't Be Opened"

Run in Terminal:
```bash
xattr -d com.apple.quarantine ~/Downloads/CAPEX_Reporting_Tool.app
```

See [docs/README_MACOS.md](docs/README_MACOS.md) for details.

### App Won't Update

Check logs:
- **Windows:** `%APPDATA%\CAPEX_Reporting_Tool\logs\update.log`
- **macOS:** `~/Applications/CAPEX_Reporting_Tool.app/Contents/Resources/logs/update.log`

---

## Documentation

| Document | Audience | Purpose |
|----------|----------|---------|
| [README_WINDOWS.md](docs/README_WINDOWS.md) | Windows Users | Download, install, troubleshoot |
| [README_MACOS.md](docs/README_MACOS.md) | macOS Users | Download, install, troubleshoot |
| [CROSS_PLATFORM_BUILD.md](docs/CROSS_PLATFORM_BUILD.md) | Developers | Build instructions for both OS |
| [RELEASES.md](docs/RELEASES.md) | Everyone | Version history & changelog |
| [CROSS_PLATFORM_CHECKLIST.md](docs/CROSS_PLATFORM_CHECKLIST.md) | Developers | Implementation tracking |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Developers | Quick command reference |

---

## Security & Privacy

### Data Processing
- **All processing local:** No files uploaded anywhere
- **No tracking:** Application doesn't track usage
- **No analytics:** No telemetry sent
- **Secure:** Excel files remain private on your computer

### Update Checking
- **Version check only:** No personal data sent
- **Network optional:** Works offline after download
- **GitHub hosted:** Binaries from official releases
- **Transparent:** You control when updates install

---

## Support

### Common Questions

**Q: Will my Excel files be uploaded?**  
A: No. All processing happens on your computer. Nothing is uploaded.

**Q: How often should I update?**  
A: App checks automatically on every launch. Updates install silently, no action needed.

**Q: Will updates interrupt my work?**  
A: No. Updates download silently in background. Install on next restart only.

**Q: Can Windows and macOS users work together?**  
A: Yes! Same application, same formats, perfect collaboration.

**Q: What if I want to run from USB?**  
A: Works great! Just copy exe/app anywhere. Updates work the same.

### Report Issues

1. Check relevant user guide for troubleshooting
2. Review logs in app data folder
3. Contact developer with error message and environment details

---

## Contact

- **Author:** Ludrein Reimar Salvador
- **Email:** ludreinreimar.salvador@gmail.com
- **GitHub:** https://github.com/reinmagine/capex-reporting-app

---

**Version:** 1.0.1  
**Last Updated:** March 3, 2026  
**Status:** Cross-platform stable release

For latest release: https://github.com/reinmagine/capex-reporting-app/releases/latest
