#!/bin/bash
# Shortcuts for PKU work

alias server="ssh wangzhi@162.105.147.95"
alias transfer="rsync --archive --update --delete --max-size=50M --verbose ~/Simulations/Current/ ~/Simulations/Transfer/"
alias run_tests='./run_tests.sh'

# Shortcuts for Impact-T
alias impact="run_with_log impact"
alias impact-test="run_with_log impact-test"
alias impact-pku="run_with_log impact-pku"
alias impact-official="run_with_log impact-official"
alias rm-impact="rm ./fort.* ./*.log ./*.dst ./*.plt ./*.csv"

# Settings for EPOCH
export COMPILER=gfortran
export MPIF90=mpifort
