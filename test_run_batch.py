# Tests run_batch.py

import run_batch
import pytest
import os
import pathlib
import shutil
from datetime import datetime
import git

class TestRunBatch:

    # Setup before testing
    def setup_class(self):
        self.run_folder = pathlib.Path.home().joinpath('Simulations/Current')
        self.archive_location = pathlib.Path.home().joinpath('Simulations')
        self.reproducible = pathlib.Path.home().joinpath('Code/Reproducible')
        self.reproduce = self.reproducible.joinpath('reproduce')
        self.pyenv = pathlib.Path.home().joinpath('.pyenv')
        self.reproduce_python = self.pyenv.joinpath('versions/reproducible/bin/python3')
        self.src_location = pathlib.Path.home().joinpath('Code/Impact/src')
        self.exe = pathlib.Path.home().joinpath('bin/ImpactTexe')
        self.repo = git.Repo(self.run_folder)
        self.src_repo = git.Repo(self.src_location.parent)
        self.test_message = 'Hello world'
        self.reproduce_message = 'Current run hash'
        self.input_branch = 'input/emittance'
        self.results_branch = 'results/emittance'
        self.settings = {
            'current_folder': self.run_folder,
            'archive_root': self.archive_location,
            'python': self.reproduce_python,
            'reproduce': self.reproduce,
            'logfile': 'simulations.log',
            'archive_log': 'simulation.log'}
        self.arguments = {
            '<command>': f'echo {self.test_message}',
            '--help': False,
            '--git': False,
            '--archive': False,
            '--class': None,
            '--input_branch': None,
            '--results_branch': None,
            '--param': None,
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


    # Fixtures
    @pytest.fixture
    def tmp_file(self):
        filename = 'test_file.tmp'
        tempfile = self.run_folder.joinpath(filename)
        with open(tempfile, 'w') as f:
            f.write(self.test_message)
        yield filename
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_file_factory(self):
        created_files = []
        def _new_temp_file(filename):
            tempfile = self.run_folder.joinpath(filename)
            with open(tempfile, 'w') as f:
                f.write(self.test_message)
            created_files.append(tempfile)
            return tempfile
        yield _new_temp_file
        for file in created_files:
            if file.is_file():
                file.unlink()

    @pytest.fixture
    def protect_log(self, tmp_path):
        logfile = self.run_folder.joinpath(self.settings['logfile'])
        assert len(set(self.run_folder.glob('reproduce-*.log'))) == 0
        if logfile.is_file():
            temp_logfile = shutil.copy2(str(logfile), str(tmp_path))
        else:
            temp_logfile = None
        yield temp_logfile
        if temp_logfile:
            shutil.copy2(temp_logfile, str(self.run_folder))
        else:
            if logfile.is_file():
                logfile.unlink()
        for file in set(self.run_folder.glob('reproduce-*.log')):
            file.unlink()

    @pytest.fixture
    def protect_git(self, protect_log):
        initial_branch = self.repo.active_branch
        initial_commit = self.repo.commit()
        results_branch = self.repo.heads[self.results_branch]
        results_commit = self.repo.heads[self.results_branch].commit
        yield initial_commit
        initial_branch.commit = initial_commit
        results_branch.commit = results_commit
        initial_branch.checkout(force=True)

    @pytest.fixture
    def tmp_srcfile(self):
        filename = 'test_file.tmp'
        tempfile = self.src_location.joinpath(filename)
        with open(tempfile, 'w') as f:
            f.write(self.test_message)
        yield filename
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def rebuild_src(self):
        if self.exe.is_file():
            self.exe.unlink()
        yield self.exe

    @pytest.fixture
    def tmp_template(self, protect_git):
        tmp_template = {
            'filename': 'template.tmp',
            'parameters': ['a', 'b', 'c'],
            'parameter_string': 'a:1,b:2,c:3',
            'text': 'Parameters include {{a}}, {{b}}, and {{c}}'}
        tempfile = self.run_folder.joinpath(tmp_template['filename'])
        with open(tempfile, 'w') as f:
            f.write(tmp_template['text'])
        initial_commit = self.repo.commit()
        self.repo.index.add(tmp_template['filename'])
        self.repo.index.commit('Test commit')
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

    def test_get_folder_archive_folder(self):
        test_folder = run_batch.get_folder(self.archive_location)
        assert test_folder == pathlib.Path.home().joinpath('Simulations')

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

    # Test get_archive_folder method
    def test_get_archive_folder_no_output(self, capsys):
        run_batch.get_archive_folder(self.archive_location)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_archive_folder_return_type(self):
        test_folder = run_batch.get_archive_folder(self.archive_location)
        assert isinstance(test_folder, pathlib.PurePath)

    def test_get_archive_folder_is_absolute(self):
        test_folder = run_batch.get_archive_folder(self.archive_location)
        assert test_folder.is_absolute()

    def test_get_archive_folder_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_archive_folder()
        with pytest.raises(TypeError):
            run_batch.get_archive_folder(self.archive_location,
                                         'extra parameter')
        with pytest.raises(AttributeError):
            run_batch.get_archive_folder('not a path')
        with pytest.raises(AttributeError):
            run_batch.get_archive_folder('/not/a/path')

    def test_get_archive_folder_contains_current_date(self):
        test_folder = run_batch.get_archive_folder(self.archive_location)
        assert (datetime.today().strftime('%Y-%m-%d') in str(test_folder))

    def test_get_archive_folder_parent_exists(self):
        test_folder = run_batch.get_archive_folder(self.archive_location)
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


    # Git methods
    # Test get_git_repo method
    def test_get_git_repo_no_output(self, capsys):
        run_batch.get_git_repo(self.settings['current_folder'])
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_git_repo_return_type(self):
        test_repo = run_batch.get_git_repo(self.settings['current_folder'])
        assert isinstance(test_repo, git.Repo)

    def test_get_git_repo_input_type_path(self):
        test_repo = run_batch.get_git_repo(self.settings['current_folder']
                                               .absolute())
        assert isinstance(test_repo, git.Repo)

    def test_get_git_repo_input_type_str(self):
        test_repo = run_batch.get_git_repo(str(self.settings['current_folder']))
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
    def test_git_checkout_no_output(self, capsys, protect_git):
        run_batch.git_checkout(self.repo, 'master')
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.gitchanges
    def test_git_checkout_result(self, protect_git):
        run_batch.git_checkout(self.repo, 'master')
        assert self.repo.head.reference == self.repo.heads['master']

    @pytest.mark.gitchanges
    def test_git_checkout_invalid_input(self, protect_git):
        with pytest.raises(TypeError):
            run_batch.git_checkout(self.repo)
        with pytest.raises(TypeError):
            run_batch.git_checkout(self.repo, 'master', 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.git_checkout('not_a_repo', 'master')
        with pytest.raises(TypeError):
            run_batch.git_checkout(self.repo, self.repo)
        with pytest.raises(TypeError):
            run_batch.git_checkout(self.repo, 3.142)
        with pytest.raises(IndexError):
            run_batch.git_checkout(self.repo, 'not_a_branch')

    # Test git_switch method
    @pytest.mark.gitchanges
    def test_git_switch_no_output(self, capsys, protect_git):
        run_batch.git_switch(self.repo, 'master')
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.gitchanges
    def test_git_switch_result(self, protect_git):
        run_batch.git_switch(self.repo, 'master')
        assert self.repo.head.reference == self.repo.heads['master']

    @pytest.mark.gitchanges
    def test_git_switch_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.git_switch(self.repo)
        with pytest.raises(TypeError):
            run_batch.git_switch(self.repo, 'master', 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.git_switch('not_a_repo', 'master')
        with pytest.raises(TypeError):
            run_batch.git_switch(self.repo, self.repo)
        with pytest.raises(TypeError):
            run_batch.git_switch(self.repo, 3.142)
        with pytest.raises(IndexError):
            run_batch.git_switch(self.repo, 'not_a_branch')

    # Test git_get_file method
    @pytest.mark.gitchanges
    def test_git_get_file_no_output(self, capsys, protect_git):
        run_batch.git_get_file(self.repo, 'master', 'README.md')
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.gitchanges
    def test_git_get_file_result(self, protect_git):
        os.remove(self.run_folder.joinpath('README.md'))
        run_batch.git_get_file(self.repo, 'master', 'README.md')
        assert self.run_folder.joinpath('README.md').is_file()

    def test_git_get_file_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.git_get_file(self.repo)
        with pytest.raises(TypeError):
            run_batch.git_get_file(self.repo, 'master')
        with pytest.raises(TypeError):
            run_batch.git_get_file(self.repo, 'master', 'README.md',
                                   'extra parameter')
        with pytest.raises(TypeError):
            run_batch.git_get_file('not_a_repo', 'master', 'README.md')
        with pytest.raises(git.exc.GitCommandError):
            run_batch.git_get_file(self.repo, self.repo, 'README.md')
        with pytest.raises(git.exc.GitCommandError):
            run_batch.git_get_file(self.repo, 'master', self.repo)
        with pytest.raises(git.exc.GitCommandError):
            run_batch.git_get_file(self.repo, 3.142, 'README.md')
        with pytest.raises(git.exc.GitCommandError):
            run_batch.git_get_file(self.repo, 'not_a_branch', 'README.md')
        with pytest.raises(git.exc.GitCommandError):
            run_batch.git_get_file(self.repo, 'master', 'not_a_file.txt')

    # Test git_commit method
    @pytest.mark.gitchanges
    def test_git_commit_no_output(self, capsys, protect_git, tmp_file):
        run_batch.git_commit(self.repo, tmp_file, 'Test commit')
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.gitchanges
    def test_git_commit_result(self, protect_git, tmp_file):
        assert len(self.repo.untracked_files) == 1
        test_message = 'Test commit'
        run_batch.git_commit(self.repo, tmp_file, test_message)
        assert not self.repo.is_dirty()
        assert len(self.repo.untracked_files) == 0
        assert self.repo.head.commit.message == test_message

    @pytest.mark.gitchanges
    def test_git_commit_multiple(self, protect_git, tmp_file_factory):
        test_files = ['test1.txt', 'test2.txt']
        test_message = 'Test commit'
        for filename in test_files:
            tmp_file_factory(filename)
        assert len(self.repo.untracked_files) == len(test_files)
        run_batch.git_commit(self.repo, test_files, test_message)
        for filename in test_files:
            assert self.run_folder.joinpath(filename).is_file()
        assert not self.repo.is_dirty()
        assert len(self.repo.untracked_files) == 0
        assert self.repo.head.commit.message == test_message

    @pytest.mark.gitchanges
    def test_git_commit_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.git_commit(self.repo)
        with pytest.raises(TypeError):
            run_batch.git_commit(self.repo, 'README.md')
        with pytest.raises(TypeError):
            run_batch.git_commit(self.repo, 'README.md', 'Test commit',
                                 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.git_commit('not_a_repo', 'README.md', 'Test commit')
        with pytest.raises(TypeError):
            run_batch.git_commit(self.repo, self.repo, 'Test commit')
        with pytest.raises(TypeError):
            run_batch.git_commit(self.repo,
                                 ['README.md', self.repo],
                                 'Test commit')
        with pytest.raises(AttributeError):
            run_batch.git_commit(self.repo, 'README.md', self.repo)
        with pytest.raises(TypeError):
            run_batch.git_commit(self.repo, 3.142, 'Test commit')
        with pytest.raises(FileNotFoundError):
            run_batch.git_commit(self.repo, 'not_a_file.txt', 'Test commit')

    # Test get_input_branch method
    def test_get_input_branch_no_output(self, capsys):
        run_batch.get_input_branch(self.repo, self.arguments['--input_branch'])
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_git_input_branch_return_type(self):
        test_branch = run_batch.get_input_branch(
            self.repo, self.arguments['--input_branch'])
        assert (   isinstance(test_branch, str)
                or isinstance(test_branch, list))

    def test_get_git_input_branch_exists(self):
        test_branch = run_batch.get_input_branch(
            self.repo, self.arguments['--input_branch'])
        if isinstance(test_branch, str):
            assert test_branch in [head.name for head in self.repo.heads]
        elif isinstance(test_branch, list):
            for this_branch in test_branch:
                assert this_branch in [head.name for head in self.repo.heads]

    def test_get_git_input_branch_specified(self):
        test_branch = run_batch.get_input_branch(self.repo, 'master')
        assert isinstance(test_branch, str)
        assert test_branch == 'master'

    def test_get_git_input_branch_multiple(self):
        test_branch = run_batch.get_input_branch(self.repo,
                                                 ['master', 'master'])
        assert isinstance(test_branch, list)
        assert test_branch == ['master', 'master']

    def test_get_git_input_branch_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_input_branch(self.repo)
        with pytest.raises(TypeError):
            run_batch.get_input_branch(self.repo,
                                       self.arguments['--input_branch'],
                                       'extra parameter')
        with pytest.raises(AttributeError):
            run_batch.get_input_branch('not a repo',
                                       self.arguments['--input_branch'])
        with pytest.raises(ValueError):
            run_batch.get_input_branch(self.repo, 'not a branch')
        with pytest.raises(ValueError):
            run_batch.get_input_branch(self.repo, ['master', 'not a branch'])

    # Test get_results_branch method
    def test_get_results_branch_no_output(self, capsys):
        run_batch.get_results_branch(
            self.repo, self.arguments['--input_branch'])
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_git_results_branch_return_type(self):
        test_branch = run_batch.get_results_branch(
            self.repo, self.arguments['--input_branch'])
        assert isinstance(test_branch, str)

    def test_get_git_results_branch_exits(self):
        test_branch = run_batch.get_results_branch(
            self.repo, self.arguments['--input_branch'])
        assert test_branch in [head.name for head in self.repo.heads]

    def test_get_git_results_branch_specified(self):
        test_branch = run_batch.get_results_branch(self.repo, 'master')
        assert isinstance(test_branch, str)
        assert test_branch == 'master'

    def test_get_git_results_branch_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_results_branch(self.repo)
        with pytest.raises(TypeError):
            run_batch.get_results_branch(self.repo,
                                         self.arguments['--results_branch'],
                                         'extra parameter')
        with pytest.raises(AttributeError):
            run_batch.get_results_branch('not a dict',
                                         self.arguments['--results_branch'])
        with pytest.raises(ValueError):
            run_batch.get_results_branch(self.repo, [3.142, 9999])
        with pytest.raises(ValueError):
            run_batch.get_results_branch(self.repo, 'not a branch')

    # Test get_commit_files method
    def test_get_commit_files_no_output(self, capsys):
        run_batch.get_commit_files(self.settings, self.single_run)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_commit_files_contains_logs(self):
        filelist = run_batch.get_commit_files(self.settings, self.single_run)
        assert self.settings['logfile'] in filelist
        assert 'reproduce-*.log' in filelist

    def test_get_commit_files_impact(self):
        test_run = self.single_run.copy()
        test_run['--class'] = 'impact'
        filelist = run_batch.get_commit_files(self.settings, self.single_run)
        assert self.settings['logfile'] in filelist
        assert 'reproduce-*.log' in filelist

    def test_get_commit_files_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_commit_files()
        with pytest.raises(TypeError):
            run_batch.get_commit_files(self.settings)
        with pytest.raises(TypeError):
            run_batch.get_commit_files(self.settings,
                                       self.single_run,
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


    # Post-processing methods
    # Test post_process method
    def test_post_process_output(self, capfd, protect_log):
        test_message = 'Post-processing output'
        test_command = f'echo {test_message}'
        result = run_batch.post_process(self.settings, test_command)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert test_message in captured.out

    def test_post_process_invalid_input(self):
        test_message = 'Post-processing output'
        test_command = f'echo {test_message}'
        with pytest.raises(TypeError):
            run_batch.post_process(self.settings)
        with pytest.raises(TypeError):
            run_batch.post_process(self.settings, test_command,
                                   'extra parameter')
        with pytest.raises(TypeError):
            run_batch.post_process('not settings', test_command)
        with pytest.raises(AttributeError):
            run_batch.post_process(self.settings, ['not', 'a', 'command'])
        with pytest.raises(TypeError):
            run_batch.post_process(['not', 'a', 'dict'], test_command)
        with pytest.raises(FileNotFoundError):
            run_batch.post_process(self.settings, 'not a command')


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
        run_batch.get_move_list(self.arguments['--class'])
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_move_list_default(self):
        move_list = run_batch.get_move_list(None)
        assert isinstance(move_list, list)
        assert 'reproduce-*.log' in move_list

    def test_get_move_list_impact(self):
        move_list = run_batch.get_move_list('impact')
        assert isinstance(move_list, list)
        assert 'fort.*' in move_list
        assert '*.dst' in move_list
        assert '*.plt' in move_list
        assert 'reproduce-*.log' in move_list

    def test_get_move_list_bdsim(self):
        move_list = run_batch.get_move_list('bdsim')
        assert isinstance(move_list, list)
        assert '*.root' in move_list
        assert '*.png' in move_list
        assert '*.eps' in move_list
        assert 'reproduce-*.log' in move_list

    def test_get_move_list_opal(self):
        move_list = run_batch.get_move_list('opal')
        assert isinstance(move_list, list)
        assert '*.h5' in move_list
        assert '*.lbal' in move_list
        assert '*.stat' in move_list
        assert '*.dat' in move_list
        assert 'data' in move_list
        assert 'reproduce-*.log' in move_list

    def test_get_move_list_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_move_list()
        with pytest.raises(TypeError):
            run_batch.get_move_list(self.arguments['--class'], 'extra parameter')
        move_list = run_batch.get_move_list('not a class')
        assert isinstance(move_list, list)

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
    def test_archive_log_no_output(self, capsys, tmp_path):
        run_batch.archive_log(self.settings, tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.slow
    def test_archive_log_result(self, tmp_path):
        run_batch.archive_log(self.settings, tmp_path)
        assert tmp_path.joinpath(self.settings['archive_log']).is_file()
        with open(tmp_path.joinpath(self.settings['archive_log']), 'r') as f:
            assert f.readline()[0:6] == 'hash: '

    @pytest.mark.slow
    def test_archive_log_custom_filename(self, tmp_path):
        test_settings = self.settings.copy()
        test_settings['archive_log'] = 'archive.log'
        run_batch.archive_log(test_settings, tmp_path)
        assert tmp_path.joinpath(test_settings['archive_log']).is_file()
        with open(tmp_path.joinpath(test_settings['archive_log']), 'r') as f:
            assert f.readline()[0:6] == 'hash: '

    @pytest.mark.slow
    def test_archive_log_invalid_input(self, tmp_path):
        with pytest.raises(TypeError):
            run_batch.archive_log()
        with pytest.raises(TypeError):
            run_batch.archive_log(self.settings)
        with pytest.raises(TypeError):
            run_batch.archive_log(self.settings, tmp_path, 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.archive_log('not a dict', tmp_path)
        with pytest.raises(AttributeError):
            run_batch.archive_log(self.settings, 'not a path')

    # Test archive_output method
    @pytest.mark.slow
    def test_archive_output_no_output(self, capsys, tmp_path):
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': [],
                         'archive_move': []})
        run_batch.archive_output(self.settings, test_run)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_archive_output_invalid_input(self, tmp_path):
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': [],
                         'archive_move': []})
        with pytest.raises(TypeError):
            run_batch.archive_output(self.settings)
        with pytest.raises(TypeError):
            run_batch.archive_output(self.settings, test_run, 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.archive_output('not a dict', test_run)
        with pytest.raises(TypeError):
            run_batch.archive_output(self.settings, 'not a dict')

    @pytest.mark.slow
    def test_archive_output_copy_single_file(self, tmp_file, tmp_path):
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': [tmp_file],
                         'archive_move': []})
        run_batch.archive_output(self.settings, test_run)
        assert tmp_path.joinpath(tmp_file).is_file()
        assert self.run_folder.joinpath(tmp_file).is_file()
        assert tmp_path.joinpath('simulation.log').is_file()

    @pytest.mark.slow
    def test_archive_output_copy_files(self, tmp_file_factory, tmp_path):
        copy_files = ['file1.tmp', 'file2.tmp', 'file3.tmp2']
        for filename in copy_files:
            tmp_file_factory(filename)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': copy_files,
                         'archive_move': []})
        run_batch.archive_output(self.settings, test_run)
        for filename in copy_files:
            assert tmp_path.joinpath(filename).is_file()
            assert self.run_folder.joinpath(filename).is_file()
            with open(tmp_path.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    @pytest.mark.slow
    def test_archive_output_copy_patterns(self, tmp_file_factory, tmp_path):
        copy_files = ['file1.tmp', 'file2.tmp', 'file3.tmp2']
        for filename in copy_files:
            tmp_file_factory(filename)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': ['*.tmp', '*.tmp2'],
                         'archive_move': []})
        run_batch.archive_output(self.settings, test_run)
        for filename in copy_files:
            assert tmp_path.joinpath(filename).is_file()
            assert self.run_folder.joinpath(filename).is_file()
            with open(tmp_path.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    @pytest.mark.slow
    def test_archive_output_move_single_file(self, tmp_file, tmp_path):
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': [],
                         'archive_move': [tmp_file]})
        run_batch.archive_output(self.settings, test_run)
        assert tmp_path.joinpath(tmp_file).is_file()
        assert not self.run_folder.joinpath(tmp_file).is_file()
        assert tmp_path.joinpath('simulation.log').is_file()

    @pytest.mark.slow
    def test_archive_output_move_files(self, tmp_file_factory, tmp_path):
        move_files = ['file1.tmp', 'file2.tmp', 'file3.tmp2']
        for filename in move_files:
            tmp_file_factory(filename)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': [],
                         'archive_move': move_files})
        run_batch.archive_output(self.settings, test_run)
        for filename in move_files:
            assert tmp_path.joinpath(filename).is_file()
            assert not self.run_folder.joinpath(filename).is_file()
            with open(tmp_path.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    @pytest.mark.slow
    def test_archive_output_move_patterns(self, tmp_file_factory, tmp_path):
        move_files = ['file1.tmp', 'file2.tmp', 'file3.tmp2']
        for filename in move_files:
            tmp_file_factory(filename)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': [],
                         'archive_move': ['*.tmp', '*.tmp2']})
        run_batch.archive_output(self.settings, test_run)
        for filename in move_files:
            assert tmp_path.joinpath(filename).is_file()
            assert not self.run_folder.joinpath(filename).is_file()
            with open(tmp_path.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    @pytest.mark.slow
    def test_archive_output_copy_and_move(self, tmp_file_factory, tmp_path):
        copy_files = ['file1.tmp', 'file2.tmp', 'file3.tmp']
        move_files = ['file4.tmp2', 'file5.tmp2', 'file6.tmp3']
        for filename in (copy_files + move_files):
            tmp_file_factory(filename)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': ['*.tmp'],
                         'archive_move': ['*.tmp2', 'file6.*']})
        run_batch.archive_output(self.settings, test_run)
        for filename in copy_files:
            assert tmp_path.joinpath(filename).is_file()
            assert self.run_folder.joinpath(filename).is_file()
            with open(tmp_path.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message
        for filename in move_files:
            assert tmp_path.joinpath(filename).is_file()
            assert not self.run_folder.joinpath(filename).is_file()
            with open(tmp_path.joinpath(filename), 'r') as f:
                assert f.readline() == self.test_message

    @pytest.mark.slow
    def test_archive_output_move_rendered_templates(self, tmp_file_factory,
                                                    tmp_path):
        test_file = 'file1.tmp'
        test_render = 'file1.tmp.rendered'
        tmp_file_factory(test_render)
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': [],
                         'archive_move': []})
        run_batch.archive_output(self.settings, test_run)
        assert tmp_path.joinpath(test_file).is_file()
        assert not tmp_path.joinpath(test_render).is_file()
        assert not self.run_folder.joinpath(test_file).is_file()
        assert not self.run_folder.joinpath(test_render).is_file()


    # Sweep methods
    # Test get_sweep_parameter method
    def test_get_sweep_parameter(self):
        test_sweep_parameter = 'I'
        test_sweep_values = [0.0, 0.2, 0.4, 0.6]
        test_sweep = (test_sweep_parameter + ':'
                      + ','.join([str(v) for v in test_sweep_values]))
        parameter = run_batch.get_sweep_parameter(test_sweep)
        assert isinstance(parameter, str)
        assert parameter == test_sweep_parameter

    def test_get_sweep_parameter_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.get_sweep_parameter()
        with pytest.raises(TypeError):
            run_batch.get_sweep_parameter('I:0.0,0.2,0.4', 'extra parameter')
        with pytest.raises(TypeError):
            run_batch.get_sweep_parameter(3.142)
        with pytest.raises(TypeError):
            run_batch.get_sweep_parameter(['not', 'a', 'sweep', 'definition'])
        with pytest.raises(ValueError):
            run_batch.get_sweep_parameter('not a sweep definition')

    # Test get_sweep_values method
    def test_get_sweep_values(self):
        test_sweep_parameter = 'I'
        test_sweep_values = [0.0, 0.2, 0.4, 0.6]
        test_sweep = (test_sweep_parameter + ':'
                      + ','.join([str(v) for v in test_sweep_values]))
        values = run_batch.get_sweep_values(test_sweep)
        assert isinstance(values, list)
        assert len(values) == len(test_sweep_values)
        assert all([isinstance(value, str) for value in values])
        assert all([str(value) in values for value in test_sweep_values])

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
    def test_get_sweep_strings(self):
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
    def test_get_parameters_no_output(self, capsys):
        run_batch.get_parameters(self.settings, self.arguments)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_parameters_return_type(self):
        test_parameters = run_batch.get_parameters(self.settings,
                                                   self.arguments)
        assert isinstance(test_parameters, dict)

    def test_get_parameters_return_command(self):
        test_parameters = run_batch.get_parameters(self.settings,
                                                   self.arguments)
        assert test_parameters['<command>'] == self.arguments['<command>']

    def test_get_parameters_archive(self):
        test_arguments = self.arguments.copy()
        test_arguments['--archive'] = True
        test_parameters = run_batch.get_parameters(self.settings,
                                                   test_arguments)
        assert '--archive' in test_parameters
        assert test_parameters['--archive'] == True
        assert 'archive' in test_parameters
        assert isinstance(test_parameters['archive'], pathlib.Path)
        assert test_parameters['archive'].is_absolute()

    def test_get_parameters_no_archive(self):
        test_arguments = self.arguments.copy()
        test_arguments['--archive'] = False
        test_parameters = run_batch.get_parameters(self.settings,
                                                   test_arguments)
        assert '--archive' in test_parameters
        assert test_parameters['--archive'] == False
        assert 'archive' in test_parameters
        assert test_parameters['archive'] == None

    def test_get_parameters_archive_folder_contains_current_date(self):
        test_arguments = self.arguments.copy()
        test_arguments['--archive'] = True
        test_parameters = run_batch.get_parameters(self.settings,
                                                   test_arguments)
        assert (datetime.today().strftime('%Y-%m-%d')
                in str(test_parameters['archive']))

    def test_get_parameters_archive_folder_parent_exists(self):
        test_arguments = self.arguments.copy()
        test_arguments['--archive'] = True
        test_parameters = run_batch.get_parameters(self.settings,
                                                   test_arguments)
        assert test_parameters['archive'].parent.is_dir()

    def test_get_parameters_runlog(self):
        test_arguments = self.arguments.copy()
        test_arguments['--runlog'] = True
        test_parameters = run_batch.get_parameters(self.settings,
                                                   test_arguments)
        assert '--runlog' in test_parameters
        assert test_parameters['--runlog'] == True

    def test_get_parameters_no_runlog(self):
        test_arguments = self.arguments.copy()
        test_arguments['--runlog'] = False
        test_parameters = run_batch.get_parameters(self.settings,
                                                   test_arguments)
        assert '--runlog' in test_parameters
        assert test_parameters['--runlog'] == False

    def test_get_parameters_git(self):
        test_arguments = self.arguments.copy()
        test_arguments['--git'] = True
        test_parameters = run_batch.get_parameters(self.settings,
                                                   test_arguments)
        assert '--git' in test_parameters
        assert test_parameters['--git'] == True

    def test_get_parameters_no_git(self):
        test_arguments = self.arguments.copy()
        test_arguments['--git'] = False
        test_parameters = run_batch.get_parameters(self.settings,
                                                   test_arguments)
        assert '--git' in test_parameters
        assert test_parameters['--git'] == False

    def test_get_parameters_invalid_git(self):
        test_arguments = self.arguments.copy()
        test_arguments['--git'] = True
        test_settings = self.settings.copy()
        test_settings['current_folder'] = pathlib.Path('/')
        with pytest.raises(git.exc.InvalidGitRepositoryError):
            run_batch.get_parameters(test_settings, test_arguments)

    def test_get_parameters_git_subsettings(self):
        test_arguments = self.arguments.copy()
        test_arguments['--git'] = True
        test_parameters = run_batch.get_parameters(self.settings,
                                                   test_arguments)
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
    def test_reproducible_run_no_options(self, capfd, protect_log):
        result = run_batch.reproducible_run(self.settings, self.single_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()

    def test_reproducible_run_invalid_input(self):
        with pytest.raises(TypeError):
            run_batch.reproducible_run(self.settings)
        with pytest.raises(TypeError):
            run_batch.reproducible_run(self.settings,
                                       self.single_run,
                                       'extra parameter')
        with pytest.raises(TypeError):
            run_batch.reproducible_run('not settings', self.single_run)
        with pytest.raises(TypeError):
            run_batch.reproducible_run(self.settings, 'not a run dict')
        with pytest.raises(TypeError):
            run_batch.reproducible_run(['not', 'a', 'dict'], self.single_run)
        with pytest.raises(TypeError):
            run_batch.reproducible_run(self.settings, ['not', 'a', 'dict'])

    @pytest.mark.slow
    def test_reproducible_run_with_runlog(self, capfd, protect_log):
        test_run = self.single_run.copy()
        test_run['--runlog'] = True
        result = run_batch.reproducible_run(self.settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()
        assert len(set(self.run_folder.glob('reproduce-*.log'))) == 1

    @pytest.mark.slow
    def test_reproducible_run_template_check(self, capfd, tmp_file, protect_log):
        test_run = self.single_run.copy()
        test_run['--template'] = tmp_file
        result = run_batch.reproducible_run(self.settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode != 0
        assert not self.test_message in captured.out
        assert ('ERROR: Input file' in captured.err
                and 'not in git' in captured.err)

    @pytest.mark.slow
    def test_reproducible_run_template_ok(self, capfd, protect_log):
        test_run = self.single_run.copy()
        test_run['--template'] = 'README.md'
        result = run_batch.reproducible_run(self.settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()

    @pytest.mark.slow
    def test_reproducible_run_show_rendered(self, capfd, tmp_file, protect_log):
        test_run = self.single_run.copy()
        test_run['--show'] = True
        test_run['--template'] = 'README.md'
        result = run_batch.reproducible_run(self.settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()
        assert '------rendered template for README.md------' in captured.err

    @pytest.mark.slow
    def test_reproducible_run_save_rendered(self, capfd, tmp_file, protect_log):
        test_run = self.single_run.copy()
        test_run['--save'] = True
        test_run['--template'] = 'README.md'
        result = run_batch.reproducible_run(self.settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()
        assert self.run_folder.joinpath('README.md.rendered').is_file()
        self.run_folder.joinpath('README.md.rendered').unlink()

    @pytest.mark.slow
    def test_reproducible_run_src_check(self, capfd, tmp_srcfile, protect_log):
        test_run = self.single_run.copy()
        test_run['--src'] = str(self.src_location)
        result = run_batch.reproducible_run(self.settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode != 0
        assert not self.test_message in captured.out
        assert ('ERROR: Source directory is not clean' in captured.err
                and str(self.src_location) in captured.err)

    @pytest.mark.slow
    def test_reproducible_run_src_ok(self, capfd, protect_log):
        test_run = self.single_run.copy()
        test_run['--src'] = str(self.src_location)
        result = run_batch.reproducible_run(self.settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()
        assert 'Source code directory:' in captured.err
        assert 'Source code commit:' in captured.err

    @pytest.mark.slow
    def test_reproducible_run_build_src(self, capfd, rebuild_src, protect_log):
        test_run = self.single_run.copy()
        test_run['--src'] = str(self.src_location)
        test_run['--build'] = True
        result = run_batch.reproducible_run(self.settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()
        assert 'Source code directory:' in captured.err
        assert 'Source code commit:' in captured.err
        assert rebuild_src.is_file()

    @pytest.mark.slow
    def test_reproducible_run_parameters(self, capfd, tmp_template,
                                         protect_log):
        test_run = self.single_run.copy()
        test_run['--template'] = tmp_template['filename']
        test_run['-p'] = tmp_template['parameter_string']
        result = run_batch.reproducible_run(self.settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()

    @pytest.mark.slow
    def test_reproducible_run_list_parameters(self, capfd, tmp_template,
                                              protect_log):
        test_run = self.single_run.copy()
        test_run['--template'] = tmp_template['filename']
        test_run['-p'] = tmp_template['parameter_string']
        test_run['--list-parameters'] = True
        result = run_batch.reproducible_run(self.settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode == 0
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()
        assert 'INFO: Parameters' in captured.err
        for p in tmp_template['parameters']:
            assert f'{p} -> ' in captured.err

    @pytest.mark.slow
    def test_reproducible_run_list_parameters_fail(self, capfd, tmp_template,
                                                   protect_log):
        test_run = self.single_run.copy()
        test_run['--template'] = tmp_template['filename']
        test_run['--list-parameters'] = True
        result = run_batch.reproducible_run(self.settings, test_run)
        captured = capfd.readouterr()
        assert result.returncode != 0
        assert not self.test_message in captured.out
        assert 'INFO: Parameters' in captured.err
        for p in tmp_template['parameters']:
            assert f'{p} -> None' in captured.err
            assert f'ERROR: Parameter "{p}" did not get a value' in captured.err

    @pytest.mark.slow
    def test_reproducible_run_oldhash(self, capfd, tmp_template, protect_log):
        first_run = self.single_run.copy()
        first_run['--template'] = tmp_template['filename']
        first_run['-p'] = tmp_template['parameter_string']
        first_result = run_batch.reproducible_run(self.settings, first_run)
        first_captured = capfd.readouterr()
        assert first_result.returncode == 0
        assert self.test_message in first_captured.out
        assert self.reproduce_message in first_captured.err
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()
        assert 'Current run hash:' in first_captured.err
        hash_loc = first_captured.err.find('Current run hash:') + 18
        oldhash = first_captured.err[hash_loc:hash_loc+40]
        assert len(oldhash) == 40
        second_run = self.single_run.copy()
        second_run['--template'] = tmp_template['filename']
        second_run['--hash'] = oldhash
        second_run['--list-parameters'] = True
        second_result = run_batch.reproducible_run(self.settings, second_run)
        second_captured = capfd.readouterr()
        assert second_result.returncode == 0
        assert self.test_message in second_captured.out
        assert self.reproduce_message in second_captured.err
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()
        assert 'INFO: Parameters' in second_captured.err
        for p in tmp_template['parameters']:
            assert f'{p} -> ' in second_captured.err
        

    # Test run_single method
    @pytest.mark.slow
    def test_run_single_no_options(self, capfd, protect_log):
        run_batch.run_single(self.settings, self.single_run)
        captured = capfd.readouterr()
        assert self.single_run['title'] in captured.out
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()

    @pytest.mark.slow
    @pytest.mark.gitchanges
    def test_run_single_with_git(self, capfd, protect_git):
        old_commit = self.repo.heads[self.results_branch].commit
        test_run = self.single_run.copy()
        test_run.update({'--git': True,
                         '--input_branch': self.input_branch,
                         '--results_branch': self.results_branch,
                         'commit_files': ['reproduce-*.log',
                                          self.settings['logfile']],
                         'commit_message': 'Test commit'})
        run_batch.run_single(self.settings, test_run)
        captured = capfd.readouterr()
        assert self.single_run['title'] in captured.out
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.repo.heads[self.results_branch].commit != old_commit
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()

    @pytest.mark.slow
    def test_run_single_with_post_process(self, capfd, protect_log):
        test_message = 'Post-processing output'
        test_command = f'echo {test_message}'
        test_run = self.single_run.copy()
        test_run['--post'] = test_command
        run_batch.run_single(self.settings, test_run)
        captured = capfd.readouterr()
        assert test_run['title'] in captured.out
        assert self.reproduce_message in captured.err
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()
        assert test_message in captured.out

    @pytest.mark.slow
    def test_run_single_with_archive(self, capfd,
                                     tmp_file, tmp_path, protect_log):
        test_run = self.single_run.copy()
        test_run.update({'--archive': True,
                         'archive': tmp_path,
                         'archive_copy': ['*.md'],
                         'archive_move': [tmp_file]})
        run_batch.run_single(self.settings, test_run)
        captured = capfd.readouterr()
        assert test_run['title'] in captured.out
        assert self.reproduce_message in captured.err
        if self.run_folder.joinpath('README.md').is_file():
            assert tmp_path.joinpath('README.md').is_file()
        assert tmp_path.joinpath(tmp_file).is_file()
        assert not self.run_folder.joinpath(tmp_file).is_file()
        with open(tmp_path.joinpath(tmp_file), 'r') as f:
            assert f.readline() == self.test_message
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()
        assert tmp_path.joinpath(self.settings['archive_log']).is_file()

    @pytest.mark.slow
    def test_run_single_with_logging(self, capfd, protect_log):
        test_run = self.single_run.copy()
        test_run['--runlog'] = True
        run_batch.run_single(self.settings, test_run)
        captured = capfd.readouterr()
        assert test_run['title'] in captured.out
        assert self.test_message in captured.out
        assert self.reproduce_message in captured.err
        assert self.run_folder.joinpath(self.settings['logfile']).is_file()
        assert len(set(self.run_folder.glob('reproduce-*.log'))) == 1
