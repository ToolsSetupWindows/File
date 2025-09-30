@echo off
mode con cols=1 lines=1
setlocal EnableExtensions

:: ===== CẤU HÌNH =====
set "URL=https://raw.githubusercontent.com/ToolsSetupWindows/File/main/Tools_Windows_Setup.bat"
set "FILENAME=Tools_Windows_Setup.bat"

:: Lấy đường dẫn Desktop chuẩn (hợp ngôn ngữ hệ thống)
for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "DESKTOP_DIR=%%D"

set "DEST_DIR=%DESKTOP_DIR%\Tools Windows Setup"
set "OUT_FILE=%DEST_DIR%\%FILENAME%"
set "FILE1=%TARGETDIR%\Tools_Windows_Setup.bat"

:: Tạo thư mục đích (nếu chưa có)
if not exist "%DEST_DIR%" mkdir "%DEST_DIR%" 2>nul
if exist "%FILE1%" (
  echo [!] Da co file cu: Tools_Windows_Setup.bat, se xoa va tai moi...
  del /f /q "%FILE1%"
)
:: ===== TẢI ẨN BẰNG PowerShell HttpClient (cửa sổ PS ẩn) =====
powershell -NoLogo -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass ^
  "$ErrorActionPreference='Stop';" ^
  "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;" ^
  "$u='%URL%'; $o='%OUT_FILE%';" ^
  "Add-Type -AssemblyName System.Net.Http;" ^
  "$cli = New-Object System.Net.Http.HttpClient;" ^
  "$res = $cli.GetAsync($u).Result;" ^
  "if(-not $res.IsSuccessStatusCode){ throw 'HTTP ' + [int]$res.StatusCode }" ^
  "[IO.File]::WriteAllBytes($o, $res.Content.ReadAsByteArrayAsync().Result);" ^
  "$cli.Dispose()"

:: Kiểm tra file tải về hợp lệ (>0 byte)
if not exist "%OUT_FILE%" exit /b 1
for %%A in ("%OUT_FILE%") do if %%~zA LEQ 0 (del /q "%OUT_FILE%" & exit /b 1)

:: Hoàn tất (không mở file)
exit /b 0
