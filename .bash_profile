# .bash_profile: executed by bash for login shells.
#  - anything bash-specific that is not in .bashrc goes here.
#  - the rest is in .profile for all shells
#  - based on content from Ubuntu and Cygwin .bash_profile files.

# Source the user's profile if it exists
if [ -f "${HOME}/.profile" ] ; then
    source "${HOME}/.profile"
fi

# Source the user's bashrc if it exists
if [ -f "${HOME}/.bashrc" ] ; then
    source "${HOME}/.bashrc"
fi
