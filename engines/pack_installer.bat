@echo off
setlocal enabledelayedexpansion


:: packs

for /f "usebackq delims=" %%a in (".\pack_list\files.txt") do (
    set "line=%%a"
    set "count=0"
    
    call :parse
    
    echo installing !list[3]!

    echo downloading...

    curl -L --retry 3 --progress-bar -o "!list[2]!" "!list[1]!"

    if not exist "!list[2]!" (
        echo [error] failed to download !list[3]!. contact creator: https://t.me/konstalker
        pause
        goto exit
    )

    echo installed.
)



:: archives

if not exist ./temp_files/ (
    call mkdir "./temp_files"
)

for /f "usebackq delims=" %%a in (".\pack_list\archives.txt") do (
    set "line=%%a"
    set "count=0"
    
    call :parse
    
    echo downloading temp file !list[3]!

    echo downloading...

    curl -L --retry 3 --progress-bar -o "./temp_files/!list[3]!" "!list[1]!"

    if not exist "./temp_files/!list[3]!" (
        echo [error] failed to download !list[3]!. contact creator: https://t.me/konstalker
        pause
        goto exit
    )
    echo downloaded.

    echo installing...
    powershell -Command "Expand-Archive -Path './temp_files/!list[3]!' -DestinationPath '!list[2]!' -Force"

    if not exist "./!list[2]!/!list[4]!" (
        echo [error] failed to install !list[3]!. contact creator: https://t.me/konstalker
        pause
        goto exit
    )

    echo installed.

)

goto exit



:: functions

:exit
rd /s /q "./temp_files"
exit /b

:parse
for /f "tokens=1* delims=;" %%b in ("!line!") do (
    set /a count+=1
    set "list[!count!]=%%b"
    set "line=%%c"
)
if defined line goto parse
exit /b