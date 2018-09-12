#!/usr/bin/env bash
# Setup environment for running BDSIM

# Setup ROOT environment
if [ -r "$(which root | sed -e 's_/root__')/thisroot.sh" ] ; then
    source "$(which root | sed -e 's_/root__')/thisroot.sh"
elif [ -r "/usr/local/bin/thisroot.sh" ] ; then
    source "/usr/local/bin/thisroot.sh"
elif [ -r "/opt/root/bin/thisroot.sh" ] ; then
    source "/opt/root/bin/thisroot.sh"
fi

# Setup Geant4 environment
if [ -r "$(which geant4-config | sed -e 's_/geant4-config__')/geant4.sh" ] ; then
    source "$(which geant4-config | sed -e 's_/geant4-config__')/geant4.sh"
elif [ -r "/usr/local/bin/geant4.sh" ] ; then
    source "/usr/local/bin/geant4.sh"
fi

# BDSIM paths
export BDSIM=/usr/local
export ROOT_INCLUDE_PATH=$BDSIM/include/bdsim/:$BDSIM/include/bdsim/analysis/
