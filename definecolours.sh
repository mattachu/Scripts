#!/bin/bash
# File: definecolours.sh
# Created: 03/07/2014 by Matt Easton
# Version: 0.1
# Modified: 03/07/2014 by Matt Easton
#
# Define colours for shell scripts
# Originally part of pbt-dev.bashrc and similar scripts,
# moved here for portability

# Colour definitions
#  - taken from Color Bash Prompt HowTo via tldp.org
#  - some colours might look different on some terminals

## Normal Colours
Black='\e[0;30m' # Black
Red='\e[0;31m' # Red
Green='\e[0;32m' # Green
Yellow='\e[0;33m' # Yellow
Blue='\e[0;34m' # Blue
Purple='\e[0;35m' # Purple
Cyan='\e[0;36m' # Cyan
White='\e[0;37m' # White

## Bold
BBlack='\e[1;30m' # Black
BRed='\e[1;31m' # Red
BGreen='\e[1;32m' # Green
BYellow='\e[1;33m' # Yellow
BBlue='\e[1;34m' # Blue
BPurple='\e[1;35m' # Purple
BCyan='\e[1;36m' # Cyan
BWhite='\e[1;37m' # White

## Background
On_Black='\e[40m' # Black
On_Red='\e[41m' # Red

## Special
NC="\e[m" # Color Reset
ALERT=${BWhite}${On_Red} # Bold White on red background
