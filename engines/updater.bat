@echo off

setlocal enabledelayedexpansion


echo Updating configs

for /f "usebackq delims=" %%a in (".\pack_list\confs.txt") do (
    set "line=%%a"
    set "count=0"
    
    call :parse
    
    echo installing !list[3]!

    echo downloading...

    curl -L --retry 3 --progress-bar -o "!list[2]!!list[3]!" "!list[1]list[3]!"

    if not exist "!list[2]!!list[3]!" (
        echo [error] failed to download !list[3]!. contact creator: https://t.me/konstalker
        pause
        goto exit
    )

    echo installed.
)

set "OSP2_URL=https://konstalker.github.io/assets/zz-osp-pak8be.pk3"
set "OSP2_FILE=..\baseq3\mods\osp\zz-osp-pak8be.pk3"

echo Updating OSP2-BE
curl -L --retry 3 --progress-bar -o "%OSP2_FILE%" "%OSP2_URL%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: OSP2 download failed!
    pause
    exit /b %ERRORLEVEL%
)
