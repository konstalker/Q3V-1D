@echo off

cd /d %~dp0/engines

call python download_tools.py "./pack_files/base.xml" "skip"

cd /d %~dp0

set "shortcutName=%USERPROFILE%\Desktop\Quake 3 Arena.lnk"
set "targetPath=%~dp0engines\launch.bat"
set "iconPath=%~dp0engines\icons\b3.ico"
set "workingDir=%~dp0engines"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut(\"%shortcutName%\"); $s.TargetPath = \"%targetPath%\"; $s.IconLocation = \"%iconPath%\"; $s.WorkingDirectory = \"%workingDir%\"; $s.Save()"
