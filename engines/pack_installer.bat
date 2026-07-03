@echo off
setlocal enabledelayedexpansion

if not exist ./temp_files/ (
    call mkdir "./temp_files"
)



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
        goto exit
    )

    echo installed.
)



:: archives
:: tar -xf pack.zip -C files

for /f "usebackq delims=" %%a in (".\pack_list\archives.txt") do (
    set "line=%%a"
    set "count=0"
    
    call :parse
    
    echo downloading temp file !list[3]!

    echo downloading...

    curl -L --retry 3 --progress-bar -o "./temp_files" "!list[1]!"

    if not exist "./temp_files/!list[3]!" (
        echo [error] failed to download !list[3]!. contact creator: https://t.me/konstalker
        goto exit
    )
    echo downloaded.

    call tar -xf "./temp_files/!list[3]!" -C "!list[2]!"

)

goto exit



:: functions

:exit
pause
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