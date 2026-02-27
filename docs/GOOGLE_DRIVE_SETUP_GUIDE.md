# Google Drive Setup Guide for CAPEX Reporting Tool Distribution

## Folder Setup Instructions

### Step 1: Rename Your Folder (Recommended)

Current name: `[CAPEX Reporting Tool] App Download`

**Better name options:**
1. **CAPEX Reporting Tool - Downloads** (Recommended - clean and simple)
2. **CAPEX Reporting Tool - Installation Files** (Descriptive)
3. **CAPEX Tool - Latest Release** (Concise)

**How to rename:**
1. Right-click the folder
2. Select "Rename"
3. Enter new name
4. Press Enter

---

### Step 2: Prepare Files for Upload

Before uploading files, organize them:

**Create subfolders inside the main folder:**
```
CAPEX Reporting Tool - Downloads/
├── Windows/
│   └── CAPEX_Reporting_Tool.exe
├── macOS/
│   └── CAPEX_Reporting_Tool.app.zip
└── Release Notes/
    └── Version_History.txt (optional)
```

**Or keep it simple (flat structure):**
```
CAPEX Reporting Tool - Downloads/
├── CAPEX_Reporting_Tool.exe
├── CAPEX_Reporting_Tool.app.zip
└── README.txt
```

---

### Step 3: Upload Files to Google Drive

**For Windows .exe:**
1. Open your Google Drive folder
2. Right-click in empty space
3. Select "File upload" or drag-drop the file
4. Select `CAPEX_Reporting_Tool.exe`
5. Wait for upload to complete

**For macOS .app.zip:**
1. Same process
2. Select `CAPEX_Reporting_Tool.app.zip`
3. Wait for upload to complete

**File sizes:**
- Windows .exe: ~50-60 MB
- macOS .app.zip: ~70-80 MB

---

### Step 4: Set Sharing Permissions

**To share with your team:**

1. Click the "Share" button in top right
2. Enter email addresses or select "Anyone with the link"
3. Choose permission level:
   - **Viewer**: Can download files (RECOMMENDED for end users)
   - **Commenter**: Can download and comment
   - **Editor**: Can modify folder contents

**For end users, select:**
- Permission: **Viewer**
- Access: **Anyone with the link** (so they don't need Google account)

4. Copy the link provided
5. Share link with your users

---

### Step 5: Create a README File (Optional but Recommended)

Create a text file with installation instructions and save in the folder:

**File name:** `READ_ME_FIRST.txt`

**Content:**
```
CAPEX REPORTING TOOL - INSTALLATION

Thank you for downloading the CAPEX Reporting Tool!

WINDOWS USERS:
1. Download: CAPEX_Reporting_Tool.exe
2. Double-click to install
3. Follow installer instructions
4. Done!

MACOS USERS:
1. Download: CAPEX_Reporting_Tool.app.zip
2. Extract the file (automatic)
3. Right-click the app, select "Open"
4. Click "Open" on the security dialog
5. Done!

NEED HELP?
- See the User Manual for detailed instructions
- Contact IT Support if you have issues

VERSION: 1.0.1
Release Date: February 2026
```

---

## Maintenance: Updating Files

### When you have a new version:

**Step 1: Delete old files from Google Drive**
1. Navigate to the folder
2. Right-click old file (e.g., CAPEX_Reporting_Tool.exe)
3. Select "Delete"

**Step 2: Upload new version**
1. Click the Google Drive folder
2. Upload new .exe or .app.zip file
3. Wait for upload to complete

**Step 3: Notify users**
- Send email to your team with subject: "CAPEX Reporting Tool Updated"
- Include download link
- List what's new in the version

---

## Sharing the Download Link

### Option 1: Direct Link Sharing

1. Right-click on the folder
2. Select "Get link"
3. Make sure it says "Viewer" and "Anyone with the link"
4. Click "Copy link"
5. Send link to users

**Link format:**
```
https://drive.google.com/drive/folders/[FOLDER_ID]?usp=sharing
```

### Option 2: In Documents or Email

Tell users:
```
Download the CAPEX Reporting Tool from:
https://drive.google.com/drive/folders/1aLJgiEJ4oeukt7zj8FCgTjRBDrle1Pz2?usp=sharing

Right-click on the file and select "Download"
```

### Option 3: Create a Shortcut Document

Create a Google Doc with:
- Application name
- What it does
- Download link
- Basic installation steps
- Contact info for support

---

## User Instructions Summary

### What to tell your users (simple version):

"Click this link to access the application download folder:
https://drive.google.com/drive/folders/1aLJgiEJ4oeukt7zj8FCgTjRBDrle1Pz2?usp=sharing

Download the file for your operating system:
- Windows: CAPEX_Reporting_Tool.exe
- macOS: CAPEX_Reporting_Tool.app.zip

Then follow the installation instructions in the User Manual."

---

## Common Issues & Solutions

**Issue: "I can't download the file"**
- Solution: Right-click the file and select "Download" (not just single-click)

**Issue: "Storage quota exceeded"**
- Solution: You may need to upgrade Google Drive storage or delete old versions

**Issue: "File is too large"**
- Solution: Google Drive should handle 50-80 MB files fine. If issues persist, use compression tools

**Issue: "Users say the link doesn't work"**
- Solution: Verify permissions are set to "Viewer" with "Anyone with the link"

---

## Recommended Folder Structure for Organization

```
CAPEX Reporting Tool - Downloads/
├── Current Release/
│   ├── CAPEX_Reporting_Tool.exe (v1.0.1)
│   └── CAPEX_Reporting_Tool.app.zip (v1.0.1)
├── Previous Releases/ (Optional archive)
│   ├── CAPEX_Reporting_Tool.exe (v1.0.0)
│   └── CAPEX_Reporting_Tool.app.zip (v1.0.0)
├── Documentation/
│   ├── User_Manual.pdf
│   ├── Quick_Start_Guide.pdf
│   └── Installation_Instructions.txt
└── Release_Notes.txt
```

---

## Quick Checklist for Updates

When releasing a new version:

- [ ] Build new Windows .exe file
- [ ] Build new macOS .app.zip file
- [ ] Test both installers on your systems
- [ ] Update version number in documentation
- [ ] Create release notes describing changes
- [ ] Delete or archive old versions from Google Drive
- [ ] Upload new files to Google Drive
- [ ] Verify link works and files download properly
- [ ] Send notification email to users with download link
- [ ] Update README_FIRST.txt if any installation steps changed

---

## Additional Tips

**Backup your files:**
- Keep copies of installer files on your local computer
- Google Drive is good for distribution but shouldn't be your only backup

**Version numbering:**
- Use format: v1.0.0, v1.0.1, v1.1.0, v2.0.0
- Increment last number for bug fixes
- Increment middle for new features
- Increment first for major changes

**Track downloads:**
- Google Drive shows download counts (though limited)
- Create a shared spreadsheet to track who downloaded what version (optional)

**Security notes:**
- Don't share the folder link publicly (use for internal team only)
- Google Drive handles virus scanning automatically
- Ensure your .exe and .app files are digitally signed if possible

---

End of Google Drive Setup Guide

