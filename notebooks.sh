#!/bin/bash
# Functions for working with notebook Markdown files
#
# General notes:
# - `sed -i''` works on both macOS (FreeBSD sed) and Ubuntu (GNU sed)
# - handling of new lines is tricky to match both systems

# Parameters
export datePattern="./[0-9]{4}-[0-9]{2}-[0-9]{2}.md"
export monthPattern="./[0-9]{4}-[0-9]{2}.md"
if [[ "$(uname)" == "Darwin" ]]; then
    export findCommand="find -E ."
else
    export findCommand="find . -regextype posix-egrep"
fi

# Build a set of monthly summaries from single notebook files
function indexLogbook()
{
    local logbookFolder="$*"
    if [[ -z $logbookFolder ]]; then logbookFolder="."; fi
    local startFolder=$(pwd)
    local lastDate=""
    local lastMonth=""

    cd "$logbookFolder"
    deleteMonthlySummaries
    getLogbookDateList "dateList"

    for currentDate in $dateList
    do
        getMonthFromDate "$currentDate" "currentMonth"
        if [[ ! -e "$currentMonth.md" ]]; then
            createMonthlySummary "$currentMonth" "$lastMonth"
            lastMonth="$currentMonth"
        fi
        addDateLinks "$currentDate" "$lastDate"
        summariseLogbookPage "$currentDate" >> "$currentMonth.md"
        lastDate="$currentDate"
    done
    cd "$startFolder"
}

# Function to summarise contents of a logbook page
function summariseLogbookPage()
{
    local thisDate="$1"
    if [[ -r "$thisDate.md" ]]; then
        printDateHeading "$thisDate"
        if [[ $(hasSummaryLine "$thisDate.md") == "true" ]]; then
            getSummaryLine "$thisDate.md"
        fi
        getHeadingsSummary "$thisDate.md"
    else
        echo "Cannot read file $thisDate.md"
    fi
}

# Function to read the first summary line from a logbook page
function getSummaryLine()
{
    local thisPage="$1"
    if [[ -r "$thisPage" ]]; then
        sed -e '1,2d' -e '/[.:!?]\s/q' -e '/[.:!?]$/q' "$thisPage" | \
        tr '\n' ' ' | tr -d '\r' | \
        sed -e 's/:/./' -e 's/`//g' -e 's/\([.:!?]\).*$/\1/' \
            -e 's/\[\([^]]*\)\]\[[^]]*\]/\1/g' \
            -e 's/\[\([^]]*\)\]([^)]*)/\1/g' \
            -e 's/^#.*$//'
        printBlankLine
    else
        echo "Cannot read file $thisPage"
    fi
}

# Function to produce a summary from the headings of a logbook page
# - `sed` on macOS cannot use '\n' so needs literal newlines
function getHeadingsSummary()
{
    local thisPage="$1"
    if [[ -r "$thisPage" ]]; then
        sed -e '/Logbook:/d' -e '/^\[.*]:/d' -e '/^$/d' -e 's/`//g' \
            -e 's/\[\([^]]*\)\]\[[^]]*\]/\1/g' -e 's/\[\([^]]*\)\]([^)]*)/\1/g' \
            "$thisPage" | \
        pcregrep -Mo -e '^#{1,2} [^.:!?#]*[.:!?#]' | \
        sed -e 's/:$/./g' -e 's/#$//g' -e 's/\(# .*\)$/\1: /g' | \
        tr '\n' ' ' | tr -d '\r' | \
        sed -e 's/  / /g' -e 's/  / /g' -e 's/[ ]*$//g' -e 's/## /\
    - /g' -e 's/[^#]# /\
* /g' -e 's/# /* /g' -e 's/ \* / /g'
        printBlankLine
    else
        echo "Cannot read file $thisPage"
    fi
}

# Function to get list of dates from a logbook folder
function getLogbookDateList()
{
    local __resultvar="$1"
    local myresult=$($findCommand -regex $datePattern | \
                     sort | \
                     sed -e 's|\./||' -e 's|\.md||')
    if [[ "$__resultvar" ]]; then
        eval $__resultvar="'$myresult'"
    else
        echo "$myresult"
    fi
}

# Function to delete existing monthly summary files
function deleteMonthlySummaries()
{
    $findCommand -regex $monthPattern -delete
}

# Function to create a new monthly summary page
function createMonthlySummary()
{
    local thisMonth="$1"
    local lastMonth="$2"
    printBlankLine > "$thisMonth.md"
    if [[ -n "$lastMonth" ]]; then
        linkNextDate "$thisMonth" "$lastMonth.md"
        linkLastDate "$lastMonth" "$thisMonth.md"
    fi
    printMonthHeading "$thisMonth" >> "$thisMonth.md"
}

# Function to add last, next and up links to logbook pages
function addDateLinks()
{
    local thisDate="$1"
    local lastDate="$2"
    if [[ -n "$thisDate" ]]; then
        blankFirstLine "$thisDate.md"
        if [[ -n "$lastDate" ]]; then
            linkNextDate "$thisDate" "$lastDate.md"
            linkLastDate "$lastDate" "$thisDate.md"
        fi
        addThisMonthLink "$thisDate"
    fi
}

# Function to blank the first line of the given page
# - if the first line has date links, these are removed
# - if the first line has other content, this is moved down
function blankFirstLine()
{
    local thisPage="$1"
    if [[ -w "$thisPage" ]]; then
        if [[ $(hasDateLink "$thisPage") == "true" ]]; then
            sed -i'' -e "1s/^.*\$//" "$thisPage"
        else
            addBlankLineAtStart "$thisPage"
        fi
    fi
}

# Function to produce month heading (level 1) for monthly summary page
function printMonthHeading()
{
    local thisMonth="$1"
    if [[ -n "$thisMonth" ]]; then
        echo -e "# $thisMonth\n"
    fi
}

# Function to produce date heading (level 2) for monthly summary page
function printDateHeading()
{
    local thisDate="$1"
    if [[ -n "$thisDate" ]]; then
        echo -e "## [$thisDate]($thisDate)\n"
    fi
}

# Function to replace first line with link to last date page
function linkLastDate()
{
    local lastDate="$1"
    local thisPage="$2"
    if [[ -n "$lastDate" && -w "$thisPage" ]]; then
        sed -i'' -e "1s/^.*\$/[< $lastDate]($lastDate)/" "$thisPage"
    fi
}

# Function to add link to the next date (day/month)
function linkNextDate()
{
    local nextDate="$1"
    local thisPage="$2"
    if [[ -n "$nextDate" && -w "$thisPage" ]]; then
        sed -i'' -e "1s/\$/ | [$nextDate >]($nextDate)/" "$thisPage"
        removeLeadingPipe "$thisPage"
    fi
}

# Function to add the link for the current month
function addThisMonthLink()
{
    local thisDate="$1"
    if [[ -n "$thisDate" && -w "$thisDate.md" ]]; then
        getMonthFromDate "$thisDate" "thisMonth"
        sed -i'' "1s/\$/ | [$thisMonth]($thisMonth)/" "$thisDate.md"
    fi
}

# Function to print a blank line, using different methods on macOS and Linux
function printBlankLine()
{
    if [[ "$(uname)" == "Darwin" ]]; then
        echo
        echo
    else
        echo -e "\n"
    fi
}

# Function to add a blank line at the start of a page
function addBlankLineAtStart()
{
    local thisPage="$1"
    if [[ -r $thisPage ]]; then
        cat "$thisPage" > ".tempLogbookPage.md"
        printBlankLine > "$thisPage"
        cat ".tempLogbookPage.md" >> "$thisPage"
        rm ".tempLogbookPage.md"
    else
        echo "Cannot read file $thisPage"
    fi
}

# Function to end the current line being written
function endLine()
{
    echo
}

# Function to remove unnecessary pipe characters at the start of a page
function removeLeadingPipe()
{
    local thisPage="$1"
    if [[ -w "$thisPage" ]]; then
        sed -i'' -e '1s/^ | //' "$thisPage"
    fi
}

# Function to work out month
function getMonthFromDate()
{
    local mydate="$1"
    local __resultvar="$2"
    local myresult=$(echo "$mydate" | cut -c -7)
    if [[ "$__resultvar" ]]; then
        eval $__resultvar="'$myresult'"
    else
        echo "$myresult"
    fi
}

# Function to check whether given page already has a date link
function hasDateLink()
{
    local thisPage="$1"
    if [[ -r "$thisPage" ]]; then
        if [[ -n $(head -n1 "$thisPage" | \
                   grep -E -e "^\[(< ){0,1}[0-9]{4}-[0-9]{2}") ]]
        then
            echo "true"
        else
            echo "false"
        fi
    else
        echo "Cannot read file $thisPage"
    fi
}

# Function to check whether given page has a summary before the first heading
function hasSummaryLine()
{
    local thisPage="$1"
    if [[ -r "$thisPage" ]]; then
        if [[ -n $(sed -n '3p' "$thisPage" | grep -e '^#') ]]
        then
            echo "false"
        else
            echo "true"
        fi
    else
        echo "Cannot read file $thisPage"
    fi
}
