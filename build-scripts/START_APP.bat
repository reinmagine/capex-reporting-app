@echo off
cd /d "%~dp0.."
echo Starting CAPEX Reporting Tool...
echo.
call venv\Scripts\activate.bat
echo.
python src\app_desktop.py
pause