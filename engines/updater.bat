@echo off
setlocal enabledelayedexpansion

call beupd.bat

set "vurl=https://github.com/konstalker/Q3V-1D/raw/refs/heads/autoupdater/baseq3/mods/osp/zzz-kon.pk3dir/version.txt"
set "temp_version=./temp_files/version.txt"
set "last_version=../baseq3/mods/osp/zzz-kon.pk3dir/version.txt"

echo ""
echo ""
echo ""
echo checking for Q3V#1D updates...

call mkdir "./temp_files"
curl -L --retry 3 --silent -o "!temp_version!" "!vurl!"

if not exist !temp_version! (
    echo [error] failed to download version information. contact creator: https://t.me/konstalker
    goto exit
)

if not exist !last_version! (
    call :download
    goto exit
)

:: Read downloaded version into variable
set "CURRENT_VER="
set /p CURRENT_VER=<"!temp_version!"

:: Read local version into variable
set "LOCAL_VER="
if exist "!last_version!" (
    set /p LOCAL_VER=<"!last_version!"
)

echo "local %LOCAL_VER%"
echo "current %CURRENT_VER%"

if "%CURRENT_VER%"=="%LOCAL_VER%" (
    echo no updates found.
    goto exit
) else (
    call :download
)


echo updated.
goto exit

:exit
rd /s /q "./temp_files"
exit /b 0

:download
call downloader.bat "./pack_list/confupd.txt" "f" ""
start downloader.bat "./pack_list/voidupd.txt" "a" ""
