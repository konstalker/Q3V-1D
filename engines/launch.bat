@echo off
setlocal enabledelayedexpansion

call ./engines/python/setup_python.bat upd.py

set VULKAN_APP="oDFe.vk.x64.exe"
set FALLBACK_APP="oDFe.x64.exe"

set ARGS=+set fs_homepath "%%~fI\baseq3\mods" +set fs_basepath "%%~fI" +set fs_game "osp"

set VULKAN_PRESENT=0
if exist "%SystemRoot%\System32\vulkan-1.dll" set VULKAN_PRESENT=1
if exist "%SystemRoot%\SysWOW64\vulkan-1.dll" set VULKAN_PRESENT=1

for %%I in ("%~dp0..") do (
    if %VULKAN_PRESENT% equ 1 (
        echo Vulkan API detected. Launching Vulkan application...
        echo "" %VULKAN_APP% %ARGS%
        start "" %VULKAN_APP% %ARGS%
    ) else (
        echo Vulkan API not detected. Launching fallback application...
        echo "" %FALLBACK_APP% %ARGS%
        start "" %FALLBACK_APP% %ARGS%
    )
)

endlocal