#!/bin/bash

cd $(dirname "$0")

cd "./engines"
python download_tools.py "./pack_files/base.xml" "skip"
python download_tools.py "./pack_files/lin.xml" "skip"
python upd.py
cd "../"

DESKTOP_DIR=$(xdg-user-dir DESKTOP)
SHORTCUT_NAME="Q3V#1D"
SHORTCUT_FILE="$(dirname "$0")/engines/launch.sh"
ICON_NAME="$(dirname "$0")/engines/icons/b3.ico"
EXEC_PATH="$(dirname "$0")/engines"

cat <<EOF > "$DESKTOP_DIR/Q3V#1D.desktop"
[Desktop Entry]
Type=Application
Name=$SHORTCUT_NAME
Comment="Q3V#1D" quake 3 compilation by KONSTALKER
Exec=$SHORTCUT_FILE
Icon=$ICON_NAME
Terminal=false
Categories=Game;
EOF

chmod +x "$SHORTCUT_FILE"
