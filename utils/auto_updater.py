"""
Auto-Update Utility for CAPEX Reporting Tool
Checks for updates and downloads them silently in background
User gets automatic updates without any technical knowledge required
"""

import sys
import os
import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None


class AutoUpdater:
    """
    Handles automatic update checking and downloading.
    
    Features:
    - Silent background checking (doesn't interrupt user)
    - Graceful failure if internet unavailable
    - Version comparison (1.0.2 > 1.0.1)
    - Automatic installation on next app restart
    - Full audit trail in logs
    """
    
    def __init__(self, current_version, version_check_url):
        """
        Args:
            current_version: Current app version string (e.g., "1.0.1")
            version_check_url: URL to version.json file on GitHub
        """
        self.current_version = current_version
        self.version_check_url = version_check_url
        self.new_version = None
        self.download_url = None
        self.has_update = False
        self.log_file = Path(__file__).parent.parent / "logs" / "update.log"
        self._ensure_log_dir()
    
    def _ensure_log_dir(self):
        """Create logs directory if it doesn't exist"""
        log_dir = self.log_file.parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    def _log(self, message):
        """Write message to update log"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"
            with open(self.log_file, 'a') as f:
                f.write(log_message)
        except:
            pass  # Fail silently if logging fails
    
    @staticmethod
    def _parse_version(version_string):
        """Convert version string to tuple of integers for comparison"""
        try:
            return tuple(int(x) for x in version_string.split('.'))
        except:
            return (0, 0, 0)
    
    @staticmethod
    def _version_greater(v1, v2):
        """Compare two version strings. Returns True if v1 > v2"""
        try:
            v1_tuple = AutoUpdater._parse_version(v1)
            v2_tuple = AutoUpdater._parse_version(v2)
            return v1_tuple > v2_tuple
        except:
            return False
    
    def check_for_updates(self):
        """
        Check if new version is available.
        Returns: (has_update, new_version, download_url)
        
        Fails gracefully if:
        - No internet connection
        - GitHub is unreachable
        - JSON is invalid
        - Version check URL is wrong
        """
        if requests is None:
            self._log("requests library not available, skipping update check")
            return False, self.current_version, None
        
        try:
            self._log(f"Checking for updates. Current version: {self.current_version}")
            
            response = requests.get(
                self.version_check_url,
                timeout=5,  # 5 second timeout
                headers={'User-Agent': f'CAPEX-Tool/{self.current_version}'}
            )
            response.raise_for_status()
            
            data = response.json()
            
            new_version = data.get('version', self.current_version)
            download_url = data.get('download_url')
            release_notes = data.get('notes', '')
            
            # Check if new version is actually newer
            if self._version_greater(new_version, self.current_version):
                self.has_update = True
                self.new_version = new_version
                self.download_url = download_url
                self._log(f"✓ Update available: {new_version} (notes: {release_notes})")
                return True, new_version, download_url
            else:
                self._log(f"✓ Already on latest version ({self.current_version})")
                return False, self.current_version, None
                
        except requests.exceptions.Timeout:
            self._log("⚠ Update check timed out (no internet)")
            return False, self.current_version, None
        except requests.exceptions.ConnectionError:
            self._log("⚠ Could not connect to GitHub (offline)")
            return False, self.current_version, None
        except json.JSONDecodeError:
            self._log("⚠ Invalid JSON from version URL")
            return False, self.current_version, None
        except Exception as e:
            self._log(f"⚠ Update check failed: {str(e)}")
            return False, self.current_version, None
    
    def download_and_schedule_update(self, download_url):
        """
        Download new version and schedule installation for next restart.
        
        The process:
        1. Download .exe to temporary location
        2. Create batch file to replace exe after app closes
        3. Execute batch file when app exits
        4. Next restart uses new version
        
        Returns: True if successfully scheduled, False otherwise
        """
        if requests is None:
            self._log("requests library not available, cannot download")
            return False
        
        try:
            self._log(f"Starting download from: {download_url}")
            
            # Determine current exe path
            if getattr(sys, 'frozen', False):
                # Running as compiled exe
                current_exe = Path(sys.executable)
            else:
                # Running from Python script - try to find exe in dist folder
                dist_path = Path(__file__).parent.parent / "dist" / "CAPEX_Reporting_Tool.exe"
                if dist_path.exists():
                    current_exe = dist_path
                else:
                    self._log("⚠ Not running as exe and dist/CAPEX_Reporting_Tool.exe not found")
                    return False
            
            if not current_exe.exists():
                self._log(f"⚠ Current exe not found at: {current_exe}")
                return False
            
            temp_file = current_exe.parent / "CAPEX_Reporting_Tool_update.exe"
            
            # Download new version
            self._log(f"Downloading update (~10-50MB depending on dependencies)...")
            response = requests.get(download_url, timeout=60)
            response.raise_for_status()
            
            # Save to temporary file
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            self._log(f"✓ Downloaded {temp_file.stat().st_size} bytes")
            
            # Create batch file for post-close replacement
            batch_file = current_exe.parent / "update_installer.bat"
            batch_content = f'''@echo off
echo Updating CAPEX Reporting Tool...
timeout /t 2 /nobreak
move /Y "{temp_file}" "{current_exe}"
if exist "{temp_file}" (
    echo Update failed - file still locked
    pause
) else (
    echo Update successful! Restarting application...
    timeout /t 1 /nobreak
    start "" "{current_exe}"
)
del "%~f0"
'''
            
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            self._log(f"✓ Created update batch file: {batch_file}")
            self._log(f"✓ Scheduled update - will install on next app close")
            
            # Schedule batch to run when Python process exits
            # Using subprocess.Popen with shell=False and detach_process
            try:
                os.startfile(str(batch_file))
            except AttributeError:
                # Non-Windows system
                subprocess.Popen([str(batch_file)])
            
            self._log("✓ Update scheduled successfully")
            return True
            
        except requests.exceptions.Timeout:
            self._log("⚠ Download timed out")
            return False
        except requests.exceptions.ConnectionError:
            self._log("⚠ Connection lost during download")
            return False
        except FileNotFoundError as e:
            self._log(f"⚠ File not found: {e}")
            return False
        except Exception as e:
            self._log(f"⚠ Download failed: {str(e)}")
            return False
    
    def check_and_update_in_background(self, callback=None):
        """
        Check for updates in background thread.
        Does not block the UI.
        
        Args:
            callback: Optional function to call with (has_update, new_version)
        """
        def _check():
            try:
                has_update, new_version, download_url = self.check_for_updates()
                
                if has_update and download_url:
                    self._log(f"Downloading update {new_version}...")
                    self.download_and_schedule_update(download_url)
                
                if callback:
                    callback(has_update, new_version)
                    
            except Exception as e:
                self._log(f"Background update check failed: {e}")
                if callback:
                    callback(False, self.current_version)
        
        # Run check in background thread so it doesn't block app startup
        thread = threading.Thread(target=_check, daemon=True)
        thread.start()
    
    def get_update_info(self):
        """Return dict with current update status"""
        return {
            'current_version': self.current_version,
            'new_version': self.new_version,
            'has_update': self.has_update,
            'version_check_url': self.version_check_url,
            'checked_at': datetime.now().isoformat()
        }


def check_updates_on_startup(current_version, version_check_url):
    """
    Convenience function - simply check for updates on app startup.
    
    Usage:
        from utils.auto_updater import check_updates_on_startup
        check_updates_on_startup("1.0.1", "https://raw.githubusercontent.com/...")
    
    This will:
    1. Check for updates in background (won't block app)
    2. Download if available
    3. Install on next app restart
    4. Log all activity to logs/update.log
    """
    updater = AutoUpdater(current_version, version_check_url)
    updater.check_and_update_in_background()
    return updater
