#!/bin/bash
set -e
set -x
#source venv/bin/activate
#mkdir -p build
#rm -rf build/*
#cd build
#pyinstaller ../pyinstaller.spec
#cp dist/spellmaker spellmaker.linux

#windows
# VM psw "Passw0rd!"

#TODO reset vbox16 VM
dirname="spellmaker"
ssh vbox16 "mkdir -p $dirname"
scp -r *.py pyinstaller.spec dependencies.txt components data loader_functions map_objects vbox16:$dirname
ssh vbox16 << HERE
    mkdir $dirname/build
    python3.6 -m virtualenv ~/venv
    source ~/venv/bin/activate
    pip install -r $dirname/dependencies.txt
    cd $dirname/build
    pyinstaller ../pyinstaller.spec
HERE
scp vbox16:$dirname/build/dist/spellmaker build/spellmaker.linux16
ssh vbox16 "rm -rf spellmaker venv"
