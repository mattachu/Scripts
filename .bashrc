# Set bash to automatically launch zsh instead
if [ -t 1 ]; then
  exec zsh
fi
