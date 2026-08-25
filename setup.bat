@echo off
setlocal enabledelayedexpansion

set "APP_DIR=%~dp0study_tracker"
if "%APP_DIR:~-1%"=="\" set "APP_DIR=%APP_DIR:~0,-1%"
set "APP_SCRIPT=%APP_DIR%\app.py"
set "SHORTCUT_PS1=%~dp0create_shortcut.ps1"
set "SHORTCUT_VBS=%~dp0create_shortcut.vbs"

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
    echo.
    pause
    exit /b 1
)

echo Found Python at: !PYEXE!
echo App folder: %APP_DIR%
echo.

if not exist "%APP_SCRIPT%" (
    echo Could not find app.py inside "%APP_DIR%".
    echo Keep setup.bat in the same folder as the study_tracker folder.
    echo.
    pause
    exit /b 1
)

echo Creating desktop shortcut...

set "SHORTCUT="
if exist "%SHORTCUT_PS1%" (
    for /f "usebackq delims=" %%L in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%SHORTCUT_PS1%" -Target "!PYEXE!" -AppScript "%APP_SCRIPT%" -WorkDir "%APP_DIR%" 2^>nul`) do (
        set "SHORTCUT=%%L"
    )
)

rem Fall back to VBScript where PowerShell is blocked or restricted.
if not defined SHORTCUT (
    if exist "%SHORTCUT_VBS%" (
        for /f "usebackq delims=" %%L in (`cscript //nologo //b "%SHORTCUT_VBS%" "!PYEXE!" "%APP_SCRIPT%" "%APP_DIR%" 2^>nul`) do (
            set "SHORTCUT=%%L"
        )
    )
)

if defined SHORTCUT (
    echo   Shortcut created: !SHORTCUT!
    set "HAVE_SHORTCUT=1"
) else (
    echo   Could not create the shortcut automatically.
    echo   You can still launch the app any time by double-clicking:
    echo   "%APP_SCRIPT%"
    echo.
    echo   To make your own shortcut: right-click that file, choose
    echo   "Send to" then "Desktop ^(create shortcut^)".
    set "HAVE_SHORTCUT="
)

echo.
echo Launching Study Tracker...
start "" "!PYEXE!" "%APP_SCRIPT%"

echo.
if defined HAVE_SHORTCUT (
    echo Setup complete. Next time, just use the "Study Tracker" icon on your Desktop.
) else (
    echo Setup finished, but without a Desktop shortcut - see the note above.
)
echo.
pause
exit /b 0
