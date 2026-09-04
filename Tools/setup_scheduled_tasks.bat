@echo off
REM Project Volusia — Windows Task Scheduler Setup
REM Creates a scheduled task to run refresh_v2.py twice daily
REM Run this script as Administrator

set SCRIPT_DIR=%~dp0
set PYTHON=python
set REFRESH_CMD=%PYTHON% %SCRIPT_DIR%volusia_data\refresh_v2.py

echo Creating Project Volusia refresh task...
schtasks /create /tn "ProjectVolusia_Refresh" /tr "%REFRESH_CMD%" /sc daily /st 06:00 /f
schtasks /create /tn "ProjectVolusia_Refresh_PM" /tr "%REFRESH_CMD%" /sc daily /st 18:00 /f

echo.
echo Tasks created:
schtasks /query /tn "ProjectVolusia_Refresh" /v /fo LIST 2>nul | findstr "TaskName Status Next Run"
schtasks /query /tn "ProjectVolusia_Refresh_PM" /v /fo LIST 2>nul | findstr "TaskName Status Next Run"
echo.
echo Done. Tasks will run refresh_v2.py at 06:00 and 18:00 daily.
pause
