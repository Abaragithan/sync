@echo off
setlocal enabledelayedexpansion
echo ======================================
echo    SyncDeployer - Windows Build Script
echo ======================================

:: Navigate to project root
cd /d "%~dp0"

:: Check if Docker is installed
echo [CHECK] Verifying Docker...
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not installed. Install Docker Desktop first.
    pause
    exit /b 1
)

:: Check if Docker daemon is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker daemon is not running. Start Docker Desktop and try again.
    pause
    exit /b 1
)

:: Build Docker image if not found
echo [CHECK] Checking Docker image...
set IMAGE_NAME=sync-ansible:latest
for /f %%i in ('docker images -q %IMAGE_NAME% 2^>nul') do set IMAGE_ID=%%i
if "!IMAGE_ID!"=="" (
    echo Docker image not found. Building now...
    docker build -t %IMAGE_NAME% .
) else (
    echo Docker image found.
)

:: Check Python
echo [CHECK] Checking Python...
set PYTHON_CMD=
where py >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
) else (
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python
    ) else (
        echo Python not found. Install Python 3 first.
        pause
        exit /b 1
    )
)
echo Using Python: %PYTHON_CMD%

:: Create venv if not exists
if not exist ".venv" (
    echo [1/5] Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
) else (
    echo [1/5] Virtual environment found.
)

:: Activate venv
echo [2/5] Activating virtual environment...
call .venv\Scripts\activate.bat

:: Install dependencies
echo [3/5] Installing dependencies...
python -m pip install --upgrade pip -q
pip install -r requirements-gui.txt -q
pip install pyinstaller -q

:: Clean old build
echo [4/5] Cleaning old build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist SyncDeployer.spec del SyncDeployer.spec

:: Build the application
echo [5/5] Building application...
pyinstaller --name "SyncDeployer" ^
  --onefile ^
  --windowed ^
  --icon "app\assets\icon.ico" ^
  --paths "app" ^
  --add-data "app\assets;assets" ^
  --add-data "data;data" ^
  --add-data "requirements-docker.txt;." ^
  --add-data "ansible.cfg;." ^
  --hidden-import "core.inventory_manager" ^
  --hidden-import "json" ^
  app\main.py

:: Check if build succeeded
if not exist "dist\SyncDeployer.exe" (
    echo Build FAILED! Check errors above.
    pause
    exit /b 1
)

:: Create Desktop shortcut
echo Creating desktop shortcut...
set EXEC_PATH=%cd%\dist\SyncDeployer.exe
set ICON_PATH=%cd%\app\assets\icon.ico
set DESKTOP_SHORTCUT=%USERPROFILE%\Desktop\SyncDeployer.lnk

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP_SHORTCUT%'); $s.TargetPath = '%EXEC_PATH%'; $s.IconLocation = '%ICON_PATH%'; $s.Save()"

:: Create Start Menu shortcut
set STARTMENU_SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\SyncDeployer.lnk
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTMENU_SHORTCUT%'); $s.TargetPath = '%EXEC_PATH%'; $s.IconLocation = '%ICON_PATH%'; $s.Save()"

echo.
echo ======================================
echo  Build complete!
echo  Binary  : %cd%\dist\SyncDeployer.exe
echo  Desktop : %DESKTOP_SHORTCUT%
echo  Run with: dist\SyncDeployer.exe
echo ======================================
pause