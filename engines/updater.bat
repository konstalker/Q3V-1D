@echo off

set "OSP2_URL=https://konstalker.github.io/assets/zz-osp-pak8be.pk3"
set "OSP2_FILE=..\baseq3\mods\osp\zz-osp-pak8be.pk3"

curl -L --retry 3 --progress-bar -o "%OSP2_FILE%" "%OSP2_URL%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: OSP2 download failed!
    pause
    exit /b %ERRORLEVEL%
)
