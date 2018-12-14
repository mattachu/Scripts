#!/bin/bash
# Functions for working with notebook Markdown files
#
# Main user functions:
# - indexLogbook([logbookFolder])
#    Adds internal links and creates monthly summaries for logbooks.
# - convertSalaryTable(inputFile, [outputFile])
#    Takes a file with values copied from the Excel export from the PKU portal
#    and converts it to a Markdown table. If `outputFile` is not given, file is
#    modified in place.
#
# General notes:
# - `sed -i''` works on both macOS (FreeBSD sed) and Ubuntu (GNU sed)
# - handling of new lines is tricky to match both systems

# Parameters
export pagePattern="./.*.md"
export datePattern="./[0-9]{4}-[0-9]{2}-[0-9]{2}.md"
export monthPattern="./[0-9]{4}-[0-9]{2}.md"
export notebookContentsText="Contents"
export notebookContentsPage="Contents.md"
export notebookHomeText="Home"
export notebookHomePage="Home.md"
export notebookReadmePage="Readme.md"
export notebookAttachmentsFolder="Attachments"
export notebookLogbookFolder="Logbook"
export notebookRootFolder="Notebooks"
if [[ "$(uname)" == "Darwin" ]]; then
    export findCommand="find -E . -maxdepth 1"
else
    export findCommand="find . -maxdepth 1 -regextype posix-egrep"
fi

# ------------------------------------------------------------------------------
# Main user functions for working with notebooks

# Process entire notebook tree
function processNotebooks()
{
    local notebookFolder="$*"
    if [[ -z $notebookFolder ]]; then notebookFolder="."; fi
    local folderList=$(getFolderList "$notebookFolder")
    local currentFolder=""
    if [[ -n "$folderList" ]]; then
        for currentFolder in $folderList
        do
            processNotebooks $currentFolder
            echo "Processing folder $currentFolder..."
            if [[ "$(isLogbookFolder "$currentFolder")" == "true" ]]; then
                indexLogbook "$currentFolder"
            else
                buildNotebookContents "$currentFolder"
            fi
        done
    fi
}

# Build contents page for the given folder
function buildNotebookContents()
{
    local notebookFolder="$*"
    if [[ -z $notebookFolder ]]; then notebookFolder="."; fi
    local contentsPage="$notebookContentsPage"
    local startFolder=$(pwd)
    cd "$notebookFolder"
    rm -f "$contentsPage"
    getNotebookNavigation >> "$contentsPage"
    printBlankLine >> "$contentsPage"
    getFolderSummary >> "$contentsPage"
    local folderList=$(getFolderList)
    if [[ -n "$folderList" ]]; then
        echo -e "# Folders\n" >> "$contentsPage"
        for currentFolder in $folderList
        do
            printFolderHeading "$currentFolder" "withLinks" >> "$contentsPage"
            getFolderSummary "$currentFolder" >> "$contentsPage"
        done
    fi
    local pageList="$(getPageList)"
    if [[ -n "$pageList" ]]; then
        echo -e "# Pages\n" >> "$contentsPage"
        for currentPage in $pageList
        do
            addNotebookNavigation "$currentPage"
            printPageHeading "$currentPage" "withLinks" >> "$contentsPage"
            getPageSummary "$currentPage" >> "$contentsPage"
        done
    fi
    cd "$startFolder"
}

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
    dateList=$(getLogbookDateList)
    for currentDate in $dateList
    do
        currentMonth=$(getMonthFromDate "$currentDate")
        if [[ ! -e "$currentMonth.md" ]]; then
            createMonthlySummary "$currentMonth" "$lastMonth"
            lastMonth="$currentMonth"
        fi
        addDateLinks "$currentDate" "$lastDate"
        summariseLogbookPage "$currentDate" >> "$currentMonth.md"
        printBlankLine >> "$currentMonth.md"
        lastDate="$currentDate"
    done
    buildLogbookContents
    cd "$startFolder"
}

# Convert salary data copied from Excel
function convertSalaryTable()
{
    local inputFile="$1"
    local outputFile="$2"
    local tempFile=".tempSalaryTable.md"
    if [[ -r "$inputFile" ]]; then
        if [[ ! -n "$outputFile" ]]; then
            outputFile="$tempFile"
        fi
        convertSalaryHeaders "$inputFile" > "$outputFile"
        convertSalaryBody "$inputFile" >> "$outputFile"
        if [[ "$outputFile" == "$tempFile" ]]; then
            mv "$tempFile" "$inputFile"
        fi
    else
        echo "Cannot read file $inputFile"
    fi
}

# ------------------------------------------------------------------------------
# Functions for processing notebooks and subfolders

# Function to get list of pages in the current folder, excluding special pages
function getPageList()
{
    getMatchingPageList "$pagePattern" | \
        sed -e "s/\b\($notebookContentsPage\|$notebookReadmePage\)\b//g" \
            -e 's/^[ ]*//'
}

# Function to get list of pages matching the given pattern
function getMatchingPageList()
{
    local matchingPattern="$1"
    if [[ -n "$matchingPattern" ]]; then
        echo $($findCommand -regex $matchingPattern | \
               sort | \
               sed -e 's|\./||')
    fi
}

# Function to get path relative to the notebook root folder
function getRelativeNotebookPath()
{
    local thisFolder="$*"
    if [[ -z $thisFolder ]]; then thisFolder="$(pwd)"; fi
    local rootFolder="$notebookRootFolder"
    echo "$thisFolder" | sed -e "s|.*/$rootFolder/||"
}

# Function to get list of subfolders, excluding special folders
function getFolderList()
{
    local notebookFolder="$*"
    if [[ -z $notebookFolder ]]; then notebookFolder="."; fi
    ls -d $notebookFolder/*/ 2> /dev/null | \
    sed -e "s|\($notebookFolder/$notebookAttachmentsFolder/\)||g" \
        -e 's|\./||g' -e 's|/ | |g' -e 's|/$||g' -e 's| $||g'
}

# Function to get navigation links for notebook pages in the current folder
function getNotebookNavigation()
{
    local thisFolder="$(getRelativeNotebookPath)"
    local contentsPage="$(echo $notebookContentsPage | sed -e 's/\.md//')"
    local homeText="$notebookHomeText"
    local homePage="$(echo $notebookHomePage | sed -e 's/\.md//')"
    local homeLink=""
    local navLinks=""
    local currentLevel=""
    local currentLink=""
    local currentTitle=""
    local remainingPath="$thisFolder"
    while [[ -n "$remainingPath" ]]
    do
        currentLink="$currentLevel$contentsPage"
        currentTitle="$(echo "$remainingPath" | \
                        sed -e 's|/$||' -e 's|.*/\([^/]*\)$|\1|')"
        navLinks=" > [$currentTitle]($currentLink)$navLinks"
        remainingPath="$(echo "$remainingPath" | \
                         sed -e 's|/$||' -e 's|[^/]*$||')"
        currentLevel="../$currentLevel"
    done
    homeLink="$currentLevel$homePage"
    navLinks="[$homeText]($homeLink)$navLinks"
    echo "$navLinks"
}

# Function to add navigation links to notebook pages
function addNotebookNavigation()
{
    local thisPage="$1"
    local navLinks="$(getNotebookNavigation)"
    if [[ -w "$thisPage" ]]; then
        blankFirstLine "$thisPage"
        sed -i'' -e "1s|^.*\$|$navLinks|" "$thisPage"
    fi
}

# Function to produce page heading (level 2) for given notebook page
function printPageHeading()
{
    local thisPage="$1"
    local style="$2"
    if [[ -n "$thisPage" ]]; then
        local pageTitle=$(getPageTitle "$thisPage")
        case "$style" in
        "withLinks")
            echo -e "## [$pageTitle]($thisPage)\n" | sed -e 's/\.md//' ;;
        *)
            echo -e "## $pageTitle\n" ;;
        esac
    fi
}

# Function to produce folder heading (level 2) for given notebook subfolder
function printFolderHeading()
{
    local thisFolder="$1"
    local style="$2"
    local contentsPage=$(echo "$notebookContentsPage" | sed -e 's/\.md//')
    if [[ -d "$thisFolder" ]]; then
        case "$style" in
        "withLinks")
            echo -e "## [$thisFolder]($thisFolder/$contentsPage)\n" ;;
        *)
            echo -e "## $thisFolder\n" ;;
        esac
    fi
}

# Function to get a page's title (from the title line or the file name)
function getPageTitle()
{
    local thisPage="$1"
    local pageTitle=""
    if [[ -r "$thisPage" ]]; then
        local i="1"
        while [[ "$(getNotebookLineType "$thisPage" "$i")" == "Navigation line" \
              || "$(getNotebookLineType "$thisPage" "$i")" == "Blank line" ]]
        do
            i=$(($i + 1))
        done
        if [[ "$(getNotebookLineType "$thisPage" "$i")" == "Title line" ]]; then
            pageTitle="$(getNotebookLine "$thisPage" "$i" | sed -e 's/^# //')"
        else
            pageTitle=$(echo "$thisPage" | sed -e 's/[_\-]/ /g' -e 's/\.md//')
        fi
        echo $pageTitle
    else
        echo "Cannot read file $thisPage"
    fi
}

# Function to get the content of a page, ignoring navigation links and titles
function getPageContent()
{
    local thisPage="$1"
    if [[ -r "$thisPage" ]]; then
        local i="1"
        until [[ "$(getNotebookLineType "$thisPage" "$i")" == "Content line" ]]
        do
            i=$(($i + 1))
        done
        sed -e "1,$(($i-1))d" "$thisPage"
    else
        echo "Cannot read page $thisPage"
    fi
}

# Function to check what type of information is on a given line on a page
function getNotebookLineType()
{
    local thisPage="$1"
    local thisLineNumber="$2"
    local thisLine=""
    local thisLineType=""
    if [[ -r "$thisPage" ]]; then
        thisLine="$(getNotebookLine "$thisPage" "$thisLineNumber")"
        thisLineType="$(echo "$thisLine" | \
                        sed -n -e 's|^# .*$|Title line|p' \
                               -e 's|^\[[^]]*\]([^)]*).*$|Navigation line|p' \
                               -e 's|^$|Blank line|p' )"
        if [[ ! -n "$thisLineType" ]]; then thisLineType="Content line"; fi
        echo "$thisLineType"
    else
        echo "Cannot read page $thisPage"
    fi
}

# Function to print a given line from a page
function getNotebookLine()
{
    local thisPage="$1"
    local thisLineNumber="$2"
    if [[ -r "$thisPage" ]]; then
        sed -n -e "${thisLineNumber}p" "$thisPage"
    else
        echo "Cannot read page $thisPage"
    fi
}

# Function to get the first full paragraph from a page
function getPageSummary()
{
    local thisPage="$1"
    if [[ -r "$thisPage" ]]; then
        getPageContent "$thisPage" | \
        tr -d '\r' | sed -e '/^$/q' | \
        sed -e 's/\[\([^]]*\)\]\[[^]]*\]/\1/g' \
            -e 's/\[\([^]]*\)\]([^)]*)/\1/g' \
            -e 's/  / /g' -e 's/  / /g' -e 's/[ ]*$//g' -e 's/:$/./g'
    else
        echo "Cannot read file $thisPage"
    fi
}

# Function to get the folder summary from the Readme file
function getFolderSummary()
{
    local notebookFolder="$*"
    if [[ -z $notebookFolder ]]; then notebookFolder="."; fi
    local readmePage="$notebookReadmePage"
    if [[ -r "$notebookFolder/$readmePage" ]]; then
        cat "$notebookFolder/$readmePage"
        printBlankLine
    fi
}

# Function to blank the first line of the given page
# - if the first line has navigation links, these are removed
# - if the first line has other content, this is moved down
function blankFirstLine()
{
    local thisPage="$1"
    if [[ -w "$thisPage" ]]; then
        if [[ $(hasNotebookNavigation "$thisPage") == "true" ]]; then
            sed -i'' -e "1s/^.*\$//" "$thisPage"
        else
            addBlankLineAtStart "$thisPage"
        fi
    fi
}

# Function to print a blank line, using different methods on macOS and Linux
function printBlankLine()
{
    if [[ "$(uname)" == "Darwin" ]]; then
        echo
        echo
    else
        echo -ne "\n"
    fi
}

# Function to add a blank line at the start of a page
function addBlankLineAtStart()
{
    local thisPage="$1"
    if [[ -r $thisPage ]]; then
        cat "$thisPage" > ".tempLogbookPage.md"
        printBlankLine > "$thisPage"
        printBlankLine >> "$thisPage"
        cat ".tempLogbookPage.md" >> "$thisPage"
        rm ".tempLogbookPage.md"
    else
        echo "Cannot read file $thisPage"
    fi
}

# Function to remove unnecessary pipe characters at the start of a page
function removeLeadingPipe()
{
    local thisPage="$1"
    if [[ -w "$thisPage" ]]; then
        sed -i'' -e '1s/^ | //' "$thisPage"
    fi
}

# Function to check whether given page already has navigation links
function hasNotebookNavigation()
{
    local thisPage="$1"
    if [[ -r "$thisPage" ]]; then
        if [[ -n $(head -n1 "$thisPage" | grep -E -e "^\[[^]]*\]([^)]*)") ]]
        then
            echo "true"
        else
            echo "false"
        fi
    else
        echo "Cannot read file $thisPage"
    fi
}

# Function to check whether a given folder is a logbook
function isLogbookFolder()
{
    local notebookFolder="$*"
    local logbookFolder="$notebookLogbookFolder"
    if [[ -z $notebookFolder ]]; then notebookFolder="."; fi
    notebookFolder="$(echo "$notebookFolder" | \
                      sed -e 's|/$||' -e 's|[^/]*/||g')"
    if [[ "$notebookFolder" == "$logbookFolder" ]]; then
        echo "true"
    else
        echo "false"
    fi
}

# ------------------------------------------------------------------------------
# Functions for processing logbook entries

# Function to build a contents page from existing monthly summary pages
function buildLogbookContents()
{
    local contentsPage="$notebookContentsPage"
    rm -f "$contentsPage"
    getNotebookNavigation >> "$contentsPage"
    printBlankLine >> "$contentsPage"
    monthList=$(getLogbookMonthList)
    for currentMonth in $monthList
    do
        printMonthHeading "$currentMonth" "full+links" >> $contentsPage
        getPageContent "$currentMonth.md" >> $contentsPage
    done
}

# Function to summarise contents of a logbook page
function summariseLogbookPage()
{
    local thisDate="$1"
    if [[ -r "$thisDate.md" ]]; then
        printDateHeading "$thisDate"
        if [[ $(hasSummaryLine "$thisDate.md") == "true" ]]; then
            getSummaryLine "$thisDate.md"
            printBlankLine
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
    getMatchingPageList "$datePattern" | sed -e 's/\.md//g'
}

# Function to get list of months from a logbook folder
function getLogbookMonthList()
{
    getMatchingPageList "$monthPattern" | sed -e 's/\.md//g'
}

# Function to convert a numeric date (XXXX-XX-XX) to a full date
function getFullDate()
{
    local thisDate="$1"
    if [[ -n "$thisDate" ]]; then
        local thisYear=$(echo "$thisDate" | cut -c -4)
        local thisMonth=$(echo "$thisDate" | cut -c 6-7)
        local thisDay=$(echo "$thisDate" | cut -c 9-10 | sed -e 's/^0//')
        case "$thisMonth" in
        "01")
            thisMonth="January" ;;
        "02")
            thisMonth="February" ;;
        "03")
            thisMonth="March" ;;
        "04")
            thisMonth="April" ;;
        "05")
            thisMonth="May" ;;
        "06")
            thisMonth="June" ;;
        "07")
            thisMonth="July" ;;
        "08")
            thisMonth="August" ;;
        "09")
            thisMonth="September" ;;
        "10")
            thisMonth="October" ;;
        "11")
            thisMonth="November" ;;
        "12")
            thisMonth="December" ;;
        esac
        if [[ -n "$thisDay" ]]; then
            echo "$thisDay $thisMonth $thisYear"
        else
            echo "$thisMonth $thisYear"
        fi
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
    printBlankLine >> "$thisMonth.md"
    if [[ -n "$lastMonth" ]]; then
        linkNextDate "$thisMonth" "$lastMonth.md"
        linkLastDate "$lastMonth" "$thisMonth.md"
    fi
    addContentsLink "$thisMonth.md"
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

# Function to produce month heading (level 1) for monthly summary page
function printMonthHeading()
{
    local thisMonth="$1"
    local style="$2"
    if [[ -n "$thisMonth" ]]; then
        case "$style" in
        "withLinks")
            echo -e "# [$thisMonth]($thisMonth)\n" ;;
        "full")
            echo -e "# $(getFullDate $thisMonth)\n" ;;
        "full+links")
            echo -e "# [$(getFullDate $thisMonth)]($thisMonth)\n" ;;
        *)
            echo -e "# $thisMonth\n" ;;
        esac
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

# Function to add the link for the contents page
function addContentsLink()
{
    local thisPage="$1"
    local contentsPage="$(echo $notebookContentsPage | sed -e 's/\.md//')"
    local contentsText="$notebookContentsText"
    if [[ -w "$thisPage" ]]; then
        sed -i'' "1s/\$/ | [$contentsText]($contentsPage)/" "$thisPage"
    fi
}

# Function to add the link for the current month
function addThisMonthLink()
{
    local thisDate="$1"
    if [[ -n "$thisDate" && -w "$thisDate.md" ]]; then
        thisMonth=$(getMonthFromDate "$thisDate")
        sed -i'' "1s/\$/ | [$thisMonth]($thisMonth)/" "$thisDate.md"
    fi
}

# Function to work out month
function getMonthFromDate()
{
    local mydate="$1"
    echo "$mydate" | cut -c -7
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

# ------------------------------------------------------------------------------
# Functions for processing salary tables

# Function to process the headers for a salary table file copied from Excel
function convertSalaryHeaders()
{
    local inputFile="$1"
    if [[ -r "$inputFile" ]]; then
        convertSalaryFirstLine "$inputFile"
        createSalaryLineFormat "$inputFile"
        convertSalarySecondLine "$inputFile"
    else
        echo "Cannot read file $inputFile"
    fi
}

# Function to process the main header line for a salary table
function convertSalaryFirstLine()
{
    local inputFile="$1"
    if [[ -r "$inputFile" ]]; then
        sed -n -e '1s/\t/ | /gp' "$inputFile"
    else
        echo "Cannot read file $inputFile"
    fi
}

# Function to produce the line formatting for a salary table
function createSalaryLineFormat()
{
    local inputFile="$1"
    if [[ -r "$inputFile" ]]; then
        sed -n -e '1s/\t/|/g' -e '1s/[^\|]*/---/gp' "$inputFile"
    else
        echo "Cannot read file $inputFile"
    fi
}

# Function to process the secondary header line for a salary table
function convertSalarySecondLine()
{
    local inputFile="$1"
    if [[ -r "$inputFile" ]]; then
        sed -n -e '2s/\t/ | /g' -e '2s/$/| /p' "$inputFile"
    else
        echo "Cannot read file $inputFile"
    fi
}

# Function to process the body for a salary table file copied from Excel
function convertSalaryBody()
{
    local inputFile="$1"
    if [[ -r "$inputFile" ]]; then
        sed -e '1,3d' -e '/^\t/d' -e '/^$/d' -e 's/\t/ | /g' "$inputFile"
    else
        echo "Cannot read file $inputFile"
    fi
}
