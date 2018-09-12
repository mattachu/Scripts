# Created: 25/06/2014 by Matt Easton
# Version: 0.2
# Modified: 07/09/2018 by Matt Easton
#
# This script is run at 'login' to a terminal session.
#
# Actions taken by this script are:
#  - run .profile (shell-independent profile setup)
#  - run .bashrc (bash-specific terminal setup)
#  - display greeting (show computer name, program versions, etc.)

# Source the user's profile if it exists and is readable
if [ -r "${HOME}/.profile" ] ; then
    source "${HOME}/.profile"
fi

# Source the user's bashrc if it exists and is readable
if [ -r "${HOME}/.bashrc" ] ; then
    source "${HOME}/.bashrc"
fi

# Show greeting if it exists and is readable
if [ -r "${HOME}/.greeting" ] ; then
    source "${HOME}/.greeting"
fi
