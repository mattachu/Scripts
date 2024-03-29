#!/usr/bin/env python3
"""Run a batch of simulations reproducibly.

Usage:
  run_batch.py <command>
  run_batch.py [options] [--] <command>
  run_batch.py [--git [--input_branch=<branch>]... [--results_branch=<branch>]]
               [--archive [--full]] [--class=<class>]
               [--sweep=<sweep>]...
               [--post=<command>]
               [--clean]
               [options] [--] <command>
  run_batch.py --help

Options:
  -h --help                 Show this screen.
  -g --git                  Use Git to checkout input files and record results.
  -a --archive              Save the results of each run in an archive folder.
  -f --full                 Save full data files to archive folder.
  -d --clean                Clean up by deleting results files after completion.
  --class=<class>           Specify the simulation class (see below)
  --input_branch=<branch>   Specify an input branch in Git.
                            Can be specified multiple times to run for multiple
                            input branches.
  --results_branch=<branch> Specify a results branch in Git.
                            Does not allow multiple branches.
  --post=<command>          Specify a post-processing command.
  --sweep=<key:v1,v2,v3...> Specify a parametric sweep with multiple values for
                            parameters leading to multiple runs.
                            Multiple parameters can be specified independently,
                            such as --sweep='a:1,2' --sweep='b:2,4'
                            or connected, like --sweep='(a,b):(1,2),(2,4)'.
                            With separate specification, all combinations are
                            simulated (e.g. (1,2), (1,4), (2,2) and (2,4)).
                            With connected specification, only the given
                            combinations are simulated (e.g. (1,2) and (2,4)).
                            See below for more examples.

Options passed to Reproducible:
  --config <configfile>     Overwrite the location of Reproducible config file.
  --logfile <logfile>       Overwrite the name of the Reproducible log file.
  -l --runlog               Save a run log to file for each Reproducible run.
  -d --devel                Run Reproducible in developer mode.

Options passed to Reproducible run:
  --template <template>     the name of the file(s) that should be treated
                            as a template inside the command;
                            for multiple templates separate with commas
  --src <sourcedir>         check the source code at <sourcedir>
  --build                   build the code from source using `make install`
  --hash <oldhash>          pre-load parameters from this run
  --show                    print out rendered template
  --save                    save the rendered template to file
  --list-parameters         list all parameters that need to be set
  -p <key:value>            for several parameters use k1:v1,k2:v2 syntax

Simulation classes:
  impact                    Simulations with Impact-T or Impact-Z.
                            Input files: *.in *.data *.txt *.xlsx
                            Output files: fort.* *.dst *.plt
  bdsim                     Simulations with BDSIM.
                            Input files: *.gmad *.data *.txt *.xlsx
                            Output files: *.root *.png *.eps
  opal                      Simulations with OPAL.
                            Input files: *.in *.data *.txt *.xlsx
                            Output files: *.h5 *.lbal *.stat *.dat data

Examples:

run_batch.py "echo Hello world"

    Run a single command reproducibly.
    This will call `reproduce run -- "echo Hello world"` without other options.

run_batch.py -l "echo Hello world"

    Pass a command to the reproduce script.
    This will call `reproduce --runlog run -- "echo Hello world"`.

run_batch.py --class=impact -- ImpactTexe

    Run a simulation reproducibly in Impact-T.
    This will call `reproduce run -- ImpactTexe` without any other options.

run_batch.py --git --input_branch=develop --results_branch=results \\
             --class=impact -- ImpactTexe

    First checkout input files from the 'develop' branch and 'simulations.log'
    from the 'results' branch, then run the simulation in Impact, then check
    in 'simulations.log' as a new commit on the 'results' branch.
    The simulation will be run as `reproduce run -- ImpactTexe`.

run_batch.py --git --input_branch=input/full --input_branch=input/nospacecharge
             --results_branch=results --class=impact -- ImpactTexe

    Run the same simulation reproducibly using two different input branches.
    This will result in two separate commits in the results branch.

run_batch.py --template=ImpactT.in --sweep=I:0.0,0.2,0.4,0.6 \\
             --class=impact -- ImpactTexe

    Sweep through the parameter options for beam current I.
    The input file 'ImpactT.in' should be set up as a template with {{I}} in
    place of the beam current, and a separate simulation will be run for each
    parameter value:
        reproduce run --template ImpactT -p I:0.0 -- ImpactTexe
        reproduce run --template ImpactT -p I:0.2 -- ImpactTexe
        reproduce run --template ImpactT -p I:0.4 -- ImpactTexe
        reproduce run --template ImpactT -p I:0.6 -- ImpactTexe
    If `--git` is specified, each run result will be in a separate commit.
    If `--archive` is specified, each run will be archived to a separate folder.
    If `--runlog` is specified, each run will produce a separate log.

run_batch.py --template=ImpactT.in --sweep=I:0.0,0.2,0.4,0.6 --sweep=E:1.0,1.5 \\
             --class=impact -- ImpactTexe

    Double parametric sweep for beam current I and energy E.
    The input file 'ImpactT.in' should be set up as a template with {{I}} in
    place of the beam current, and {{E}} in place of the beam energy.
    All combinations of parameter values for the two sweeps will run in separate
    simulations:
        reproduce run --template ImpactT -p I:0.0,E:1.0 -- ImpactTexe
        reproduce run --template ImpactT -p I:0.2,E:1.0 -- ImpactTexe
        reproduce run --template ImpactT -p I:0.4,E:1.0 -- ImpactTexe
        reproduce run --template ImpactT -p I:0.6,E:1.0 -- ImpactTexe
        reproduce run --template ImpactT -p I:0.0,E:1.5 -- ImpactTexe
        reproduce run --template ImpactT -p I:0.2,E:1.5 -- ImpactTexe
        reproduce run --template ImpactT -p I:0.4,E:1.5 -- ImpactTexe
        reproduce run --template ImpactT -p I:0.6,E:1.5 -- ImpactTexe

run_batch.py --template=ImpactT.in --sweep=(I,E):(0.0,1.0),(0.2,1.0),(0.4,1.5) \\
             --class=impact -- ImpactTexe

    Single parametric sweep for multiple parameters I and E.
    The input file 'ImpactT.in' is set up as a template with {{I}} and {{E}}
    as above, but only the given combinations of parameter values will run:
        reproduce run --template ImpactT -p I:0.0,E:1.0 -- ImpactTexe
        reproduce run --template ImpactT -p I:0.2,E:1.0 -- ImpactTexe
        reproduce run --template ImpactT -p I:0.4,E:1.5 -- ImpactTexe

"""

import sys
import os
import pathlib
import git
import subprocess
import shutil
from datetime import datetime
from docopt import docopt
import itertools
import unicodedata
import re

# User settings
REPRODUCIBLE = '~/Code/Reproducible'
PYENV        = '~/.pyenv'
LOGFILE      = 'simulations.log'
ARCHIVE_LOG  = 'simulation.log'
ARCHIVE_ROOT = '~/Simulations/'


# Utility methods
def get_folder(folder_path = '.'):
    """Get an absolute path object from a given path"""
    return pathlib.Path(folder_path).expanduser().absolute()

def get_date_as_folder_name():
    """Get a date string in YYYY-MM-DD format for making an archive folder"""
    return datetime.today().strftime('%Y-%m-%d')

def get_safe_folder_name(value):
    """Get a name for a folder without special characters."""
    value = unicodedata.normalize('NFKD', value)
    value = value.encode('ascii', 'replace').decode('ascii')
    value = re.sub(r'[^\.\w\s-]', '-', re.sub(r'\?', '_', value)).strip()
    value = re.sub(r'([^0-9])\.([^0-9])', r'\1-\2', value)
    value = re.sub(r'-$', '', re.sub(r'[-\s]+', '-', value))
    return value

def get_archive_folder(archive_root):
    """Get an absolute path object for a new archive folder with today's date"""
    if not archive_root.is_dir():
        raise OSError(f'Archive location not found: {archive_root}')
    else:
        return archive_root.joinpath(get_date_as_folder_name())

def get_python_for_reproducible(reproducible_folder, pyenv_folder):
    """Get the path of the correct version of Python to run Reproducible"""
    if not reproducible_folder.is_dir():
        raise OSError('Reproducible script folder not found: '
                      + str(reproducible_folder))
    if (reproducible_folder.joinpath('.python-version').is_file()
        and pyenv_folder.is_dir()):
        with open(reproducible_folder.joinpath('.python-version'), 'r') as f:
            python_version = f.readline().strip()
        return str(pyenv_folder.joinpath('versions')
                   .joinpath(python_version)
                   .joinpath('bin/python3'))
    else:
        return 'python3'

# Communication methods
def announce(message):
    """Announce a given message."""
    print(str(message))

def announce_error(message):
    """Announce a given error message."""
    print(str(message), file=sys.stderr)

def announce_start(this_run):
    """Announce that a particular run is about to start"""
    print('-----------------------------------------------------------------')
    announce(f'Start of run: {this_run["title"]}')
    print()

def announce_end(this_run):
    """Announce that a particular run has finished"""
    print()
    announce(f'End of run: {this_run["title"]}')
    print('-----------------------------------------------------------------')

# Git methods
def get_git_repo(repo_path):
    """Return a repo object for the Git repo at a given path"""
    if not pathlib.Path(repo_path).is_dir():
        raise OSError(f'Repo folder not found: {repo_path}')
    else:
        return git.Repo(repo_path)

def git_checkout(repo, branch_name):
    """Check out the given branch"""
    if not isinstance(repo, git.Repo):
        raise TypeError(f'Not a valid repo: {repo}')
    repo.heads[branch_name].checkout()

def git_switch(repo, branch_name):
    """Switch branches without checking anything out"""
    if not isinstance(repo, git.Repo):
        raise TypeError(f'Not a valid repo: {repo}')
    repo.head.reference = repo.heads[branch_name]
    repo.head.reset(index=True, working_tree=False)

def git_get_file(repo, branch_name, file_name):
    """Checkout a single file from a given branch"""
    if not isinstance(repo, git.Repo):
        raise TypeError(f'Not a valid repo: {repo}')
    repo.git.checkout(branch_name, '--', file_name)

def git_commit(repo, commit_files, commit_message):
    """Add and commit the given files"""
    if not isinstance(repo, git.Repo):
        raise TypeError(f'Not a valid repo: {repo}')
    repo.index.add(commit_files)
    repo.index.commit(commit_message)

def get_input_branch(repo, given_input_branch):
    """Get a list of all input branches, unless given an override"""
    if given_input_branch:
        if not (   isinstance(given_input_branch, str)
                or isinstance(given_input_branch, list)):
            raise ValueError('Invalid input for input branch: '
                             + str(given_input_branch))
        else:
            input_branch = given_input_branch
    else:
        input_branch = [head.name for head in repo.heads
                        if 'input' in head.name]
        if len(input_branch) == 1:
            input_branch = input_branch[0]
    if isinstance(input_branch, str):
        if input_branch not in [head.name for head in repo.heads]:
            raise ValueError(f'Input branch not found: {input_branch}')
    elif isinstance(input_branch, list):
        for branch in input_branch:
            if branch not in [head.name for head in repo.heads]:
                raise ValueError(f'Input branch not found: {branch}')
    else:
        raise ValueError(f'Invalid value for input branch: {input_branch}')
    return input_branch

def get_results_branch(repo, given_results_branch):
    """Get the default result branch, unless given an override"""
    if given_results_branch:
        if not isinstance(given_results_branch, str):
            raise ValueError('Invalid input for results branch: '
                             + str(given_results_branch))
        else:
            results_branch = given_results_branch
    else:
        results_branch = [head.name for head in repo.heads
                          if 'results' in head.name]
        if len(results_branch) > 1:
            raise ValueError('Ambiguous results branches in Git')
        else:
            results_branch = results_branch[0]
    if results_branch not in [head.name for head in repo.heads]:
        raise ValueError(f'Results branch not found: {results_branch}')
    else:
        return results_branch

def get_commit_files(settings, parameters):
    """Get a list of files to commit to the results branch"""
    patterns = list()
    patterns.append(settings['logfile'])
    return patterns

def get_commit_message(this_run):
    """Create a message string to commit results of the current run"""
    return 'Results for ' + this_run['title']

# Template methods
def get_valid_templates(run_folder, templates):
    """Check which files exist and return lists of valid and invalid files."""
    valid_templates = []
    invalid_templates = []
    for template in templates.split(','):
        if run_folder.joinpath(template).is_file():
            valid_templates.append(template)
        else:
            invalid_templates.append(template)
    return (None if len(valid_templates) == 0 else ','.join(valid_templates),
            None if len(invalid_templates) == 0 else ','.join(invalid_templates))

# Post-processing methods
def post_process(settings, command):
    """Run the given post-processing command in the run folder"""
    folder = settings['current_folder']
    environ = os.environ.copy()
    this_env = str(pathlib.Path.home().joinpath('.pyenv/versions/scripts/bin'))
    environ['PATH'] = environ['PATH'].replace(f'{this_env}:', '')
    environ['PYENV_DIR'] = ''
    environ['PYENV_VERSION'] = ''
    return subprocess.run(command.split(), cwd=folder, env=environ)

# Archive methods
def create_archive_folder(archive_folder):
    """Make a new folder at the given location, or access an existing folder"""
    if not archive_folder.is_dir():
        archive_folder.mkdir(parents=True)

def get_copy_list(simulation_class):
    """Get list of file patterns to copy for a particular simulation type"""
    copy_list = ['*.data', '*.txt', '*.xlsx']
    if simulation_class == 'impact':
        copy_list.append('*.in')
    elif simulation_class == 'bdsim':
        copy_list.append('*.gmad')
    elif simulation_class == 'opal':
        copy_list.append('*.in')
    else:
        copy_list.append('*.in')
    return copy_list

def get_move_list(simulation_class, is_full_archive):
    """Get list of file patterns to move for a particular simulation type"""
    move_list = ['*.png', '*.eps', '*.ps', '*.jpg', '*.log']
    if simulation_class == 'impact':
        move_list.extend(['*.dst', '*.plt', '*.T7out'])
        if is_full_archive:
            move_list.append('fort.*')
    elif simulation_class == 'bdsim':
        if is_full_archive:
            move_list.append('*.root')
    elif simulation_class == 'opal':
        if is_full_archive:
            move_list.extend(['*.h5', '*.lbal', '*.stat', '*.dat', 'data'])
    return move_list

def get_delete_list(simulation_class):
    """Get list of file patterns to delete - same as full archive list."""
    return get_move_list(simulation_class, is_full_archive=True)

def copy_to_archive(run_folder, archive_folder, copy_patterns):
    """Copy files to the given archive folder based on glob patterns"""
    if not run_folder.is_dir():
        raise OSError(f'Cannot access source folder: {run_folder}')
    if not archive_folder.is_dir():
        raise OSError(f'Cannot access archive folder: {archive_folder}')
    if not isinstance(copy_patterns, list):
        raise ValueError(f'Invalid archive copy pattern: {copy_patterns}')
    file_list = set()
    for pattern in copy_patterns:
        file_list.update(set(run_folder.glob(pattern)))
    for this_file in file_list:
        if this_file.name != LOGFILE:
            shutil.copy2(str(this_file), str(archive_folder))

def move_to_archive(run_folder, archive_folder, move_patterns):
    """Move files to the given archive folder based on glob patterns"""
    if not run_folder.is_dir():
        raise OSError(f'Cannot access source folder: {run_folder}')
    if not archive_folder.is_dir():
        raise OSError(f'Cannot access archive folder: {archive_folder}')
    if not isinstance(move_patterns, list):
        raise ValueError(f'Invalid archive move pattern: {move_patterns}')
    file_list = set()
    for pattern in move_patterns:
        file_list.update(set(run_folder.glob(pattern)))
    for this_file in file_list:
        if this_file.name != LOGFILE:
            shutil.move(str(this_file), str(archive_folder))

def move_rendered_templates(run_folder, archive_folder):
    """Save rendered template files to archive folder"""
    if not run_folder.is_dir():
        raise OSError(f'Cannot access source folder: {run_folder}')
    if not archive_folder.is_dir():
        raise OSError(f'Cannot access archive folder: {archive_folder}')
    file_list = run_folder.glob('*.rendered')
    for this_file in file_list:
        new_filename = str(this_file.name).replace('.rendered','')
        shutil.move(str(this_file), str(archive_folder.joinpath(new_filename)))

def archive_log(settings, archive_folder):
    """Get a log of the last run and save it to the archive folder"""
    log_command = [str(settings['python']),
                   str(settings['reproduce']), 'log', '-n1']
    log_output = subprocess.run(log_command,
                                cwd=settings['current_folder'],
                                capture_output=True).stdout
    with open(archive_folder.joinpath(settings['archive_log']), 'wb') as f:
        f.write(log_output)

def archive_output(settings, this_run):
    """Archive the input, output and log files of the latest run"""
    create_archive_folder(this_run['archive'])
    copy_to_archive(settings['current_folder'],
                    this_run['archive'],
                    this_run['archive_copy'])
    move_to_archive(settings['current_folder'],
                    this_run['archive'],
                    this_run['archive_move'])
    move_rendered_templates(settings['current_folder'], this_run['archive'])
    archive_log(settings, this_run['archive'])

def delete_output(settings, this_run):
    """Delete any output files that haven't been archived."""
    delete_list = get_delete_list(this_run['--class'])
    for pattern in delete_list:
        files = settings['current_folder'].glob(pattern)
        for this_file in files:
            if this_file.name != LOGFILE:
                this_file.unlink()

# Sweep methods
def get_sweep_parameters(sweep_definition):
    """Return the parameter name for a given sweep string"""
    if not ':' in sweep_definition:
        raise ValueError('Invalid sweep definition: ' + sweep_definition)
    sweep_parameters = sweep_definition.split(':')[0]
    if ',' in sweep_parameters:
        return sweep_parameters.replace('(', '').replace(')', '').split(',')
    else:
        return [sweep_parameters]

def get_sweep_values(sweep_definition):
    """Return the parameter name for a given sweep string"""
    if not ':' in sweep_definition:
        raise ValueError('Invalid sweep definition: ' + sweep_definition)
    sweep_values = sweep_definition.split(':')[1]
    if '(' in sweep_values:
        return [tuple(this_set.replace('(', '').replace(')', '').split(','))
                for this_set in sweep_values.split('),')]
    else:
        return sweep_values.split(',')

def get_sweep_strings(sweep_definition):
    """Get all single-value parameter strings for a given sweep string"""
    if not ':' in sweep_definition:
        raise ValueError('Invalid sweep definition: ' + sweep_definition)
    sweep_parameters = get_sweep_parameters(sweep_definition)
    if len(sweep_parameters) > 1:
        return [','.join([sweep_parameters[i] + ':' + values[i]
                        for i in range(len(sweep_parameters))])
                for values in get_sweep_values(sweep_definition)]
    else:
        return [sweep_parameters[0] + ':' + value
                for value in get_sweep_values(sweep_definition)]

def get_sweep_combinations(sweeps):
    """Get all combinations of parameter values for multiple sweeps"""
    sweep_strings = [get_sweep_strings(sweep) for sweep in sweeps]
    combinations = itertools.product(*sweep_strings)
    combination_strings = [','.join(item) for item in combinations]
    return combination_strings

# Define run settings and parameters
def get_settings(arguments):
    """Get the required settings as a dictionary"""
    settings = dict()
    settings['current_folder'] = get_folder('.')
    settings['archive_root'] = get_folder(ARCHIVE_ROOT)
    settings['reproducible'] = get_folder(REPRODUCIBLE)
    settings['pyenv'] = get_folder(PYENV)
    settings['python'] = get_python_for_reproducible(settings['reproducible'],
                                                     settings['pyenv'])
    settings['reproduce'] = get_folder(REPRODUCIBLE).joinpath('reproduce')
    settings['logfile'] = LOGFILE
    settings['archive_log'] = ARCHIVE_LOG
    return settings

def get_parameters(settings, arguments):
    """Get the parameters for the batch run based on the given arguments"""
    parameters = arguments.copy()
    if parameters['--archive']:
        parameters['archive'] = (
            get_archive_folder(settings['archive_root']))
        parameters['archive_copy'] = get_copy_list(parameters['--class'])
        parameters['archive_move'] = (
            get_move_list(parameters['--class'], parameters['--full']))
    else:
        parameters['archive'] = None
    if parameters['--git']:
        repo = get_git_repo(settings['current_folder'])
        parameters['--input_branch'] = (
            get_input_branch(repo, arguments['--input_branch']))
        parameters['--results_branch'] = (
            get_results_branch(repo, arguments['--results_branch']))
    return parameters

def get_title(this_run):
    """Create a title string including the run date and main command"""
    if 'title' in this_run:
        if this_run['title']:
            return this_run['title']
    title = ' '.join([datetime.today().strftime('%Y-%m-%d'),
                      this_run['<command>'].split()[0]])
    return title

# Run methods
def reproducible_run(settings, this_run):
    """Run the given command using Reproducible"""
    command = [str(settings['python']), str(settings['reproduce'])]
    if this_run['--config']:
        command.append('--config')
        command.append(this_run['--config'])
    if this_run['--logfile']:
        command.append('--logfile=')
        command.append(this_run['--logfile'])
    if this_run['--runlog']:
        command.append('--runlog')
    if this_run['--devel']:
        command.append('--devel')
    command.append('run')
    if this_run['--template']:
        command.append('--template')
        command.append(this_run['--template'])
    if this_run['--src']:
        command.append('--src')
        command.append(this_run['--src'])
    if this_run['--build']:
        command.append('--build')
    if this_run['--hash']:
        command.append('--hash')
        command.append(this_run['--hash'])
    if this_run['--show']:
        command.append('--show')
    if this_run['--save']:
        command.append('--save')
    if this_run['--list-parameters']:
        command.append('--list-parameters')
    if this_run['-p']:
        command.append('-p')
        command.append(this_run['-p'])
    command.append('--')
    command.append(this_run['<command>'])
    return subprocess.run(command, cwd=settings['current_folder'])

def run_single(settings, this_run):
    """Work through the simulation steps for each individual run"""
    announce_start(this_run)
    if this_run['--git']:
        repo = get_git_repo(settings['current_folder'])
        git_checkout(repo, this_run['--input_branch'])
        git_get_file(repo, this_run['--results_branch'], settings['logfile'])
    if this_run['--template']:
        valid, invalid = get_valid_templates(settings['current_folder'],
                                             this_run['--template'])
        if invalid:
            announce_error(f'Skipping missing templates: {invalid}')
        this_run['--template'] = valid
    reproducible_run(settings, this_run)
    if this_run['--post']:
        post_process(settings, this_run['--post'])
    if this_run['--git']:
        git_switch(repo, this_run['--results_branch'])
        git_commit(repo, this_run['commit_files'], this_run['commit_message'])
        git_switch(repo, this_run['--input_branch'])
    if this_run['--archive']:
        archive_output(settings, this_run)
    if this_run['--clean']:
        delete_output(settings, this_run)
    announce_end(this_run)

def run_with_git(settings, this_run):
    """Run for a single or multiple input branches"""
    this_run['commit_files'] = get_commit_files(settings, this_run)
    this_run['commit_message'] = get_commit_message(this_run)
    if isinstance(this_run['--input_branch'], list):
        for this_branch in this_run['--input_branch']:
            branch_run = this_run.copy()
            branch_run['--input_branch'] = this_branch
            branch_run['title'] = (
                this_run['title'] + ' for branch ' + this_branch)
            branch_run['commit_message'] = (
                this_run['commit_message'] + ' for branch ' + this_branch)
            if branch_run['--archive']:
                branch_run['archive'] = this_run['archive'].joinpath(
                    this_branch.replace('input/', ''))
            run_single(settings, branch_run)
    else:
        run_single(settings, this_run)

# Main batch method
def run_batch(settings, parameters):
    """Run through the batch for different parameter values and input files"""
    batch_run = parameters.copy()
    batch_run['title'] = get_title(batch_run)
    if batch_run['--sweep']:
        for this_combination in get_sweep_combinations(batch_run['--sweep']):
            this_run = batch_run.copy()
            this_run['title'] = batch_run['title'] + ' for ' + this_combination
            if this_run['-p']:
                this_run['-p'] += ',' + this_combination
            else:
                this_run['-p'] = this_combination
            if this_run['--archive']:
                folder_name = get_safe_folder_name(this_combination)
                this_run['archive'] = batch_run['archive'].joinpath(folder_name)
            if this_run['--git']:
                run_with_git(settings, this_run)
            else:
                run_single(settings, this_run)
    else:
        if batch_run['--git']:
            run_with_git(settings, batch_run)
        else:
            run_single(settings, batch_run)


# What to do when run as a script
if __name__ == '__main__':
    arguments = docopt(__doc__)
    settings = get_settings(arguments)
    parameters = get_parameters(settings, arguments)
    run_batch(settings, parameters)
