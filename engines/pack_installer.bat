@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

set "LIST_FILE=./pack_list/files.txt"



:: files

if not exist "%LIST_FILE%" (
    echo [error]: file list not found, contacts of creator: t.me/konstalker
    pause
    exit /b
)

for /F "usebackq tokens=1,2,3,4 delims=;" %%A in ("%LIST_FILE%") do (
    set "URL=%%A"
    set "DL_DIR=%%B"
    set "FILENAME=%%C"
    set "INSTALL_CMD=%%D"

    echo.
    echo installing pack: !FILENAME!
    )

    echo Downloading...
    curl -# -L -o "!DL_DIR!\!FILENAME!" "!URL!"

    if exist "!DL_DIR!\!FILENAME!" (
        echo Установка !FILENAME! в заданную локацию...
        start /wait "" !INSTALL_CMD!
        echo Установка завершена.
    ) else (
        echo [error] url not found, contacts of creator t.me/konstalker
    )
)



:: archives

set "LIST_FILE=./pack_list/archives.txt"

if not exist "%LIST_FILE%" (
    echo [error] archive list not found, contacts of creator: t.me/konstalker
    pause
    exit /b
)

:: %%A - URL, %%B - Временная папка, %%C - Имя zip-файла, %%D - Папка назначения
for /F "usebackq tokens=1,2,3,4 delims=;" %%A in ("%LIST_FILE%") do (
    set "URL=%%A"
    set "DL_DIR=%%B"
    set "ZIP_NAME=%%C"
    set "EXTRACT_DIR=%%D"

    echo.
    echo Installing !ZIP_NAME!

    echo Downloading...
    curl -# -L -o "!DL_DIR!\!ZIP_NAME!" "!URL!"

    if exist "!DL_DIR!\!ZIP_NAME!" (
    
        :: -x (extract), -f (file), -C (change to directory - куда распаковывать)
        echo Unpacking...
        tar -xf "!DL_DIR!\!ZIP_NAME!" -C "!EXTRACT_DIR!"
        
        if !errorlevel! equ 0 (
            echo Installed.

            echo Deleting archive...
            del /q /f "!DL_DIR!\!ZIP_NAME!"
            echo everything correct.
        ) else (
            echo [error] cannot unpack archive, contacts of creator: t.me/konstalker 
        )

    ) else (
        echo [error] cannot download archive, contacts of creator: t.me/konstalker
    )
)

pause