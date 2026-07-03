@echo off

call downloader.bat "./pack_list/confupd.txt" "f" ""
call beupd.bat
call downloader.bat "./pack_list/voidupd.txt" "a" ""

echo updated.
pause
