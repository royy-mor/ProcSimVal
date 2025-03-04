@echo off
setlocal enabledelayedexpansion

REM Set the base directory from the first argument; if none is provided, use a default directory.
if "%~1"=="" (
    set "basedir=C:\Users\roymo\Documents\ProcSimVal\RunResults"
) else (
    set "basedir=%~1"
)

REM Define the folder name prefix.
set "prefix=505_"

REM Initialize the counter to 0.
set count=0

:findAvailable
if exist "%basedir%\%prefix%%count%" (
    set /a count+=1
    goto findAvailable
)

REM Create the new folder with the next available count.
mkdir "%basedir%\%prefix%%count%"
echo Created folder: "%basedir%\%prefix%%count%"

"C:\Program Files (x86)\Intel\oneAPI\vtune\2025.0\bin64\vtune" -target-system ssh:cc@procsimval-chameleon -target-install-dir=/tmp/vtune_profiler_2025.0.1.629235 -collect uarch-exploration -result-dir="%basedir%\%prefix%%count%" --app-working-dir=/home/cc/bench_exe/505.mcf_r -- /home/cc/bench_exe/505.mcf_r/505.mcf_r.sh

endlocal


