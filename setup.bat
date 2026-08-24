@echo off
setlocal enabledelayedexpansion

set "APP_DIR=%~dp0study_tracker"
if "%APP_DIR:~-1%"=="\" set "APP_DIR=%APP_DIR:~0,-1%"
set "APP_SCRIPT=%APP_DIR%\app.py"

echo ============================================
echo   Study Tracker - Setup
echo ============================================
echo.

set "PYEXE="

for /f "delims=" %%P in ('where pythonw 2^>nul') do (
    if not defined PYEXE set "PYEXE=%%P"
)

if not defined PYEXE (
    for /f "delims=" %%P in ('where python 2^>nul') do (
        if not defined PYEXE (
            set "PYFOLDER=%%~dpP"
            if exist "!PYFOLDER!pythonw.exe" (
                set "PYEXE=!PYFOLDER!pythonw.exe"
            ) else (
                set "PYEXE=%%P"
            )
        )
    )
)

if not defined PYEXE (
    echo Python was not found on this computer.
    echo Please install it from https://www.python.org/downloads/
    echo and make sure to check "Add Python to PATH" during setup.
    echo Then run this file again.
    pause
    exit /b 1
)

echo Found Python at: !PYEXE!
echo App folder: %APP_DIR%
echo.

if not exist "%APP_SCRIPT%" (
    echo Could not find app.py inside "%APP_DIR%".
    echo Keep setup.bat in the same folder as the study_tracker folder.
    pause
    exit /b 1
)

set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\Study Tracker.lnk"

echo Creating desktop shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$s = (New-Object -ComObject WScript.Shell).CreateShortcut('%SHORTCUT%'); $s.TargetPath = '!PYEXE!'; $s.Arguments = '\"%APP_SCRIPT%\"'; $s.WorkingDirectory = '%APP_DIR%'; $s.Description = 'Study Tracker - track your study hours'; $s.Save()"

if exist "%SHORTCUT%" (
    echo Shortcut created on your Desktop: "Study Tracker"
) else (
    echo Could not create the shortcut automatically.
    echo You can still launch the app any time by double-clicking:
    echo %APP_SCRIPT%
)

echo.
echo Launching Study Tracker...
start "" "!PYEXE!" "%APP_SCRIPT%"

echo.
echo Setup complete. Next time, just use the "Study Tracker" icon on your Desktop.
pause
exit /b 0
