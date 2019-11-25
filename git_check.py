# Check current _Git_ status

import git
import pathlib
import socket
from tabulate import tabulate
from termcolor import colored
import colorama


# Utility methods
def get_repo_path_list():
    home_folder = pathlib.Path.home()
    code_folder = home_folder.joinpath('Code')
    scripts_folder = code_folder.joinpath('Scripts')
    hostname = socket.gethostname()
    if hostname == 'MJEaston':
        docs_folder = home_folder.joinpath('OneDrive/Documents')
        sim_folder = pathlib.Path('D:/Simulations/Current')
    elif 'MacBook Pro' in hostname:
        docs_folder = home_folder.joinpath('OneDrive/Documents')
        sim_folder = home_folder.joinpath('Code/CurrentSimulation')
    elif hostname == 'ubuntu42':
        docs_folder = home_folder.joinpath('Documents')
        sim_folder = home_folder.joinpath('Simulations/Current')
    return[scripts_folder,
           sim_folder,
           code_folder.joinpath('Impact'),
           code_folder.joinpath('Reproducible'),
           code_folder.joinpath('runLORASR'),
           code_folder.joinpath('sweep'),
           code_folder.joinpath('OPAL'),
           code_folder.joinpath('BDSIM'),
           docs_folder.joinpath('Projects'),
           docs_folder.joinpath('Presentations'),
           docs_folder.joinpath('Editing'),
           docs_folder.joinpath('Manuscripts'),
           docs_folder.joinpath('Notebooks')]


# Methods working with a given repo
def list_remotes(repo):
    """List all remotes (with urls) of a given repo"""
    if not isinstance(repo, git.repo.base.Repo): raise ValueError
    print('## Remotes')
    remote_list = []
    for remote in repo.remotes:
        remote_list.append([str(remote.name) + ":",
                            str([url for url in remote.urls]).strip("'[]")])
    print(tabulate(remote_list, tablefmt='plain'))

def list_branches(repo):
    """List all branches of a given repo"""
    if not isinstance(repo, git.repo.base.Repo): raise ValueError
    print('## Branches')
    print(repo.git.branch(['-vv', '--all']))

def fetch_all_remotes(repo, show_progress=False):
    """Fetch latest data from all remotes"""
    if not isinstance(repo, git.repo.base.Repo): raise ValueError
    for remote in repo.remotes:
        if show_progress: print(f'Fetching {remote.name}...', end=' ')
        remote.fetch()
        if show_progress: print('done.')

def show_status(repo):
    """Show the status of the given repo and its working tree"""
    if not isinstance(repo, git.repo.base.Repo): raise ValueError
    print('## Status')
    print(repo.git.status())

def check_repo(dir, fetch=True):
    """Check remotes, branches and status of given repo"""
    if isinstance(dir, git.repo.base.Repo):
        repo = dir
    elif isinstance(dir, str) or isinstance(dir, pathlib.Path):
        repo = git.Repo(pathlib.Path(dir))
    else:
        raise ValueError
    print(f'Checking Git status at {repo.working_tree_dir}...\n')
    list_remotes(repo)
    if fetch: fetch_all_remotes(repo, show_progress=True)
    print()
    list_branches(repo)
    print()
    show_status(repo)
    print()


# Methods working through all repos
def show_all():
    repo_path_list = get_repo_path_list()
    path_count = len(repo_path_list)
    clean_count = 0
    dirty_count = 0
    missing_count = 0
    error_count = 0
    colorama.init()
    for repo_path in repo_path_list:
        try:
            if not repo_path.exists():
                print(colored(f'{repo_path} does not exist.', 'red'))
                missing_count += 1
                continue
            elif not repo_path.is_dir():
                print(colored(f'{repo_path} is not a folder.', 'red'))
                missing_count += 1
                continue
            else:
                repo = git.Repo(repo_path)
                if repo.is_dirty():
                    print(colored(f'{repo_path} is dirty.',
                                  'blue', attrs=['bold']))
                    dirty_count += 1
                else:
                    print(colored(f'{repo_path} is clean.', 'green'))
                    clean_count += 1
        except git.exc.InvalidGitRepositoryError:
            print(colored(f'{repo_path} is not a Git repo', 'red'))
            missing_count += 1
            continue
        except:
            print(colored(f'{repo_path} gave an error.', 'red'))
            error_count += 1
            continue
    message = f'Checked {path_count} {"path" if path_count == 1 else "paths"}. '
    if clean_count > 0 or dirty_count > 0:
        message += (f'{clean_count if clean_count > 0 else "No"} '
                    f'{"repo is" if clean_count == 1 else "repos are"} clean '
                    f'and {dirty_count if dirty_count > 0 else "no"} '
                    f'{"repo is" if dirty_count == 1 else "repos are"} dirty. ')
    if missing_count > 0 or error_count > 0:
        message += (f'Encountered ')
        if missing_count > 0:
            message += (f'{missing_count} missing '
                        f'{"path" if missing_count == 1 else "paths"}')
        if missing_count > 0 and error_count > 0:
            message += ' and '
        if error_count > 0:
            message += (f'{error_count} '
                        f'{"error" if error_count == 1 else "errors"}')
        message += '. '
    print(message)

def fetch_all(show_progress=False):
    """Fetch latest data from all remotes for all repos"""
    repo_path_list = get_repo_path_list()
    for repo_path in repo_path_list:
        try:
            if repo_path.is_dir():
                repo = git.Repo(repo_path)
                if show_progress: 
                    print(f'Fetching remotes for {repo_path}...', end=' ')
                fetch_all_remotes(repo, show_progress=False)
                if show_progress: 
                    print('done.')
        except git.exc.InvalidGitRepositoryError:
            continue
        except:
            if show_progress: 
                print(colored(f'{repo_path} gave an error.', 'red'))
            continue

def check_all(fetch=True):
    repo_path_list = get_repo_path_list()
    for repo in repo_path_list:
        try:
            if not repo.is_dir:
                print(f'\nCannot find folder {repo}. Continuing...\n')
                continue
            else:
                repo = git.Repo(repo)
                check_repo(repo, fetch=fetch)
        except git.exc.InvalidGitRepositoryError:
            print(f'\nFolder {repo} is not a Git repository. Continuing...\n')
            continue
        except:
            print(f'\nError while checking {repo}. Continuing...\n')
            continue


# Main routine
def main():
    print('Current status:\n')
    show_all()
    print()
    prompt = 'Do you want to fetch data for all repos? [Y/n] '
    if not input(prompt).lower() in ['n', 'no']:
        fetch_all(show_progress=True)
        print()
        show_all()

if __name__ == '__main__':
    main()
    input('Press [Enter] to finish.')
