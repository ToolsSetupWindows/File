@echo off
title Cai dat WinToHDD
FOR %%i IN ("WinToHDD*.exe") DO Set FileName="%%i"
%FileName% /SILENT
endlocal
exit /b
