#!/bin/bash
cd $(dirname "$0")

python autoupdater.py

ARGS="+set fs_homepath ../baseq3/mods +set fs_basepath ../ +set fs_game osp"

./quake3e-vulkan.x64 $ARGS
