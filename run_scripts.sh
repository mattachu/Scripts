#!/bin/bash
# Functions for running programs

# Report the time taken since $SECONDS was reset
function time_taken {
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
function run_with_timer {
    SECONDS=0
    $*
    time_taken
}
# Run the given command with a log file
function run_with_log {
    rm -f $1.log
    echo "Current directory: " $(pwd -P) > >(tee -a $1.log) 2> >(tee -a $1.log >&2)
    echo "Current command: $*" > >(tee -a $1.log) 2> >(tee -a $1.log >&2)
    echo "Current time: " $(date) > >(tee -a $1.log) 2> >(tee -a $1.log >&2)
    SECONDS=0
    $* > >(tee -a $1.log) 2> >(tee -a $1.log >&2)
    time_taken > >(tee -a $1.log) 2> >(tee -a $1.log >&2)
    sleep 0.1
}
# Show progress of a run through subfolders, based on count of log files
function show_progress {
    runfolder="$*"
    if [[ -z $runfolder ]]; then runfolder="."; fi
    subfoldercount="$(ls -l $runfolder/*/*-current $runfolder/*/single 2>/dev/null | grep -c total)"
    if [ $subfoldercount == 0 ]; then subfoldercount="$(ls -l $runfolder/ 2>/dev/null | grep -c ^d)"; fi
    logfilecount="$(ls -l $runfolder/*/*.log $runfolder/*/*/*.log 2>/dev/null | grep -c log)"
    echo "Found log files in $logfilecount out of $subfoldercount subfolders"
}
# Create a subfolder for an Impact-T simulation with particular parameter value
function parameterise {
    input_file="$1"
    exe_name="impact-test"
    parameter_name="PARAM1"
    parameter_value="$2"
    mkdir -p ./$parameter_value
    cp *.in ./$parameter_value/
    cd ./$parameter_value
    ln -s ../*.data
    ln -s ../$exe_name
    cd ..
    cat $input_file | sed "s/$parameter_name/$parameter_value/" > $parameter_value/$input_file
}
# Recursive remove
function recursive_rm {
    find_command="find . -mindepth 0 -iname '$1'"
    for i in `seq 2 $#`; do
        find_command="${find_command} -o -iname '${!i}'"
    done
    for dir in `eval ${find_command}`; do
        echo "Deleting ${dir}"
        eval "rm -f ${dir}"
    done
}
