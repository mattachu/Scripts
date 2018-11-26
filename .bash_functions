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
