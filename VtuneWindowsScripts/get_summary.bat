@echo off
setlocal

if "%~1"=="" (
    echo Error: Report type not provided.
    echo Usage: %~n0 report_type result_folder
    goto :end
)

:: Call PowerShell to execute Select-String
powershell -Command "& { .\get_report.bat summary '%~1' | Select-String 'Memory Bound', 'Front-End Bound', 'Core Bound', 'Bad Speculation', 'Retiring', 'Elapsed Time', 'CPI Rate', 'Average CPU Freq' }"

:end
endlocal
