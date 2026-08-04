@echo off
setlocal enabledelayedexpansion

set "BASE_DIR=%~dp0"
set "PY_ROOT=%BASE_DIR%pyenv"
set "UV_EXE=%PY_ROOT%\uv.exe"
set "VENV_DIR=%PY_ROOT%\venv"
set "REQUIREMENTS=%BASE_DIR%requirements.txt"
set "PYTHON_VERSION=3.12"

:: === Всё, что использует uv, изолируем внутри PY_ROOT ===
set "UV_CACHE_DIR=%PY_ROOT%\cache"
set "UV_PYTHON_INSTALL_DIR=%PY_ROOT%\python"
set "UV_TOOL_DIR=%PY_ROOT%\tools"
set "UV_TOOL_BIN_DIR=%PY_ROOT%\bin"
set "UV_NO_MODIFY_PATH=1"
set "UV_PYTHON_PREFERENCE=only-managed"

if not exist "%PY_ROOT%" mkdir "%PY_ROOT%"

:: === 1. Скачиваем uv.exe, если его ещё нет ===
if not exist "%UV_EXE%" (
    echo Скачивание uv...
    powershell -NoProfile -Command ^
        "Invoke-WebRequest -Uri 'https://astral.sh/uv/install.ps1' -OutFile '%PY_ROOT%\install-uv.ps1'"
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$env:UV_INSTALL_DIR='%PY_ROOT%'; $env:UV_NO_MODIFY_PATH='1'; & '%PY_ROOT%\install-uv.ps1'"
    if not exist "%UV_EXE%" (
        echo Ошибка: не удалось скачать uv.
        exit /b 1
    )
)

:: === 2. Ставим нужную версию Python внутрь PY_ROOT (если ещё не стоит) ===
"%UV_EXE%" python install %PYTHON_VERSION%
if !ERRORLEVEL! neq 0 (
    echo Ошибка при установке Python.
    exit /b 1
)

:: === 3. Создаём venv внутри той же папки, если его ещё нет ===
:: === Создаём venv, если его ещё нет ===
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
    )

    :: === Чиним pythonw.exe: берём настоящий из managed-установки uv ===
    for /f "delims=" %%P in ('"%UV_EXE%" python find %PYTHON_VERSION%') do set "BASE_PYTHON_EXE=%%P"
    set "BASE_PYTHONW_EXE=!BASE_PYTHON_EXE:python.exe=pythonw.exe!"

    if exist "!BASE_PYTHONW_EXE!" (
        echo Копирование корректного pythonw.exe...
        copy /y "!BASE_PYTHONW_EXE!" "%VENV_DIR%\Scripts\pythonw.exe" >nul
    ) else (
        echo Предупреждение: не найден исходный pythonw.exe, GUI-режим может не работать.
    )
)

:: === 4. Запуск скрипта пользователя внутри venv ===
start "" "%VENV_DIR%\Scripts\pythonw.exe" %*
exit
