# .profile: executed by the command interpreter for login shells.
#  - based on content from Ubuntu and Cygwin .profile files.
#  - this file is not read by bash if .bash_profile or .bash_login exists.

# Locations:
#  - Scripts folder
if [ -d "${HOME}/Code/Scripts/" ]; then
    SCRIPTS="${HOME}/Code/Scripts/"
else
    if [ -d "${HOME}/Documents/Code/Scripts/" ]
    then
        SCRIPTS="${HOME}/Documents/Code/Scripts/"
    fi
fi
#  - User versions of bin, man, info
if [ -d "${HOME}/bin" ]; then
    PATH="${HOME}/bin:${PATH}"
fi
if [ -d "${HOME}/man" ]; then
    MANPATH="${HOME}/man:${MANPATH}"
fi
if [ -d "${HOME}/info" ]; then
    INFOPATH="${HOME}/info:${INFOPATH}"
fi
#  - User .local versions of bin, man, info
if [ -d "${HOME}/.local/bin" ]; then
    PATH="${HOME}/.local/bin:${PATH}"
fi
if [ -d "${HOME}/.local/man" ]; then
    MANPATH="${HOME}/.local/man:${MANPATH}"
fi
if [ -d "${HOME}/.local/info" ]; then
    INFOPATH="${HOME}/.local/info:${INFOPATH}"
fi
