# Tests process_notebooks.py

import pytest
import pathlib
import git
import shutil

#import process_notebooks

class TestProcessNotebooks:

    # Setup before testing
    def setup_class(self):
        """Settings and variables shared for all tests."""
        self.notebook_path = (pathlib.Path.home()
                              .joinpath('OneDrive/Documents/Notebooks'))
        self.test_page_contents = 'Hello world'
        self.test_logbook_contents = 'Hello world'


    # Fixtures
    @pytest.fixture
    def tmp_page(self, tmp_path):
        """Create a new notebook page in a temp folder and return its path."""
        tempfile = tmp_path.joinpath('tempfile.md')
        with open(tempfile, 'w') as f:
            f.write(self.test_page_contents)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_logbook_page(self, tmp_path):
        """Create a new logbook page in a temp folder and return its path."""
        tempfile = tmp_path.joinpath('tempfile.md')
        with open(tempfile, 'w') as f:
            f.write(self.test_logbook_contents)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture(scope="class")
    def clone_notebook(self, tmpdir_factory):
        """Create a complete clone of the Notebooks repo in a temp folder."""
        source_repo = git.Repo(self.notebook_path)
        destination_path = tmpdir_factory.mktemp('data').join('Notebooks')
        cloned_repo = source_repo.clone(destination_path)
        yield cloned_repo
        shutil.rmtree(destination_path)

    @pytest.fixture
    def preserve_repo(self, clone_notebook):
        """Make sure no files are changed within the cloned repo."""
        cloned_repo = clone_notebook
        cloned_repo.head.reference = cloned_repo.commit('master')
        cloned_repo.head.reset(index=True, working_tree=True)
        assert not cloned_repo.is_dirty()
        assert len(cloned_repo.untracked_files) == 0
        yield cloned_repo
        assert not cloned_repo.is_dirty()
        assert len(cloned_repo.untracked_files) == 0


    # Dummy test
    def test_dummy1(self):
        assert True

    def test_dummy2(self, clone_notebook):
        assert False

    def test_dummy3(self, preserve_repo):
        assert False
