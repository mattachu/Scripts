#!/usr/bin/env bash
# Setup environment for running BDSIM

# Setup ROOT and Geant4 environments
source /opt/root/bin/thisroot.sh
source /usr/local/bin/geant4.sh

# BDSIM paths
export BDSIM=/usr/local
export ROOT_INCLUDE_PATH=$BDSIM/include/bdsim/:$BDSIM/include/bdsim/analysis/
