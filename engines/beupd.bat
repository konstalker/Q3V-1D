@echo off
setlocal

:: Define URLs and paths
set "OSP2_URL=https://konstalker.github.io/assets/zz-osp-pak8be.pk3"
set "OSP2_FILE=..\baseq3\mods\osp\zz-osp-pak8be.pk3"
set "VERSION_URL=https://konstalker.github.io/assets/version.txt"
set "CHANGELOG_URL=https://konstalker.github.io/assets/version_changelog.txt"
set "LAST_VERSION_FILE=osp2_last_version.txt"
set "TEMP_VERSION=%TEMP%\osp2_version.txt"
set "TEMP_CHANGELOG=%TEMP%\osp2_changelog.txt"

echo Download OSP2-BE...

:: Download version and changelog
echo Downloading version information...
curl -L --retry 3 --silent -o "%TEMP_VERSION%" "%VERSION_URL%"
curl -L --retry 3 --silent -o "%TEMP_CHANGELOG%" "%CHANGELOG_URL%"

:: Read downloaded version into variable
set "CURRENT_VER="
if exist "%TEMP_VERSION%" (
    set /p CURRENT_VER=<"%TEMP_VERSION%"
)

:: Read local version into variable
set "LOCAL_VER="
if exist "%LAST_VERSION_FILE%" (
    set /p LOCAL_VER=<"%LAST_VERSION_FILE%"
)

:: Display version and changelog
if defined CURRENT_VER (
    echo.
    echo Current version: %CURRENT_VER%
    echo.
)

if exist "%TEMP_CHANGELOG%" (
    echo Changelog:
    type "%TEMP_CHANGELOG%"
    echo.
)

:: Compare versions
if not "%CURRENT_VER%"=="%LOCAL_VER%" (
    echo Downloading OSP2 package...
    
    :: Ensure the target directory exists before downloading
    if not exist "..\baseq3\mods\osp\" (
        mkdir "..\baseq3\mods\osp\" 2>nul
    )

    curl -L --retry 3 --progress-bar -o "%OSP2_FILE%" "%OSP2_URL%"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: OSP2 download failed!
        del "%TEMP_VERSION%" 2>nul
        del "%TEMP_CHANGELOG%" 2>nul
        pause
        exit /b %ERRORLEVEL%
    )
    
    :: Save the new version to the local file
    echo %CURRENT_VER%>"%LAST_VERSION_FILE%"
    echo.
    echo OSP2 updated successfully!
) else (
    echo.
    echo You already have the latest version. No update needed.
)

:: Clean up temporary files
del "%TEMP_VERSION%" 2>nul
del "%TEMP_CHANGELOG%" 2>nul

exit /b 0