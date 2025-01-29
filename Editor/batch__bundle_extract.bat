@echo off
setlocal enabledelayedexpansion

:ask_source
set "source="
set /p "source=Enter folder containing _AT.BIN files: "
if "%source%"=="" (
    echo Error: No input provided.
    goto ask_source
)
if not exist "%source%\" (
    echo Error: Folder "%source%" does not exist.
    goto ask_source
)

:ask_dest
set "dest="
set /p "dest=Enter destination folder for extraction: "
if "%dest%"=="" (
    echo Error: No input provided.
    goto ask_dest
)
mkdir "%dest%" 2> nul

echo Scanning "%source%" for _AT.BIN files...
for %%F in ("%source%\*_AT.BIN") do (
    set "filename=%%~nF"
    echo Extracting "%%~nxF"...
    mkdir "%dest%\!filename!" 2> nul
    yap e "%%F" "%dest%\!filename!"
)

echo Done! Extracted files saved to "%dest%"
pause