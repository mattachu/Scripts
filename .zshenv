# .zshenv - set up environment for zsh

# Locations:
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
#  - pyenv
if [ -r "$HOME/.pyenv" ]; then
    export PYENV_ROOT="$HOME/.pyenv"
fi
if [ -r "$PYENV_ROOT/bin" ]; then
    export PATH="$PYENV_ROOT/bin:$PATH"
fi
if command -v pyenv 1>/dev/null 2>&1; then
    eval "$(pyenv init --path)"
fi
