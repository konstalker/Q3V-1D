@echo off
setlocal enabledelayedexpansion

set "BASE_DIR=%~dp0"
set "PY_ROOT=%BASE_DIR%pyenv"
set "UV_EXE=%PY_ROOT%\uv.exe"
set "VENV_DIR=%PY_ROOT%\venv"
set "REQUIREMENTS=%BASE_DIR%requirements.txt"
set "PYTHON_VERSION=3.12"
set "UV_ZIP_URL=https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"

set "UV_CACHE_DIR=%PY_ROOT%\cache"
set "UV_PYTHON_INSTALL_DIR=%PY_ROOT%\python"
set "UV_TOOL_DIR=%PY_ROOT%\tools"
set "UV_TOOL_BIN_DIR=%PY_ROOT%\bin"
set "UV_NO_MODIFY_PATH=1"
set "UV_PYTHON_PREFERENCE=only-managed"

if not exist "%PY_ROOT%" mkdir "%PY_ROOT%"

if not exist "%UV_EXE%" (
    echo Downloading uv...
    set "UV_ZIP=%PY_ROOT%\uv.zip"
    powershell -NoProfile -Command ^
        "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%UV_ZIP_URL%' -OutFile '!UV_ZIP!'"
    if !ERRORLEVEL! neq 0 (
        echo ERROR: failed to download uv.
        exit /b 1
    )
    powershell -NoProfile -Command "Expand-Archive -Path '!UV_ZIP!' -DestinationPath '%PY_ROOT%' -Force"
    del "!UV_ZIP!" >nul 2>&1
    if not exist "%UV_EXE%" (
        echo ERROR: uv.exe not found after extraction.
        exit /b 1
    )
)

"%UV_EXE%" python install %PYTHON_VERSION% --no-registry
if !ERRORLEVEL! neq 0 (
    echo ERROR: failed to install Python.
    exit /b 1
)

for /f "delims=" %%P in ('"%UV_EXE%" python find %PYTHON_VERSION%') do set "BASE_PYTHON=%%P"
if not defined BASE_PYTHON (
    echo ERROR: could not find base Python interpreter.
    exit /b 1
)
for %%F in ("%BASE_PYTHON%") do set "BASE_PY_DIR=%%~dpF"
set "REAL_PYTHONW=%BASE_PY_DIR%pythonw.exe"
if not exist "%REAL_PYTHONW%" (
    echo ERROR: pythonw.exe not found next to base python.exe.
    echo Path: %REAL_PYTHONW%
    exit /b 1
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating virtual environment...
    "%UV_EXE%" venv "%VENV_DIR%" --python %PYTHON_VERSION%
    if !ERRORLEVEL! neq 0 (
        echo ERROR: failed to create venv.
        exit /b 1
    )

    if exist "%REQUIREMENTS%" (
        echo Installing dependencies...
        "%UV_EXE%" pip install --python "%VENV_DIR%\Scripts\python.exe" --link-mode copy -r "%REQUIREMENTS%"
        if !ERRORLEVEL! neq 0 (
            echo ERROR: failed to install dependencies.
            exit /b 1
        )
    )
)

set "VIRTUAL_ENV=%VENV_DIR%"
set "PYTHONPATH=%VENV_DIR%\Lib\site-packages"
start "" "%REAL_PYTHONW%" %*
exit
