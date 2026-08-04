@echo off
setlocal enabledelayedexpansion

set "BASE_DIR=%~dp0"
set "PY_ROOT=%BASE_DIR%pyenv"
set "UV_EXE=%PY_ROOT%\bin\uv.exe"
set "VENV_DIR=%PY_ROOT%\venv"
set "SCRIPT_PATH=%BASE_DIR%..\script.py"
set "REQUIREMENTS=%BASE_DIR%requirements.txt"
set "LAUNCHER_VBS=%PY_ROOT%\launcher.vbs"
set "PYTHON_VERSION=3.12"

:: === Изолируем всё, что использует uv, внутри PY_ROOT ===
set "UV_CACHE_DIR=%PY_ROOT%\cache"
set "UV_PYTHON_INSTALL_DIR=%PY_ROOT%\python"
set "UV_TOOL_DIR=%PY_ROOT%\tools"
set "UV_TOOL_BIN_DIR=%PY_ROOT%\toolbin"
set "UV_NO_MODIFY_PATH=1"
set "UV_PYTHON_PREFERENCE=only-managed"

if not exist "%PY_ROOT%" mkdir "%PY_ROOT%"

:: === 1. Скачиваем uv, если его ещё нет ===
if not exist "%UV_EXE%" (
    echo Скачивание uv...
    powershell -NoProfile -Command ^
        "Invoke-WebRequest -Uri 'https://astral.sh/uv/install.ps1' -OutFile '%PY_ROOT%\install-uv.ps1'"
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$env:UV_INSTALL_DIR='%PY_ROOT%\bin'; $env:UV_NO_MODIFY_PATH='1'; & '%PY_ROOT%\install-uv.ps1'"
    if not exist "%UV_EXE%" (
        echo Ошибка: не удалось скачать uv.
        pause
        exit /b 1
    )
)

:: === 2. Ставим нужную версию Python внутрь PY_ROOT ===
"%UV_EXE%" python install %PYTHON_VERSION%
if !ERRORLEVEL! neq 0 (
    echo Ошибка при установке Python.
    pause
    exit /b 1
)

:: === 3. Создаём venv, если его ещё нет ===
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Создание виртуального окружения...
    "%UV_EXE%" venv "%VENV_DIR%" --python %PYTHON_VERSION%
    if !ERRORLEVEL! neq 0 (
        echo Ошибка при создании venv.
        pause
        exit /b 1
    )

    if exist "%REQUIREMENTS%" (
        echo Установка зависимостей...
        "%UV_EXE%" pip install --python "%VENV_DIR%\Scripts\python.exe" -r "%REQUIREMENTS%"
    )
)

:: === 4. Генерируем launcher.vbs, если его ещё нет ===
if not exist "%LAUNCHER_VBS%" (
    > "%LAUNCHER_VBS%" echo Set objShell = CreateObject("WScript.Shell"^)
    >> "%LAUNCHER_VBS%" echo strArgs = ""
    >> "%LAUNCHER_VBS%" echo For i = 0 To WScript.Arguments.Count - 1
    >> "%LAUNCHER_VBS%" echo     strArgs = strArgs ^& " """ ^& WScript.Arguments(i^) ^& """"
    >> "%LAUNCHER_VBS%" echo Next
    >> "%LAUNCHER_VBS%" echo cmd = """" ^& WScript.Arguments(0^) ^& """"
    >> "%LAUNCHER_VBS%" echo objShell.Run """%VENV_DIR%\Scripts\python.exe"" ""%SCRIPT_PATH%""" ^& strArgs, 0, False
)

:: === 5. Запуск скрипта полностью без консоли ===
wscript.exe //nologo "%LAUNCHER_VBS%" %*
exit
