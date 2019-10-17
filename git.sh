#!/bin/bash
# Shortcut functions for Git
# - uses locations from `.bash_locations`
# - uses `pause` function from `.bash_functions`

# Load prerequisites
if [ -r "${HOME}/.bash_locations" ]; then
    source "${HOME}/.bash_locations"
fi
if [ -r "${HOME}/.bash_functions" ]; then
    source "${HOME}/.bash_functions"
fi

# Check the current _Git_ repository
function git-check() {
    echo "Remotes:"
    git remote -vv
    git fetch --all --prune
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
    folderlist="$folderlist ${RUN_FOLDER}"
    folderlist="$folderlist ${CODE_FOLDER}/Impact"
    folderlist="$folderlist ${CODE_FOLDER}/runLORASR"
    folderlist="$folderlist ${CODE_FOLDER}/sweep"
    folderlist="$folderlist ${CODE_FOLDER}/BDSIM"
    folderlist="$folderlist ${CODE_FOLDER}/OPAL"
    folderlist="$folderlist ${CODE_FOLDER}/Reproducible"
    folderlist="$folderlist ${PKU_FOLDER}/Projects"
    folderlist="$folderlist ${PKU_FOLDER}/Presentations"
    folderlist="$folderlist ${PKU_FOLDER}/Editing"
    folderlist="$folderlist ${PKU_FOLDER}/Manuscripts"
    folderlist="$folderlist ${PKU_FOLDER}/Notebooks"
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
