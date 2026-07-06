@echo off

cd /d %~dp0/engines

call %~dp0/engines/python/setup_python.bat download_tools.py "./pack_files/base.dconf" "skip"
call %~dp0/engines/python/setup_python.bat download_tools.py "./pack_files/win.dconf" "skip"
call %~dp0/engines/python/setup_python.bat "./upd.py"

cd /d %~dp0

set "shortcutName=%USERPROFILE%\Desktop\Q3V#1D.lnk"
set "targetPath=%~dp0engines\launch.bat"
set "iconPath=%~dp0engines\icons\b3.ico"
set "workingDir=%~dp0engines"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut(\"%shortcutName%\"); $s.TargetPath = \"%targetPath%\"; $s.IconLocation = \"%iconPath%\"; $s.WorkingDirectory = \"%workingDir%\"; $s.Save()"
