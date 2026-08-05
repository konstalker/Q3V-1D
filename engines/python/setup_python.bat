@echo off
setlocal enabledelayedexpansion

:: === Базовые пути ===
set "BASE_DIR=%~dp0"
set "PY_ROOT=%BASE_DIR%pyenv"
set "UV_EXE=%PY_ROOT%\bin\uv.exe"
set "VENV_DIR=%PY_ROOT%\venv"
set "SCRIPT_PATH=%BASE_DIR%..\script.py"
set "REQUIREMENTS=%BASE_DIR%requirements.txt"
set "PYTHON_VERSION=3.12"

:: === Полная изоляция uv внутри PY_ROOT ===
set "UV_CACHE_DIR=%PY_ROOT%\cache"
set "UV_PYTHON_INSTALL_DIR=%PY_ROOT%\python"
set "UV_TOOL_DIR=%PY_ROOT%\tools"
set "UV_TOOL_BIN_DIR=%PY_ROOT%\toolbin"
set "UV_PYTHON_PREFERENCE=only-managed"
set "UV_NO_MODIFY_PATH=1"

if not exist "%PY_ROOT%" mkdir "%PY_ROOT%"
if not exist "%PY_ROOT%\bin" mkdir "%PY_ROOT%\bin"

:: === 1. Скачиваем uv.exe, если его ещё нет ===
if not exist "%UV_EXE%" (
    echo Скачивание uv...
    powershell -NoProfile -Command ^
        "Invoke-WebRequest -Uri 'https://astral.sh/uv/install.ps1' -OutFile '%PY_ROOT%\install-uv.ps1'"
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$env:UV_INSTALL_DIR='%PY_ROOT%\bin'; $env:UV_NO_MODIFY_PATH='1'; & '%PY_ROOT%\install-uv.ps1'"
    if not exist "%UV_EXE%" (
        echo Ошибка: не удалось скачать uv.
        exit /b 1
    )
)

:: === 2. Ставим нужную версию Python внутрь PY_ROOT ===
"%UV_EXE%" python install %PYTHON_VERSION%
if !ERRORLEVEL! neq 0 (
    echo Ошибка при установке Python.
    exit /b 1
)

:: === 3. Находим путь к настоящему python.exe/pythonw.exe в managed-установке ===
for /f "delims=" %%P in ('"%UV_EXE%" python find %PYTHON_VERSION%') do set "BASE_PYTHON_EXE=%%P"
if not defined BASE_PYTHON_EXE (
    echo Ошибка: не удалось определить путь к базовому Python.
    exit /b 1
)
for %%F in ("!BASE_PYTHON_EXE!") do set "BASE_PYTHON_DIR=%%~dpF"
set "BASE_PYTHONW_EXE=!BASE_PYTHON_DIR!pythonw.exe"

if not exist "!BASE_PYTHONW_EXE!" (
    echo Ошибка: pythonw.exe не найден в базовой установке.
    exit /b 1
)

:: === 4. Создаём venv, если его ещё нет ===
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Создание виртуального окружения...
    "%UV_EXE%" venv "%VENV_DIR%" --python %PYTHON_VERSION%
    if !ERRORLEVEL! neq 0 (
        echo Ошибка при создании venv.
        exit /b 1
    )

    if exist "%REQUIREMENTS%" (
        echo Установка зависимостей...
        "%UV_EXE%" pip install --python "%VENV_DIR%\Scripts\python.exe" -r "%REQUIREMENTS%"
        if !ERRORLEVEL! neq 0 (
            echo Ошибка при установке зависимостей.
            exit /b 1
        )
    )
)

:: === 5. Запуск через настоящий pythonw.exe, но с окружением venv ===
set "VIRTUAL_ENV=%VENV_DIR%"
set "PATH=%VENV_DIR%\Scripts;!BASE_PYTHON_DIR!;%PATH%"

echo BASE_PYTHON_EXE=!BASE_PYTHON_EXE!
echo BASE_PYTHON_DIR=!BASE_PYTHON_DIR!
echo BASE_PYTHONW_EXE=!BASE_PYTHONW_EXE!
pause

start "" "!BASE_PYTHONW_EXE!" "%SCRIPT_PATH%" %*
exit
