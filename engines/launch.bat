@echo off
setlocal enabledelayedexpansion

:: 1. Запуск апдейтера (Проверьте, чтобы он сам НЕ запускал игру!)
call ./python/setup_python.bat autoupdater.py

set "VULKAN_APP="
set "FALLBACK_APP="

:: 2. Читаем названия файлов из конфига
< "engine.txt" (
    set /p "VULKAN_APP="
    set /p "FALLBACK_APP="
)

:: 3. Получаем абсолютный путь к родительской папке ОДИН раз
for %%I in ("%~dp0..") do set "PARENT_PATH=%%~fI"

:: 4. Теперь спокойно формируем аргументы с правильным путем
set "ARGS=+set fs_homepath "%PARENT_PATH%\baseq3\mods" +set fs_basepath "%PARENT_PATH%" +set fs_game "osp""

:: 5. Проверяем наличие Vulkan
set VULKAN_PRESENT=0
if exist "%SystemRoot%\System32\vulkan-1.dll" set VULKAN_PRESENT=1
if exist "%SystemRoot%\SysWOW64\vulkan-1.dll" set VULKAN_PRESENT=1

:: 6. Запуск строго один раз вне всяких циклов
if %VULKAN_PRESENT% equ 1 (
    echo Vulkan API detected. Launching Vulkan application...
    echo "" "%VULKAN_APP%" %ARGS%
    start "" "%VULKAN_APP%" %ARGS%
) else (
    echo Vulkan API not detected. Launching fallback application...
    echo "" "%FALLBACK_APP%" %ARGS%
    start "" "%FALLBACK_APP%" %ARGS%
)

endlocal
