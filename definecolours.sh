#!/bin/bash
# File: definecolours.sh
# Created: 03/07/2014 by Matt Easton
# Version: 0.2
# Modified: 07/09/2018 by Matt Easton
#
# Define colours for shell scripts.
#
# Colour definitions
#  - taken from Color Bash Prompt HowTo via tldp.org
#  - some colours might look different on some terminals
#  - different commands for different operating systems

# Set command string for current OS
if [[ "$(uname)" == "Darwin" ]]; then
    CS="\033"
else
    CS="\e"
fi

## Normal Colours
Black="${CS}[0;30m" # Black
Red="${CS}[0;31m" # Red
Green="${CS}[0;32m" # Green
Yellow="${CS}[0;33m" # Yellow
Blue="${CS}[0;34m" # Blue
Purple="${CS}[0;35m" # Purple
Cyan="${CS}[0;36m" # Cyan
White="${CS}[0;37m" # White

## Bold
BBlack="${CS}[1;30m" # Black
BRed="${CS}[1;31m" # Red
BGreen="${CS}[1;32m" # Green
BYellow="${CS}[1;33m" # Yellow
BBlue="${CS}[1;34m" # Blue
BPurple="${CS}[1;35m" # Purple
BCyan="${CS}[1;36m" # Cyan
BWhite="${CS}[1;37m" # White

## Background
On_Black="${CS}[40m" # Black
On_Red="${CS}[41m" # Red

## Special
NC="${CS}[m" # Color Reset
ALERT=${BWhite}${On_Red} # Bold White on red background
