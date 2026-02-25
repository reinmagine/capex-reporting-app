# Windows Installation & Usage Guide

Complete guide for Windows users to download, install, and use CAPEX Reporting Tool

---

## 📥 STEP 1: Download Application

### Option A: From GitHub Releases (Recommended)

1. Visit: https://github.com/ludreinsalvador/capex-reporting-app/releases
2. Find the latest release
3. Download `CAPEX_Reporting_Tool.exe` (~54 MB)
4. Wait for download to complete

### Option B: Direct Download Link

```
https://github.com/ludreinsalvador/capex-reporting-app/releases/download/v1.0.1/CAPEX_Reporting_Tool.exe
```

---

## ⬇️ STEP 2: Run Installer Batch File (Optional)

**Choose One Method:**

### Method A: Automatic Install (Recommended)
```bash
# Double-click this file:
START_DESKTOP_APP.bat
```

This batch file:
- Creates `C:\Program Files\CAPEX_Reporting_Tool\` folder
- Copies exe to that location
- Creates desktop shortcut
- Starts app immediately

### Method B: Manual Copy
1. Create folder: `C:\Program Files\CAPEX_Reporting_Tool\`
2. Copy `CAPEX_Reporting_Tool.exe` into that folder
3. Double-click exe to run

### Method C: Portable (No Install)
1. Keep `CAPEX_Reporting_Tool.exe` in any folder
2. Double-click exe to run
3. Updates check automatically

---

## ✅ STEP 3: Run Application

### From Desktop Shortcut
- Double-click shortcut created by `START_DESKTOP_APP.bat`

### From File Explorer
- Navigate to `C:\Program Files\CAPEX_Reporting_Tool\`
- Double-click `CAPEX_Reporting_Tool.exe`

### From Command Prompt
```bash
C:\Program Files\CAPEX_Reporting_Tool\CAPEX_Reporting_Tool.exe
```

### From PowerShell
```powershell
& 'C:\Program Files\CAPEX_Reporting_Tool\CAPEX_Reporting_Tool.exe'
```

---

## 🔓 TROUBLESHOOTING: "Windows Protected Your PC"

### Error Message:
> "Windows Defender SmartScreen prevented an unrecognized app from starting"

### Solution:

#### Method 1: Allow Execution (Recommended)
1. Click **"More info"** link
2. Click **"Run anyway"** button
3. App launches successfully
4. No message appears next time

#### Method 2: Disable SmartScreen
1. Settings → Privacy and Security → App and browser control
2. Turn off "SmartScreen for Microsoft Edge"
3. Run exe again
4. Click "Run" when prompted

#### Method 3: Properties/Unblock
1. Right-click `CAPEX_Reporting_Tool.exe`
2. Select **Properties**
3. At bottom, check **"Unblock"**
4. Click **Apply** → **OK**
5. Run exe normally

---

## 🚀 STEP 4: First Time Use

1. App launches → CAPEX Reporting Tool window opens
2. Choose tab: "WP LOA Report", "CJI", "RFP Reclass", or "ZMM"
3. Select Excel file to process
4. Click process button
5. Download processed file

**Behind the scenes:** App checks for updates automatically (you won't see anything)

---

## 🔄 AUTOMATIC UPDATES

### How Updates Work

1. Every time you open the app, it checks for new versions
2. If update available:
   - Downloads silently in background
   - Shows no dialogs
   - Installs on next restart
3. Next time you open app → new version runs
4. **You never need to do anything!**

### What About Notifications?

- No popups or notifications
- Updates happen silently
- You just get the latest version automatically

### Manual Update Check

To see if update is available:
1. Open app
2. Check window title: shows version (e.g., "CAPEX Reporting Tool v1.0.1")
3. App is checking in background
4. Updates found? → Installs next time you restart

### Force Check Update

Delete update cache to force fresh check:
```bash
# In Command Prompt (admin not required)
del %APPDATA%\CAPEX_Reporting_Tool\update_check.tmp
```

Then restart app.

---

## 📂 WHERE FILES GO

### Default Location
```
C:\Program Files\CAPEX_Reporting_Tool\
```

### Portable Usage (No Install)
- Keep exe anywhere you want
- Create folder for it if desired
- Works from USB drive too!

### Logs & Updates
```
C:\Users\[YourUsername]\AppData\Local\CAPEX_Reporting_Tool\logs\
```

Automatically created, no action needed from you.

---

## 🆘 COMMON ISSUES

### Issue: "Windows Protected Your PC"
**Solution:** Follow security dialog troubleshooting steps above

### Issue: "Python not found" Error
**Solution:** Shouldn't happen with packaged exe. If it does:
1. Re-download exe
2. Delete old version
3. Run new version

### Issue: "File Not Found" Error
**Solution:**
1. Make sure Excel files exist in the folder you're navigating to
2. Use file dialog to browse
3. Select correct file

### Issue: App Won't Start
**Solution:**
1. Make sure exe is not corrupted (re-download if unsure)
2. Check Windows Defender isn't blocking (see security steps above)
3. Restart computer and try again

### Issue: Very Slow on First Launch
**Solution:**
- First launch unpacks internal files (~5-10 sec)
- Subsequent launches are fast (<2 sec)
- This is normal!

### Issue: Want Portable Version (No Install)
**Solution:**
- Just run exe from any folder
- No installation needed
- Works from USB drive
- Each run creates temp folder automatically

---

## 🔒 SECURITY & PRIVACY

### Does App Phone Home?

**Update checking only:**
- Checks version file on GitHub
- Downloads exe if update available
- No personal data sent
- No tracking
- No analytics

**Excel File Processing:**
- All processing happens on your computer
- No files uploaded anywhere
- No internet required after download
- Private and secure

### What Permissions Needed?

- **File access:** To read/write your Excel files
- **Network access:** Only to check for updates
- **No admin rights needed**
- **No system-wide changes**

---

## 📌 CREATE SHORTCUTS (Optional)

### Desktop Shortcut
1. Right-click `CAPEX_Reporting_Tool.exe`
2. Click **"Send to"** → **"Desktop (create shortcut)"**
3. Shortcut appears on Desktop!

### Start Menu
1. Run `START_DESKTOP_APP.bat` (creates automatically)
2. Find "CAPEX Reporting Tool" in Start Menu
3. Pin to Start screen if desired

### Quick Access (File Explorer)
1. Open File Explorer
2. Go to `C:\Program Files\CAPEX_Reporting_Tool\`
3. Right-click exe → **"Pin to Quick access"**

---

## 🌐 SHARE WITH OTHERS

### Step 1: Send Install Instructions
Forward them this guide or:

```
https://github.com/ludreinsalvador/capex-reporting-app/docs/README_WINDOWS.md
```

### Step 2: Share Download Link
```
https://github.com/ludreinsalvador/capex-reporting-app/releases/download/v1.0.1/CAPEX_Reporting_Tool.exe
```

### Step 3: They Follow Steps 1-4 Above
Done! They have working app with automatic updates.

---

## 📞 SUPPORT & HELP

### Where to Find Answers

| Issue | Solution |
|-------|----------|
| App won't open | See "Security" section above |
| Update questions | Updates happen automatically, no action needed |
| Excel errors | Check Excel file format (.xlsx) |
| Features question | Open app, explore tabs for different tools |

### Report Issues

- Check app version (window title shows version)
- Check `%APPDATA%\CAPEX_Reporting_Tool\logs\` for error messages
- Contact developer with error message

---

## 📝 NOTES FOR ADVANCED USERS

### Command Line Launch

```bash
# From Command Prompt/PowerShell
cd C:\Program Files\CAPEX_Reporting_Tool
CAPEX_Reporting_Tool.exe

# Or with full path
C:\Program Files\CAPEX_Reporting_Tool\CAPEX_Reporting_Tool.exe
```

### Kill App from Command Prompt

```bash
taskkill /IM CAPEX_Reporting_Tool.exe /F
```

### Check Update Log

```bash
# Command Prompt
type %APPDATA%\CAPEX_Reporting_Tool\logs\update.log

# PowerShell
Get-Content "$env:APPDATA\CAPEX_Reporting_Tool\logs\update.log"
```

### View Application Data

```bash
# Command Prompt
explorer %APPDATA%\CAPEX_Reporting_Tool

# PowerShell
explorer "$env:APPDATA\CAPEX_Reporting_Tool"
```

### Uninstall Application

#### Option 1: Control Panel
1. Settings → Apps → Installed apps
2. Find "CAPEX Reporting Tool"
3. Click → **Uninstall**

#### Option 2: Manual
1. Delete `C:\Program Files\CAPEX_Reporting_Tool\` folder
2. Delete desktop shortcut (optional)
3. Delete shortcut in Start Menu (optional)

#### Option 3: Remove All Data
```bash
# Command Prompt (removes all app data and logs)
rmdir /s %APPDATA%\CAPEX_Reporting_Tool
```

---

## ✨ TIPS & TRICKS

- **Tip 1:** First launch slower than usual (unpacking files - normal!)
- **Tip 2:** Create desktop shortcut for quick access
- **Tip 3:** Keep Excel file and app in same location for easier browsing
- **Tip 4:** Check window title to see current version
- **Tip 5:** No need to update manually - app does it automatically!
- **Tip 6:** Can run from USB drive (no installation needed)
- **Tip 7:** Share exe link with teammates - they get same auto-update system!

---

**Version:** 1.0.1  
**Last Updated:** 2026-02-25  
**Windows Support:** Windows 7, 10, 11 (32-bit & 64-bit)

Questions? Contact developer or check GitHub repository.
