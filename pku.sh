#!/bin/bash
# Shortcuts for PKU work

# Load certain environments
alias load-root="source /opt/root/bin/thisroot.sh"
alias load-geant4="source /usr/local/bin/geant4.sh"
alias load-opal="source /opt/OPAL-2.0.0rc2/etc/profile.d/opal.sh"
alias load-bdsim="source ~/Code/Scripts/bdsim.sh"

# Shortcuts for common actions
alias server="ssh wangzhi@162.105.147.95"
alias transfer="rsync --archive --update --delete --max-size=50M --verbose ~/Simulations/Current/ ~/Simulations/Transfer/"
alias run-tests='./run-tests.sh'

# Shortcuts for Impact-T
alias impact="run-with-log mpirun -np 8 impact; mv mpirun.log impact.log"
alias impact-test="run-with-log mpirun -np 8 impact-test; mv mpirun.log impact-test.log"
alias impact-pku="run-with-log mpirun -np 8 impact-pku; mv mpirun.log impact-pku.log"
alias impact-official="run-with-log impact-official"
alias rm-impact="recursive-rm 'fort.*' '*.log' '*.plt' '*.dst' '*.csv'"

# Settings for EPOCH
export COMPILER=gfortran
export MPIF90=mpifort
