# Tests process_notebooks.py

import pytest
import pathlib
import git
import shutil

import process_notebooks

class TestProcessNotebooks:

    # Setup before testing
    def setup_class(self):
        """Settings and variables shared for all tests."""
        self.notebook_path = (pathlib.Path.home()
                              .joinpath('OneDrive/Documents/Notebooks'))
        self.test_page =     (pathlib.Path(__file__).parent
                              .joinpath('data/notebook_page.md'))
        self.test_logbook =  (pathlib.Path(__file__).parent
                              .joinpath('data/logbook_page.md'))


    # Fixtures
    @pytest.fixture
    def tmp_page(self, tmp_path):
        """Create a new notebook page in a temp folder and return its path."""
        tempfile = tmp_path.joinpath('tempfile.md')
        shutil.copyfile(self.test_page, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_logbook_page(self, tmp_path):
        """Create a new logbook page in a temp folder and return its path."""
        tempfile = tmp_path.joinpath('tempfile.md')
        shutil.copyfile(self.test_logbook, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture(scope="class")
    def clone_notebooks(self, tmpdir_factory):
        """Create a complete clone of the Notebooks repo in a temp folder."""
        source_repo = git.Repo(self.notebook_path)
        destination_path = tmpdir_factory.mktemp('data').join('Notebooks')
        cloned_repo = source_repo.clone(destination_path)
        yield cloned_repo
        shutil.rmtree(destination_path)

    @pytest.fixture
    def preserve_repo(self, clone_notebooks):
        """Make sure no files are changed within the cloned repo."""
        cloned_repo = clone_notebooks
        cloned_repo.head.reference = cloned_repo.commit('master')
        cloned_repo.head.reset(index=True, working_tree=True)
        assert not cloned_repo.is_dirty()
        assert len(cloned_repo.untracked_files) == 0
        yield cloned_repo
        assert not cloned_repo.is_dirty()
        assert len(cloned_repo.untracked_files) == 0


    # Loading data
    def test_load_page_no_output(self, tmp_page, capsys):
        process_notebooks.Page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_load_page_contents(self, tmp_page):
        page_content = process_notebooks.Page(tmp_page).content
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert page_content == test_content

    def test_load_page_invalid_input(self, tmp_page):
        with pytest.raises(AttributeError):
            process_notebooks.Page('string')
        with pytest.raises(AttributeError):
            process_notebooks.Page(3.142)
        with pytest.raises(AttributeError):
            process_notebooks.Page([tmp_page, tmp_page])

    def test_load_logbook_page_no_output(self, tmp_page, capsys):
        process_notebooks.LogbookPage(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_load_logbook_page_contents(self, tmp_logbook_page):
        page_content = process_notebooks.LogbookPage(tmp_logbook_page).content
        with open(self.test_logbook, 'r')  as f:
            test_content = f.readlines()
        assert page_content == test_content

    def test_load_logbook_page_invalid_input(self, tmp_page):
        with pytest.raises(AttributeError):
            process_notebooks.LogbookPage('string')
        with pytest.raises(AttributeError):
            process_notebooks.LogbookPage(3.142)
        with pytest.raises(AttributeError):
            process_notebooks.LogbookPage([tmp_page, tmp_page])
        with pytest.raises(OSError):
            process_notebooks.LogbookPage(pathlib.Path('/not/a/path'))
