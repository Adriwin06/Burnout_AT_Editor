@echo off
setlocal enabledelayedexpansion

:ask_source
set "source="
set /p "source=Enter folder containing extracted bundle folders: "
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
set /p "dest=Enter output folder for new .BIN bundles: "
if "%dest%"=="" (
    echo Error: No input provided.
    goto ask_dest
)
mkdir "%dest%" 2> nul

echo Scanning "%source%" for bundle folders...
for /D %%F in ("%source%\*_AT") do (
    if exist "%%F\.meta.yaml" (
        echo Creating bundle for "%%~nxF"...
        yap c "%%F" "%dest%\%%~nxF.BIN"
    ) else (
        echo Skipping "%%~nxF" (missing .meta.yaml)
    )
)

echo Done! New bundles saved to "%dest%"
pause