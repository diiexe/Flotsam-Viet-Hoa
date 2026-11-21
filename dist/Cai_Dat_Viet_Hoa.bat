@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
title CAI DAT VA GO BO VIET HOA FLOTSAM - By Diiexe

:: Tu dong yeu cau quyen Administrator neu chua co (can thiet cho C:\Program Files)
if /i not "%~1"=="--no-elevate" (
    net session >nul 2>&1
    if errorlevel 1 (
        echo [THONG BAO] Dang mo bang quyen Administrator...
        powershell -NoProfile -Command "Start-Process cmd.exe -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
        exit /b 0
    )
)

cd /d "%~dp0"

:MENU
set "PATCH_DIR="
if exist "%~dp0resources.assets" set "PATCH_DIR=%~dp0"
if exist "%~dp0build\resources.assets" set "PATCH_DIR=%~dp0build\"
if exist "%~dp0data\resources.assets" set "PATCH_DIR=%~dp0data\"
if exist "%~dp0..\dist\build\resources.assets" set "PATCH_DIR=%~dp0..\dist\build\"
if exist "%~dp0..\build\resources.assets" set "PATCH_DIR=%~dp0..\build\"

cls
echo ========================================================================
echo                 CAI DAT VA GO VIET HOA GAME: FLOTSAM
echo               Phien ban ho tro: v1.1.0f5  ^|  Ban dich: v1.0.0
echo            Thuc hien boi: Diiexe (https://github.com/diiexe)
echo   [MIEN PHI 100%%] Neu ban phai tra tien mua ban dich nay la bi lua dao
echo ========================================================================
echo.
echo   1. Cai dat ban Viet Hoa vao game
echo   2. Go bo Viet Hoa (Khoi phuc game goc sach)
echo   0. Thoat
echo.
echo ========================================================================
set "CHOICE="
set /p "CHOICE=Nhap lua chon cua ban (1, 2, 0) [Mac dinh la 1]: "

if not defined CHOICE set "CHOICE=1"
if "!CHOICE!"=="0" exit /b 0
if "!CHOICE!"=="1" goto CHON_CAI_DAT
if "!CHOICE!"=="2" goto CHON_GO_BO
goto MENU

:CHON_CAI_DAT
call :DETECT_GAME
if "!USER_CANCEL!"=="1" goto MENU
goto DO_INSTALL

:CHON_GO_BO
call :DETECT_GAME
if "!USER_CANCEL!"=="1" goto MENU
goto DO_UNINSTALL

:DETECT_GAME
set "USER_CANCEL=0"
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
    echo.
    echo ------------------------------------------------------------------------
    echo [OK] Da tu dong tim thay thu muc game tai:
    echo      !DETECTED_PATH!
    echo ------------------------------------------------------------------------
    echo - Nhan Enter de dung thu muc nay.
    echo - Hoac nhap 'M' / dan luon duong dan thu muc khac vao day.
    echo - Hoac nhap '0' de quay lai Menu.
    set "AUTO_CONFIRM="
    set /p "AUTO_CONFIRM=> "
    if not defined AUTO_CONFIRM (
        set "GAME_DATA=!DETECTED_PATH!"
        exit /b 0
    )
    if "!AUTO_CONFIRM!"=="0" (
        set "USER_CANCEL=1"
        exit /b 0
    )
    if /i not "!AUTO_CONFIRM!"=="M" (
        set "RAW_PATH=!AUTO_CONFIRM!"
        goto VALIDATE_RAW_PATH
    )
)

:MANUAL_INPUT
echo.
echo ========================================================================
echo Dan duong dan thu muc game Flotsam vao day roi nhan Enter:
echo (Vi du: C:\Program Files\Epic Games\Flotsam)
echo Hoac nhap '0' de quay lai Menu.
echo ========================================================================
set "RAW_PATH="
set /p "RAW_PATH=Duong dan: "

if not defined RAW_PATH goto MANUAL_INPUT
if "!RAW_PATH!"=="0" (
    set "USER_CANCEL=1"
    exit /b 0
)

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
    echo.
    echo ========================================================================
    echo [LOI] Khong tim thay Flotsam_Data\resources.assets tai:
    echo       !CLEAN_PATH!
    echo Vui long kiem tra lai duong dan thu muc game.
    echo ========================================================================
    echo.
    pause
    goto MANUAL_INPUT
)
exit /b 0

:DO_INSTALL
echo.
echo ========================================================================
echo DANG TIEN HANH CAI DAT VAO:
echo !GAME_DATA!
echo ========================================================================

del /f /q "!GAME_DATA!\.perm_test.tmp" >nul 2>&1
echo test > "!GAME_DATA!\.perm_test.tmp" 2>nul
if not exist "!GAME_DATA!\.perm_test.tmp" (
    echo.
    echo [LOI] Khong co quyen ghi vao thu muc game nay.
    echo Hay nhap chuot phai vao file Cai_Dat_Viet_Hoa.bat va chon "Run as Administrator".
    echo.
    pause
    goto MENU
)
del /f /q "!GAME_DATA!\.perm_test.tmp" >nul 2>&1

set "BACKUP_DIR=!GAME_DATA!\backup_goc"
if not exist "!BACKUP_DIR!" mkdir "!BACKUP_DIR!"

if not exist "!BACKUP_DIR!\resources.assets" (
    echo [1/3] Dang sao luu resources.assets goc sach...
    copy /y "!GAME_DATA!\resources.assets" "!BACKUP_DIR!\resources.assets" >nul
    if errorlevel 1 goto INSTALL_FAIL
) else (
    echo [1/3] Ban sao luu resources.assets goc da ton tai tu truoc.
)

if not exist "!BACKUP_DIR!\sharedassets0.assets" (
    echo [1/3] Dang sao luu sharedassets0.assets goc sach...
    copy /y "!GAME_DATA!\sharedassets0.assets" "!BACKUP_DIR!\sharedassets0.assets" >nul
    if errorlevel 1 goto INSTALL_FAIL
) else (
    echo [1/3] Ban sao luu sharedassets0.assets goc da ton tai tu truoc.
)

if not defined PATCH_DIR (
    if exist "%~dp0..\src\tools\build_patch.py" (
        echo.
        echo [*] Dang bien dich ban dich tu ma nguon src/ cho thu muc game da chon...
        python "%~dp0..\src\tools\build_patch.py" "!GAME_DATA!" --build-only
        if exist "%~dp0build\resources.assets" set "PATCH_DIR=%~dp0build\"
        if exist "%~dp0..\dist\build\resources.assets" set "PATCH_DIR=%~dp0..\dist\build\"
    )
)

if not defined PATCH_DIR (
    echo.
    echo ========================================================================
    echo [LOI] Khong tim thay file resources.assets va sharedassets0.assets.
    echo       Vui long giai nen day du goi cai dat truoc khi chay script.
    echo ========================================================================
    echo.
    pause
    goto MENU
)

echo [2/3] Dang chep du lieu Viet Hoa va Font SDF chuan net vao game...
copy /y "!PATCH_DIR!resources.assets" "!GAME_DATA!\resources.assets" >nul
if errorlevel 1 goto INSTALL_FAIL
copy /y "!PATCH_DIR!sharedassets0.assets" "!GAME_DATA!\sharedassets0.assets" >nul
if errorlevel 1 goto INSTALL_FAIL

echo [3/3] Dang kich hoat mac dinh Tieng Viet trong he thong...
reg add "HKCU\Software\Pajama Llama Games\Flotsam" /v "I2 Language_h3293684300" /t REG_BINARY /d 5469e1babf6e67205669e1bb877400 /f >nul 2>&1

echo.
echo ========================================================================
echo   [OK] CHUC MUNG - BAN VIET HOA FLOTSAM DA DUOC CAI DAT THANH CONG
echo ========================================================================
echo - Tac gia ban Viet Hoa ^& Bo cong cu: Diiexe (github.com/diiexe)
echo - Ban dich MIEN PHI 100%%. Neu ban phai mua bang tien la bi lua dao.
echo - 100%% Hoi thoai, nhiem vu, huong dan, cu dan deu hien thi Tieng Viet.
echo - Font chu Noto Sans Bold native net chu day dan, khong bi loi phong.
echo - File goc da duoc sao luu tai: !BACKUP_DIR!
echo - Bay gio ban co the khoi dong game va thuong thuc Tieng Viet.
echo ========================================================================
echo.
pause
exit /b 0

:INSTALL_FAIL
echo.
echo ========================================================================
echo [LOI] Khong the chep file vao thu muc game.
echo Hay dam bao game Flotsam dang TAT hoan toan truoc khi cai dat,
echo va chay file .bat bang quyen "Run as Administrator".
echo ========================================================================
echo.
pause
goto MENU

:DO_UNINSTALL
echo.
echo ========================================================================
echo DANG TIEN HANH GO BO VIET HOA VA KHOI PHUC BAN GOC:
echo !GAME_DATA!
echo ========================================================================

del /f /q "!GAME_DATA!\.perm_test.tmp" >nul 2>&1
echo test > "!GAME_DATA!\.perm_test.tmp" 2>nul
if not exist "!GAME_DATA!\.perm_test.tmp" (
    echo.
    echo [LOI] Khong co quyen ghi vao thu muc game nay.
    echo Hay nhap chuot phai vao file .bat va chon "Run as Administrator".
    echo.
    pause
    goto MENU
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
echo   Game da tro ve trang thai nguyen ban 100%% cua nha phat hanh.
echo ========================================================================
goto UNINSTALL_END

:UNINSTALL_NO_BACKUP
echo ========================================================================
echo [THONG BAO] Khong tim thay thu muc backup_goc tai thu muc game nay.
echo Co the game chua tung cai Viet Hoa hoac ban da khoi phuc truoc do.
echo Ban cung co the dung tinh nang Verify/Kiem tra cua Epic hoac Steam.
echo ========================================================================
goto UNINSTALL_END

:UNINSTALL_FAIL
echo.
echo ========================================================================
echo [LOI] Khong the ghi de file khi khoi phuc.
echo Hay dam bao game Flotsam dang TAT hoan toan truoc khi go cai dat.
echo ========================================================================
goto UNINSTALL_END

:UNINSTALL_END
echo.
pause
exit /b 0
