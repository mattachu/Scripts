# Tests git-check.py

import git_check
import pytest
import git
import pathlib
import socket

class TestGitCheck:

    # Set paths
    hostname = socket.gethostname()
    if hostname == 'MJEaston':
        scripts_dir = 'C:\\Users\\Matt\\Code\\Scripts'
    elif 'MacBook Pro' in hostname:
        scripts_dir = '/Users/Matt/Code/Scripts'
    elif hostname == 'ubuntu42':
        scripts_dir = '/home/matt/Code/Scripts'

    # Setup before testing
    def setup_class(self):
        self.test_dir = self.scripts_dir
        self.test_repo = git.Repo(pathlib.Path(self.test_dir))


    # Test get_repo_path_list method
    def test_get_repo_path_list_return_type(self):
        self.repo_path_list = git_check.get_repo_path_list()
        assert isinstance(self.repo_path_list, list)

    def test_get_repo_path_list_contains_scripts(self):
        self.repo_path_list = git_check.get_repo_path_list()
        assert pathlib.Path(self.scripts_dir) in self.repo_path_list


    # Test list_remotes method
    def test_list_remotes_header(self, capsys):
        git_check.list_remotes(self.test_repo)
        captured = capsys.readouterr()
        assert captured.out.startswith('## Remotes')

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
            git_check.list_remotes(git.Repo(pathlib.Path('/not/a/path')))
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            git_check.list_remotes(git.Repo(pathlib.Path('/')))

    # Test list_branches method
    def test_list_branches_header(self, capsys):
        git_check.list_branches(self.test_repo)
        captured = capsys.readouterr()
        assert captured.out.startswith('## Branches')

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
            git_check.list_branches(git.Repo(pathlib.Path('/not/a/path')))
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            git_check.list_branches(git.Repo(pathlib.Path('/')))

    # Test show_status method
    def test_show_status_header(self, capsys):
        git_check.show_status(self.test_repo)
        captured = capsys.readouterr()
        assert captured.out.startswith('## Status')

    def test_show_status_contains_at_least_something(self, capsys):
        git_check.show_status(self.test_repo)
        captured = capsys.readouterr()
        assert captured.out != '## Status\n'

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
            git_check.show_status(git.Repo(pathlib.Path('/not/a/path')))
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            git_check.show_status(git.Repo(pathlib.Path('/')))

    # Test fetch_all_remotes method
    @pytest.mark.slow
    def test_fetch_all_remotes_quiet(self, capsys):
        assert 1 == 0
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

    def test_fetch_all_remotes_invalid_repo(self):
        with pytest.raises(git.exc.NoSuchPathError):
            git_check.fetch_all_remotes(git.Repo(pathlib.Path('/not/a/path')))
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            git_check.fetch_all_remotes(git.Repo(pathlib.Path('/')))

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

    def test_report_invalid_repo(self):
        with pytest.raises(git.exc.NoSuchPathError):
            git_check.report(git.Repo(pathlib.Path('/not/a/path')), fetch=False)
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            git_check.report(git.Repo(pathlib.Path('/')), fetch=False)

    @pytest.mark.slow
    def test_report_output_explicit_fetch(self, capsys):
        git_check.report(self.test_dir, fetch=True)
        captured = capsys.readouterr()
        assert 'Fetch' in captured.out

    @pytest.mark.slow
    def test_report_output_default_fetch(self, capsys):
        git_check.report(self.test_dir)
        captured = capsys.readouterr()
        assert 'Fetch' in captured.out


    # Test show_all method
    def test_show_all_output(self, capsys):
        git_check.show_all()
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert 'clean' in captured.out
        assert 'dirty' in captured.out

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