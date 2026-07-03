@echo off

cd /d %~dp0/engines

call downloader.bat "./pack_list/files.txt" "f" "skip"
call downloader.bat "./pack_list/archives.txt" "a" "skip"
call ./beupd.bat

cd /d %~dp0

set "shortcutName=%USERPROFILE%\Desktop\Quake 3 Arena.lnk"
set "targetPath=%~dp0engines\launch.bat"
set "iconPath=%~dp0engines\icons\b3.ico"
set "workingDir=%~dp0engines"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut(\"%shortcutName%\"); $s.TargetPath = \"%targetPath%\"; $s.IconLocation = \"%iconPath%\"; $s.WorkingDirectory = \"%workingDir%\"; $s.Save()"