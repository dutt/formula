#!/bin/bash

set -e
set -x

currdir=$(readlink -f $(dirname "$0"))
parent_dir=$(dirname "$currdir")
hooks_dir="$parent_dir"/.git/hooks
cp $currdir/pre-commit "$hooks_dir"

venvpath=$currdir/venv
if [[ ! -d "$venvpath" ]]; then
    python3.7 -m venv $venvpath
fi

source "$venvpath"/bin/activate
pip install -U pip
pip install black
