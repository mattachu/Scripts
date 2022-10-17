# .zprofile - set up environment for zsh login sessions

# Locations:
#  - User versions of bin, man, info
if [ -d "${HOME}/bin" ]; then
    path=(~/bin $path)
fi
if [ -d "${HOME}/man" ]; then
    MANPATH="${HOME}/man:${MANPATH}"
fi
if [ -d "${HOME}/info" ]; then
    INFOPATH="${HOME}/info:${INFOPATH}"
fi
#  - User .local versions of bin, man, info
if [ -d "${HOME}/.local/bin" ]; then
    path=(~/.local/bin $path)
fi
if [ -d "${HOME}/.local/man" ]; then
    MANPATH="${HOME}/.local/man:${MANPATH}"
fi
if [ -d "${HOME}/.local/info" ]; then
    INFOPATH="${HOME}/.local/info:${INFOPATH}"
fi
#  - pyenv
if [ -r "$HOME/.pyenv" ]; then
    export PYENV_ROOT="$HOME/.pyenv"
fi
if [ -r "$PYENV_ROOT/bin" ]; then
    path=("$PYENV_ROOT/bin" $path)
fi
if [[ $OSTYPE -ne "msys" ]]; then
    if command -v pyenv 1>/dev/null 2>/dev/null; then
        eval "$(pyenv init --path)"
    fi
else
    # MSYS adds some paths at the front of the path list,
    # so we need to move the .pyenv paths back to the front
    path=(~/.pyenv/pyenv-win/bin ~/.pyenv/pyenv-win/shims $path)
fi
# - remove duplicates
typeset -U PATH path
