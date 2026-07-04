@echo off
setlocal enabledelayedexpansion

call beupd.bat

set "vurl=https://github.com/konstalker/Q3V-1D/tree/autoupdater/baseq3/mods/osp/zzz-kon.pk3dir/version.txt"
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

if !last_version! == !temp_version! (
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
call downloader.bat "./pack_list/voidupd.txt" "a" ""
