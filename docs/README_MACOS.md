# macOS Installation & Usage Guide

Complete guide for macOS users to download, install, and use CAPEX Reporting Tool

---

## 📥 STEP 1: Download Application

### Option A: From GitHub Releases (Recommended)

1. Visit: https://github.com/ludreinsalvador/capex-reporting-app/releases
2. Find the latest release
3. Download `CAPEX_Reporting_Tool.app.zip` (~80 MB)
4. Wait for download to complete

### Option B: Direct Download Link

```
https://github.com/ludreinsalvador/capex-reporting-app/releases/download/v1.0.1/CAPEX_Reporting_Tool.app.zip
```

---

## 📦 STEP 2: Extract Application

### Automatically (Recommended)

1. Open **Finder**
2. Go to **Downloads** folder
3. Double-click `CAPEX_Reporting_Tool.app.zip`
4. macOS automatically extracts → `CAPEX_Reporting_Tool.app`

### Manually

```bash
# In Terminal
cd ~/Downloads
unzip CAPEX_Reporting_Tool.app.zip
```

---

## ✅ STEP 3: Run Application

### First Time Launch

**Important: macOS will show a security warning**

1. Open **Finder**
2. Navigate to **Downloads** folder
3. Right-click on `CAPEX_Reporting_Tool.app`
4. Select **"Open"** (not just double-click)
5. Click **"Open"** button in security dialog
6. App launches successfully

### Subsequent Launches

Double-click `CAPEX_Reporting_Tool.app` normally - no security dialog needed

---

## 🔓 TROUBLESHOOTING: "App Can't Be Opened"

### Error Message:
> "CAPEX_Reporting_Tool cannot be opened because Apple cannot check it for malicious software"

### Solution:

#### Method 1: Command Line (Fastest)
```bash
# Copy this entire line and paste into Terminal, press Enter
xattr -d com.apple.quarantine ~/Downloads/CAPEX_Reporting_Tool.app
```

#### Method 2: System Preferences
1. Try to open the app (security dialog appears)
2. Go to **System Preferences** → **Security & Privacy**
3. Click **General** tab
4. Find message about CAPEX_Reporting_Tool
5. Click **"Open Anyway"**
6. Click **"Open"** in confirmation dialog

#### Method 3: Bypass Gatekeeper
```bash
# Copy and paste entire line into Terminal
sudo xattrattr -d -r com.apple.quarantine ~/Downloads/CAPEX_Reporting_Tool.app
# Enter your Mac password when prompted
```

After any method, app will open normally!

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

---

## 📂 WHERE FILES GO

### Application Location
```
~/Downloads/CAPEX_Reporting_Tool.app
```

Or move to Applications:
```bash
# Drag CAPEX_Reporting_Tool.app to Applications folder
# OR use Terminal:
mv ~/Downloads/CAPEX_Reporting_Tool.app ~/Applications/
```

### Logs & Updates
```
~/Downloads/CAPEX_Reporting_Tool.app/Contents/Resources/logs/
```

Automatically created, no action needed from you.

---

## 🆘 COMMON ISSUES

### Issue: App Won't Open
**Solution:** Follow security dialog troubleshooting steps above

### Issue: "Python not found" Error
**Solution:** Shouldn't happen with bundled app. If it does:
1. Re-download app
2. Delete old version
3. Extract and run new version

### Issue: Excel Files Not Found
**Solution:**
1. Make sure Excel files are in a folder you can access
2. Use file dialog to navigate
3. Select correct file

### Issue: Very Slow on First Launch
**Solution:**
- First launch extracts internal files (~2-3 min)
- Subsequent launches are fast (<2 sec)
- This is normal!

### Issue: Want to Move App to Applications
```bash
# Option 1: Drag in Finder (easiest)
# Drag CAPEX_Reporting_Tool.app to Applications folder

# Option 2: Terminal
mv ~/Downloads/CAPEX_Reporting_Tool.app ~/Applications/
```

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
- **Network access:** Only to check for updates (can work offline)
- **No admin rights needed**
- **No system-wide changes**

---

## 💾 CREATE SHORTCUT (Optional)

### Add to Dock (Easiest)
1. Open **Finder**
2. Go to folder with app
3. Drag `CAPEX_Reporting_Tool.app` onto **Dock**
4. Shortcut appears in Dock!

### Create Desktop Shortcut
```bash
# Create alias on Desktop
ln -s ~/Applications/CAPEX_Reporting_Tool.app ~/Desktop/CAPEX_Reporting_Tool.app
```

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
- Check `logs/update.log` for error messages
- Contact developer with error message

---

## 📝 NOTES FOR ADVANCED USERS

### Terminal Launch (Optional)

```bash
open ~/Applications/CAPEX_Reporting_Tool.app
```

### Kill App from Terminal

```bash
pkill -f "CAPEX_Reporting_Tool"
```

### Check Update Log

```bash
cat ~/Applications/CAPEX_Reporting_Tool.app/Contents/Resources/logs/update.log
```

### View App Contents

```bash
open ~/Applications/CAPEX_Reporting_Tool.app/Contents/Resources/
```

---

## ✨ TIPS & TRICKS

- **Tip 1:** First launch slower than usual (normal!)
- **Tip 2:** Add to Dock for quick access
- **Tip 3:** Keep Excel file and app in same location for easier browsing
- **Tip 4:** Check window title to see current version
- **Tip 5:** No need to update manually - app does it automatically!

---

**Version:** 1.0.1  
**Last Updated:** 2026-02-25  
**macOS Support:** 10.13+ (High Sierra and newer)

Questions? Contact developer or check GitHub repository.
