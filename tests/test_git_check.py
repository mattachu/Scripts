# Tests git_check.py

import git_check
import pytest
import git
import pathlib
import socket
import sys

class TestGitCheck:

    # Set paths
    hostname = socket.gethostname()
    if hostname == 'MJEaston':
        if sys.platform.startswith('linux'):
            scripts_dir = '/home/matt/Code/Scripts'
        else:
            scripts_dir = 'C:\\Users\\Matt\\Code\\Scripts'
    elif hostname == 'MattBookPro':
        scripts_dir = '/Users/matt/Code/Scripts'
    elif 'MacBook' in hostname:
        scripts_dir = '/Users/matt/Code/Scripts'
    elif hostname == 'ubuntu42':
        scripts_dir = '/home/matt/Code/Scripts'

    # Setup before testing
    def setup_class(self):
        self.test_dir = self.scripts_dir
        self.test_repo = git.Repo(self.test_dir)


    # Test get_repo_path_list method
    def test_get_repo_path_list_no_output(self, capsys):
        self.status_list = git_check.get_repo_path_list()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_repo_path_list_return_types(self):
        self.repo_path_list = git_check.get_repo_path_list()
        assert isinstance(self.repo_path_list, list)
        for repo_path in self.repo_path_list:
            assert isinstance(repo_path, str)

    def test_get_repo_path_list_contains_scripts(self):
        self.repo_path_list = git_check.get_repo_path_list()
        assert self.scripts_dir in self.repo_path_list

    def test_get_repo_path_list_invalid_input(self):
        with pytest.raises(ValueError):
            git_check.get_repo_path_list(self.test_repo)
        with pytest.raises(ValueError):
            git_check.get_repo_path_list(3.142)
        with pytest.raises(ValueError):
            git_check.get_repo_path_list(99999999)
        with pytest.raises(ValueError):
            git_check.get_repo_path_list([self.test_dir, '/usr/bin/'])

    def test_get_repo_path_list_invalid_file(self):
        with pytest.raises(OSError):
            git_check.get_repo_path_list('Random text')
        with pytest.raises(OSError):
            git_check.get_repo_path_list('/not/a/path/')
        with pytest.raises(OSError):
            git_check.get_repo_path_list('/')

    # Test get_repo_status_list method
    def test_get_repo_status_list_no_output(self, capsys):
        self.status_list = git_check.get_repo_status_list()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_repo_status_list_contains_scripts(self):
        self.status_list = git_check.get_repo_status_list()
        self.found_scripts = False
        for repo_status in self.status_list:
            if repo_status['path'] == self.scripts_dir:
                self.found_scripts = True
        assert self.found_scripts == True

    def test_get_repo_status_list_length(self):
        self.path_list = git_check.get_repo_path_list()
        self.status_list = git_check.get_repo_status_list()
        assert len(self.status_list) == len (self.path_list)

    def test_get_repo_status_list_contents(self):
        self.status_list = git_check.get_repo_status_list() # default branches = True
        for repo_status in self.status_list:
            assert 'path' in repo_status
            assert 'state' in repo_status
            assert isinstance(repo_status['path'], str)
            assert isinstance(repo_status['state'], str)
            assert repo_status['state'] in ('clean', 'dirty', 'out-of-sync',
                                            'missing', 'not_folder', 'not_repo',
                                            'error', 'check_failed')

    def test_get_repo_status_list_contents_with_branches(self):
        self.status_list = git_check.get_repo_status_list(branches=True)
        for repo_status in self.status_list:
            if repo_status['state'] in ['clean', 'dirty']:
                assert 'branches' in repo_status
                assert isinstance(repo_status['branches'], list)
                assert len(repo_status['branches']) > 0
                for branch_info in repo_status['branches']:
                    assert isinstance(branch_info, dict)
                    assert isinstance(branch_info['name'], str)
                    assert isinstance(branch_info['state'], str)
                    assert branch_info['state'] in ('synced', 'behind', 'ahead',
                                                    'out-of-sync', 'untracked')

    def test_get_repo_status_list_contents_no_branches(self):
        self.status_list = git_check.get_repo_status_list(branches=False)
        for repo_status in self.status_list:
            assert 'branches' not in repo_status

    def test_get_repo_status_list_contents_default(self):
        self.status_list = git_check.get_repo_status_list() # default branches = True
        for repo_status in self.status_list:
            if repo_status['state'] in ['clean', 'dirty']:
                assert 'branches' in repo_status

    def test_get_repo_status_list_invalid_input(self):
        with pytest.raises(ValueError):
            git_check.get_repo_status_list('false')
        with pytest.raises(ValueError):
            git_check.get_repo_status_list('True')
        with pytest.raises(ValueError):
            git_check.get_repo_status_list('Random text')
        with pytest.raises(ValueError):
            git_check.get_repo_status_list(1)
        with pytest.raises(ValueError):
            git_check.get_repo_status_list(0)
        with pytest.raises(ValueError):
            git_check.get_repo_status_list(3.142)
        with pytest.raises(ValueError):
            git_check.get_repo_status_list(99999999)
        with pytest.raises(ValueError):
            git_check.get_repo_status_list('/usr/bin')
        with pytest.raises(ValueError):
            git_check.get_repo_status_list('C:\\Windows\\')
        with pytest.raises(ValueError):
            git_check.get_repo_status_list(self.test_repo)


    # Test list_remotes method
    def test_list_remotes_invalid_input(self):
        with pytest.raises(ValueError):
            git_check.list_remotes(self.test_dir)
        with pytest.raises(ValueError):
            git_check.list_remotes('Random text')
        with pytest.raises(ValueError):
            git_check.list_remotes(3.142)
        with pytest.raises(ValueError):
            git_check.list_remotes(99999999)
        with pytest.raises(ValueError):
            git_check.list_remotes('/usr/bin')
        with pytest.raises(ValueError):
            git_check.list_remotes('C:\\Windows\\')

    def test_list_remotes_invalid_repo(self):
        with pytest.raises(git.exc.NoSuchPathError):
            git_check.list_remotes(git.Repo('/not/a/path'))
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            git_check.list_remotes(git.Repo('/'))

    # Test list_branches method
    def test_list_branches_contains_at_least_one_branch(self, capsys):
        git_check.list_branches(self.test_repo)
        captured = capsys.readouterr()
        assert captured.out != '## Branches\n'

    def test_list_branches_invalid_input(self):
        with pytest.raises(ValueError):
            git_check.list_branches(self.test_dir)
        with pytest.raises(ValueError):
            git_check.list_branches('Random text')
        with pytest.raises(ValueError):
            git_check.list_branches(3.142)
        with pytest.raises(ValueError):
            git_check.list_branches(99999999)
        with pytest.raises(ValueError):
            git_check.list_branches('/usr/bin')
        with pytest.raises(ValueError):
            git_check.list_remotes('C:\\Windows\\')

    def test_list_branches_invalid_repo(self):
        with pytest.raises(git.exc.NoSuchPathError):
            git_check.list_branches(git.Repo('/not/a/path'))
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            git_check.list_branches(git.Repo('/'))

    # Test get_branch_state method
    def test_get_branch_state_no_output(self, capsys):
        self.branch_status = git_check.get_branch_state(self.test_repo,
                                                         'master')
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_branch_state_return_value(self):
        self.branch_status = git_check.get_branch_state(self.test_repo,
                                                        'master')
        assert isinstance(self.branch_status, str)
        assert self.branch_status in ('synced', 'behind', 'ahead',
                                      'out-of-sync', 'untracked')

    def test_get_branch_state_invalid_input(self):
        with pytest.raises(ValueError):
            git_check.get_branch_state(self.test_dir, 'master')
        with pytest.raises(ValueError):
            git_check.get_branch_state('Random text', 'master')
        with pytest.raises(ValueError):
            git_check.get_branch_state(3.142, 'master')
        with pytest.raises(ValueError):
            git_check.get_branch_state(99999999, 'master')
        with pytest.raises(ValueError):
            git_check.get_branch_state('/usr/bin', 'master')
        with pytest.raises(ValueError):
            git_check.get_branch_state('C:\\Windows\\', 'master')
        with pytest.raises(ValueError):
            git_check.get_branch_state(self.test_repo, 3.142)
        with pytest.raises(ValueError):
            git_check.get_branch_state(self.test_repo, 99999999)

    def test_get_branch_state_invalid_repo(self):
        with pytest.raises(git.exc.NoSuchPathError):
            git_check.get_branch_state(git.Repo('/not/a/path'),
                                        'master')
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            git_check.get_branch_state(git.Repo('/'),
                                        'master')

    def test_get_branch_state_invalid_branch(self):
        with pytest.raises(IndexError):
            git_check.get_branch_state(self.test_repo, 'random text')

    # Test get_branch_report method
    def test_get_branch_report_return_type(self):
        self.branch_list = [{'name': 'master', 'state': 'synced'}]
        assert isinstance(git_check.get_branch_report(self.branch_list), str)

    def test_get_branch_report_synced(self):
        self.branch_list = [{'name': 'master', 'state': 'synced'}]
        self.response = git_check.get_branch_report(self.branch_list)
        assert 'in sync' in self.response

    def test_get_branch_report_behind(self):
        self.branch_list = [{'name': 'master', 'state': 'behind'}]
        self.response = git_check.get_branch_report(self.branch_list)
        assert 'behind' in self.response

    def test_get_branch_report_ahead(self):
        self.branch_list = [{'name': 'master', 'state': 'ahead'}]
        self.response = git_check.get_branch_report(self.branch_list)
        assert 'ahead' in self.response

    def test_get_branch_report_untracked(self):
        self.branch_list = [{'name': 'master', 'state': 'untracked'}]
        self.response = git_check.get_branch_report(self.branch_list)
        assert 'not tracking' in self.response

    def test_get_branch_report_unsynced(self):
        self.branch_list = [{'name': 'master', 'state': 'out-of-sync'}]
        self.response = git_check.get_branch_report(self.branch_list)
        assert 'out of sync' in self.response

    def test_get_branch_report_invalid_input(self):
        with pytest.raises(ValueError):
            git_check.get_branch_report([])
        with pytest.raises(ValueError):
            git_check.get_branch_report(['apple', 'orange', 'carrot'])
        with pytest.raises(ValueError):
            git_check.get_branch_report('Random text')
        with pytest.raises(ValueError):
            git_check.get_branch_report(3.142)
        with pytest.raises(ValueError):
            git_check.get_branch_report(99999999)
        with pytest.raises(ValueError):
            git_check.get_branch_report('/usr/bin')
        with pytest.raises(ValueError):
            git_check.get_branch_report('C:\\Windows\\')

    # Test show_status method
    def test_show_status_contains_at_least_something(self, capsys):
        git_check.show_status(self.test_repo)
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_show_status_invalid_input(self):
        with pytest.raises(ValueError):
            git_check.show_status(self.test_dir)
        with pytest.raises(ValueError):
            git_check.show_status('Random text')
        with pytest.raises(ValueError):
            git_check.show_status(3.142)
        with pytest.raises(ValueError):
            git_check.show_status(99999999)
        with pytest.raises(ValueError):
            git_check.show_status('/usr/bin')
        with pytest.raises(ValueError):
            git_check.show_status('C:\\Windows\\')

    def test_show_status_invalid_repo(self):
        with pytest.raises(git.exc.NoSuchPathError):
            git_check.show_status(git.Repo('/not/a/path'))
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            git_check.show_status(git.Repo('/'))

    # Test fetch_all_remotes method
    @pytest.mark.slow
    def test_fetch_all_remotes_quiet(self, capsys):
        git_check.fetch_all_remotes(self.test_repo, show_progress=False)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.slow
    def test_fetch_all_remotes_with_progress(self, capsys):
        git_check.fetch_all_remotes(self.test_repo, show_progress=True)
        captured = capsys.readouterr()
        if len(self.test_repo.remotes) == 0:
            assert len(captured.out) == 0
        else:
            assert captured.out.startswith('Fetching')
            assert captured.out.endswith('done.\n')

    @pytest.mark.slow
    def test_fetch_all_remotes_default(self, capsys):
        git_check.fetch_all_remotes(self.test_repo) # default show_progress=False
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_fetch_all_remotes_invalid_input(self):
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(self.test_dir)
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes('Random text')
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(3.142)
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(99999999)
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes('/usr/bin')
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes('C:\\Windows\\')
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(self.test_dir, False)
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes('Random text', False)
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(3.142, False)
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(99999999, False)
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes('/usr/bin', False)
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes('C:\\Windows\\', False)
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(self.test_repo, 'false')
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(self.test_repo, 'True')
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(self.test_repo, 1)
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(self.test_repo, 0)
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(self.test_repo, 3.142)
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(self.test_repo, 99999999)
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(self.test_repo, 'random text')
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(self.test_repo, '/')
        with pytest.raises(ValueError):
            git_check.fetch_all_remotes(self.test_repo, self.test_repo)

    def test_fetch_all_remotes_invalid_repo(self):
        with pytest.raises(git.exc.NoSuchPathError):
            git_check.fetch_all_remotes(git.Repo('/not/a/path'))
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            git_check.fetch_all_remotes(git.Repo('/'))

    # Test report method
    def test_report_output_no_fetch(self, capsys):
        git_check.report(self.test_repo, fetch=False)
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert self.test_dir in captured.out
        assert 'Remotes' in captured.out
        assert 'Fetch' not in captured.out
        assert 'Branches' in captured.out
        assert 'Status' in captured.out

    @pytest.mark.slow
    def test_report_output_explicit_fetch(self, capsys):
        git_check.report(self.test_repo, fetch=True)
        captured = capsys.readouterr()
        assert 'Fetch' in captured.out

    @pytest.mark.slow
    def test_report_output_default_fetch(self, capsys):
        git_check.report(self.test_repo)
        captured = capsys.readouterr()
        assert 'Fetch' in captured.out

    def test_report_invalid_input(self):
        with pytest.raises(ValueError):
            git_check.report(self.test_dir, fetch=False)
        with pytest.raises(ValueError):
            git_check.report('Random text', fetch=False)
        with pytest.raises(ValueError):
            git_check.report(3.142, fetch=False)
        with pytest.raises(ValueError):
            git_check.report(99999999, fetch=False)
        with pytest.raises(ValueError):
            git_check.report('/usr/bin', fetch=False)
        with pytest.raises(ValueError):
            git_check.report('C:\\Windows\\', fetch=False)
        with pytest.raises(ValueError):
            git_check.report(self.test_repo, fetch='false')
        with pytest.raises(ValueError):
            git_check.report(self.test_repo, fetch='True')
        with pytest.raises(ValueError):
            git_check.report(self.test_repo, fetch=1)
        with pytest.raises(ValueError):
            git_check.report(self.test_repo, fetch=0)
        with pytest.raises(ValueError):
            git_check.report(self.test_repo, fetch=3.142)
        with pytest.raises(ValueError):
            git_check.report(self.test_repo, fetch=99999999)
        with pytest.raises(ValueError):
            git_check.report(self.test_repo, fetch='random text')
        with pytest.raises(ValueError):
            git_check.report(self.test_repo, fetch='/')
        with pytest.raises(ValueError):
            git_check.report(self.test_repo, fetch=self.test_repo)

    def test_report_invalid_repo(self):
        with pytest.raises(git.exc.NoSuchPathError):
            git_check.report(git.Repo('/not/a/path'), fetch=False)
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            git_check.report(git.Repo('/'), fetch=False)


    # Test show_all method
    def test_show_all_output(self, capsys):
        git_check.show_all()
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert 'clean' in captured.out
        assert 'dirty' in captured.out

    def test_show_all_with_branches(self, capsys):
        git_check.show_all(branches=True)
        captured = capsys.readouterr()
        assert 'branch' in captured.out

    def test_show_all_no_branches(self, capsys):
        git_check.show_all(branches=False)
        captured = capsys.readouterr()
        assert 'branch' not in captured.out

    def test_show_all_default(self, capsys):
        git_check.show_all() # default branches = True
        captured = capsys.readouterr()
        assert 'branch' in captured.out

    def test_show_all_invalid_input(self):
        with pytest.raises(ValueError):
            git_check.show_all(branches='false')
        with pytest.raises(ValueError):
            git_check.show_all(branches='True')
        with pytest.raises(ValueError):
            git_check.show_all(branches=0)
        with pytest.raises(ValueError):
            git_check.show_all(branches=1)
        with pytest.raises(ValueError):
            git_check.show_all(branches=3.142)
        with pytest.raises(ValueError):
            git_check.show_all(branches=99999999)
        with pytest.raises(ValueError):
            git_check.show_all(branches='random text')
        with pytest.raises(ValueError):
            git_check.show_all(branches='/')
        with pytest.raises(ValueError):
            git_check.show_all(branches=self.test_repo)

    # Test fetch_all method
    @pytest.mark.slow
    def test_fetch_all_quiet(self, capsys):
        git_check.fetch_all(show_progress=False)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.slow
    def test_fetch_all_with_progress(self, capsys):
        git_check.fetch_all(show_progress=True)
        captured = capsys.readouterr()
        if len(self.test_repo.remotes) == 0:
            assert len(captured.out) == 0
        else:
            assert captured.out.startswith('Fetching')
            assert captured.out.endswith('done.\n')

    @pytest.mark.slow
    def test_fetch_all_default(self, capsys):
        git_check.fetch_all() # default show_progress=False
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_fetch_all_invalid_input(self):
        with pytest.raises(ValueError):
            git_check.fetch_all(show_progress='false')
        with pytest.raises(ValueError):
            git_check.fetch_all(show_progress='True')
        with pytest.raises(ValueError):
            git_check.fetch_all(show_progress=0)
        with pytest.raises(ValueError):
            git_check.fetch_all(show_progress=1)
        with pytest.raises(ValueError):
            git_check.fetch_all(show_progress=3.142)
        with pytest.raises(ValueError):
            git_check.fetch_all(show_progress=99999999)
        with pytest.raises(ValueError):
            git_check.fetch_all(show_progress='random text')
        with pytest.raises(ValueError):
            git_check.fetch_all(show_progress='/')
        with pytest.raises(ValueError):
            git_check.fetch_all(show_progress=self.test_repo)

    # Test report_all method
    def test_report_all_output_no_fetch(self, capsys):
        git_check.report_all(fetch=False)
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert self.scripts_dir in captured.out
        assert 'Remotes' in captured.out
        assert 'Fetch' not in captured.out
        assert 'Branches' in captured.out
        assert 'Status' in captured.out

    @pytest.mark.slow
    def test_report_all_output_explicit_fetch(self, capsys):
        git_check.report_all(fetch=True)
        captured = capsys.readouterr()
        assert 'Fetch' in captured.out

    @pytest.mark.slow
    def test_report_all_output_default_fetch(self, capsys):
        git_check.report_all()
        captured = capsys.readouterr()
        assert 'Fetch' in captured.out

    def test_report_all_input(self):
        git_check.report_all(filter='none', fetch=False)
        git_check.report_all(filter='exists', fetch=False)
        git_check.report_all(filter='dirty', fetch=False)
        git_check.report_all(filter='out-of-sync', fetch=False)
        git_check.report_all(filter='not clean', fetch=False)

    def test_report_all_invalid_input(self):
        with pytest.raises(ValueError):
            git_check.report_all(fetch='false')
        with pytest.raises(ValueError):
            git_check.report_all(fetch='True')
        with pytest.raises(ValueError):
            git_check.report_all(fetch=0)
        with pytest.raises(ValueError):
            git_check.report_all(fetch=1)
        with pytest.raises(ValueError):
            git_check.report_all(fetch=3.142)
        with pytest.raises(ValueError):
            git_check.report_all(fetch=99999999)
        with pytest.raises(ValueError):
            git_check.report_all(fetch='random text')
        with pytest.raises(ValueError):
            git_check.report_all(fetch='/')
        with pytest.raises(ValueError):
            git_check.report_all(fetch=self.test_repo)
        with pytest.raises(ValueError):
            git_check.report_all(filter='random text', fetch=False)
        with pytest.raises(ValueError):
            git_check.report_all(filter=False, fetch=False)
        with pytest.raises(ValueError):
            git_check.report_all(filter=None, fetch=False)
        with pytest.raises(ValueError):
            git_check.report_all(filter=3.142, fetch=False)
        with pytest.raises(ValueError):
            git_check.report_all(filter=99999999, fetch=False)
        with pytest.raises(ValueError):
            git_check.report_all(filter='/', fetch=False)
        with pytest.raises(ValueError):
            git_check.report_all(filter=self.test_repo, fetch=False)
