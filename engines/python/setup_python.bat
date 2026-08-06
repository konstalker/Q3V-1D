@echo off
setlocal enabledelayedexpansion

set "BASE_DIR=%~dp0"
set "PY_ROOT=%BASE_DIR%pyenv"
set "UV_EXE=%PY_ROOT%\uv.exe"
set "VENV_DIR=%PY_ROOT%\venv"
set "REQUIREMENTS=%BASE_DIR%requirements.txt"
set "PYTHON_VERSION=3.12"

:: === Полная изоляция всего, что использует uv, внутри PY_ROOT ===
:: ВАЖНО: без UV_PYTHON_BIN_DIR uv создаёт шим-ссылку на python
:: в системной папке (%APPDATA%\...\bin или аналог) - это утечка в систему,
:: которую и убирает эта переменная.
set "UV_CACHE_DIR=%PY_ROOT%\cache"
set "UV_PYTHON_INSTALL_DIR=%PY_ROOT%\python"
set "UV_PYTHON_BIN_DIR=%PY_ROOT%\python-bin"
set "UV_TOOL_DIR=%PY_ROOT%\tools"
set "UV_TOOL_BIN_DIR=%PY_ROOT%\bin"
set "UV_NO_MODIFY_PATH=1"
set "UV_PYTHON_PREFERENCE=only-managed"

if not exist "%PY_ROOT%" mkdir "%PY_ROOT%"

:: === 1. Скачиваем uv.exe, если его ещё нет ===
:: Используем однострочный вариант из офиц. документации Astral -
:: он надёжнее, чем скачивание install.ps1 отдельным файлом
if not exist "%UV_EXE%" (
    echo Скачивание uv...
    powershell -NoProfile -ExecutionPolicy ByPass -Command ^
        "$env:UV_INSTALL_DIR='%PY_ROOT%'; $env:UV_NO_MODIFY_PATH='1'; irm https://astral.sh/uv/install.ps1 | iex"
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

:: === 3. Находим путь к базовому интерпретатору (не venv!), скачанному uv ===
:: Нужен для обхода бага, при котором pythonw.exe в venv является копией python.exe
:: (см. https://github.com/astral-sh/uv/issues/19226)
:: ВАЖНО: команда обёрнута через "call" - без этого у cmd.exe известный баг:
:: если команда внутри for /f начинается с закавыченного пути с пробелами,
:: cmd обрезает путь по первому пробелу ("...\Program' is not recognized...").
:: call меняет способ построения внутренней команды и обходит баг.
for /f "delims=" %%P in ('call "%UV_EXE%" python find %PYTHON_VERSION%') do set "BASE_PY=%%P"
if not defined BASE_PY (
    echo Ошибка: не удалось определить путь к базовому интерпретатору.
    exit /b 1
)
for %%F in ("%BASE_PY%") do set "BASE_PY_DIR=%%~dpF"
set "REAL_PYTHONW=%BASE_PY_DIR%pythonw.exe"

if not exist "%REAL_PYTHONW%" (
    echo Ошибка: настоящий pythonw.exe не найден по пути %REAL_PYTHONW%
    exit /b 1
)

:: === 4. Создаём venv внутри той же папки, если его ещё нет ===
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
)

:: === 5. Запуск скрипта пользователя через настоящий pythonw.exe ===
:: PYTHONPATH указывает на site-packages venv, т.к. запускаем не через
:: битый shim venv, а напрямую через базовый интерпретатор
set "PYTHONPATH=%VENV_DIR%\Lib\site-packages"
start "" "%REAL_PYTHONW%" "%*"
exit
