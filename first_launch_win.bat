@echo off

cd /d %~dp0/engines

call %~dp0/engines/python/setup_python.bat flaunch.py

findstr /C:"windows" "%~dp0engines\mod_tree\branch.txt" >nul
if errorlevel 1 (
    echo windows>> "%~dp0engines\mod_tree\branch.txt"
)

cd /d %~dp0

set "shortcutName=%USERPROFILE%\Desktop\Q3V#1D.lnk"
set "targetPath=%~dp0engines\launch.bat"
set "iconPath=%~dp0engines\icons\b3.ico"
set "workingDir=%~dp0engines"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut(\"%shortcutName%\"); $s.TargetPath = \"%targetPath%\"; $s.IconLocation = \"%iconPath%\"; $s.WorkingDirectory = \"%workingDir%\"; $s.Save()"
