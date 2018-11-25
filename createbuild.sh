#!/bin/bash
set -e

pwd=`pwd`

build_win=1
build_u18=1
build_u16=1
#cleanup
find . -name "*.pyc" -delete

if [[ $build_u18 == 1 ]]; then

# local, ubuntu 18
source venv/bin/activate
mkdir -p build
rm -rf build/*
cd build
pyinstaller --clean ../pyinstaller.spec
cp dist/formula formula.linux18

cd $pwd

fi #u18

if [[ $build_win == 1 ]]; then

#windows, Passw0rd!
vm_name="formulabuilderwin"
ssh_name="win"
VBoxManage controlvm $vm_name poweroff || true
sleep 5
VBoxManage snapshot $vm_name restore builder
sleep 5
VBoxManage startvm $vm_name --type headless
sleep 60 # windows takes ages to boot up to ssh server reachability
dirname="formula"
ssh $ssh_name "mkdir $dirname"
scp -rq *.py pyinstaller.spec dependencies.txt graphics components data loader_functions map_objects $ssh_name:$dirname
ssh $ssh_name bash << HERE
    mkdir $dirname\build
    set PATH=%PATH%;C:\Users\IEUser\AppData\Local\Programs\Python\Python36;C:\Users\IEUser\AppData\Local\Programs\Python\Python36\Scripts
    cd $dirname\build
    python -m PyInstaller --clean ..\pyinstaller.spec
HERE
scp $ssh_name:$dirname/build/dist/formula.exe build/formula.windows.exe

cd $pwd

fi #win

if [[ $build_u16 == 1 ]]; then

# ubuntu 16 needs a VM because GLIBC <censored>
vm_name="formulabuilder16"
ssh_name="vbox16"
VBoxManage controlvm $vm_name poweroff || true
sleep 5
VBoxManage snapshot $vm_name restore builder
sleep 5
VBoxManage startvm $vm_name --type headless
sleep 10
dirname="formula"
ssh $ssh_name "mkdir -p $dirname"
scp -rq *.py pyinstaller.spec dependencies.txt graphics components data loader_functions map_objects $ssh_name:$dirname
ssh $ssh_name << HERE
    mkdir -p $dirname/build
    python3.6 -m virtualenv ~/venv
    source ~/venv/bin/activate
    pip install -r $dirname/dependencies.txt
    cd $dirname/build
    pyinstaller --clean ../pyinstaller.spec
HERE
scp $ssh_name:$dirname/build/dist/formula build/formula.linux16
fi #u16