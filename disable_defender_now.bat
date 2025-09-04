@echo off
:: Tắt tạm thời Windows Defender cho Windows 7, 10, 11 (không cần khởi động lại)
:: Yêu cầu quyền Administrator

:: Kiểm tra quyền admin
openfiles >nul 2>&1
if not "%errorlevel%"=="0" (
    echo Vui long chay file nay voi quyen Administrator!
    pause
    exit /b
)

echo Dang tat tam thoi dich vu Windows Defender...
echo Se tu dong bat Windows Defender khi khoi dong lai may tinh.
:: Tắt dịch vụ Windows Defender
sc stop WinDefend >nul 2>&1
if not errorlevel 1 (
    echo [Thanh cong] Da tat dich vu Windows Defender
) else (
    echo [That bai] Khong the tat dich vu Windows Defender (co the da bi tat hoac bi khoa boi he thong)
)

:: Tắt dịch vụ Sense (Windows Security Center, chi co tren Win 10/11)
sc stop Sense >nul 2>&1
if not errorlevel 1 (
    echo [Thanh cong] Da tat dich vu Windows Security Center (Sense)
) else (
    echo [That bai] Khong the tat dich vu Security Center (Sense) (khong ton tai hoac bi khoa)
)

echo.
echo Luu y: Mot so he dieu hanh co the tu dong bat lai dich vu nay!
pause
