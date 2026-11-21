@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
title GO CAI DAT VIET HOA FLOTSAM - By Diiexe

if /i not "%~1"=="--no-elevate" (
    net session >nul 2>&1
    if errorlevel 1 (
        echo [THONG BAO] Dang mo bang quyen Administrator...
        powershell -NoProfile -Command "Start-Process cmd.exe -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
        exit /b 0
    )
)

cd /d "%~dp0"

echo ========================================================================
echo                 GO CAI DAT VIET HOA GAME: FLOTSAM
echo                     Khoi phuc game ve ban goc sach
echo            Thuc hien boi: Diiexe (https://github.com/diiexe)
echo   [MIEN PHI 100%%] Neu ban phai tra tien mua ban dich nay la bi lua dao
echo ========================================================================
echo.

set "GAME_DATA="
set "DETECTED_PATH="

for %%P in (
    "C:\Program Files\Epic Games\Flotsam"
    "D:\Epic Games\Flotsam"
    "E:\Epic Games\Flotsam"
    "D:\Epic\Flotsam"
    "C:\Program Files (x86)\Steam\steamapps\common\Flotsam"
    "D:\SteamLibrary\steamapps\common\Flotsam"
    "E:\SteamLibrary\steamapps\common\Flotsam"
    "%~dp0.."
    "%~dp0"
) do (
    if not defined DETECTED_PATH (
        if exist "%%~P\Flotsam_Data\resources.assets" set "DETECTED_PATH=%%~P\Flotsam_Data"
    )
)

if defined DETECTED_PATH (
    echo [OK] Da tim thay game tai: !DETECTED_PATH!
    echo - Nhan Enter de khoi phuc ngay.
    echo - Hoac nhap 'M' / dan luon duong dan thu muc khac vao day:
    set "AUTO_CONFIRM="
    set /p "AUTO_CONFIRM=> "
    if not defined AUTO_CONFIRM (
        set "GAME_DATA=!DETECTED_PATH!"
        goto DO_UNINSTALL
    )
    if /i not "!AUTO_CONFIRM!"=="M" (
        set "RAW_PATH=!AUTO_CONFIRM!"
        goto VALIDATE_RAW_PATH
    )
)

:MANUAL_INPUT
echo.
echo Dan duong dan thu muc game Flotsam vao day roi nhan Enter:
echo (Vi du: C:\Program Files\Epic Games\Flotsam)
set "RAW_PATH="
set /p "RAW_PATH=Duong dan: "
if not defined RAW_PATH goto MANUAL_INPUT

:VALIDATE_RAW_PATH
set "CLEAN_PATH="
set "PARENT_DIR="
for /f "tokens=* delims=" %%A in ("!RAW_PATH!") do (
    set "CLEAN_PATH=%%~A"
    set "PARENT_DIR=%%~dpA"
)
if not defined CLEAN_PATH goto MANUAL_INPUT
if "!CLEAN_PATH:~-1!"=="\" set "CLEAN_PATH=!CLEAN_PATH:~0,-1!"
if defined PARENT_DIR (
    if "!PARENT_DIR:~-1!"=="\" set "PARENT_DIR=!PARENT_DIR:~0,-1!"
)

set "GAME_DATA="
if exist "!CLEAN_PATH!\Flotsam_Data\resources.assets" set "GAME_DATA=!CLEAN_PATH!\Flotsam_Data"
if not defined GAME_DATA (
    if exist "!CLEAN_PATH!\resources.assets" set "GAME_DATA=!CLEAN_PATH!"
)
if not defined GAME_DATA (
    if defined PARENT_DIR (
        if exist "!PARENT_DIR!\Flotsam_Data\resources.assets" set "GAME_DATA=!PARENT_DIR!\Flotsam_Data"
    )
)

if not defined GAME_DATA (
    echo [LOI] Khong tim thay thu muc Flotsam hop le tai: !CLEAN_PATH!
    pause
    goto MANUAL_INPUT
)

:DO_UNINSTALL
echo.
echo Dang khoi phuc game tai: !GAME_DATA!

del /f /q "!GAME_DATA!\.perm_test.tmp" >nul 2>&1
echo test > "!GAME_DATA!\.perm_test.tmp" 2>nul
if not exist "!GAME_DATA!\.perm_test.tmp" (
    echo [LOI] Khong co quyen ghi vao thu muc game. Hay chay bang Run as Administrator.
    pause
    exit /b 1
)
del /f /q "!GAME_DATA!\.perm_test.tmp" >nul 2>&1

set "BACKUP_DIR=!GAME_DATA!\backup_goc"
set "RESTORED=0"

if exist "!BACKUP_DIR!\resources.assets" (
    copy /y "!BACKUP_DIR!\resources.assets" "!GAME_DATA!\resources.assets" >nul
    if errorlevel 1 goto UNINSTALL_FAIL
    echo - Da khoi phuc resources.assets goc sach.
    set "RESTORED=1"
)

if exist "!BACKUP_DIR!\sharedassets0.assets" (
    copy /y "!BACKUP_DIR!\sharedassets0.assets" "!GAME_DATA!\sharedassets0.assets" >nul
    if errorlevel 1 goto UNINSTALL_FAIL
    echo - Da khoi phuc sharedassets0.assets goc sach.
    set "RESTORED=1"
)

reg delete "HKCU\Software\Pajama Llama Games\Flotsam" /v "I2 Language_h3293684300" /f >nul 2>&1

echo.
if "!RESTORED!"=="1" goto UNINSTALL_SUCCESS
goto UNINSTALL_NO_BACKUP

:UNINSTALL_SUCCESS
echo ========================================================================
echo   [OK] DA GO BO VIET HOA THANH CONG
echo   Game da tro ve nguyen ban goc 100%% cua nha san xuat.
echo ========================================================================
goto UNINSTALL_END

:UNINSTALL_NO_BACKUP
echo ========================================================================
echo [THONG BAO] Khong tim thay thu muc backup_goc tai thu muc game nay.
echo ========================================================================
goto UNINSTALL_END

:UNINSTALL_FAIL
echo ========================================================================
echo [LOI] Khong the ghi de file. Hay dam bao game Flotsam dang TAT hoan toan.
echo ========================================================================
goto UNINSTALL_END

:UNINSTALL_END
echo.
pause
exit /b 0
