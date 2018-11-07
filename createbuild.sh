#!/bin/bash
set -e

source venv/bin/activate
mkdir -p build
rm -rf build/*
cd build
pyinstaller --clean -F ../engine.py -n spellmaker
cp dist/spellmaker spellmaker.linux

#windows
# VM psw "Passw0rd!"
