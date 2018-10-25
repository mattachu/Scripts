#!/bin/bash
# Shortcuts for various work-related programs and environments

# Shortcuts for common actions
alias server="ssh wangzhi@162.105.147.95"
alias transfer="rsync --archive --update --delete --max-size=50M --verbose ~/Simulations/Current/ ~/Simulations/Transfer/"
alias run-tests='./run-tests.sh'
alias git-check="git remote -vv; git fetch --all; git branch -vv --all; git status"

# Load certain environments (machine specific)
if [[ "$(uname)" == "Darwin" ]]; then
    computer_name=$(scutil --get ComputerName)
else
    computer_name=$(hostname)
fi
case ${computer_name} in
"Matt’s MacBook Pro")
    alias load-root="source /usr/local/bin/thisroot.sh"
    alias load-geant4="source /usr/local/bin/geant4.sh"
    alias load-opal="source /opt/OPAL-1.4.0-1/etc/profile.d/opal.sh"
    ;;
"MJEaston")
    alias load-root="source /opt/root/bin/thisroot.sh"
    alias load-geant4="source /usr/local/bin/geant4.sh"
    alias load-opal="source /opt/OPAL-2.0.0rc2/etc/profile.d/opal.sh"
    ;;
esac

# Shortcuts for Reproducible
alias reproduce="~/Code/Reproducible/reproduce"

# Shortcuts for BDSIM
alias load-bdsim="source ${SCRIPTS}/bdsim.sh"

# Shortcuts for Impact-T
alias impact="run-with-log mpirun -np 8 impact; mv mpirun.log impact.log"
alias impact-test="run-with-log mpirun -np 8 impact-test; mv mpirun.log impact-test.log"
alias impact-pku="run-with-log mpirun -np 8 impact-pku; mv mpirun.log impact-pku.log"
alias impact-official="run-with-log impact-official"
alias rm-impact="recursive-rm 'fort.*' '*.log' '*.plt' '*.dst' '*.csv'"

# Settings for EPOCH
export COMPILER=gfortran
export MPIF90=mpifort
