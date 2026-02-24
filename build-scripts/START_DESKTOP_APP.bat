@echo off
cd /d "%~dp0.."
echo Starting CAPEX Reporting Tool (Desktop Version)...
echo.
call venv\Scripts\activate.bat
echo.
python src\app_desktop.py
pause