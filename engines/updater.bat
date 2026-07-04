@echo off
call beupd.bat


set "vurl=https://github.com/konstalker/Q3V-1D/tree/main/baseq3/mods/osp/zzz-kon.pk3dir/version.txt"
set "temp_version=./temp_files/version.txt"
set "last_version=../baseq3/mods/osp/zzz-kon.pk3dir/version.txt"

echo checking for updates...
curl -L --retry 3 --silent -o "%TEMP_VERSION%" "%VERSION_URL%"

if not exist !temp_version! (
    echo [error] failed to download version information. contact creator: https://t.me/konstalker
    exit /b 1
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
exit /b 0

:download
call downloader.bat "./pack_list/confupd.txt" "f" ""
call downloader.bat "./pack_list/voidupd.txt" "a" ""
