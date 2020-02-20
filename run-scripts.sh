#!/bin/bash
# Functions for running programs

# Load machine-specific locations
if [ -r "${HOME}/.locations" ]; then
    source "${HOME}/.locations"
fi

# Report the time taken since $SECONDS was reset
function time-taken {
    if (( $SECONDS > 3600 )) ; then
        let "hours=SECONDS/3600"
        let "minutes=(SECONDS%3600)/60"
        let "seconds=(SECONDS%3600)%60"
        echo "Completed in $hours hour(s), $minutes minute(s) and $seconds second(s)"
    elif (( $SECONDS > 60 )) ; then
        let "minutes=(SECONDS%3600)/60"
        let "seconds=(SECONDS%3600)%60"
        echo "Completed in $minutes minute(s) and $seconds second(s)"
    else
        echo "Completed in $SECONDS seconds"
    fi
}

# Run the given command with a timer
function run-with-timer {
    SECONDS=0
    $*
    time-taken
}

# Run the given command with a log file
function run-with-log {
    local logFile="$(echo "$1" | sed -e 's|.*/\([^/]*\)$|\1|' -e 's|$|.log|' )"
    rm -f $logFile
    echo "Current directory: " $(pwd -P) > >(tee -a $logFile) 2> >(tee -a $logFile >&2)
    echo "Current command: $*" > >(tee -a $logFile) 2> >(tee -a $logFile >&2)
    echo "Current time: " $(date) > >(tee -a $logFile) 2> >(tee -a $logFile >&2)
    local githash=$(git log -n1 --format=format:"%H" 2>/dev/null)
    if [[ -n $githash ]]; then
        echo "Current commit: $githash" > >(tee -a $logFile) 2> >(tee -a $logFile >&2);
    fi
    SECONDS=0
    $* > >(tee -a $logFile) 2> >(tee -a $logFile >&2)
    time-taken > >(tee -a $logFile) 2> >(tee -a $logFile >&2)
    sleep 0.1
}

# Run the given command reproducibly with a log file
function reproduce-with-log {
    run-with-log "${CODE_FOLDER}/Reproducible/reproduce" "$*"
}

# Show progress of a run through subfolders, based on count of log files
function show-progress {
    runfolder="$*"
    if [[ -z $runfolder ]]; then runfolder="."; fi
    subfoldercount="$(ls -l $runfolder/*/*-current $runfolder/*/single 2>/dev/null | grep -c total)"
    if [ $subfoldercount == 0 ]; then subfoldercount="$(ls -l $runfolder/ 2>/dev/null | grep -c ^d)"; fi
    logfilecount="$(ls -l $runfolder/*/*.log $runfolder/*/*/*.log 2>/dev/null | grep -c log)"
    echo "Found log files in $logfilecount out of $subfoldercount subfolders"
}

# Create a subfolder for an Impact-T simulation with particular parameter value
function parameterise {
    inputfile="$1"
    exename="impact-test"
    parametername="PARAM1"
    parametervalue="$2"
    mkdir -p ./$parametervalue
    cp *.in ./$parametervalue/
    cd ./$parametervalue
    ln -s ../*.data
    ln -s ../$exename
    cd ..
    cat $inputfile | sed "s/$parametername/$parametervalue/" > $parametervalue/$inputfile
}

# Recursive remove
function recursive-rm {
    findcommand="find . -mindepth 0 -iname '$1'"
    for i in `seq 2 $#`; do
        findcommand="${findcommand} -o -iname '${!i}'"
    done
    for dir in `eval ${findcommand}`; do
        echo "Deleting ${dir}"
        eval "rm -f ${dir}"
    done
}

# Archive simulation
SIM_INPUT_FILES="*.in *.gmad *.data *.txt *.xlsx"
SIM_OUTPUT_FILES="*.log fort.* *.dst *.plt" # Impact-T
SIM_OUTPUT_FILES="${SIM_OUTPUT_FILES} *.root *.png *.eps" # BDSIM
SIM_OUTPUT_FILES="${SIM_OUTPUT_FILES} *.h5 *.lbal *.stat *.dat data" # OPAL
function archive {
    archivefolder="$*"
    if [[ -d $archivefolder ]]; then
        mv -i $(ls -d ${SIM_OUTPUT_FILES} 2>/dev/null | grep -v 'simulations.log') "$archivefolder"
        cp -ai $(ls -d ${SIM_INPUT_FILES} 2>/dev/null | grep -v 'simulations.log') "$archivefolder"
        eval "reproduce log -n1 > \"$archivefolder/simulation.log\""
    else
        echo "Could not find archive folder $archivefolder"
    fi
}

# Remove output files
function rm-output {
    filelist=$(ls -d ${SIM_OUTPUT_FILES} 2>/dev/null | grep -v 'simulations.log')
    if [[ -n $filelist ]]
    then
        if [[ "$1" == "--force" ]]
        then
            rm -rvf $filelist
        else
            rm -rvi $filelist
        fi
    fi
}

# Run a simulation for a list of parameter values
# - only one parameter can be swept
# - uses _Git_ branches `run` and `log` and uses tags for each parameter value
#    - these need to be set up before the start
# - syntax: `run-list "list" "command" "hash" "parameters" "template" "archive"`
# - parameters:
#    - `list` is the list of parameter values, e.g. "100 200 300 400"
#    - `command` is the command to run (after the `--` in `reproduce` command)
#    - `hash` is the run hash to base the simulation on (i.e. previous run)
#    - `parameters` is the parameter list, with the parameter you want to vary
#       left blank at the end, e.g. "I:50.0e-3,interact:0,Np:"
#    - `template` is the input file to be modified by `reproduce`
#    - `archive` is the root folder for archiving; separate subfolders will be
#       created for each run
function run-list
{
    local runList="$1"
    local runCommand="$2"
    local runHash="$3"
    local runParameters="$(echo "$4" | sed -e 's|:$||')"
    local templateFile="$5"
    local archiveFolder="$(echo "$6" | sed -e 's|/$||')"
    local gitRun="run"
    local gitLog="log"
    for currentRun in $runList
    do
        echo "Starting run $currentRun..."
        git checkout $gitRun
        git reset --hard $currentRun
        git cherry-pick -n $gitLog
        reproduce-with-log run --hash $runHash \
                               -p "$runParameters:$currentRun" \
                               --template="$templateFile" \
                               --list-parameters --show \
                               -- "$runCommand"
        echo "Archiving run $currentRun..."
        mkdir -p "$archiveFolder/$currentRun"
        rm -rf "\"$archiveFolder/$currentRun\"/*"
        archive "$archiveFolder/$currentRun"
        rm-output --force
        git add simulations.log
        git commit -m "Run log"
        git checkout $gitLog
        git reset --hard $gitRun
        echo "Run $currentRun complete."
        beep
    done
    echo "Parametric run complete."
}
