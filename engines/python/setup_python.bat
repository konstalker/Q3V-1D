@echo off
setlocal enabledelayedexpansion

set "PYPY_URL=https://downloads.python.org/pypy/pypy3.11-v7.3.23-win64.zip"
set "BASE_DIR=%~dp0"
set "ZIP_FILE=%BASE_DIR%pypy-portable.zip"
set "EXTRACT_DIR=%BASE_DIR%pypy-portable"
set "PYPY_FOLDER=%EXTRACT_DIR%\pypy3.11-v7.3.23-win64"

:: 1. Проверяем системный Python (ИГНОРИРУЯ пустышки от Windows Store)
set "PYTHON_EXEC="
for /f "delims=" %%I in ('where python 2^>nul') do (
    echo "%%I" | find /i "WindowsApps" >nul
    if errorlevel 1 (
        if not defined PYTHON_EXEC set "PYTHON_EXEC="%%I""
    )
)
if defined PYTHON_EXEC goto :run_python

for /f "delims=" %%I in ('where python3 2^>nul') do (
    echo "%%I" | find /i "WindowsApps" >nul
    if errorlevel 1 (
        if not defined PYTHON_EXEC set "PYTHON_EXEC="%%I""
    )
)
if defined PYTHON_EXEC goto :run_python

:: 2. Если системного Python нет, ищем портативную версию
if exist "%PYPY_FOLDER%\python.exe" (
    set "PYTHON_EXEC="%PYPY_FOLDER%\python.exe""
    goto :run_python
)
if exist "%PYPY_FOLDER%\pypy3.exe" (
    set "PYTHON_EXEC="%PYPY_FOLDER%\pypy3.exe""
    goto :run_python
)

:: 3. Если портативной версии нет — скачиваем
if not exist "%ZIP_FILE%" (
    echo Скачивание PyPy...
    curl -L -o "%ZIP_FILE%" "%PYPY_URL%"
    if %ERRORLEVEL% neq 0 (
        echo Ошибка: Не удалось скачать архив.
        exit /b 1
    )
)

:: 4. Распаковываем
if not exist "%EXTRACT_DIR%" (
    echo Распаковка архива...
    mkdir "%EXTRACT_DIR%"
    powershell -NoProfile -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%EXTRACT_DIR%' -Force"
)

:: 5. Проверяем после распаковки
if exist "%PYPY_FOLDER%\python.exe" (
    set "PYTHON_EXEC="%PYPY_FOLDER%\python.exe""
) else if exist "%PYPY_FOLDER%\pypy3.exe" (
    set "PYTHON_EXEC="%PYPY_FOLDER%\pypy3.exe""
) else (
    echo Ошибка: Исполняемый файл не найден.
    exit /b 1
)

:run_python
:: 6. Запускаем интерпретатор с передачей всех аргументов (%*)
%PYTHON_EXEC% %*