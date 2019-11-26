# Check current _Git_ status

import git
import pathlib
import socket
import tabulate
import termcolor
import colorama


# Methods working with list of repos
def get_repo_path_list():
    """Get lists of all paths to check Git status"""
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

def get_repo_status_list(branches=True):
    """Get status of all repos and return a list with status details"""
    if not isinstance(branches, bool): raise ValueError
    repo_path_list = get_repo_path_list()
    repo_status_list = []
    for repo_path in repo_path_list:
        repo_status = {'path': repo_path}
        try:
            if not repo_path.exists():
                repo_status['state'] = 'missing'
            elif not repo_path.is_dir():
                repo_status['state'] = 'not_folder'
            else:
                repo = git.Repo(str(repo_path))
                if repo.is_dirty() or len(repo.untracked_files) > 0:
                    repo_status['state'] = 'dirty'
                else:
                    repo_status['state'] = 'clean'
        except git.exc.InvalidGitRepositoryError:
            repo_status['state'] = 'not_repo'
        except:
            repo_status['state'] = 'error'
        if not repo_status['state']:
            repo_status['state'] = 'check_failed'
        if repo_status['state'] in ['clean', 'dirty']:
            if branches:
                branch_list = []
                for branch in repo.branches:
                    branch_state = get_branch_state(repo, branch.name)
                    branch_info = {'name': branch.name, 'state': branch_state}
                    branch_list.append(branch_info)
                    if (repo_status['state'] == 'clean' 
                        and branch_state != 'synced'):
                        repo_status['state'] = 'out-of-sync'
                repo_status['branches'] = branch_list
        repo_status_list.append(repo_status)
    return repo_status_list


# Methods working with a given repo
def list_remotes(repo):
    """List all remotes (with urls) of a given repo"""
    if not isinstance(repo, git.repo.base.Repo): raise ValueError
    print('## Remotes')
    remote_list = []
    for remote in repo.remotes:
        remote_list.append([str(remote.name) + ":",
                            str([url for url in remote.urls]).strip("'[]")])
    print(tabulate.tabulate(remote_list, tablefmt='plain'))

def list_branches(repo):
    """List all branches of a given repo"""
    if not isinstance(repo, git.repo.base.Repo): raise ValueError
    print('## Branches')
    print(repo.git.branch(['-vv', '--all']))

def get_branch_state(repo, branch_name):
    """Return sync status of a given branch in a given repo"""
    if not isinstance(repo, git.repo.base.Repo): raise ValueError
    if not isinstance(branch_name, str): raise ValueError
    branch = repo.heads[branch_name]
    remote_branch = branch.tracking_branch()
    if not remote_branch:
        return 'untracked'
    else:
        if branch.commit.hexsha == branch.tracking_branch().commit.hexsha:
            return 'synced'
        elif branch.commit.hexsha in [log_entry.newhexsha 
                                      for log_entry 
                                      in branch.tracking_branch().log()]:
            return 'behind'
        elif branch.tracking_branch().commit.hexsha in [log_entry.newhexsha 
                                                        for log_entry 
                                                        in branch.log()]:
            return 'ahead'
        else:
            return 'out-of-sync'

def get_branch_report(branch_state_list):
    """Summarise the branch status of a repo as a human-readable string"""
    if not isinstance(branch_state_list, list): raise ValueError
    if len(branch_state_list) == 0: raise ValueError
    for item in branch_state_list:
        if not isinstance(item, dict): raise ValueError
    synced_count = sum(b['state'] == 'synced' for b in branch_state_list)
    behind_count = sum(b['state'] == 'behind' for b in branch_state_list)
    ahead_count = sum(b['state'] == 'ahead' for b in branch_state_list)
    untracked_count = sum(b['state'] == 'untracked' for b in branch_state_list)
    unsynced_count = sum(b['state'] == 'out-of-sync' for b in branch_state_list)
    message = ''
    if synced_count > 0:
        if synced_count == len(branch_state_list):
            message = 'All branches are in sync with remote'
        else:
            message += (f'{synced_count} '
                        f'{"branch is" if synced_count == 1 else "branches are"} '
                        'in sync with remote')
    if behind_count > 0:
        if len(message) > 0: message += ', '
        message += (f'{behind_count} '
                    f'{"branch is" if behind_count == 1 else "branches are"} '
                    'behind remote')
    if ahead_count > 0:
        if len(message) > 0: message += ', '
        message += (f'{ahead_count} '
                    f'{"branch is" if ahead_count == 1 else "branches are"} '
                    'ahead of remote')
    if untracked_count > 0:
        if len(message) > 0: message += ', '
        message += (f'{untracked_count} '
                    f'{"branch is" if untracked_count == 1 else "branches are"} '
                    'not tracking a remote branch')
    if unsynced_count > 0:
        if len(message) > 0: message += ', '
        message += (f'{unsynced_count} '
                    f'{"branch is" if unsynced_count == 1 else "branches are"} '
                    'out of sync with remote')
    message += '.'
    return message

def show_status(repo):
    """Show the status of the given repo and its working tree"""
    if not isinstance(repo, git.repo.base.Repo): raise ValueError
    print('## Status')
    print(repo.git.status())

def fetch_all_remotes(repo, show_progress=False):
    """Fetch latest data from all remotes"""
    if not isinstance(repo, git.repo.base.Repo): raise ValueError
    if not isinstance(show_progress, bool): raise ValueError
    for remote in repo.remotes:
        if show_progress: print(f'Fetching {remote.name}...', end=' ')
        remote.fetch()
        if show_progress: print('done.')

def report(repo, fetch=True):
    """Report remotes, branches and status of given repo"""
    if not isinstance(repo, git.repo.base.Repo): raise ValueError
    if not isinstance(fetch, bool): raise ValueError
    print(f'Checking Git status at {repo.working_tree_dir}...\n')
    list_remotes(repo)
    if fetch: fetch_all_remotes(repo, show_progress=True)
    print()
    list_branches(repo)
    print()
    show_status(repo)
    print()


# Methods working through all repos
def show_all(branches=True):
    """Print out the status of all repos"""
    if not isinstance(branches, bool): raise ValueError
    repo_status_list = get_repo_status_list(branches=branches)
    path_count = len(repo_status_list)
    clean_count = 0
    dirty_count = 0
    missing_count = 0
    error_count = 0
    colorama.init()
    for repo in repo_status_list:
        if repo['state'] == 'clean':
            print(termcolor.colored(f'{repo["path"]} is clean.', 'green'))
            clean_count += 1
            if branches:
                print('    ' + get_branch_report(repo['branches']))
        elif repo['state'] == 'dirty':
            print(termcolor.colored(f'{repo["path"]} is dirty.', 
                                    'blue', attrs=['bold']))
            dirty_count += 1
            if branches:
                print('    ' + get_branch_report(repo['branches']))
        elif repo['state'] == 'out-of-sync':
            print(termcolor.colored(f'{repo["path"]} is out of sync with remote.', 
                                    'blue', attrs=['bold']))
            dirty_count += 1
            if branches:
                print('    ' + get_branch_report(repo['branches']))
        elif repo['state'] == 'missing':
            print(termcolor.colored(f'{repo["path"]} does not exist.', 'red'))
            missing_count += 1
        elif repo['state'] == 'not_folder':
            print(termcolor.colored(f'{repo["path"]} is not a folder.', 'red'))
            missing_count += 1
        elif repo['state'] == 'not_repo':
            print(termcolor.colored(f'{repo["path"]} is not a Git repo', 'red'))
            missing_count += 1
        elif repo['state'] == 'error':
            print(termcolor.colored(f'{repo["path"]} gave an error.', 'red'))
            error_count += 1
        elif repo['state'] == 'check_failed':
            print(termcolor.colored(f'{repo["path"]} check failed.', 'red'))
            error_count += 1
        else:
            print(termcolor.colored(f'{repo["path"]} could not be processed.', 
                                    'red'))
            error_count += 1
    message = f'Checked {path_count} {"path" if path_count == 1 else "paths"}. '
    if clean_count > 0 or dirty_count > 0:
        message += (f'{clean_count if clean_count > 0 else "No"} '
                    f'{"repo is" if clean_count == 1 else "repos are"} clean '
                    f'and {dirty_count if dirty_count > 0 else "no"} '
                    f'{"repo is" if dirty_count == 1 else "repos are"} dirty')
        if branches: message += ' or out of sync with remote'
        message += '. '
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
    print()
    print(message)

def fetch_all(show_progress=False):
    """Fetch latest data from all remotes for all repos"""
    if not isinstance(show_progress, bool): raise ValueError
    repo_path_list = get_repo_path_list()
    for repo_path in repo_path_list:
        try:
            if repo_path.is_dir():
                repo = git.Repo(str(repo_path))
                if show_progress: 
                    print(f'Fetching remotes for {repo_path}...', end=' ')
                fetch_all_remotes(repo, show_progress=False)
                if show_progress: 
                    print('done.')
        except git.exc.InvalidGitRepositoryError:
            continue
        except:
            if show_progress: 
                print(termcolor.colored(f'{repo_path} gave an error.', 'red'))
            continue

def report_all(filter='none', fetch=True):
    """Report the full status of all repos"""
    if not isinstance(filter, str): raise ValueError
    if not isinstance(fetch, bool): raise ValueError
    if not filter in ('none', 'exists', 'dirty', 'out-of-sync', 'not clean'): 
        raise ValueError
    repo_list = get_repo_status_list(branches=True)
    if filter == 'none': 
        repo_path_list = [repo['path'] for repo in repo_list]
    elif filter == 'exists':
        repo_path_list = [repo['path'] for repo in repo_list 
                          if repo['state'] not in ('missing', 'not_folder', 
                                                   'not_repo', 'error', 
                                                   'check_failed')]
    elif filter == 'dirty':
        repo_path_list = [repo['path'] for repo in repo_list 
                          if repo['state'] == 'dirty']
    elif filter == 'out-of-sync':
        repo_path_list = [repo['path'] for repo in repo_list 
                          if repo['state'] == 'out-of-sync']
    elif filter == 'not clean':
        repo_path_list = [repo['path'] for repo in repo_list 
                          if repo['state'] in ('dirty', 'out-of-sync')]
    for repo in repo_path_list:
        try:
            if not repo.is_dir:
                print(f'\nCannot find folder {repo}. Continuing...\n')
                continue
            else:
                repo = git.Repo(str(repo))
                report(repo, fetch=fetch)
        except git.exc.InvalidGitRepositoryError:
            print(f'\nFolder {repo} is not a Git repository. Continuing...\n')
            continue
        except:
            print(f'\nError while checking {repo}. Continuing...\n')
            continue


# Main routine
def main():
    """Main routine that runs through the check and report process"""
    print('Current status:\n')
    show_all(branches=False)
    print()
    prompt = 'Do you want to fetch data for all repos? [Y/n] '
    fetch_response = input(prompt)
    if fetch_response.lower() in ['n', 'no']:
        fetch_later = True
    else:
        fetch_all(show_progress=True)
        fetch_later = False
        print()
        show_all(branches=True)
        print()
    prompt = ('Do you want to see more details for '
              '[A]ll repos, [D]irty and out-of-sync repos, or [N]o details? '
              '[A/D/N] ')
    details_response = input(prompt)
    if details_response.lower() in ['a', 'all', 'al']:
        print()
        report_all(filter='exists', fetch=fetch_later)
    elif details_response.lower() in ['d', 'dirty', 'dirt', 'o', 'out-of-sync', 'out']:
        print()
        report_all(filter='not clean', fetch=fetch_later)


# What to do when run as a script
if __name__ == '__main__':
    main()
    print()
    input('Press [Enter] to finish.')
