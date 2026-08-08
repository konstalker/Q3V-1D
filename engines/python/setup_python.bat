@echo off
setlocal enabledelayedexpansion

:: ============================================================
::  Портативный запуск Python-скрипта через uv
::  Всё (uv, Python, кэш, venv) хранится ТОЛЬКО в папке pyenv\
::  рядом с этим bat-файлом. Ничего не пишется в систему.
:: ============================================================

set "BASE_DIR=%~dp0"
set "PY_ROOT=%BASE_DIR%pyenv"
set "UV_EXE=%PY_ROOT%\uv.exe"
set "VENV_DIR=%PY_ROOT%\venv"
set "REQUIREMENTS=%BASE_DIR%requirements.txt"
set "PYTHON_VERSION=3.12"
set "UV_ZIP_URL=https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"

:: === Полная изоляция: перенаправляем ВСЕ рабочие каталоги uv внутрь PY_ROOT ===
set "UV_CACHE_DIR=%PY_ROOT%\cache"
set "UV_PYTHON_INSTALL_DIR=%PY_ROOT%\python"
set "UV_TOOL_DIR=%PY_ROOT%\tools"
set "UV_TOOL_BIN_DIR=%PY_ROOT%\bin"
set "UV_NO_MODIFY_PATH=1"
set "UV_PYTHON_PREFERENCE=only-managed"

if not exist "%PY_ROOT%" mkdir "%PY_ROOT%"

:: === 1. Скачиваем uv.exe напрямую с GitHub Releases (без инсталлятора и без PATH) ===
if not exist "%UV_EXE%" (
    echo Скачивание uv...
    set "UV_ZIP=%PY_ROOT%\uv.zip"
    powershell -NoProfile -Command ^
        "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%UV_ZIP_URL%' -OutFile '!UV_ZIP!'"
    if !ERRORLEVEL! neq 0 (
        echo Ошибка: не удалось скачать uv.
        exit /b 1
    )
    powershell -NoProfile -Command "Expand-Archive -Path '!UV_ZIP!' -DestinationPath '%PY_ROOT%' -Force"
    del "!UV_ZIP!" >nul 2>&1
    if not exist "%UV_EXE%" (
        echo Ошибка: uv.exe не найден после распаковки.
        exit /b 1
    )
)

:: === 2. Ставим нужную версию Python внутрь PY_ROOT ===
:: --no-registry: НЕ регистрировать интерпретатор в реестре Windows
"%UV_EXE%" python install %PYTHON_VERSION% --no-registry
if !ERRORLEVEL! neq 0 (
    echo Ошибка при установке Python.
    exit /b 1
)

:: === 3. Находим НАСТОЯЩИЙ pythonw.exe базового интерпретатора ===
:: (обход бага uv: pythonw.exe внутри venv — это копия python.exe и открывает консоль)
for /f "delims=" %%P in ('"%UV_EXE%" python find %PYTHON_VERSION%') do set "BASE_PYTHON=%%P"
if not defined BASE_PYTHON (
    echo Ошибка: не удалось найти базовый интерпретатор Python.
    exit /b 1
)
for %%F in ("%BASE_PYTHON%") do set "BASE_PY_DIR=%%~dpF"
set "REAL_PYTHONW=%BASE_PY_DIR%pythonw.exe"
if not exist "%REAL_PYTHONW%" (
    echo Ошибка: pythonw.exe не найден рядом с базовым python.exe.
    echo Путь: %REAL_PYTHONW%
    exit /b 1
)

:: === 4. Создаём venv внутри той же папки (один раз) ===
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Создание виртуального окружения...
    "%UV_EXE%" venv "%VENV_DIR%" --python %PYTHON_VERSION%
    if !ERRORLEVEL! neq 0 (
        echo Ошибка при создании venv.
        exit /b 1
    )

    if exist "%REQUIREMENTS%" (
        echo Установка зависимостей...
        :: --link-mode copy: файлы физически копируются в venv,
        :: а не хардлинкаются из кэша — важно для переносимости на флешке
        "%UV_EXE%" pip install --python "%VENV_DIR%\Scripts\python.exe" --link-mode copy -r "%REQUIREMENTS%"
        if !ERRORLEVEL! neq 0 (
            echo Ошибка при установке зависимостей.
            exit /b 1
        )
    )
)

:: === 5. Запуск скрипта пользователя через НАСТОЯЩИЙ pythonw (без консоли, без бага) ===
set "VIRTUAL_ENV=%VENV_DIR%"
set "PYTHONPATH=%VENV_DIR%\Lib\site-packages"
start "" "%REAL_PYTHONW%" %*
exit
