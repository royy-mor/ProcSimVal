@echo off
setlocal

REM Define a local variable for the base directory.
set "base=C:\Users\roymo\Documents\ProcSimVal\RunResults\"

REM Check if report type (param1) is provided.
if "%~1"=="" (
echo Error: Report type not provided.
echo Usage: %~n0 report_type result_folder
goto :end
)

REM Check if result folder (param2) is provided.
if "%~2"=="" (
echo Error: Result folder not provided.
echo Usage: %~n0 report_type result_folder
goto :end
)

set "report_type=%~1"
set "result_folder=%~2"

REM Call vtune with the provided parameters.
"C:\Program Files (x86)\Intel\oneAPI\vtune\2025.0\bin64\vtune" -report %report_type% -result-dir="%base%%result_folder%"

:end
endlocal