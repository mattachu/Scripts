#!/bin/sh

#  tmate.sh
#  Scripts for working with tmate.io for remote connections
#
#  Created by Matt Easton on 2018.08.24.
#

# Variables
TMATE_FOLDER="/tmp/tmate-1000"                              # holds temp tmate items
TMATE_MAIN_SESSION="main"                                   # main session name
TMATE_MAIN_SOCKET="${TMATE_FOLDER}/tmate-main.sock"         # main socket
TMATE_BACKUP_SESSION="backup"                               # backup session name
TMATE_BACKUP_SOCKET="${TMATE_FOLDER}/tmate-backup.sock"     # backup socket
TMATE_TMUX_SESSION="${TMATE_FOLDER}/tmate-tmux-session"     # default TMUX location
TMATE_URL_FILE="${HOME}/Filing/tmate.txt"                   # (synced) file with URLs

# Get current tmate connection url.
# If a session name is given as an argument, it looks for this session,
#   otherwise the main session is used.
tmate_url() {
    if [ -n "$1" ]; then
        TMATE_SESSION="$1"
        TMATE_SOCKET="${TMATE_FOLDER}/tmate-$1.sock"
    else
        TMATE_SESSION="${TMATE_MAIN_SESSION}"
        TMATE_SOCKET="${TMATE_MAIN_SOCKET}"
    fi
    url="$(tmate -S ${TMATE_SOCKET} display -p '#{tmate_ssh}')"
    echo "tmate url for ${TMATE_SESSION} session: $url"
}

# Start a new tmate pair session
# Two arguments:
#   1. Session name for tmate
#   2. TMUX session to connect to
tmate_pair() {
    if [ -n "$1" ]; then
        TMATE_SESSION="$1"
        TMATE_SOCKET="${TMATE_FOLDER}/tmate-$1.sock"
    else
        TMATE_SESSION="${TMATE_MAIN_SESSION}"
        TMATE_SOCKET="${TMATE_MAIN_SOCKET}"
    fi

    if [ ! -e "${TMATE_SOCKET}" ]; then

        # Start a new tmate session
        tmate -S "${TMATE_SOCKET}" -f "${HOME}/.tmate.conf" new-session -d -s "${TMATE_SESSION}"

        # Get url
        tmate -S "${TMATE_SOCKET}" wait tmate-ready
        tmate_url "${TMATE_SESSION}"
        sleep 1

        # Connect to existing TMUX session
        if [ -n "$2" ]; then
            echo $2 > $TMATE_TMUX_SESSION
            tmate -S "${TMATE_SOCKET}" send -t "${TMATE_SESSION}" "TMUX='' tmux attach-session -t $2" ENTER
        fi
    fi
}

# Close the pair because security
tmate_unpair() {
    if [ -n "$1" ]; then
        TMATE_SESSION="$1"
        TMATE_SOCKET="${TMATE_FOLDER}/tmate-$1.sock"
    else
        TMATE_SESSION="${TMATE_MAIN_SESSION}"
        TMATE_SOCKET="${TMATE_MAIN_SOCKET}"
    fi

    if [ -e "${TMATE_SOCKET}" ]; then
        if [ -e "${TMATE_TMUX_SESSION}" ]; then
            tmux detach -s $(cat ${TMATE_TMUX_SESSION})
            rm -f "${TMATE_TMUX_SESSION}"
        fi

        tmate -S "${TMATE_SOCKET}" kill-session -t "${TMATE_SESSION}"
        rm -f "${TMATE_SOCKET}"
        echo "Killed session ${TMATE_SESSION}"
    else
        echo "Session already killed"
    fi
}

# Connect to an existing tmate session
# Two arguments:
#   1. Session name for tmate [default: main]
#   2. [optional] TMUX session to connect to
tmate_connect() {
    if [ -n "$1" ]; then
        TMATE_SESSION="$1"
        TMATE_SOCKET="${TMATE_FOLDER}/tmate-$1.sock"
    else
        TMATE_SESSION="${TMATE_MAIN_SESSION}"
        TMATE_SOCKET="${TMATE_MAIN_SOCKET}"
    fi

    # Connect to existing TMUX session
    if [ -n "$2" ]; then
        echo $2 > $TMATE_TMUX_SESSION
        tmate -S "${TMATE_SOCKET}" send -t "${TMATE_SESSION}" "TMUX='' tmux attach-session -t $2" ENTER
    fi

    # Connect to existing tmate session
    tmate -S "${TMATE_SOCKET}" attach-session -t "${TMATE_SESSION}"
}

# Start main and backup sessions and record urls
tmate_start() {
    tmate_unpair "${TMATE_MAIN_SESSION}"; sleep 1
    tmate_pair "${TMATE_MAIN_SESSION}"
    tmate_url "${TMATE_MAIN_SESSION}" > "${TMATE_URL_FILE}"
    tmate_unpair "${TMATE_BACKUP_SESSION}"; sleep 1
    tmate_pair "${TMATE_BACKUP_SESSION}"
    tmate_url "${TMATE_BACKUP_SESSION}" >> "${TMATE_URL_FILE}"
}
