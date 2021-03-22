# Tests run_batch.py

import run_batch
import pytest
import os
import pathlib
import shutil
import subprocess
from datetime import datetime
import git

RUN_FOLDER = pathlib.Path.home().joinpath('Simulations/Current')
SRC_PATH = pathlib.Path.home().joinpath('Code/Impact')
SRC_FOLDER = 'src'
EXE_NAME = 'ImpactTexe'
INSTALLDIR = pathlib.Path.home().joinpath('.local/bin')
REPRODUCIBLE = pathlib.Path.home().joinpath('Code/Reproducible')
PYENV = pathlib.Path.home().joinpath('.pyenv')

class TestRunBatch:

    # Setup before testing
    def setup_class(self):
        self.reproducible = REPRODUCIBLE
        self.reproduce = REPRODUCIBLE.joinpath('reproduce')
        self.pyenv = PYENV
        self.reproduce_python = PYENV.joinpath('versions/reproducible/bin/python3')
        self.test_message = 'Hello world'
        self.reproduce_message = 'Current run hash'
        self.input_branch = 'input/no-spacecharge'
        self.results_branch = 'results/clapa-t-collection'
        self.logfile = 'simulations.log'
        self.archive_log = 'simulation.log'
        self.arguments = {
            '<command>': f'echo {self.test_message}',
            '--help': False,
            '--git': False,
            '--archive': False,
            '--full': False,
            '--clean': False,
            '--class': None,
            '--input_branch': None,
            '--results_branch': None,
            '--sweep': None,
            '--post': False,
            '--config': False,
            '--logfile': False,
            '--runlog': False,
            '--devel': False,
            '--template': False,
            '--src': False,
            '--build': False,
            '--hash': False,
            '--show': False,
            '--save': False,
            '--list-parameters': False,
            '-p': False}
        self.single_run = self.arguments.copy()
        self.single_run.update({
            'title': 'Test run',
            'archive': None,
            'archive_move': None,
            'archive_copy': None,
            'commit_files': None,
            'commit_message': None})

    def get_run_folder(self, cloned_repo):
        return pathlib.Path(cloned_repo.working_dir)

    def get_src_location(self, cloned_src):
        return pathlib.Path(cloned_src.working_dir).joinpath(SRC_FOLDER)

    def get_settings(self, cloned_repo, tmp_archive):
        return {
            'current_folder': self.get_run_folder(cloned_repo),
            'archive_root': tmp_archive,
            'python': self.reproduce_python,
            'reproduce': self.reproduce,
            'logfile': self.logfile,
            'archive_log': self.archive_log}

    def add_repo(self, folder):
        """Add the given folder as a temporary repo for Reproducible."""
        command = [str(self.reproduce_python), str(self.reproduce),
                   'addrepo', '--force', 'temp', str(folder)]
        subprocess.run(command, cwd=self.reproducible, capture_output=True)


    # Fixtures
    @pytest.fixture(scope="class")
    def cloned_repo(self, tmp_path_factory):
        """Create a complete clone of repo in a temp folder."""
        source_repo = git.Repo(RUN_FOLDER)
        destination_path = tmp_path_factory.mktemp('run')
        cloned_repo = source_repo.clone(destination_path, branch='master')
        for branch in self.input_branch, self.results_branch:
            cloned_repo.create_head(branch, cloned_repo.remote().refs[branch])
        self.add_repo(destination_path)
        yield cloned_repo
        shutil.rmtree(destination_path)

    @pytest.fixture(scope="class")
    def cloned_src(self, tmp_path_factory):
        """Create a complete clone of the source code repo."""
        source_repo = git.Repo(SRC_PATH)
        destination_path = tmp_path_factory.mktemp('source')
        cloned_src = source_repo.clone(destination_path, branch='develop')
        yield cloned_src
        shutil.rmtree(destination_path)

    @pytest.fixture(scope="class")
    def tmp_archive(self, tmp_path_factory):
        """Create a temporary archive folder that persists across all tests."""
        tmp_archive = tmp_path_factory.mktemp('archive')
        yield tmp_archive
        shutil.rmtree(tmp_archive)

    @pytest.fixture
    def tmp_file(self, cloned_repo):
        filename = 'test_file.tmp'
        tempfile = self.get_run_folder(cloned_repo).joinpath(filename)
        with open(tempfile, 'w') as f:
            f.write(self.test_message)
        yield filename
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_file_factory(self, cloned_repo):
        created_files = []
        def _new_temp_file(filename):
            tempfile = self.get_run_folder(cloned_repo).joinpath(filename)
            with open(tempfile, 'w') as f:
                f.write(self.test_message)
            created_files.append(tempfile)
            return tempfile
        yield _new_temp_file
        for file in created_files:
            if file.is_file():
                file.unlink()

    @pytest.fixture
    def protect_log(self, cloned_repo, tmp_path):
        logfile = self.get_run_folder(cloned_repo).joinpath(self.logfile)
        assert len(set(self.get_run_folder(cloned_repo).glob('reproduce-*.log'))) == 0
        if logfile.is_file():
            temp_logfile = shutil.copy2(str(logfile), str(tmp_path))
        else:
            temp_logfile = None
        yield temp_logfile
        if temp_logfile:
            shutil.copy2(temp_logfile, str(self.get_run_folder(cloned_repo)))
        else:
            if logfile.is_file():
                logfile.unlink()
        for file in set(self.get_run_folder(cloned_repo).glob('reproduce-*.log')):
            file.unlink()

    @pytest.fixture
    def protect_git(self, cloned_repo, protect_log):
        initial_branch = cloned_repo.active_branch
        initial_commit = cloned_repo.commit()
        results_branch = cloned_repo.heads[self.results_branch]
        results_commit = cloned_repo.heads[self.results_branch].commit
        yield initial_commit
        initial_branch.commit = initial_commit
        results_branch.commit = results_commit
        initial_branch.checkout(force=True)

    @pytest.fixture
    def tmp_srcfile(self, cloned_src):
        filename = 'test_file.tmp'
        tempfile = self.get_src_location(cloned_src).joinpath(filename)
        with open(tempfile, 'w') as f:
            f.write(self.test_message)
        yield filename
        if tempfile.is_file():
            tempfile.unlink()

    # Not used as it affects the production file system
    # @pytest.fixture
    # def rebuild_src(self):
    #     exe = INSTALLDIR.joinpath(EXE_NAME)
    #     if exe.is_file():
    #         exe.unlink()
    #     yield exe

    @pytest.fixture
    def tmp_template(self, cloned_repo, protect_git):
        tmp_template = {
            'filename': 'template.tmp',
            'parameters': ['a', 'b', 'c'],
            'parameter_string': 'a:1,b:2,c:3',
            'text': 'Parameters include {{a}}, {{b}}, and {{c}}'}
        tempfile = self.get_run_folder(cloned_repo).joinpath(tmp_template['filename'])
        with open(tempfile, 'w') as f:
            f.write(tmp_template['text'])
        cloned_repo.index.add(tmp_template['filename'])
        cloned_repo.index.commit('Test commit')
        yield tmp_template
        if tempfile.is_file():
            tempfile.unlink()


    # Utility methods
    # Test get_folder method
    def test_get_folder_no_output(self, capsys):
        run_batch.get_folder()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_folder_return_type(self):
        test_folder = run_batch.get_folder()
        assert isinstance(test_folder, pathlib.PurePath)

    def test_get_folder_is_absolute(self):
        test_folder = run_batch.get_folder()
        assert test_folder.is_absolute()

    def test_get_folder_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_folder(0)

    def test_get_folder_current_folder_implicit(self):
        test_folder = run_batch.get_folder()
        assert test_folder == pathlib.Path.cwd().absolute()

    def test_get_folder_current_folder_explicit(self):
        test_folder = run_batch.get_folder('.')
        assert test_folder == pathlib.Path.cwd().absolute()

    def test_get_folder_archive_folder(self, tmp_archive):
        test_folder = run_batch.get_folder(tmp_archive)
        assert test_folder == tmp_archive

    # Test get_date_as_folder_name method
    def test_get_date_as_folder_name_no_output(self, capsys):
        run_batch.get_date_as_folder_name()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_date_as_folder_name_return_type(self):
        test_folder = run_batch.get_date_as_folder_name()
        assert isinstance(test_folder, str)

    def test_get_date_as_folder_name_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_date_as_folder_name(0)

    def test_get_date_as_folder_name_current_date(self):
        test_folder = run_batch.get_date_as_folder_name()
        assert test_folder == datetime.today().strftime('%Y-%m-%d')

    # Test get_safe_folder_name method
    def test_get_safe_folder_name_no_output(self, capsys):
        run_batch.get_safe_folder_name('test')
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_safe_folder_name_return_type(self):
        test_folder = run_batch.get_safe_folder_name('test')
        assert isinstance(test_folder, str)

    def test_get_safe_folder_name_invalid_input(self, cloned_repo, tmp_archive):
        with pytest.raises(TypeError):
            run_batch.get_safe_folder_name()
        with pytest.raises(TypeError):
            run_batch.get_safe_folder_name('test', 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.get_safe_folder_name(
                self.get_settings(cloned_repo, tmp_archive))

    def test_get_safe_folder_name_results(self):
        test_folder = run_batch.get_safe_folder_name('test')
        assert test_folder == 'test'
        test_folder = run_batch.get_safe_folder_name('test123')
        assert test_folder == 'test123'
        test_folder = run_batch.get_safe_folder_name('test with spaces')
        assert test_folder == 'test-with-spaces'
        test_folder = run_batch.get_safe_folder_name('test, incl. punctuation')
        assert test_folder == 'test-incl-punctuation'
        test_folder = run_batch.get_safe_folder_name('test with value 12.4')
        assert test_folder == 'test-with-value-12.4'
        test_folder = run_batch.get_safe_folder_name('test: even_stranger;((')
        assert test_folder == 'test-even_stranger'
        test_folder = run_batch.get_safe_folder_name('有中文的test')
        assert test_folder == '____test'
        test_folder = run_batch.get_safe_folder_name('E:1.5,I:1.0E-3,q:-1.0')
        assert test_folder == 'E-1.5-I-1.0E-3-q-1.0'

    # Test get_archive_folder method
    def test_get_archive_folder_no_output(self, capsys, tmp_archive):
        run_batch.get_archive_folder(tmp_archive)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_archive_folder_return_type(self, tmp_archive):
        test_folder = run_batch.get_archive_folder(tmp_archive)
        assert isinstance(test_folder, pathlib.PurePath)

    def test_get_archive_folder_is_absolute(self, tmp_archive):
        test_folder = run_batch.get_archive_folder(tmp_archive)
        assert test_folder.is_absolute()

    def test_get_archive_folder_invalid_input(self, tmp_archive):
        with pytest.raises(TypeError):
            run_batch.get_archive_folder()
        with pytest.raises(TypeError):
            run_batch.get_archive_folder(tmp_archive, 'extra parameter')
        with pytest.raises(AttributeError):
            run_batch.get_archive_folder('not a path')
        with pytest.raises(AttributeError):
            run_batch.get_archive_folder('/not/a/path')

    def test_get_archive_folder_contains_current_date(self, tmp_archive):
        test_folder = run_batch.get_archive_folder(tmp_archive)
        assert (datetime.today().strftime('%Y-%m-%d') in str(test_folder))

    def test_get_archive_folder_parent_exists(self, tmp_archive):
        test_folder = run_batch.get_archive_folder(tmp_archive)
        assert test_folder.parent.is_dir()

    # Test get_python_for_reproducible method
    def test_get_python_for_reproducible_no_output(self, capsys):
        run_batch.get_python_for_reproducible(self.reproducible, self.pyenv)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_python_for_reproducible_pyenv(self, capfd):
        test_python = run_batch.get_python_for_reproducible(self.reproducible,
                                                            self.pyenv)
        assert isinstance(test_python, str)
        assert pathlib.Path(test_python).is_file()
        assert pathlib.Path(test_python) == self.reproduce_python
        os.system(f'{str(test_python)} -c "print(\'{self.test_message}\')"')
        captured = capfd.readouterr()
        assert self.test_message in captured.out

    def test_get_python_for_reproducible_default(self, capfd):
        test_python = run_batch.get_python_for_reproducible(
            pathlib.Path().home(), '')
        assert isinstance(test_python, str)
        assert test_python == 'python3'
        os.system(f'{str(test_python)} -c "print(\'{self.test_message}\')"')
        captured = capfd.readouterr()
        assert self.test_message in captured.out

    def test_get_python_for_reproducible_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_python_for_reproducible(self.reproducible)
        with pytest.raises(TypeError):
            run_batch.get_python_for_reproducible(self.reproducible,
                                                  self.pyenv,
                                                  'extra parameter')
        with pytest.raises(AttributeError):
            run_batch.get_python_for_reproducible('not a path',
                                                  self.pyenv)
        with pytest.raises(AttributeError):
            run_batch.get_python_for_reproducible('/not/a/path',
                                                  self.pyenv)
        with pytest.raises(AttributeError):
            run_batch.get_python_for_reproducible(self.reproducible,
                                                  'not a path')
        with pytest.raises(AttributeError):
            run_batch.get_python_for_reproducible(self.reproducible,
                                                  '/not/a/path')


    # Communication methods
    # Test announce method
    def test_announce_output(self, capsys):
        run_batch.announce(self.test_message)
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert self.test_message in captured.out

    def test_announce_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.announce()
        with pytest.raises(TypeError):
            run_batch.announce(self.test_message, 'extra parameter')

    # Test announce_start method
    def test_announce_start_output(self, capsys):
        test_run = {'title': 'Test run'}
        run_batch.announce_start(test_run)
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert test_run['title'] in captured.out

    def test_announce_start_invalid_input(self):
        test_run = {'title': 'Test run'}
        with pytest.raises(TypeError):
            run_batch.announce_start()
        with pytest.raises(TypeError):
            run_batch.announce_start(test_run, 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.announce_start('not a dict')
        with pytest.raises(TypeError):
            run_batch.announce_start(3.142)

    # Test announce_end method
    def test_announce_end_output(self, capsys):
        test_run = {'title': 'Test run'}
        run_batch.announce_end(test_run)
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_announce_end_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.announce_end()
        with pytest.raises(TypeError):
            run_batch.announce_end('', '')
        with pytest.raises(TypeError):
            run_batch.announce_end('nothing')
        with pytest.raises(TypeError):
            run_batch.announce_end(3.142)

    # Test announce_error method
    def test_announce_error_output(self, capsys):
        run_batch.announce_error(self.test_message)
        captured = capsys.readouterr()
        assert len(captured.err) > 0
        assert self.test_message in captured.err

    def test_announce_error_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.announce_error()
        with pytest.raises(TypeError):
            run_batch.announce_error(self.test_message, 'extra parameter')


    # Git methods
    # Test get_git_repo method
    def test_get_git_repo_no_output(self, capsys, cloned_repo):
        run_batch.get_git_repo(self.get_run_folder(cloned_repo))
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_git_repo_return_type(self, cloned_repo):
        test_repo = run_batch.get_git_repo(self.get_run_folder(cloned_repo))
        assert isinstance(test_repo, git.Repo)

    def test_get_git_repo_input_type_path(self, cloned_repo):
        test_repo = run_batch.get_git_repo(self.get_run_folder(cloned_repo)
                                               .absolute())
        assert isinstance(test_repo, git.Repo)

    def test_get_git_repo_input_type_str(self, cloned_repo):
        test_repo = run_batch.get_git_repo(str(self.get_run_folder(cloned_repo)))
        assert isinstance(test_repo, git.Repo)

    def test_get_git_repo_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_git_repo(3.142)
        with pytest.raises(TypeError):
            run_batch.get_git_repo(99999999)
        with pytest.raises(OSError):
            run_batch.get_git_repo('not a path')
        with pytest.raises(OSError):
            run_batch.get_git_repo('/not/a/path/')
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            run_batch.get_git_repo('/')

    # Test git_checkout method
    @pytest.mark.gitchanges
    def test_git_checkout_no_output(self, capsys, cloned_repo, protect_git):
        run_batch.git_checkout(cloned_repo, 'master')
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.gitchanges
    def test_git_checkout_result(self, cloned_repo, protect_git):
        run_batch.git_checkout(cloned_repo, 'master')
        assert cloned_repo.head.reference == cloned_repo.heads['master']

    @pytest.mark.gitchanges
    def test_git_checkout_invalid_input(self, cloned_repo, protect_git):
        with pytest.raises(TypeError):
            run_batch.git_checkout(cloned_repo)
        with pytest.raises(TypeError):
            run_batch.git_checkout(cloned_repo, 'master', 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.git_checkout('not_a_repo', 'master')
        with pytest.raises(TypeError):
            run_batch.git_checkout(cloned_repo, cloned_repo)
        with pytest.raises(TypeError):
            run_batch.git_checkout(cloned_repo, 3.142)
        with pytest.raises(IndexError):
            run_batch.git_checkout(cloned_repo, 'not_a_branch')

    # Test git_switch method
    @pytest.mark.gitchanges
    def test_git_switch_no_output(self, capsys, cloned_repo, protect_git):
        run_batch.git_switch(cloned_repo, 'master')
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.gitchanges
    def test_git_switch_result(self, cloned_repo, protect_git):
        run_batch.git_switch(cloned_repo, 'master')
        assert cloned_repo.head.reference == cloned_repo.heads['master']

    @pytest.mark.gitchanges
    def test_git_switch_invalid_input(self, cloned_repo):
        with pytest.raises(TypeError):
            run_batch.git_switch(cloned_repo)
        with pytest.raises(TypeError):
            run_batch.git_switch(cloned_repo, 'master', 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.git_switch('not_a_repo', 'master')
        with pytest.raises(TypeError):
            run_batch.git_switch(cloned_repo, cloned_repo)
        with pytest.raises(TypeError):
            run_batch.git_switch(cloned_repo, 3.142)
        with pytest.raises(IndexError):
            run_batch.git_switch(cloned_repo, 'not_a_branch')

    # Test git_get_file method
    @pytest.mark.gitchanges
    def test_git_get_file_no_output(self, capsys, cloned_repo, protect_git):
        run_batch.git_get_file(cloned_repo, 'master', 'README.md')
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.gitchanges
    def test_git_get_file_result(self, cloned_repo, protect_git):
        os.remove(self.get_run_folder(cloned_repo).joinpath('README.md'))
        run_batch.git_get_file(cloned_repo, 'master', 'README.md')
        assert self.get_run_folder(cloned_repo).joinpath('README.md').is_file()

    def test_git_get_file_invalid_input(self, cloned_repo):
        with pytest.raises(TypeError):
            run_batch.git_get_file(cloned_repo)
        with pytest.raises(TypeError):
            run_batch.git_get_file(cloned_repo, 'master')
        with pytest.raises(TypeError):
            run_batch.git_get_file(cloned_repo, 'master', 'README.md',
                                   'extra parameter')
        with pytest.raises(TypeError):
            run_batch.git_get_file('not_a_repo', 'master', 'README.md')
        with pytest.raises(git.exc.GitCommandError):
            run_batch.git_get_file(cloned_repo, cloned_repo, 'README.md')
        with pytest.raises(git.exc.GitCommandError):
            run_batch.git_get_file(cloned_repo, 'master', cloned_repo)
        with pytest.raises(git.exc.GitCommandError):
            run_batch.git_get_file(cloned_repo, 3.142, 'README.md')
        with pytest.raises(git.exc.GitCommandError):
            run_batch.git_get_file(cloned_repo, 'not_a_branch', 'README.md')
        with pytest.raises(git.exc.GitCommandError):
            run_batch.git_get_file(cloned_repo, 'master', 'not_a_file.txt')

    # Test git_commit method
    @pytest.mark.gitchanges
    def test_git_commit_no_output(self, capsys, cloned_repo, protect_git, tmp_file):
        run_batch.git_commit(cloned_repo, tmp_file, 'Test commit')
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.gitchanges
    def test_git_commit_result(self, cloned_repo, protect_git, tmp_file):
        assert len(cloned_repo.untracked_files) == 1
        test_message = 'Test commit'
        run_batch.git_commit(cloned_repo, tmp_file, test_message)
        assert not cloned_repo.is_dirty()
        assert len(cloned_repo.untracked_files) == 0
        assert cloned_repo.head.commit.message == test_message

    @pytest.mark.gitchanges
    def test_git_commit_multiple(self, cloned_repo, protect_git, tmp_file_factory):
        test_files = ['test1.txt', 'test2.txt']
        test_message = 'Test commit'
        for filename in test_files:
            tmp_file_factory(filename)
        assert len(cloned_repo.untracked_files) == len(test_files)
        run_batch.git_commit(cloned_repo, test_files, test_message)
        for filename in test_files:
            assert self.get_run_folder(cloned_repo).joinpath(filename).is_file()
        assert not cloned_repo.is_dirty()
        assert len(cloned_repo.untracked_files) == 0
        assert cloned_repo.head.commit.message == test_message

    @pytest.mark.gitchanges
    def test_git_commit_invalid_input(self, cloned_repo):
        with pytest.raises(TypeError):
            run_batch.git_commit(cloned_repo)
        with pytest.raises(TypeError):
            run_batch.git_commit(cloned_repo, 'README.md')
        with pytest.raises(TypeError):
            run_batch.git_commit(cloned_repo, 'README.md', 'Test commit',
                                 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.git_commit('not_a_repo', 'README.md', 'Test commit')
        with pytest.raises(TypeError):
            run_batch.git_commit(cloned_repo, cloned_repo, 'Test commit')
        with pytest.raises(TypeError):
            run_batch.git_commit(cloned_repo,
                                 ['README.md', cloned_repo],
                                 'Test commit')
        with pytest.raises(AttributeError):
            run_batch.git_commit(cloned_repo, 'README.md', cloned_repo)
        with pytest.raises(TypeError):
            run_batch.git_commit(cloned_repo, 3.142, 'Test commit')
        with pytest.raises(FileNotFoundError):
            run_batch.git_commit(cloned_repo, 'not_a_file.txt', 'Test commit')

    # Test get_input_branch method
    def test_get_input_branch_no_output(self, cloned_repo, capsys):
        run_batch.get_input_branch(cloned_repo, self.arguments['--input_branch'])
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_git_input_branch_return_type(self, cloned_repo):
        test_branch = run_batch.get_input_branch(
            cloned_repo, self.arguments['--input_branch'])
        assert (   isinstance(test_branch, str)
                or isinstance(test_branch, list))

    def test_get_git_input_branch_exists(self, cloned_repo):
        test_branch = run_batch.get_input_branch(
            cloned_repo, self.arguments['--input_branch'])
        if isinstance(test_branch, str):
            assert test_branch in [head.name for head in cloned_repo.heads]
        elif isinstance(test_branch, list):
            for this_branch in test_branch:
                assert this_branch in [head.name for head in cloned_repo.heads]

    def test_get_git_input_branch_specified(self, cloned_repo):
        test_branch = run_batch.get_input_branch(cloned_repo, 'master')
        assert isinstance(test_branch, str)
        assert test_branch == 'master'

    def test_get_git_input_branch_multiple(self, cloned_repo):
        test_branch = run_batch.get_input_branch(cloned_repo,
                                                 ['master', 'master'])
        assert isinstance(test_branch, list)
        assert test_branch == ['master', 'master']

    def test_get_git_input_branch_invalid_input(self, cloned_repo):
        with pytest.raises(TypeError):
            run_batch.get_input_branch(cloned_repo)
        with pytest.raises(TypeError):
            run_batch.get_input_branch(cloned_repo,
                                       self.arguments['--input_branch'],
                                       'extra parameter')
        with pytest.raises(AttributeError):
            run_batch.get_input_branch('not a repo',
                                       self.arguments['--input_branch'])
        with pytest.raises(ValueError):
            run_batch.get_input_branch(cloned_repo, 'not a branch')
        with pytest.raises(ValueError):
            run_batch.get_input_branch(cloned_repo, ['master', 'not a branch'])

    # Test get_results_branch method
    def test_get_results_branch_no_output(self, capsys, cloned_repo):
        run_batch.get_results_branch(
            cloned_repo, self.arguments['--input_branch'])
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_git_results_branch_return_type(self, cloned_repo):
        test_branch = run_batch.get_results_branch(
            cloned_repo, self.arguments['--input_branch'])
        assert isinstance(test_branch, str)

    def test_get_git_results_branch_exits(self, cloned_repo):
        test_branch = run_batch.get_results_branch(
            cloned_repo, self.arguments['--input_branch'])
        assert test_branch in [head.name for head in cloned_repo.heads]

    def test_get_git_results_branch_specified(self, cloned_repo):
        test_branch = run_batch.get_results_branch(cloned_repo, 'master')
        assert isinstance(test_branch, str)
        assert test_branch == 'master'

    def test_get_git_results_branch_invalid_input(self, cloned_repo):
        with pytest.raises(TypeError):
            run_batch.get_results_branch(cloned_repo)
        with pytest.raises(TypeError):
            run_batch.get_results_branch(cloned_repo,
                                         self.arguments['--results_branch'],
                                         'extra parameter')
        with pytest.raises(AttributeError):
            run_batch.get_results_branch('not a dict',
                                         self.arguments['--results_branch'])
        with pytest.raises(ValueError):
            run_batch.get_results_branch(cloned_repo, [3.142, 9999])
        with pytest.raises(ValueError):
            run_batch.get_results_branch(cloned_repo, 'not a branch')

    # Test get_commit_files method
    def test_get_commit_files_no_output(self, capsys, cloned_repo, tmp_archive):
        run_batch.get_commit_files(
            self.get_settings(cloned_repo, tmp_archive), self.single_run)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_commit_files_no_logs(self, cloned_repo, tmp_archive):
        filelist = run_batch.get_commit_files(
            self.get_settings(cloned_repo, tmp_archive), self.single_run)
        assert self.get_settings(cloned_repo, tmp_archive)['logfile'] in filelist
        assert 'reproduce-*.log' not in filelist

    def test_get_commit_files_impact(self, cloned_repo, tmp_archive):
        test_run = self.single_run.copy()
        test_run['--class'] = 'impact'
        filelist = run_batch.get_commit_files(
            self.get_settings(cloned_repo, tmp_archive), self.single_run)
        assert self.get_settings(cloned_repo, tmp_archive)['logfile'] in filelist
        assert 'reproduce-*.log' not in filelist

    def test_get_commit_files_invalid_input(self, cloned_repo, tmp_archive):
        with pytest.raises(TypeError):
            run_batch.get_commit_files()
        with pytest.raises(TypeError):
            run_batch.get_commit_files(
                self.get_settings(cloned_repo, tmp_archive))
        with pytest.raises(TypeError):
            run_batch.get_commit_files(
                self.get_settings(cloned_repo, tmp_archive), self.single_run,
                'extra parameter')
        with pytest.raises(TypeError):
            run_batch.get_commit_files('not a dict', self.single_run)

    # Test get_commit_message method
    def test_get_commit_message_no_output(self, capsys):
        run_batch.get_commit_message(self.single_run)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_commit_message_contains_title(self):
        message = run_batch.get_commit_message(self.single_run)
        assert self.single_run['title'] in message

    def test_get_commit_message_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_commit_message()
        with pytest.raises(TypeError):
            run_batch.get_commit_message(self.single_run, 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.get_commit_files('not a dict')


    # Template methods
    # Test get_valid_templates method
    def test_get_valid_templates_no_output(self, capsys, cloned_repo):
        run_batch.get_valid_templates(
            self.get_run_folder(cloned_repo), 'not_a_file.in')
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_valid_templates_single_invalid_template(self, cloned_repo):
        valid, invalid = run_batch.get_valid_templates(
            self.get_run_folder(cloned_repo), 'not_a_file.in')
        assert valid is None
        assert isinstance(invalid, str)
        assert invalid == 'not_a_file.in'
        assert len(invalid.split(',')) == 1

    def test_get_valid_templates_single_valid_template(
            self, cloned_repo, tmp_file):
        valid, invalid = run_batch.get_valid_templates(
            self.get_run_folder(cloned_repo), tmp_file)
        assert isinstance(valid, str)
        assert invalid is None
        assert len(valid.split(',')) == 1
        assert valid == tmp_file

    def test_get_valid_templates_multiple_invalid_templates(self, cloned_repo):
        invalid_template_list = ['not_a_file1.in', 'not_a_file1.in']
        template_list = ','.join(invalid_template_list)
        valid, invalid = run_batch.get_valid_templates(
            self.get_run_folder(cloned_repo), template_list)
        assert valid is None
        assert isinstance(invalid, str)
        assert len(invalid.split(',')) == len(invalid_template_list)
        for template in invalid.split(','):
            assert template in invalid_template_list

    def test_get_valid_templates_multiple_valid_templates(
            self, cloned_repo, tmp_file_factory):
        valid_template_list = ['template1.in', 'template2.in']
        template_list = ','.join(valid_template_list)
        for template in valid_template_list:
            tmp_file_factory(template)
        valid, invalid = run_batch.get_valid_templates(
            self.get_run_folder(cloned_repo), template_list)
        assert isinstance(valid, str)
        assert invalid is None
        assert len(valid.split(',')) == len(valid_template_list)
        for template in valid.split(','):
            assert template in valid_template_list

    def test_get_valid_templates_mixed_templates(
            self, cloned_repo, tmp_file_factory):
        valid_template_list = ['template1.in', 'template2.in']
        invalid_template_list = ['not_a_file1.in', 'not_a_file1.in']
        template_list = ','.join(valid_template_list + invalid_template_list)
        for template in valid_template_list:
            tmp_file_factory(template)
        valid, invalid = run_batch.get_valid_templates(
            self.get_run_folder(cloned_repo), template_list)
        assert isinstance(valid, str)
        assert isinstance(invalid, str)
        assert len(valid.split(',')) == len(valid_template_list)
        assert len(invalid.split(',')) == len(invalid_template_list)
        for template in valid.split(','):
            assert template in valid_template_list
        for template in invalid.split(','):
            assert template in invalid_template_list

    def test_get_valid_templates_invalid_input(self, cloned_repo):
        with pytest.raises(TypeError):
            run_batch.get_valid_templates()
        with pytest.raises(TypeError):
            run_batch.get_valid_templates(self.get_run_folder(cloned_repo))
        with pytest.raises(TypeError):
            run_batch.get_valid_templates(
                self.get_run_folder(cloned_repo), None, 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.get_commit_files('not a folder', None)
        with pytest.raises(TypeError):
            run_batch.get_commit_files(
                self.get_run_folder(cloned_repo), ['not', 'a', 'string'])


    # Post-processing methods
    # Test post_process method
    def test_post_process_output(
            self, capfd, cloned_repo, tmp_archive, protect_log):
        test_message = 'Post-processing output'
        test_command = f'echo {test_message}'
        result = run_batch.post_process(
            self.get_settings(cloned_repo, tmp_archive), test_command)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert test_message in captured.out

    def test_post_process_invalid_input(self, cloned_repo, tmp_archive):
        test_message = 'Post-processing output'
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        test_command = f'echo {test_message}'
        with pytest.raises(TypeError):
            run_batch.post_process(test_settings)
        with pytest.raises(TypeError):
            run_batch.post_process(
                test_settings, test_command, 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.post_process('not settings', test_command)
        with pytest.raises(AttributeError):
            run_batch.post_process(test_settings, ['not', 'a', 'command'])
        with pytest.raises(TypeError):
            run_batch.post_process(['not', 'a', 'dict'], test_command)
        with pytest.raises(FileNotFoundError):
            run_batch.post_process(test_settings, 'not a command')


    # Archive methods
    # Test create_archive_folder method
    def test_create_archive_folder_no_output(self, capsys, tmp_path):
        run_batch.create_archive_folder(tmp_path.joinpath('temp'))
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_create_archive_folder_result(self, tmp_path):
        test_folder = tmp_path.joinpath('test')
        assert not test_folder.is_dir()
        run_batch.create_archive_folder(test_folder)
        assert test_folder.is_dir()

    def test_create_archive_folder_already_exists(self, capsys, tmp_path):
        assert tmp_path.is_dir()
        run_batch.create_archive_folder(tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0
        assert tmp_path.is_dir()

    def test_create_archive_folder_invalid_input(self, tmp_path):
        with pytest.raises(TypeError):
            run_batch.create_archive_folder()
        with pytest.raises(TypeError):
            run_batch.create_archive_folder(tmp_path,
                                            'extra parameter')
        with pytest.raises(AttributeError):
            run_batch.create_archive_folder('not a path')
        with pytest.raises(AttributeError):
            run_batch.create_archive_folder(['not', 'a', 'path'])
        with pytest.raises(AttributeError):
            run_batch.create_archive_folder(3.142)
        with pytest.raises(AttributeError):
            run_batch.create_archive_folder(None)

    # Test get_copy_list method
    def test_get_copy_list_no_output(self, capsys):
        run_batch.get_copy_list(self.arguments['--class'])
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_copy_list_default(self):
        copy_list = run_batch.get_copy_list(None)
        assert isinstance(copy_list, list)
        assert '*.in' in copy_list
        assert '*.data' in copy_list
        assert '*.txt' in copy_list
        assert '*.xlsx' in copy_list

    def test_get_copy_list_impact(self):
        copy_list = run_batch.get_copy_list('impact')
        assert isinstance(copy_list, list)
        assert '*.in' in copy_list
        assert '*.data' in copy_list
        assert '*.txt' in copy_list
        assert '*.xlsx' in copy_list

    def test_get_copy_list_bdsim(self):
        copy_list = run_batch.get_copy_list('bdsim')
        assert isinstance(copy_list, list)
        assert '*.gmad' in copy_list
        assert '*.data' in copy_list
        assert '*.txt' in copy_list
        assert '*.xlsx' in copy_list

    def test_get_copy_list_opal(self):
        copy_list = run_batch.get_copy_list('opal')
        assert isinstance(copy_list, list)
        assert '*.in' in copy_list
        assert '*.data' in copy_list
        assert '*.txt' in copy_list
        assert '*.xlsx' in copy_list

    def test_get_copy_list_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_copy_list()
        with pytest.raises(TypeError):
            run_batch.get_copy_list(self.arguments['--class'], 'extra parameter')
        copy_list = run_batch.get_copy_list('not a class')
        assert isinstance(copy_list, list)

    # Test get_move_list method
    def test_get_move_list_no_output(self, capsys):
        run_batch.get_move_list(None, False)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_move_list_default(self):
        move_list = run_batch.get_move_list(None, False)
        assert isinstance(move_list, list)
        assert '*.log' in move_list

    def test_get_move_list_impact(self):
        move_list = run_batch.get_move_list('impact', False)
        assert isinstance(move_list, list)
        assert 'fort.*' not in move_list
        assert '*.dst' in move_list
        assert '*.plt' in move_list
        assert '*.log' in move_list

    def test_get_move_list_impact_full(self):
        move_list = run_batch.get_move_list('impact', True)
        assert isinstance(move_list, list)
        assert 'fort.*' in move_list
        assert '*.dst' in move_list
        assert '*.plt' in move_list
        assert '*.log' in move_list

    def test_get_move_list_bdsim(self):
        move_list = run_batch.get_move_list('bdsim', False)
        assert isinstance(move_list, list)
        assert '*.root' not in move_list
        assert '*.png' in move_list
        assert '*.eps' in move_list
        assert '*.log' in move_list

    def test_get_move_list_bdsim_full(self):
        move_list = run_batch.get_move_list('bdsim', True)
        assert isinstance(move_list, list)
        assert '*.root' in move_list
        assert '*.png' in move_list
        assert '*.eps' in move_list
        assert '*.log' in move_list

    def test_get_move_list_opal(self):
        move_list = run_batch.get_move_list('opal', False)
        assert isinstance(move_list, list)
        assert '*.h5' not in move_list
        assert '*.lbal' not in move_list
        assert '*.stat' not in move_list
        assert '*.dat' not in move_list
        assert 'data' not in move_list
        assert '*.log' in move_list

    def test_get_move_list_opal_full(self):
        move_list = run_batch.get_move_list('opal', True)
        assert isinstance(move_list, list)
        assert '*.h5' in move_list
        assert '*.lbal' in move_list
        assert '*.stat' in move_list
        assert '*.dat' in move_list
        assert 'data' in move_list
        assert '*.log' in move_list

    def test_get_move_list_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_move_list()
        with pytest.raises(TypeError):
            run_batch.get_move_list(self.arguments['--class'])
        with pytest.raises(TypeError):
            run_batch.get_move_list(self.arguments['--class'],
                                    self.arguments['--full'],
                                    'extra parameter')
        move_list = run_batch.get_move_list('not a class',
                                            self.arguments['--full'])
        assert isinstance(move_list, list)

    # Test get_delete_list method
    def test_get_delete_list_no_output(self, capsys):
        run_batch.get_delete_list(None)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_delete_list_default(self):
        delete_list = run_batch.get_delete_list(None)
        assert isinstance(delete_list, list)
        assert '*.log' in delete_list

    def test_get_delete_list_impact(self):
        delete_list = run_batch.get_delete_list('impact')
        assert isinstance(delete_list, list)
        assert 'fort.*' in delete_list
        assert '*.dst' in delete_list
        assert '*.plt' in delete_list
        assert '*.log' in delete_list

    def test_get_delete_list_bdsim(self):
        delete_list = run_batch.get_delete_list('bdsim')
        assert isinstance(delete_list, list)
        assert '*.root' in delete_list
        assert '*.png' in delete_list
        assert '*.eps' in delete_list
        assert '*.log' in delete_list

    def test_get_delete_list_opal(self):
        delete_list = run_batch.get_delete_list('opal')
        assert isinstance(delete_list, list)
        assert '*.h5' in delete_list
        assert '*.lbal' in delete_list
        assert '*.stat' in delete_list
        assert '*.dat' in delete_list
        assert 'data' in delete_list
        assert '*.log' in delete_list

    def test_get_delete_list_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_delete_list()
        with pytest.raises(TypeError):
            run_batch.get_delete_list(self.arguments['--class'],
                                      'extra parameter')
        delete_list = run_batch.get_delete_list('not a class')
        assert isinstance(delete_list, list)

    # Test copy_to_archive method
    def test_copy_to_archive_no_output(self, capsys, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        run_batch.copy_to_archive(source, destination, [])
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_copy_to_archive_single_file(self, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        test_file = 'test_file.tmp'
        with open(source.joinpath(test_file), 'w') as f:
            f.write(self.test_message)
        run_batch.copy_to_archive(source, destination, [test_file])
        assert source.joinpath(test_file).is_file()
        assert destination.joinpath(test_file).is_file()
        with open(source.joinpath(test_file), 'r') as f:
            assert f.readline() == self.test_message
        with open(destination.joinpath(test_file), 'r') as f:
            assert f.readline() == self.test_message

    def test_copy_to_archive_single_pattern(self, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        test_files = ['file1.tmp', 'file2.tmp']
        for filename in test_files:
            with open(source.joinpath(filename), 'w') as f:
                f.write(self.test_message)
        run_batch.copy_to_archive(source, destination, ['*.tmp'])
        for filename in test_files:
            assert source.joinpath(filename).is_file()
            assert destination.joinpath(filename).is_file()
            with open(source.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message
            with open(destination.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    def test_copy_to_archive_multiple_patterns(self, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        test_files = ['file1.tmp', 'file2.tmp', 'file3.tmp2']
        for filename in test_files:
            with open(source.joinpath(filename), 'w') as f:
                f.write(self.test_message)
        run_batch.copy_to_archive(source,
                                  destination,
                                  ['*.tmp', '*.tmp2'])
        for filename in test_files:
            assert source.joinpath(filename).is_file()
            assert destination.joinpath(filename).is_file()
            with open(source.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message
            with open(destination.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    def test_copy_to_archive_overlapping_patterns(self, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        test_files = ['file1.tmp', 'file2.tmp', 'file3.tmp']
        for filename in test_files:
            with open(source.joinpath(filename), 'w') as f:
                f.write(self.test_message)
        run_batch.copy_to_archive(source,
                                  destination,
                                  ['*.tmp', 'file3.*'])
        for filename in test_files:
            assert source.joinpath(filename).is_file()
            assert destination.joinpath(filename).is_file()
            with open(source.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message
            with open(destination.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    def test_copy_to_archive_null_pattern(self, capsys, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        test_files = ['file1.tmp', 'file2.tmp', 'file3.tmp']
        for filename in test_files:
            with open(source.joinpath(filename), 'w') as f:
                f.write(self.test_message)
        run_batch.copy_to_archive(source,
                                  destination,
                                  ['*.tmp', 'file3.*', '*.strange_extension'])
        captured = capsys.readouterr()
        assert len(captured.out) == 0
        for filename in test_files:
            assert source.joinpath(filename).is_file()
            assert destination.joinpath(filename).is_file()
            with open(source.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message
            with open(destination.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    def test_copy_to_archive_exclude_logfile(self, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        test_files = ['file1.log', 'file2.log', run_batch.LOGFILE]
        for filename in test_files:
            with open(source.joinpath(filename), 'w') as f:
                f.write(self.test_message)
        run_batch.copy_to_archive(source, destination, ['*.log'])
        for filename in test_files:
            assert source.joinpath(filename).is_file()
            with open(source.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message
            if filename == run_batch.LOGFILE:
                assert not destination.joinpath(filename).is_file()
            else:
                assert destination.joinpath(filename).is_file()
                with open(destination.joinpath(filename), 'r') as f:
                    assert f.readline() == self.test_message

    def test_copy_to_archive_invalid_input(self, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        with pytest.raises(TypeError):
            run_batch.copy_to_archive()
        with pytest.raises(TypeError):
            run_batch.copy_to_archive(source)
        with pytest.raises(TypeError):
            run_batch.copy_to_archive(source, destination)
        with pytest.raises(TypeError):
            run_batch.copy_to_archive(source, destination, [],
                                      'extra parameter')
        with pytest.raises(AttributeError):
            run_batch.copy_to_archive('not a path', destination, [])
        with pytest.raises(AttributeError):
            run_batch.copy_to_archive(source, 'not a path', [])
        with pytest.raises(ValueError):
            run_batch.copy_to_archive(source, destination, 'not a list')

    # Test move_to_archive method
    def test_move_to_archive_no_output(self, capsys, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        run_batch.move_to_archive(source, destination, [])
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_move_to_archive_single_file(self, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        test_file = 'test_file.tmp'
        with open(source.joinpath(test_file), 'w') as f:
            f.write(self.test_message)
        run_batch.move_to_archive(source, destination, [test_file])
        assert destination.joinpath(test_file).is_file()
        assert not source.joinpath(test_file).is_file()
        with open(destination.joinpath(test_file), 'r') as f:
            assert f.readline() == self.test_message

    def test_move_to_archive_single_pattern(self, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        test_files = ['file1.tmp', 'file2.tmp']
        for filename in test_files:
            with open(source.joinpath(filename), 'w') as f:
                f.write(self.test_message)
        run_batch.move_to_archive(source, destination, ['*.tmp'])
        for filename in test_files:
            assert destination.joinpath(filename).is_file()
            assert not source.joinpath(filename).is_file()
            with open(destination.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    def test_move_to_archive_multiple_patterns(self, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        test_files = ['file1.tmp', 'file2.tmp', 'file3.tmp2']
        for filename in test_files:
            with open(source.joinpath(filename), 'w') as f:
                f.write(self.test_message)
        run_batch.move_to_archive(source,
                                  destination,
                                  ['*.tmp', '*.tmp2'])
        for filename in test_files:
            assert destination.joinpath(filename).is_file()
            assert not source.joinpath(filename).is_file()
            with open(destination.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    def test_move_to_archive_overlapping_patterns(self, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        test_files = ['file1.tmp', 'file2.tmp', 'file3.tmp']
        for filename in test_files:
            with open(source.joinpath(filename), 'w') as f:
                f.write(self.test_message)
        run_batch.move_to_archive(source,
                                  destination,
                                  ['*.tmp', 'file3.*'])
        for filename in test_files:
            assert destination.joinpath(filename).is_file()
            assert not source.joinpath(filename).is_file()
            with open(destination.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    def test_move_to_archive_null_pattern(self, capsys, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        test_files = ['file1.tmp', 'file2.tmp', 'file3.tmp']
        for filename in test_files:
            with open(source.joinpath(filename), 'w') as f:
                f.write(self.test_message)
        run_batch.move_to_archive(source,
                                  destination,
                                  ['*.tmp', 'file3.*', '*.strange_extension'])
        captured = capsys.readouterr()
        assert len(captured.out) == 0
        for filename in test_files:
            assert destination.joinpath(filename).is_file()
            assert not source.joinpath(filename).is_file()
            with open(destination.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    def test_move_to_archive_exclude_logfile(self, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        test_files = ['file1.log', 'file2.log', run_batch.LOGFILE]
        for filename in test_files:
            with open(source.joinpath(filename), 'w') as f:
                f.write(self.test_message)
        run_batch.move_to_archive(source, destination, ['*.log'])
        for filename in test_files:
            if filename == run_batch.LOGFILE:
                assert source.joinpath(filename).is_file()
                assert not destination.joinpath(filename).is_file()
            else:
                assert destination.joinpath(filename).is_file()
                assert not source.joinpath(filename).is_file()
                with open(destination.joinpath(filename), 'r') as f:
                    assert f.readline() == self.test_message

    def test_move_to_archive_invalid_input(self, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        with pytest.raises(TypeError):
            run_batch.move_to_archive()
        with pytest.raises(TypeError):
            run_batch.move_to_archive(source)
        with pytest.raises(TypeError):
            run_batch.move_to_archive(source, destination)
        with pytest.raises(TypeError):
            run_batch.move_to_archive(source, destination, [],
                                      'extra parameter')
        with pytest.raises(AttributeError):
            run_batch.move_to_archive('not a path', destination, [])
        with pytest.raises(AttributeError):
            run_batch.move_to_archive(source, 'not a path', [])
        with pytest.raises(ValueError):
            run_batch.move_to_archive(source, destination, 'not a list')

    # Test move_rendered_templates method
    def test_move_rendered_templates_no_output(self, capsys, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        run_batch.move_rendered_templates(source, destination)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_move_rendered_templates(self, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        test_file = 'file1.tmp'
        test_render = 'file1.tmp.rendered'
        with open(source.joinpath(test_render), 'w') as f:
            f.write(self.test_message)
        run_batch.move_rendered_templates(source, destination)
        assert destination.joinpath(test_file).is_file()
        assert not source.joinpath(test_file).is_file()
        assert not destination.joinpath(test_render).is_file()
        assert not source.joinpath(test_render).is_file()
        with open(destination.joinpath(test_file), 'r') as f:
            assert f.readline() == self.test_message

    def test_move_rendered_templates_invalid_input(self, tmp_path_factory):
        source = tmp_path_factory.mktemp('from')
        destination = tmp_path_factory.mktemp('to')
        with pytest.raises(TypeError):
            run_batch.move_rendered_templates()
        with pytest.raises(TypeError):
            run_batch.move_rendered_templates(source)
        with pytest.raises(TypeError):
            run_batch.move_rendered_templates(source, destination,
                                              'extra parameter')
        with pytest.raises(AttributeError):
            run_batch.move_rendered_templates('not a path', destination)
        with pytest.raises(AttributeError):
            run_batch.move_rendered_templates(source, 'not a path')

    # Test archive_log method
    @pytest.mark.slow
    def test_archive_log_no_output(
            self, capsys, cloned_repo, tmp_archive, tmp_path):
        run_batch.archive_log(
            self.get_settings(cloned_repo, tmp_archive), tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.slow
    def test_archive_log_result(self, cloned_repo, tmp_archive, tmp_path):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        run_batch.archive_log(test_settings, tmp_path)
        assert tmp_path.joinpath(test_settings['archive_log']).is_file()
        with open(tmp_path.joinpath(test_settings['archive_log']), 'r') as f:
            assert f.readline()[0:6] == 'hash: '

    @pytest.mark.slow
    def test_archive_log_custom_filename(
            self, cloned_repo, tmp_archive, tmp_path):
        test_settings = self.get_settings(cloned_repo, tmp_archive).copy()
        test_settings['archive_log'] = 'archive.log'
        run_batch.archive_log(test_settings, tmp_path)
        assert tmp_path.joinpath(test_settings['archive_log']).is_file()
        with open(tmp_path.joinpath(test_settings['archive_log']), 'r') as f:
            assert f.readline()[0:6] == 'hash: '

    @pytest.mark.slow
    def test_archive_log_invalid_input(self, cloned_repo, tmp_archive, tmp_path):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        with pytest.raises(TypeError):
            run_batch.archive_log()
        with pytest.raises(TypeError):
            run_batch.archive_log(test_settings)
        with pytest.raises(TypeError):
            run_batch.archive_log(test_settings, tmp_path, 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.archive_log('not a dict', tmp_path)
        with pytest.raises(AttributeError):
            run_batch.archive_log(test_settings, 'not a path')

    # Test archive_output method
    @pytest.mark.slow
    def test_archive_output_no_output(
            self, capsys, cloned_repo, tmp_archive, tmp_path):
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': [],
                         'archive_move': []})
        run_batch.archive_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_archive_output_invalid_input(self, cloned_repo, tmp_archive, tmp_path):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': [],
                         'archive_move': []})
        with pytest.raises(TypeError):
            run_batch.archive_output(test_settings)
        with pytest.raises(TypeError):
            run_batch.archive_output(test_settings, test_run, 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.archive_output('not a dict', test_run)
        with pytest.raises(TypeError):
            run_batch.archive_output(test_settings, 'not a dict')

    @pytest.mark.slow
    def test_archive_output_copy_single_file(
            self, cloned_repo, tmp_archive, tmp_file, tmp_path):
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': [tmp_file],
                         'archive_move': []})
        run_batch.archive_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        assert tmp_path.joinpath(tmp_file).is_file()
        assert self.get_run_folder(cloned_repo).joinpath(tmp_file).is_file()
        assert tmp_path.joinpath('simulation.log').is_file()

    @pytest.mark.slow
    def test_archive_output_copy_files(
            self, cloned_repo, tmp_archive, tmp_file_factory, tmp_path):
        copy_files = ['file1.tmp', 'file2.tmp', 'file3.tmp2']
        for filename in copy_files:
            tmp_file_factory(filename)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': copy_files,
                         'archive_move': []})
        run_batch.archive_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        for filename in copy_files:
            assert tmp_path.joinpath(filename).is_file()
            assert self.get_run_folder(cloned_repo).joinpath(filename).is_file()
            with open(tmp_path.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    @pytest.mark.slow
    def test_archive_output_copy_patterns(
            self, cloned_repo, tmp_archive, tmp_file_factory, tmp_path):
        copy_files = ['file1.tmp', 'file2.tmp', 'file3.tmp2']
        for filename in copy_files:
            tmp_file_factory(filename)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': ['*.tmp', '*.tmp2'],
                         'archive_move': []})
        run_batch.archive_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        for filename in copy_files:
            assert tmp_path.joinpath(filename).is_file()
            assert self.get_run_folder(cloned_repo).joinpath(filename).is_file()
            with open(tmp_path.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    @pytest.mark.slow
    def test_archive_output_move_single_file(
            self, cloned_repo, tmp_archive, tmp_file, tmp_path):
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': [],
                         'archive_move': [tmp_file]})
        run_batch.archive_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        assert tmp_path.joinpath(tmp_file).is_file()
        assert not self.get_run_folder(cloned_repo).joinpath(tmp_file).is_file()
        assert tmp_path.joinpath('simulation.log').is_file()

    @pytest.mark.slow
    def test_archive_output_move_files(
            self, cloned_repo, tmp_archive, tmp_file_factory, tmp_path):
        move_files = ['file1.tmp', 'file2.tmp', 'file3.tmp2']
        for filename in move_files:
            tmp_file_factory(filename)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': [],
                         'archive_move': move_files})
        run_batch.archive_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        for filename in move_files:
            assert tmp_path.joinpath(filename).is_file()
            assert not self.get_run_folder(cloned_repo).joinpath(filename).is_file()
            with open(tmp_path.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    @pytest.mark.slow
    def test_archive_output_move_patterns(
            self, cloned_repo, tmp_archive, tmp_file_factory, tmp_path):
        move_files = ['file1.tmp', 'file2.tmp', 'file3.tmp2']
        for filename in move_files:
            tmp_file_factory(filename)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': [],
                         'archive_move': ['*.tmp', '*.tmp2']})
        run_batch.archive_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        for filename in move_files:
            assert tmp_path.joinpath(filename).is_file()
            assert not self.get_run_folder(cloned_repo).joinpath(filename).is_file()
            with open(tmp_path.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    @pytest.mark.slow
    def test_archive_output_copy_and_move(
            self, cloned_repo, tmp_archive, tmp_file_factory, tmp_path):
        copy_files = ['file1.tmp', 'file2.tmp', 'file3.tmp']
        move_files = ['file4.tmp2', 'file5.tmp2', 'file6.tmp3']
        for filename in (copy_files + move_files):
            tmp_file_factory(filename)
        test_folder = self.get_run_folder(cloned_repo)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': ['*.tmp'],
                         'archive_move': ['*.tmp2', 'file6.*']})
        run_batch.archive_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        for filename in copy_files:
            assert tmp_path.joinpath(filename).is_file()
            assert test_folder.joinpath(filename).is_file()
            with open(tmp_path.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message
        for filename in move_files:
            assert tmp_path.joinpath(filename).is_file()
            assert not test_folder.joinpath(filename).is_file()
            with open(tmp_path.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    @pytest.mark.slow
    def test_archive_output_exclude_logfile(
            self, cloned_repo, tmp_archive, tmp_file_factory, tmp_path):
        copy_files = ['file1.tmp', 'file2.tmp', 'file3.tmp']
        move_files = ['file4.log', 'file5.log', 'file6.data', run_batch.LOGFILE]
        for filename in (copy_files + move_files):
            tmp_file_factory(filename)
        test_folder = self.get_run_folder(cloned_repo)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': ['*.tmp'],
                         'archive_move': ['*.log', 'file6.*']})
        run_batch.archive_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        for filename in copy_files:
            assert test_folder.joinpath(filename).is_file()
            if filename == run_batch.LOGFILE:
                assert not tmp_path.joinpath(filename).is_file()
            else:
                assert tmp_path.joinpath(filename).is_file()
                with open(tmp_path.joinpath(filename), 'r') as f:
                    assert f.readline() == self.test_message
        for filename in move_files:
            if filename == run_batch.LOGFILE:
                assert test_folder.joinpath(filename).is_file()
                assert not tmp_path.joinpath(filename).is_file()
            else:
                assert not test_folder.joinpath(filename).is_file()
                assert tmp_path.joinpath(filename).is_file()
                with open(tmp_path.joinpath(filename), 'r') as f:
                    assert f.readline() == self.test_message

    @pytest.mark.slow
    def test_archive_output_move_rendered_templates(
            self, cloned_repo, tmp_archive, tmp_file_factory, tmp_path):
        test_folder = self.get_run_folder(cloned_repo)
        test_file = 'file1.tmp'
        test_render = 'file1.tmp.rendered'
        tmp_file_factory(test_render)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': [],
                         'archive_move': []})
        run_batch.archive_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        assert tmp_path.joinpath(test_file).is_file()
        assert not tmp_path.joinpath(test_render).is_file()
        assert not test_folder.joinpath(test_file).is_file()
        assert not test_folder.joinpath(test_render).is_file()

    # Test delete_output method
    def test_delete_output_no_output(
            self, capsys, cloned_repo, tmp_archive, tmp_path):
        run_batch.delete_output(
            self.get_settings(cloned_repo, tmp_archive), self.single_run)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_delete_output_invalid_input(
            self, cloned_repo, tmp_archive, tmp_path):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        with pytest.raises(TypeError):
            run_batch.delete_output(test_settings)
        with pytest.raises(TypeError):
            run_batch.delete_output(
                test_settings, self.single_run, 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.delete_output('not a dict', self.single_run)
        with pytest.raises(TypeError):
            run_batch.delete_output(test_settings, 'not a dict')

    def test_delete_output_default(
            self, cloned_repo, tmp_archive, tmp_file_factory):
        temp_files = ['tmp.png', 'tmp.eps', 'tmp.ps', 'tmp.jpg',
                      'reproduce-temp.log']
        for filename in temp_files:
            tmp_file_factory(filename)
        test_run = self.single_run.copy()
        test_run['--class'] = None
        run_batch.delete_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        for filename in temp_files:
            assert not self.get_run_folder(cloned_repo).joinpath(filename).is_file()

    def test_delete_output_impact(
            self, cloned_repo, tmp_archive, tmp_file_factory):
        temp_files = ['tmp.png', 'tmp.eps', 'tmp.ps', 'tmp.jpg',
                      'reproduce-temp.log', 'fort.tmp', 'tmp.dst', 'tmp.plt']
        for filename in temp_files:
            tmp_file_factory(filename)
        test_run = self.single_run.copy()
        test_run['--class'] = 'impact'
        run_batch.delete_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        for filename in temp_files:
            assert not self.get_run_folder(cloned_repo).joinpath(filename).is_file()

    def test_delete_output_bdsim(
            self, cloned_repo, tmp_archive, tmp_file_factory):
        temp_files = ['tmp.png', 'tmp.eps', 'tmp.ps', 'tmp.jpg',
                      'reproduce-temp.log', 'tmp.root']
        for filename in temp_files:
            tmp_file_factory(filename)
        test_run = self.single_run.copy()
        test_run['--class'] = 'bdsim'
        run_batch.delete_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        for filename in temp_files:
            assert not self.get_run_folder(cloned_repo).joinpath(filename).is_file()

    def test_delete_output_opal(
            self, cloned_repo, tmp_archive, tmp_file_factory):
        temp_files = ['tmp.png', 'tmp.eps', 'tmp.ps', 'tmp.jpg',
                      'reproduce-temp.log',
                      'tmp.h5', 'tmp.lbal', 'tmp.stat', 'tmp.dat', 'data']
        for filename in temp_files:
            tmp_file_factory(filename)
        test_run = self.single_run.copy()
        test_run['--class'] = 'opal'
        run_batch.delete_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        for filename in temp_files:
            assert not self.get_run_folder(cloned_repo).joinpath(filename).is_file()

    def test_delete_output_exclude_logfile(
            self, cloned_repo, tmp_archive, tmp_file_factory):
        temp_files = ['file1.log', 'file2.log', run_batch.LOGFILE]
        for filename in temp_files:
            tmp_file_factory(filename)
        test_run = self.single_run.copy()
        test_run['--class'] = None
        run_batch.delete_output(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        for filename in temp_files:
            if filename == run_batch.LOGFILE:
                assert self.get_run_folder(cloned_repo).joinpath(filename).is_file()
            else:
                assert not self.get_run_folder(cloned_repo).joinpath(filename).is_file()


    # Sweep methods
    # Test get_sweep_parameters method
    def test_get_sweep_parameters_no_output(self, capsys):
        test_sweep_parameter = 'I'
        test_sweep_values = [0.0, 0.2, 0.4, 0.6]
        test_sweep = (test_sweep_parameter + ':'
                      + ','.join([str(v) for v in test_sweep_values]))
        run_batch.get_sweep_parameters(test_sweep)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_sweep_parameters_single(self):
        test_sweep_parameter = 'I'
        test_sweep_values = [0.0, 0.2, 0.4, 0.6]
        test_sweep = (test_sweep_parameter + ':'
                      + ','.join([str(v) for v in test_sweep_values]))
        sweep_parameters = run_batch.get_sweep_parameters(test_sweep)
        assert isinstance(sweep_parameters, list)
        assert len(sweep_parameters) == 1
        assert sweep_parameters[0] == test_sweep_parameter

    def test_get_sweep_parameters_multiple(self):
        test_sweep = '(a,b):(1, 10),(2,20),(3,30),(4,40)'
        test_sweep_parameters = ['a', 'b']
        sweep_parameters = run_batch.get_sweep_parameters(test_sweep)
        assert isinstance(sweep_parameters, list)
        assert len(sweep_parameters) == 2
        assert sweep_parameters == test_sweep_parameters

    def test_get_sweep_parameters_multiple_no_brackets(self):
        test_sweep = 'a,b:(1, 10),(2,20),(3,30),(4,40)'
        test_sweep_parameters = ['a', 'b']
        sweep_parameters = run_batch.get_sweep_parameters(test_sweep)
        assert isinstance(sweep_parameters, list)
        assert len(sweep_parameters) == 2
        assert sweep_parameters == test_sweep_parameters

    def test_get_sweep_parameters_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_sweep_parameters()
        with pytest.raises(TypeError):
            run_batch.get_sweep_parameters('I:0.0,0.2,0.4', 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.get_sweep_parameters(3.142)
        with pytest.raises(TypeError):
            run_batch.get_sweep_parameters(['not', 'a', 'sweep', 'definition'])
        with pytest.raises(ValueError):
            run_batch.get_sweep_parameters('not a sweep definition')

    # Test get_sweep_values method
    def test_get_sweep_values_no_output(self, capsys):
        test_sweep_parameter = 'I'
        test_sweep_values = [0.0, 0.2, 0.4, 0.6]
        test_sweep = (test_sweep_parameter + ':'
                      + ','.join([str(v) for v in test_sweep_values]))
        run_batch.get_sweep_values(test_sweep)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_sweep_values_single(self):
        test_sweep_parameter = 'I'
        test_sweep_values = [0.0, 0.2, 0.4, 0.6]
        test_sweep = (test_sweep_parameter + ':'
                      + ','.join([str(v) for v in test_sweep_values]))
        values = run_batch.get_sweep_values(test_sweep)
        assert isinstance(values, list)
        assert len(values) == len(test_sweep_values)
        assert all([isinstance(value, str) for value in values])
        assert all([str(value) in values for value in test_sweep_values])

    def test_get_sweep_values_multiple(self):
        test_sweep = '(a,b):(1,10),(2,20),(3,30),(4,40)'
        test_sweep_values = [('1', '10'), ('2', '20'), ('3', '30'), ('4', '40')]
        values = run_batch.get_sweep_values(test_sweep)
        assert isinstance(values, list)
        assert len(values) == len(test_sweep_values)
        for i in range(len(values)):
            assert isinstance(values[i], tuple)
            assert len(values[i]) == len(test_sweep_values[i])
            assert all([isinstance(value, str) for value in values[i]])
            assert all([str(value) in values[i] for value in test_sweep_values[i]])

    def test_get_sweep_values_multiple_no_brackets(self):
        test_sweep = 'a,b:(1,10),(2,20),(3,30),(4,40)'
        test_sweep_values = [('1', '10'), ('2', '20'), ('3', '30'), ('4', '40')]
        values = run_batch.get_sweep_values(test_sweep)
        assert isinstance(values, list)
        assert len(values) == len(test_sweep_values)
        for i in range(len(values)):
            assert isinstance(values[i], tuple)
            assert len(values[i]) == len(test_sweep_values[i])
            assert all([isinstance(value, str) for value in values[i]])
            assert all([str(value) in values[i] for value in test_sweep_values[i]])

    def test_get_sweep_values_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_sweep_values()
        with pytest.raises(TypeError):
            run_batch.get_sweep_values('I:0.0,0.2,0.4', 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.get_sweep_values(3.142)
        with pytest.raises(TypeError):
            run_batch.get_sweep_values(['not', 'a', 'sweep', 'definition'])
        with pytest.raises(ValueError):
            run_batch.get_sweep_values('not a sweep definition')

    # Test get_sweep_strings method
    def test_get_sweep_strings_no_output(self, capsys):
        test_sweep_parameter = 'I'
        test_sweep_values = [0.0, 0.2, 0.4, 0.6]
        test_sweep = (test_sweep_parameter + ':'
                      + ','.join([str(v) for v in test_sweep_values]))
        run_batch.get_sweep_strings(test_sweep)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_sweep_strings_single(self):
        test_sweep_parameter = 'I'
        test_sweep_values = [0.0, 0.2, 0.4, 0.6]
        test_sweep = (test_sweep_parameter + ':'
                      + ','.join([str(v) for v in test_sweep_values]))
        sweeps = run_batch.get_sweep_strings(test_sweep)
        assert isinstance(sweeps, list)
        assert len(sweeps) == len(test_sweep_values)
        assert all([isinstance(sweep, str) for sweep in sweeps])
        assert all([sweep in sweeps
                    for sweep in [test_sweep_parameter + ':' + str(v)
                                  for v in test_sweep_values]])

    def test_get_sweep_strings_multiple(self):
        test_sweep = '(a,b):(1,10),(2,20),(3,30),(4,40)'
        test_sweep_strings = ['a:1,b:10', 'a:2,b:20', 'a:3,b:30', 'a:4,b:40']
        sweeps = run_batch.get_sweep_strings(test_sweep)
        assert isinstance(sweeps, list)
        assert len(sweeps) == len(test_sweep_strings)
        assert all([isinstance(sweep, str) for sweep in sweeps])
        assert all([sweep in sweeps
                    for sweep in test_sweep_strings])

    def test_get_sweep_strings_multiple_no_brackets(self):
        test_sweep = 'a,b:(1,10),(2,20),(3,30),(4,40)'
        test_sweep_strings = ['a:1,b:10', 'a:2,b:20', 'a:3,b:30', 'a:4,b:40']
        sweeps = run_batch.get_sweep_strings(test_sweep)
        assert isinstance(sweeps, list)
        assert len(sweeps) == len(test_sweep_strings)
        assert all([isinstance(sweep, str) for sweep in sweeps])
        assert all([sweep in sweeps
                    for sweep in test_sweep_strings])

    def test_get_sweep_strings_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_sweep_strings()
        with pytest.raises(TypeError):
            run_batch.get_sweep_strings('I:0.0,0.2,0.4', 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.get_sweep_strings(3.142)
        with pytest.raises(TypeError):
            run_batch.get_sweep_strings(['not', 'a', 'sweep', 'definition'])
        with pytest.raises(ValueError):
            run_batch.get_sweep_strings('not a sweep definition')

    # Test get_sweep_combinations method
    def test_get_sweep_combinations_no_output(self, capsys):
        test_sweep_parameter = 'I'
        test_sweep_values = [0.0, 0.2, 0.4, 0.6]
        test_sweep = [test_sweep_parameter + ':'
                      + ','.join([str(v) for v in test_sweep_values])]
        run_batch.get_sweep_combinations(test_sweep)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_sweep_combinations_single_sweep(self):
        test_sweep_parameter = 'I'
        test_sweep_values = [0.0, 0.2, 0.4, 0.6]
        test_sweep = [test_sweep_parameter + ':'
                      + ','.join([str(v) for v in test_sweep_values])]
        combinations = run_batch.get_sweep_combinations(test_sweep)
        assert isinstance(combinations, list)
        assert len(combinations) == len(test_sweep_values)
        assert all([isinstance(sweep, str) for sweep in combinations])
        assert all([sweep in combinations
                    for sweep in [test_sweep_parameter + ':' + str(v)
                                  for v in test_sweep_values]])

    def test_get_sweep_combinations_double_sweep(self):
        test_sweep_parameters = ['I', 'E']
        test_sweep_values = [[0.0, 0.2, 0.4, 0.6], [0.5, 1.0, 1.5]]
        test_sweep = [test_sweep_parameters[i] + ':'
                      + ','.join([str(v) for v in test_sweep_values[i]])
                                  for i in range(len(test_sweep_parameters))]
        combinations = run_batch.get_sweep_combinations(test_sweep)
        assert isinstance(combinations, list)
        assert len(combinations) == (len(test_sweep_values[0])
                                     * len(test_sweep_values[1]))
        assert all([isinstance(sweep, str) for sweep in combinations])
        assert all([[sweep in combinations
                     for sweep in [test_sweep_parameters[i] + ':' + str(v)
                                   for v in test_sweep_values[i]]]
                    for i in range(len(test_sweep_parameters))])

    def test_get_sweep_combinations_triple_sweep(self):
        test_sweep_parameters = ['I', 'E', 'z']
        test_sweep_values = [[0.0, 0.2, 0.4, 0.6], [0.5, 1.0, 1.5], [0,1]]
        test_sweep = [test_sweep_parameters[i] + ':'
                      + ','.join([str(v) for v in test_sweep_values[i]])
                                  for i in range(len(test_sweep_parameters))]
        combinations = run_batch.get_sweep_combinations(test_sweep)
        assert isinstance(combinations, list)
        assert len(combinations) == (len(test_sweep_values[0])
                                     * len(test_sweep_values[1])
                                     * len(test_sweep_values[2]))
        assert all([isinstance(sweep, str) for sweep in combinations])
        assert all([[sweep in combinations
                     for sweep in [test_sweep_parameters[i] + ':' + str(v)
                                   for v in test_sweep_values[i]]]
                    for i in range(len(test_sweep_parameters))])

    def test_get_sweep_combinations_single_multiple(self):
        test_sweeps = ['(a,b):(1,10),(2,20),(3,30),(4,40)']
        test_sweep_strings = ['a:1,b:10', 'a:2,b:20', 'a:3,b:30', 'a:4,b:40']
        combinations = run_batch.get_sweep_combinations(test_sweeps)
        assert isinstance(combinations, list)
        assert len(combinations) == len(test_sweep_strings)
        assert all([isinstance(sweep, str) for sweep in combinations])
        assert all([sweep in combinations
                    for sweep in test_sweep_strings])

    def test_get_sweep_combinations_double_multiple(self):
        test_sweeps = ['(a,b):(1,10),(2,20)', 'c:100,200']
        test_sweep_combinations = ['a:1,b:10,c:100', 'a:2,b:20,c:100',
                                   'a:1,b:10,c:200', 'a:2,b:20,c:200',]
        combinations = run_batch.get_sweep_combinations(test_sweeps)
        assert isinstance(combinations, list)
        assert len(combinations) == len(test_sweep_combinations)
        assert all([isinstance(sweep, str) for sweep in combinations])
        assert all([sweep in combinations
                    for sweep in test_sweep_combinations])

    def test_get_sweep_combinations_double_multiple_no_brackets(self):
        test_sweeps = ['a,b:(1,10),(2,20)', 'c:100,200']
        test_sweep_combinations = ['a:1,b:10,c:100', 'a:2,b:20,c:100',
                                   'a:1,b:10,c:200', 'a:2,b:20,c:200',]
        combinations = run_batch.get_sweep_combinations(test_sweeps)
        assert isinstance(combinations, list)
        assert len(combinations) == len(test_sweep_combinations)
        assert all([isinstance(sweep, str) for sweep in combinations])
        assert all([sweep in combinations
                    for sweep in test_sweep_combinations])

    def test_sweep_combinations_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_sweep_combinations()
        with pytest.raises(TypeError):
            run_batch.get_sweep_combinations(['I:0.0,0.2'], 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.get_sweep_combinations(3.142)
        with pytest.raises(ValueError):
            run_batch.get_sweep_combinations('not a sweep list')
        with pytest.raises(ValueError):
            run_batch.get_sweep_combinations(['not', 'a', 'sweep', 'list'])


    # Run settings and parameters methods
    # Test get_settings method
    def test_get_settings_no_output(self, capsys):
        run_batch.get_settings('')
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_settings_results(self):
        test_settings = run_batch.get_settings('')
        assert isinstance(test_settings, dict)
        assert 'current_folder' in test_settings
        assert 'archive_root' in test_settings
        assert 'reproducible' in test_settings
        assert 'reproduce' in test_settings
        assert 'logfile' in test_settings
        assert 'python' in test_settings

    def test_get_settings_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_settings()

    def test_get_settings_current_folder_is_absolute(self):
        test_settings = run_batch.get_settings('')
        assert test_settings['current_folder'].is_absolute()

    def test_get_settings_archive_folder_is_absolute(self):
        test_settings = run_batch.get_settings('')
        assert test_settings['archive_root'].is_absolute()

    def test_get_settings_current_folder_exists(self):
        test_settings = run_batch.get_settings('')
        assert test_settings['current_folder'].is_dir()

    def test_get_settings_archive_folder_exists(self):
        test_settings = run_batch.get_settings('')
        assert test_settings['archive_root'].is_dir()

    # Test get_parameters method
    def test_get_parameters_no_output(self, capsys, cloned_repo, tmp_archive):
        run_batch.get_parameters(
            self.get_settings(cloned_repo, tmp_archive), self.arguments)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_parameters_return_type(self, cloned_repo, tmp_archive):
        test_parameters = run_batch.get_parameters(
            self.get_settings(cloned_repo, tmp_archive), self.arguments)
        assert isinstance(test_parameters, dict)

    def test_get_parameters_return_command(self, cloned_repo, tmp_archive):
        test_parameters = run_batch.get_parameters(
            self.get_settings(cloned_repo, tmp_archive), self.arguments)
        assert test_parameters['<command>'] == self.arguments['<command>']

    def test_get_parameters_archive(self, cloned_repo, tmp_archive):
        test_arguments = self.arguments.copy()
        test_arguments['--archive'] = True
        test_parameters = run_batch.get_parameters(
            self.get_settings(cloned_repo, tmp_archive), test_arguments)
        assert '--archive' in test_parameters
        assert test_parameters['--archive'] == True
        assert 'archive' in test_parameters
        assert isinstance(test_parameters['archive'], pathlib.Path)
        assert test_parameters['archive'].is_absolute()

    def test_get_parameters_no_archive(self, cloned_repo, tmp_archive):
        test_arguments = self.arguments.copy()
        test_arguments['--archive'] = False
        test_parameters = run_batch.get_parameters(
            self.get_settings(cloned_repo, tmp_archive), test_arguments)
        assert '--archive' in test_parameters
        assert test_parameters['--archive'] == False
        assert 'archive' in test_parameters
        assert test_parameters['archive'] == None

    def test_get_parameters_archive_folder_contains_current_date(
            self, cloned_repo, tmp_archive):
        test_arguments = self.arguments.copy()
        test_arguments['--archive'] = True
        test_parameters = run_batch.get_parameters(
            self.get_settings(cloned_repo, tmp_archive), test_arguments)
        assert (datetime.today().strftime('%Y-%m-%d')
                in str(test_parameters['archive']))

    def test_get_parameters_archive_folder_parent_exists(
            self, cloned_repo, tmp_archive):
        test_arguments = self.arguments.copy()
        test_arguments['--archive'] = True
        test_parameters = run_batch.get_parameters(
            self.get_settings(cloned_repo, tmp_archive), test_arguments)
        assert test_parameters['archive'].parent.is_dir()

    def test_get_parameters_runlog(self, cloned_repo, tmp_archive):
        test_arguments = self.arguments.copy()
        test_arguments['--runlog'] = True
        test_parameters = run_batch.get_parameters(
            self.get_settings(cloned_repo, tmp_archive), test_arguments)
        assert '--runlog' in test_parameters
        assert test_parameters['--runlog'] == True

    def test_get_parameters_no_runlog(self, cloned_repo, tmp_archive):
        test_arguments = self.arguments.copy()
        test_arguments['--runlog'] = False
        test_parameters = run_batch.get_parameters(
            self.get_settings(cloned_repo, tmp_archive), test_arguments)
        assert '--runlog' in test_parameters
        assert test_parameters['--runlog'] == False

    def test_get_parameters_git(self, cloned_repo, tmp_archive):
        test_arguments = self.arguments.copy()
        test_arguments['--git'] = True
        test_parameters = run_batch.get_parameters(
            self.get_settings(cloned_repo, tmp_archive), test_arguments)
        assert '--git' in test_parameters
        assert test_parameters['--git'] == True

    def test_get_parameters_no_git(self, cloned_repo, tmp_archive):
        test_arguments = self.arguments.copy()
        test_arguments['--git'] = False
        test_parameters = run_batch.get_parameters(
            self.get_settings(cloned_repo, tmp_archive), test_arguments)
        assert '--git' in test_parameters
        assert test_parameters['--git'] == False

    def test_get_parameters_invalid_git(self, cloned_repo, tmp_archive):
        test_arguments = self.arguments.copy()
        test_arguments['--git'] = True
        test_settings = self.get_settings(cloned_repo, tmp_archive).copy()
        test_settings['current_folder'] = pathlib.Path('/')
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            run_batch.get_parameters(test_settings, test_arguments)

    def test_get_parameters_git_subsettings(self, cloned_repo, tmp_archive):
        test_arguments = self.arguments.copy()
        test_arguments['--git'] = True
        test_parameters = run_batch.get_parameters(
            self.get_settings(cloned_repo, tmp_archive), test_arguments)
        assert '--input_branch' in test_parameters
        assert (   isinstance(test_parameters['--input_branch'], str)
                or isinstance(test_parameters['--input_branch'], list))
        assert '--results_branch' in test_parameters
        assert isinstance(test_parameters['--results_branch'], str)

    # Test get_title method
    def test_get_title_no_output(self, capsys):
        run_batch.get_title(self.single_run)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_title_existing_title(self):
        test_run = self.single_run.copy()
        test_text = 'Test run'
        test_run['title'] = test_text
        test_title = run_batch.get_title(test_run)
        assert isinstance(test_title, str)
        assert test_title == test_text

    def test_get_title_no_existing_title(self):
        test_run = self.single_run.copy()
        test_run['title'] = None
        test_title = run_batch.get_title(test_run)
        assert isinstance(test_title, str)

    def test_get_title_contains_date(self):
        test_run = self.single_run.copy()
        test_run['title'] = None
        test_title = run_batch.get_title(test_run)
        assert isinstance(test_title, str)
        assert datetime.today().strftime('%Y-%m-%d') in test_title

    def test_get_title_contains_command(self):
        test_run = self.single_run.copy()
        test_run['title'] = None
        test_title = run_batch.get_title(test_run)
        assert isinstance(test_title, str)
        assert self.single_run['<command>'].split()[0] in test_title

    def test_get_title_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_title()
        with pytest.raises(TypeError):
            run_batch.get_title(self.single_run, 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.get_title('not a dict')


    # Run methods
    # Test reproducible_run method
    @pytest.mark.slow
    def test_reproducible_run_no_options(
            self, capfd, cloned_repo, tmp_archive, protect_log):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        result = run_batch.reproducible_run(test_settings, self.single_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()

    def test_reproducible_run_invalid_input(self, cloned_repo, tmp_archive):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        with pytest.raises(TypeError):
            run_batch.reproducible_run(test_settings)
        with pytest.raises(TypeError):
            run_batch.reproducible_run(
                test_settings, self.single_run, 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.reproducible_run('not settings', self.single_run)
        with pytest.raises(TypeError):
            run_batch.reproducible_run(test_settings, 'not a run dict')
        with pytest.raises(TypeError):
            run_batch.reproducible_run(['not', 'a', 'dict'], self.single_run)
        with pytest.raises(TypeError):
            run_batch.reproducible_run(test_settings, ['not', 'a', 'dict'])

    @pytest.mark.slow
    def test_reproducible_run_with_runlog(
            self, capfd, cloned_repo, tmp_archive, protect_log):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        test_run = self.single_run.copy()
        test_run['--runlog'] = True
        result = run_batch.reproducible_run(test_settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()
        assert len(set(self.get_run_folder(cloned_repo).glob('reproduce-*.log'))) == 1

    @pytest.mark.slow
    def test_reproducible_run_template_check(
            self, capfd, cloned_repo, tmp_archive, tmp_file, protect_log):
        test_run = self.single_run.copy()
        test_run['--template'] = tmp_file
        result = run_batch.reproducible_run(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        captured = capfd.readouterr()
        assert result.returncode != 0
        assert not self.test_message in captured.out
        assert ('ERROR: Input file' in captured.err
                and 'not in git' in captured.err)

    @pytest.mark.slow
    def test_reproducible_run_template_ok(
            self, cloned_repo, tmp_archive, capfd, protect_log):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        test_run = self.single_run.copy()
        test_run['--template'] = 'README.md'
        result = run_batch.reproducible_run(test_settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()

    @pytest.mark.slow
    def test_reproducible_run_show_rendered(
            self, capfd, cloned_repo, tmp_archive, tmp_file, protect_log):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        test_run = self.single_run.copy()
        test_run['--show'] = True
        test_run['--template'] = 'README.md'
        result = run_batch.reproducible_run(test_settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.get_run_folder(cloned_repo).joinpath(test_settings['logfile']).is_file()
        assert '------rendered template for README.md------' in captured.err

    @pytest.mark.slow
    def test_reproducible_run_save_rendered(
            self, capfd, cloned_repo, tmp_archive, tmp_file, protect_log):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        test_run = self.single_run.copy()
        test_run['--save'] = True
        test_run['--template'] = 'README.md'
        result = run_batch.reproducible_run(test_settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()
        assert self.get_run_folder(cloned_repo).joinpath(
            'README.md.rendered').is_file()
        self.get_run_folder(cloned_repo).joinpath('README.md.rendered').unlink()

    @pytest.mark.slow
    def test_reproducible_run_src_check(
            self, capfd, cloned_repo, cloned_src, tmp_archive, tmp_srcfile,
            protect_log):
        test_run = self.single_run.copy()
        test_run['--src'] = str(self.get_src_location(cloned_src))
        result = run_batch.reproducible_run(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        captured = capfd.readouterr()
        assert result.returncode != 0
        assert not self.test_message in captured.out
        assert ('ERROR: Source directory is not clean' in captured.err
                and str(self.get_src_location(cloned_src)) in captured.err)

    @pytest.mark.slow
    def test_reproducible_run_src_ok(
            self, capfd, cloned_repo, cloned_src, tmp_archive, protect_log):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        test_run = self.single_run.copy()
        test_run['--src'] = str(self.get_src_location(cloned_src))
        result = run_batch.reproducible_run(test_settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()
        assert 'Source code directory:' in captured.err
        assert 'Source code commit:' in captured.err

    # Not used as it affects the production file system
    # @pytest.mark.slow
    # def test_reproducible_run_build_src(
    #         self, capfd, cloned_repo, cloned_src, tmp_archive, rebuild_src,
    #         protect_log):
    #     test_settings = self.get_settings(cloned_repo, tmp_archive)
    #     test_run = self.single_run.copy()
    #     test_run['--src'] = str(self.get_src_location(cloned_src))
    #     test_run['--build'] = True
    #     result = run_batch.reproducible_run(test_settings, test_run)
    #     captured = capfd.readouterr()
    #     assert result.returncode == 0
    #     assert self.test_message in captured.out
    #     assert self.reproduce_message in captured.err
    #     assert self.get_run_folder(cloned_repo).joinpath(
    #         test_settings['logfile']).is_file()
    #     assert 'Source code directory:' in captured.err
    #     assert 'Source code commit:' in captured.err
    #     assert rebuild_src.is_file()

    @pytest.mark.slow
    def test_reproducible_run_parameters(
            self, capfd, cloned_repo, tmp_archive, tmp_template, protect_log):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        test_run = self.single_run.copy()
        test_run['--template'] = tmp_template['filename']
        test_run['-p'] = tmp_template['parameter_string']
        result = run_batch.reproducible_run(test_settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()

    @pytest.mark.slow
    def test_reproducible_run_list_parameters(
            self, capfd, cloned_repo, tmp_archive, tmp_template, protect_log):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        test_run = self.single_run.copy()
        test_run['--template'] = tmp_template['filename']
        test_run['-p'] = tmp_template['parameter_string']
        test_run['--list-parameters'] = True
        result = run_batch.reproducible_run(test_settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()
        assert 'INFO: Parameters' in captured.err
        for p in tmp_template['parameters']:
            assert f'{p} -> ' in captured.err

    @pytest.mark.slow
    def test_reproducible_run_list_parameters_fail(
            self, capfd, cloned_repo, tmp_archive, tmp_template, protect_log):
        test_run = self.single_run.copy()
        test_run['--template'] = tmp_template['filename']
        test_run['--list-parameters'] = True
        result = run_batch.reproducible_run(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        captured = capfd.readouterr()
        assert result.returncode != 0
        assert not self.test_message in captured.out
        assert 'INFO: Parameters' in captured.err
        for p in tmp_template['parameters']:
            assert f'{p} -> None' in captured.err
            assert f'ERROR: Parameter "{p}" did not get a value' in captured.err

    @pytest.mark.slow
    def test_reproducible_run_oldhash(
            self, capfd, cloned_repo, tmp_archive, tmp_template, protect_log):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        first_run = self.single_run.copy()
        first_run['--template'] = tmp_template['filename']
        first_run['-p'] = tmp_template['parameter_string']
        first_result = run_batch.reproducible_run(test_settings, first_run)
        first_captured = capfd.readouterr()
        assert first_result.returncode == 0
        assert self.test_message in first_captured.out
        assert self.reproduce_message in first_captured.err
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()
        assert 'Current run hash:' in first_captured.err
        hash_loc = first_captured.err.find('Current run hash:') + 18
        oldhash = first_captured.err[hash_loc:hash_loc+40]
        assert len(oldhash) == 40
        second_run = self.single_run.copy()
        second_run['--template'] = tmp_template['filename']
        second_run['--hash'] = oldhash
        second_run['--list-parameters'] = True
        second_result = run_batch.reproducible_run(test_settings, second_run)
        second_captured = capfd.readouterr()
        assert second_result.returncode == 0
        assert self.test_message in second_captured.out
        assert self.reproduce_message in second_captured.err
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()
        assert 'INFO: Parameters' in second_captured.err
        for p in tmp_template['parameters']:
            assert f'{p} -> ' in second_captured.err


    # Test run_single method
    @pytest.mark.slow
    def test_run_single_no_options(
            self, capfd, cloned_repo, tmp_archive, protect_log):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        run_batch.run_single(test_settings, self.single_run)
        captured = capfd.readouterr()
        assert self.single_run['title'] in captured.out
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()

    @pytest.mark.slow
    @pytest.mark.gitchanges
    def test_run_single_with_git(
            self, capfd, cloned_repo, tmp_archive, protect_git):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        old_commit = cloned_repo.heads[self.results_branch].commit
        test_run = self.single_run.copy()
        test_run.update({'--git': True,
                         '--input_branch': self.input_branch,
                         '--results_branch': self.results_branch,
                         'commit_files': ['reproduce-*.log',
                                          test_settings['logfile']],
                         'commit_message': 'Test commit'})
        run_batch.run_single(test_settings, test_run)
        captured = capfd.readouterr()
        assert self.single_run['title'] in captured.out
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert cloned_repo.heads[self.results_branch].commit != old_commit
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()

    @pytest.mark.slow
    def test_run_single_with_post_process(
            self, capfd, cloned_repo, tmp_archive, protect_log):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        test_message = 'Post-processing output'
        test_command = f'echo {test_message}'
        test_run = self.single_run.copy()
        test_run['--post'] = test_command
        run_batch.run_single(test_settings, test_run)
        captured = capfd.readouterr()
        assert test_run['title'] in captured.out
        assert self.reproduce_message in captured.err
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()
        assert test_message in captured.out

    @pytest.mark.slow
    def test_run_single_with_archive(
            self, capfd, cloned_repo, tmp_archive, tmp_file, tmp_path,
            protect_log):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': ['*.md'],
                         'archive_move': [tmp_file]})
        run_batch.run_single(test_settings, test_run)
        captured = capfd.readouterr()
        assert test_run['title'] in captured.out
        assert self.reproduce_message in captured.err
        if self.get_run_folder(cloned_repo).joinpath('README.md').is_file():
            assert tmp_path.joinpath('README.md').is_file()
        assert tmp_path.joinpath(tmp_file).is_file()
        assert not self.get_run_folder(cloned_repo).joinpath(tmp_file).is_file()
        with open(tmp_path.joinpath(tmp_file), 'r') as f:
            assert f.readline() == self.test_message
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()
        assert tmp_path.joinpath(test_settings['archive_log']).is_file()

    @pytest.mark.slow
    def test_run_single_with_logging(
            self, capfd, cloned_repo, tmp_archive, protect_log):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        test_run = self.single_run.copy()
        test_run['--runlog'] = True
        run_batch.run_single(test_settings, test_run)
        captured = capfd.readouterr()
        assert test_run['title'] in captured.out
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()
        assert len(set(self.get_run_folder(cloned_repo).glob('reproduce-*.log'))) == 1

    @pytest.mark.slow
    def test_run_single_with_templates(
            self, capfd, cloned_repo, tmp_archive, protect_log):
        test_settings = self.get_settings(cloned_repo, tmp_archive)
        valid_template_list = ['README.md']
        invalid_template_list = ['not_a_file1.in', 'not_a_file2.in']
        template_list = ','.join(valid_template_list + invalid_template_list)
        test_run = self.single_run.copy()
        test_run['--template'] = template_list
        run_batch.run_single(test_settings, test_run)
        captured = capfd.readouterr()
        assert test_run['title'] in captured.out
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.get_run_folder(cloned_repo).joinpath(
            test_settings['logfile']).is_file()
        assert 'Skipping missing templates' in captured.err
        for template in invalid_template_list:
            assert template in captured.err

    @pytest.mark.slow
    def test_run_single_with_cleanup(
            self, capfd, cloned_repo, tmp_archive, tmp_file_factory, protect_log):
        test_run = self.single_run.copy()
        test_run['--clean'] = True
        temp_files = ['tmp.png', 'tmp.eps', 'tmp.ps', 'tmp.jpg',
                      'reproduce-temp.log']
        for filename in temp_files:
            tmp_file_factory(filename)
        run_batch.run_single(
            self.get_settings(cloned_repo, tmp_archive), test_run)
        captured = capfd.readouterr()
        assert self.single_run['title'] in captured.out
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        for filename in temp_files:
            assert not self.get_run_folder(cloned_repo).joinpath(filename).is_file()
