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

    # Test get_repo_list method
    def test_get_repo_list_return_type(self):
        self.repo_list = git_check.get_repo_list()
        assert isinstance(self.repo_list, list)

    def test_get_repo_list_contains_scripts(self):
        self.repo_list = git_check.get_repo_list()
        assert pathlib.Path(self.scripts_dir) in self.repo_list

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
        assert captured.out != "## Branches\n"

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
        assert captured.out != "## Status\n"

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

    def test_show_statuss_invalid_repo(self):
        with pytest.raises(git.exc.NoSuchPathError):
            git_check.show_status(git.Repo(pathlib.Path('/not/a/path')))
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            git_check.show_status(git.Repo(pathlib.Path('/')))

    # Test show_all
    def test_show_all_output(self, capsys):
        git_check.show_all()
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert 'clean' in captured.out
        assert 'dirty' in captured.out

    # -------------------------------------------------------------
    # Note: tests below here include fetching data over the network
    # -------------------------------------------------------------

    # Test fetch_all method
    def test_fetch_all_quiet(self, capsys):
        git_check.fetch_all(self.test_repo, show_progress=False)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_fetch_all_with_progress(self, capsys):
        git_check.fetch_all(self.test_repo, show_progress=True)
        captured = capsys.readouterr()
        if len(self.test_repo.remotes) == 0:
            assert len(captured.out) == 0
        else:
            assert captured.out.startswith("Fetching")
            assert captured.out.endswith("done.\n")

    def test_fetch_all_default(self, capsys):
        git_check.fetch_all(self.test_repo) # default show_progress=False
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_fetch_all_invalid_input(self):
        with pytest.raises(ValueError):
            git_check.fetch_all(self.test_dir)
        with pytest.raises(ValueError):
            git_check.fetch_all('Random text')
        with pytest.raises(ValueError):
            git_check.fetch_all(3.142)
        with pytest.raises(ValueError):
            git_check.fetch_all(99999999)
        with pytest.raises(ValueError):
            git_check.fetch_all('/usr/bin')
        with pytest.raises(ValueError):
            git_check.fetch_all('C:\\Windows\\')

    def test_fetch_all_invalid_repo(self):
        with pytest.raises(git.exc.NoSuchPathError):
            git_check.fetch_all(git.Repo(pathlib.Path('/not/a/path')))
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            git_check.fetch_all(git.Repo(pathlib.Path('/')))

    # Test check_repo
    def test_check_repo_output(self, capsys):
        git_check.check_repo(self.test_dir)
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert self.test_dir in captured.out
        assert 'Remotes' in captured.out
        assert 'Fetch' in captured.out
        assert 'Branches' in captured.out
        assert 'Status' in captured.out

    def test_check_repo_accepts_repo_as_input(self, capsys):
        git_check.check_repo(self.test_repo)
        captured = capsys.readouterr()
        assert self.test_dir in captured.out

    def test_check_repo_accepts_path_as_input(self, capsys):
        git_check.check_repo(pathlib.Path(self.test_dir))
        captured = capsys.readouterr()
        assert self.test_dir in captured.out

    def test_check_repo_invalid_input(self):
        with pytest.raises(ValueError):
            git_check.check_repo(3.142)
        with pytest.raises(ValueError):
            git_check.check_repo(99999999)
        with pytest.raises(ValueError):
            git_check.check_repo([self.test_dir, self.test_dir])

    def test_check_repo_invalid_repo(self):
        with pytest.raises(git.exc.NoSuchPathError):
            git_check.check_repo('/not/a/path')
        with pytest.raises(git.exc.NoSuchPathError):
            git_check.check_repo('Random text')
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            git_check.check_repo('/')

    # Test check_all
    def test_check_all_output(self, capsys):
        git_check.check_all()
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert self.scripts_dir in captured.out
        assert 'Remotes' in captured.out
        assert 'Fetch' in captured.out
        assert 'Branches' in captured.out
        assert 'Status' in captured.out
