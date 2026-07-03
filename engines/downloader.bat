@echo off
setlocal enabledelayedexpansion

if not exist ./temp_files/ (
    call mkdir "./temp_files"
)

for /f "usebackq delims=" %%a in (%1) do (
    set "line=%%a"
    set "count=0"
    
    call :parse
    
    echo installing !list[3]!

    echo downloading...
    
    if %2 == "a" if %3=="s" if exist "!list[2]!!list[4]!" (
        set "skip=1"
    ) 

    if %2 == "f" if %3=="s" if exist "!list[2]!!list[3]!" (
        set "skip=1"
    )
    
    set "downloaded=1"

    if not defined skip (
        if %2 == "a" (
            
            if not exist "./temp_files/!list[3]!" (
                curl -L --retry 3 --progress-bar -o "./temp_files/!list[3]!" "!list[1]!"
                set "exsist=0"
            ) else (
                set "exsist=1"
            )
            
            if not exist "./temp_files/!list[3]!" (
                set "downloaded=0"
            ) else if !exsist! == 1 if not exist "./temp_files/!list[3]!dir" (
                set "exsist=0"
            )

            if !downloaded! == 1 if not "!list[5]!"=="" (
                if !exsist! == 0 (
                    powershell -Command "Expand-Archive -Path './temp_files/!list[3]!' -DestinationPath './temp_files/!list[3]!dir/' -Force"
                )

                rd /s /q "../!list[5]!"

                if !list[6]! == "" (
                    move "./temp_files/!list[3]!dir/!list[5]!" "../!list[5]!"
                ) else (
                    move "./temp_files/!list[3]!dir/!list[6]!/!list[5]!" "../!list[5]!"
                )

            ) else (
                if not !list5! == "" (
                    powershell -Command "Expand-Archive -Path './temp_files/!list[5]!/!list[3]!' -DestinationPath '!list[2]!' -Force"
                ) else (
                    powershell -Command "Expand-Archive -Path './temp_files/!list[3]!' -DestinationPath '!list[2]!' -Force"
                )
            )

        ) else (
            curl -L --retry 3 --progress-bar -o "!list[2]!!list[3]!" "!list[1]!"

            if not exist "!list[2]!!list[3]!" (
                set "downloaded=0"
            )
        )
    ) else (
        echo skipping download of !list[3]! because it already exists.
    )

    if !downloaded! == 0 (
        echo [error] failed to download !list[3]!. contact creator: https://t.me/konstalker
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
