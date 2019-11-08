#!/bin/bash
# Shortcuts for various work-related programs and environments

# Load machine-specific locations
source "${HOME}/.bash_locations"

# Shortcuts for common actions
alias beep="echo -e '\a'"
alias transfer="rsync --archive --update --delete --max-size=50M --verbose ~/Simulations/Current/ ~/Simulations/Transfer/"
alias run-tests="./run-tests.sh"
alias sync-usb="unison -fat -rsrc false ${SYNC_FOLDER}/ ${USB_FOLDER}/"

# Load certain environments (machine specific)
if [[ "$(uname)" == "Darwin" ]]; then
    computer_name=$(scutil --get ComputerName)
else
    computer_name=$(hostname)
fi
case ${computer_name} in
    "Matt's MacBook Pro"|"MacBook Pro")
        alias load-root="source /usr/local/bin/thisroot.sh"
        alias load-geant4="source /usr/local/bin/geant4.sh"
        alias load-opal="source /opt/OPAL-1.4.0-1/etc/profile.d/opal.sh"
        ;;
    "MJEaston")
        alias load-root="source /opt/root/bin/thisroot.sh"
        alias load-geant4="source /usr/local/bin/geant4.sh"
        alias load-opal="source /opt/OPAL-2.0.0rc2/etc/profile.d/opal.sh"
        ;;
    "ubuntu42")
        alias load-root="source ~/Software/ROOT/bin/thisroot.sh"
        ;;
esac

# Shortcuts for Impact-T
alias ImpactGUI="~/Code/Impact/GUI/ImpactGUI.py"

# Shortcuts for Reproducible
alias reproduce="~/Code/Reproducible/reproduce"

# Shortcuts for BDSIM
alias load-bdsim="source ${SCRIPTS_FOLDER}/bdsim.sh"

# Settings for EPOCH
export COMPILER=gfortran
export MPIF90=mpifort
