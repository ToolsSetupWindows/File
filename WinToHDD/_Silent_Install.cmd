if exist "C:\Program Files\Hasleo\WinToHDD\bin\WinToHDD.exe" (
    echo Da ton tai WinToHDD. Bo qua cai dat.
    endlocal
    exit /b 0
)

:: --- Tìm file cài đặt khớp WinToHDD*.exe ---
set "FileName="
for %%i in ("WinToHDD*.exe") do (
    set "FileName=%%~fi"
    goto :run
)

echo Khong tim thay file cai dat: WinToHDD*.exe
endlocal
exit /b 1

:run
"%FileName%" /SILENT
endlocal
exit /b
