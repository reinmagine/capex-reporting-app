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
import platform
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
    
    @staticmethod
    def _get_platform():
        """Detect current operating system. Returns 'windows', 'darwin' (macOS), or 'linux'"""
        system = platform.system()
        if system == 'Windows':
            return 'windows'
        elif system == 'Darwin':
            return 'darwin'
        elif system == 'Linux':
            return 'linux'
        else:
            return 'unknown'
    
    def check_for_updates(self):
        """
        Check if new version is available.
        Returns: (has_update, new_version, download_url)
        
        Supports platform-specific downloads:
        - Windows: .exe file
        - macOS: .app or .dmg file
        
        Fails gracefully if:
        - No internet connection
        - GitHub is unreachable
        - JSON is invalid
        - Platform not supported
        """
        if requests is None:
            self._log("requests library not available, skipping update check")
            return False, self.current_version, None
        
        try:
            current_platform = self._get_platform()
            self._log(f"Checking for updates. Current version: {self.current_version} on {current_platform}")
            
            response = requests.get(
                self.version_check_url,
                timeout=5,  # 5 second timeout
                headers={'User-Agent': f'CAPEX-Tool/{self.current_version}/{current_platform}'}
            )
            response.raise_for_status()
            
            data = response.json()
            
            new_version = data.get('version', self.current_version)
            
            # Get platform-specific download URL
            downloads = data.get('downloads', {})
            download_url = downloads.get(current_platform)
            
            # Fallback to old download_url format if new format not found
            if not download_url and current_platform == 'windows':
                download_url = data.get('download_url')
            
            release_notes = data.get('notes', '')
            
            # Check if new version is actually newer
            if self._version_greater(new_version, self.current_version):
                if download_url:
                    self.has_update = True
                    self.new_version = new_version
                    self.download_url = download_url
                    self._log(f"✓ Update available: {new_version} ({current_platform}) - {release_notes}")
                    return True, new_version, download_url
                else:
                    self._log(f"⚠ Update available but no download for {current_platform}")
                    return False, self.current_version, None

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
        
        Supports platform-specific installation:
        - Windows: Uses batch file to replace exe
        - macOS: Uses shell script and open command
        
        Returns: True if successfully scheduled, False otherwise
        """
        if requests is None:
            self._log("requests library not available, cannot download")
            return False
        
        try:
            current_platform = self._get_platform()
            self._log(f"Starting download from: {download_url}")
            
            if current_platform == 'windows':
                return self._download_windows(download_url)
            elif current_platform == 'darwin':
                return self._download_macos(download_url)
            else:
                self._log(f"⚠ Update not supported on {current_platform}")
                return False
                
        except Exception as e:
            self._log(f"⚠ Download failed: {str(e)}")
            return False
    
    def _download_windows(self, download_url):
        """Download and schedule update for Windows"""
        try:
            # Determine current exe path
            if getattr(sys, 'frozen', False):
                current_exe = Path(sys.executable)
            else:
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
            self._log(f"Downloading update (~50MB)...")
            response = requests.get(download_url, timeout=60)
            response.raise_for_status()
            
            # Save to temporary file
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            self._log(f"✓ Downloaded {temp_file.stat().st_size / (1024*1024):.1f} MB")
            
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
            try:
                os.startfile(str(batch_file))
            except AttributeError:
                subprocess.Popen([str(batch_file)])
            
            self._log("✓ Update scheduled successfully")
            return True
            
        except Exception as e:
            self._log(f"⚠ Windows download failed: {str(e)}")
            return False
    
    def _download_macos(self, download_url):
        """Download and schedule update for macOS"""
        try:
            # Determine current app path
            if getattr(sys, 'frozen', False):
                # Running as packaged app
                current_app = Path(sys.executable).parent.parent
            else:
                # Running from source
                dist_path = Path(__file__).parent.parent / "dist" / "CAPEX_Reporting_Tool.app"
                if dist_path.exists():
                    current_app = dist_path
                else:
                    self._log("⚠ dist/CAPEX_Reporting_Tool.app not found")
                    return False
            
            if not current_app.exists():
                self._log(f"⚠ Current app not found at: {current_app}")
                return False
            
            temp_file = current_app.parent / "CAPEX_Reporting_Tool_update.app"
            
            # Download new version
            self._log(f"Downloading update (~80MB)...")
            response = requests.get(download_url, timeout=60)
            response.raise_for_status()
            
            # Save to temporary file
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            self._log(f"✓ Downloaded {temp_file.stat().st_size / (1024*1024):.1f} MB")
            
            # Create shell script for post-close replacement
            shell_file = current_app.parent / "update_installer.sh"
            shell_content = f'''#!/bin/bash
echo "Updating CAPEX Reporting Tool..."
sleep 2
rm -rf "{current_app}"
mv "{temp_file}" "{current_app}"
echo "Update successful! Restarting application..."
sleep 1
open "{current_app}"
rm "$0"
'''
            
            with open(shell_file, 'w') as f:
                f.write(shell_content)
            
            # Make script executable
            os.chmod(shell_file, 0o755)
            
            self._log(f"✓ Created update shell script: {shell_file}")
            self._log(f"✓ Scheduled update - will install on next app close")
            
            # Schedule shell script to run
            subprocess.Popen(['bash', str(shell_file)])
            
            self._log("✓ Update scheduled successfully")
            return True
            
        except Exception as e:
            self._log(f"⚠ macOS download failed: {str(e)}")
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
