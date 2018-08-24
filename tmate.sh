#!/bin/sh

#  tmate.sh
#  Scripts for working with tmate.io for remote connections
#
#  Created by Matt Easton on 2018.08.24.
#

# Variables
TMATE_MAIN_SESSION="main"                           # main session name
TMATE_MAIN_SOCKET="/tmp/tmate-main.sock"            # main socket
TMATE_BACKUP_SESSION="backup"                       # backup session name
TMATE_BACKUP_SOCKET="/tmp/tmate-backup.sock"        # backup socket
TMATE_TMUX_SESSION="/tmp/tmate-tmux-session"        # default TMUX location

# Get current tmate connection url.
# If a session name is given as an argument, it looks for this session,
#   otherwise the main session is used.
tmate-url() {
if [ -n "$1" ]; then
TMATE_SESSION="$1"
TMATE_SOCKET="/tmp/tmate-$1.sock"
else
TMATE_SESSION="$TMATE_MAIN_SESSION"
TMATE_SOCKET="$TMATE_MAIN_SOCKET"
fi
url="$(tmate -S $TMATE_SOCKET display -p '#{tmate_ssh}')"
echo "$url" | tr -d '\n' | pbcopy
echo "Copied tmate url for $TMATE_SESSION session: "
echo "$url"
}

# Start a new tmate pair session if one doesn't already exist
# Two arguments:
#   1. TMUX session to connect to
#   2. Session name for tmate
tmate-pair() {
if [ -n "$2" ]; then
TMATE_SESSION="$2"
TMATE_SOCKET="/tmp/tmate-$2.sock"
else
TMATE_SESSION="$TMATE_MAIN_SESSION"
TMATE_SOCKET="$TMATE_MAIN_SOCKET"
fi

if [ ! -e "$TMATE_SOCKET" ]; then

# Start a new tmate session
tmate -S "$TMATE_SOCKET" -f "$HOME/.tmate.conf" new-session -d -s "$TMATE_SESSION"

# Get url
while [ -z "$url" ]; do
url="$(tmate -S $TMATE_SOCKET display -p '#{tmate_ssh}')"
done
tmate-url
sleep 1

# Connect to existing TMUX session
if [ -n "$1" ]; then
echo $1 > $TMATE_TMUX_SESSION
tmate -S "$TMATE_SOCKET" send -t "$TMATE_SESSION" "TMUX='' tmux attach-session -t $1" ENTER
fi
fi

# Connect to existing tmate session
tmate -S "$TMATE_SOCKET" attach-session -t "$TMATE_SESSION"
}

# Close the pair because security
tmate-unpair() {
if [ -e "$TMATE_SOCKET_LOCATION" ]; then
if [ -e "$TMATE_TMUX_SESSION" ]; then
tmux detach -s $(cat $TMATE_TMUX_SESSION)
rm -f $TMATE_TMUX_SESSION
fi

tmate -S "$TMATE_SOCKET_LOCATION" kill-session -t "$TMATE_PAIR_NAME"
echo "Killed session $TMATE_PAIR_NAME"
else
echo "Session already killed"
fi
}
