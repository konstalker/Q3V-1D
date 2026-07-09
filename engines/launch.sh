#!/bin/bash
cd $(dirname "$0")

python autoupdater.py

ARGS="+set fs_homepath ../baseq3/mods +set fs_basepath ../ +set fs_game osp"

chmod +x ./oDFe.vk.x64
./oDFe.vk.x64 $ARGS
