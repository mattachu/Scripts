# To the extent possible under law, the author(s) have dedicated all
# copyright and related and neighboring rights to this software to the
# public domain worldwide. This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software.
# If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

# base-files version 4.2-4

# ~/.bash_profile: executed by bash(1) for login shells.

# The latest version as installed by the Cygwin Setup program can
# always be found at /etc/defaults/etc/skel/.bash_profile

# Modifying /etc/skel/.bash_profile directly will prevent
# setup from updating it.

# The copy in your home directory (~/.bash_profile) is yours, please
# feel free to customise it to create a shell
# environment to your liking.  If you feel a change
# would be benifitial to all, please feel free to send
# a patch to the cygwin mailing list.

# User dependent .bash_profile file

# source the users bashrc if it exists
if [ -f "${HOME}/.bashrc" ] ; then
  source "${HOME}/.bashrc"
fi

# Set PATH so it includes user's private bin if it exists
# if [ -d "${HOME}/bin" ] ; then
#   PATH="${HOME}/bin:${PATH}"
# fi

# Set MANPATH so it includes users' private man if it exists
# if [ -d "${HOME}/man" ]; then
#   MANPATH="${HOME}/man:${MANPATH}"
# fi

# Set INFOPATH so it includes users' private info if it exists
# if [ -d "${HOME}/info" ]; then
#   INFOPATH="${HOME}/info:${INFOPATH}"
# fi

# Functions
function time_taken {
    if (( $SECONDS > 3600 )) ; then
        let "hours=SECONDS/3600"
        let "minutes=(SECONDS%3600)/60"
        let "seconds=(SECONDS%3600)%60"
        echo "Completed in $hours hour(s), $minutes minute(s) and $seconds second(s)"
    elif (( $SECONDS > 60 )) ; then
        let "minutes=(SECONDS%3600)/60"
        let "seconds=(SECONDS%3600)%60"
        echo "Completed in $minutes minute(s) and $seconds second(s)"
    else
        echo "Completed in $SECONDS seconds"
    fi
}
function run_with_timer {
    SECONDS=0
    $*
    echo "Time taken: $SECONDS s"
}
function run_with_log {
    rm -f $1.log
    SECONDS=0
    $* > >(tee -a $1.log) 2> >(tee -a $1.log >&2)
    time_taken > >(tee -a $1.log) 2> >(tee -a $1.log >&2)
    sleep 0.1
}

# Aliases
alias server="ssh wangzhi@162.105.147.95"
alias impact="run_with_log impact"
alias impact-test="run_with_log impact-test"
alias impact-pku="cp ImpactT.in ImpactT.txt; run_with_log impact-pku; rm ImpactT.txt"
alias impact-official="run_with_log impact-official"
alias rm-impact="rm ./fort.* ./*.log ./*.dst ./*.plt ./*.csv"
alias transfer="rsync --archive --update --delete --max-size=50M --verbose ~/Simulations/Current/ ~/Simulations/Transfer/"
