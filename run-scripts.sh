#!/bin/bash
# Functions for running programs

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
    rm -f $1.log
    echo "Current directory: " $(pwd -P) > >(tee -a $1.log) 2> >(tee -a $1.log >&2)
    echo "Current command: $*" > >(tee -a $1.log) 2> >(tee -a $1.log >&2)
    echo "Current time: " $(date) > >(tee -a $1.log) 2> >(tee -a $1.log >&2)
    githash=$(git log -n1 --format=format:"%H" 2>/dev/null)
    if [[ -n $githash ]]; then echo "Current commit: $githash" > >(tee -a $1.log) 2> >(tee -a $1.log >&2); fi
    SECONDS=0
    $* > >(tee -a $1.log) 2> >(tee -a $1.log >&2)
    time-taken > >(tee -a $1.log) 2> >(tee -a $1.log >&2)
    sleep 0.1
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
SIM_INPUT_FILES="*.in *.gmad *.data *.txt"
SIM_OUTPUT_FILES="*.log fort.* *.dst *.plt" # Impact-T
SIM_OUTPUT_FILES="${SIM_OUTPUT_FILES} *.root *.png *.eps" # BDSIM
SIM_OUTPUT_FILES="${SIM_OUTPUT_FILES} *.h5 *.lbal *.stat *.dat data" # OPAL
function archive {
    archivefolder="$*"
    if [[ -d $archivefolder ]]; then
        cp -ai $(ls -d ${SIM_INPUT_FILES} ${SIM_OUTPUT_FILES} 2>/dev/null | grep -v 'simulations.log') "$archivefolder"
        eval "reproduce log -n1 > \"$archivefolder/reproduce.log\""
    else
        echo "Could not find archive folder $archivefolder"
    fi
}
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
