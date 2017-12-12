# Shortcuts for PKU work

alias server="ssh wangzhi@162.105.147.95"
alias transfer="rsync --archive --update --delete --max-size=50M --verbose ~/Simulations/Current/ ~/Simulations/Transfer/"

alias impact="run_with_log impact"
alias impact-test="run_with_log impact-test"
alias impact-multibunch="ln -s ImpactT.in ImpactT.txt; run_with_log impact-multibunch"
alias impact-mb="ln -s ImpactT.in ImpactT.txt; run_with_log impact-multibunch"
alias impact-pku="ln -s ImpactT.in ImpactT.txt; run_with_log impact-pku"
alias impact-official="run_with_log impact-official"

alias rm-impact="rm ./fort.* ./*.log ./*.dst ./*.plt ./*.csv"

alias run_tests='./run_tests.sh'
