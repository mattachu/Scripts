#!/bin/bash
# Shortcut functions

# Load machine-specific locations
source "${HOME}/.bash_locations"

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
    folderlist="${SCRIPTS_FOLDER}"
    folderlist="$folderlist ${CODE_FOLDER}/Impact"
    folderlist="$folderlist ${CODE_FOLDER}/runLORASR"
    folderlist="$folderlist ${CODE_FOLDER}/sweep"
    folderlist="$folderlist ${CODE_FOLDER}/BDSIM"
    folderlist="$folderlist ${CODE_FOLDER}/OPAL"
    folderlist="$folderlist ${CODE_FOLDER}/Reproducible"
    folderlist="$folderlist ${PKU_FOLDER}/Projects"
    folderlist="$folderlist ${PKU_FOLDER}/Presentations"
    folderlist="$folderlist ${PKU_FOLDER}/Editing"
    folderlist="$folderlist ${PKU_FOLDER}/Notebooks"
    folderlist="$folderlist ${PKU_FOLDER}/Manuscripts/Hydrogen"
    folderlist="$folderlist ${PKU_FOLDER}/Manuscripts"
    for folder in $folderlist
    do
        echo
        if [ -d $folder ]; then
            pause "Press the [Enter] key to check $folder"
            echo
            cd $folder
            git-check
        else
            echo "Folder $folder not found."
        fi
    done
    cd $startfolder
}
