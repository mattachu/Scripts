#!/bin/bash
# Shortcut functions

# Pause
function pause() {
    if [[ -n $* ]]
    then
        prompt="$*"
    else
        prompt="Press the [Enter] key to continue..."
    fi
    read -p "$*"
}

# Check the current _Git_ repository
function git-check() {
    echo "Remotes:"
    git remote -vv
    git fetch --all
    echo
    echo "Branches:"
    git branch -vv --all
    echo
    echo "Status:"
    git status
}

# Check all my _Git_ repositories
#  - uses `git-check` above
#  - repository locations are currently hard-coded
function git-check-all() {
    startfolder=$(pwd)
    folderlist="${HOME}/Code/Scripts"
    folderlist="$folderlist ${HOME}/Code/Impact"
    folderlist="$folderlist ${HOME}/Code/runLORASR"
    folderlist="$folderlist ${HOME}/Code/sweep"
    folderlist="$folderlist ${HOME}/Code/BDSIM"
    folderlist="$folderlist ${HOME}/Code/OPAL"
    folderlist="$folderlist ${HOME}/Code/Reproducible"
    folderlist="$folderlist ${HOME}/Projects"
    folderlist="$folderlist ${HOME}/Presentations"
    folderlist="$folderlist ${HOME}/Editing"
    folderlist="$folderlist ${HOME}/Notebooks"
    folderlist="$folderlist ${HOME}/Manuscripts/Hydrogen"
    folderlist="$folderlist ${HOME}/Manuscripts"
    for folder in $folderlist
    do
        echo
        pause "Press the [Enter] key to check $folder"
        echo
        cd $folder
        git-check
    done
    cd $startfolder
}
