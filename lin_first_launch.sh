#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $SCRIPT_DIR

cd "./engines"
python download_tools.py "./pack_files/base.dconf" "skip"
python download_tools.py "./pack_files/lin.dconf" "skip"
python upd.py

chmod +x ./quake3e-vulkan.x64
cd "../"

DESKTOP_DIR=$(xdg-user-dir DESKTOP)
SHORTCUT_NAME="Q3V#1D"
SHORTCUT_FILE="$SCRIPT_DIR/engines/launch.sh"
ICON_NAME="$SCRIPT_DIR/engines/icons/b3.png"
EXEC_PATH="$SCRIPT_DIR/engines"

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
