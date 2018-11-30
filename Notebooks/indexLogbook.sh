#!/bin/bash
# Build a set of monthly summaries from single notebook files
# - only searches the current folder

# Parameters
datePattern="./[0-9]{4}-[0-9]{2}-[0-9]{2}.md"
monthPattern="./[0-9]{4}-[0-9]{2}.md"

# Clear out existing versions of monthly summary files
find . -regextype posix-egrep -regex $monthPattern -delete

# Get list of files matching date pattern `XXXX-XX-XX.md`
dateList=$(find . -regextype posix-egrep -regex $datePattern | \
           sed -e 's|\./||' -e 's|\.md||')

# Work through list of dates
lastDate=""
lastMonth=""
for currentDate in $dateList
do
    # Get month from date
    currentMonth=$(echo $currentDate | cut -c -7)
    # Create monthly summary (first date in month)
    if [[ ! -e "$currentMonth.md" ]]; then
        if [[ -n "$lastMonth" ]]; then
            # Link to last month
            echo -e "[< $lastMonth]($lastMonth)\n" > "$currentMonth.md"
            # Link to current month in last month page
            sed -i "1s/\$/ | [$currentMonth >]($currentMonth)/" "$lastMonth.md"
            sed -i '1s/^ | //' "$lastMonth.md"
        else
            echo -e "\n" > "$currentMonth.md"
        fi
        echo -e "# $currentMonth\n" >> "$currentMonth.md"
        lastMonth="$currentMonth"
    fi
    # Summarise contents:
    # - first remove logbook links, links and blank lines
    # - use grep to find major headings (# and ##)
    # - remove line breaks and add colons
    # - replace headings with bullet points
    echo -e "## [$currentDate]($currentDate)" >> "$currentMonth.md"
    sed -e '/Logbook:/d' -e '/^\[.*]:/d' -e '/^$/d'  -e '1s|^| |' \
        -e 's|\[\([^]]*\)\]\[[^]]*\]|\1|g' -e 's|\[\([^]]*\)\]([^)]*)|\1|g' \
        "$currentDate.md" | \
    grep -Pzo -e "[^#]#{1,2} [^.:!?]*[.:!?]" | sed -e 's|:|.|g' | \
    sed -e 's|\(# .*\)$|\1: |g' | tr '\n' ' ' | tr -d '\r' | tr -d '\000' | \
    sed -e 's|## |\n    - |g' -e 's|# |\n* |g' -e 's| \* | |g' \
        >> "$currentMonth.md"
    echo -e "\n" >> "$currentMonth.md"
    # Add forward, back and up links to logbooks
    sed -i "1s/^\([^[]\)/\n\n\1/" "$currentDate.md"
    if [[ -n "$lastDate" ]]; then
        sed -i "1s/^.*\$/[< $lastDate]($lastDate)/" "$currentDate.md"
    else
        sed -i "1s/^.*\$//" "$currentDate.md"
    fi
    sed -i "1s/\$/ | [$currentMonth]($currentMonth)/" "$currentDate.md"
    if [[ -n "$lastDate" ]]; then
        sed -i "1s/\$/ | [$currentDate >]($currentDate)/" "$lastDate.md"
        sed -i '1s/^ | //' "$lastDate.md"
    fi
    lastDate="$currentDate"
done
