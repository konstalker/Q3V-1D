 @echo off
setlocal enabledelayedexpansion
call ./python/setup_python.bat autoupdater.py

set "VULKAN_APP="
set "FALLBACK_APP="

< "engine.txt" (
    set /p "VULKAN_APP="
    set /p "FALLBACK_APP="
)

set VULKAN_PRESENT=0
set "ARGS=+set fs_homepath "%%~fI\baseq3\mods" +set fs_basepath "%%~fI" +set fs_game "osp""

if exist "%SystemRoot%\System32\vulkan-1.dll" set VULKAN_PRESENT=1
if exist "%SystemRoot%\SysWOW64\vulkan-1.dll" set VULKAN_PRESENT=1

for %%I in ("%~dp0..") do (
    if %VULKAN_PRESENT% equ 1 (
        echo Vulkan API detected. Launching Vulkan application...
        echo "" %VULKAN_APP% %ARGS%
        start "" %VULKAN_APP% %ARGS%
        echo launched
        goto :end
    ) else (
        echo Vulkan API not detected. Launching fallback application...
        echo "" %FALLBACK_APP% %ARGS%
        start "" %FALLBACK_APP% %ARGS%
        echo launched
        goto :end
    )
)

:end
endlocal
exit /b 0
