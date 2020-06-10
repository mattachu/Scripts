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
        self.test_page = (pathlib.Path(__file__).parent
                            .joinpath('data/notebook_page.md'))
        self.test_logbook = (pathlib.Path(__file__).parent
                                .joinpath('data/2020-01-01.md'))
        self.test_title = 'Page title'
        self.temp_page = 'temp_file'
        self.temp_logbook = '2020-01-01'


    # Fixtures
    @pytest.fixture
    def tmp_page(self, tmp_path):
        """Create a new notebook page in a temp folder and return its path."""
        tempfile = tmp_path.joinpath(f'{self.temp_page}.md')
        shutil.copyfile(self.test_page, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_logbook_page(self, tmp_path):
        """Create a new logbook page in a temp folder and return its path."""
        tempfile = tmp_path.joinpath(f'{self.temp_logbook}.md')
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
    def test_load_page(self, tmp_page):
        test_page = process_notebooks.Page(tmp_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert isinstance(test_page.content, list)
        assert test_page.path == tmp_page
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def test_load_page_no_output(self, tmp_page, capsys):
        process_notebooks.Page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_load_page_invalid_input(self, tmp_page):
        with pytest.raises(AttributeError):
            process_notebooks.Page('string')
        with pytest.raises(AttributeError):
            process_notebooks.Page(3.142)
        with pytest.raises(AttributeError):
            process_notebooks.Page([tmp_page, tmp_page])

    def test_load_logbook_page(self, tmp_logbook_page):
        test_page = process_notebooks.LogbookPage(tmp_logbook_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert isinstance(test_page.content, list)
        assert test_page.path == tmp_logbook_page
        with open(self.test_logbook, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def test_load_logbook_page_no_output(self, tmp_logbook_page, capsys):
        process_notebooks.LogbookPage(tmp_logbook_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_load_logbook_page_invalid_input(self, tmp_logbook_page):
        with pytest.raises(AttributeError):
            process_notebooks.LogbookPage('string')
        with pytest.raises(AttributeError):
            process_notebooks.LogbookPage(3.142)
        with pytest.raises(AttributeError):
            process_notebooks.LogbookPage([tmp_logbook_page, tmp_logbook_page])
        with pytest.raises(OSError):
            process_notebooks.LogbookPage(pathlib.Path('/not/a/path'))


    # Getting information from page objects
    def test_get_title(self, tmp_page):
        test_title = process_notebooks.Page(tmp_page).get_title()
        assert isinstance(test_title, str)
        assert test_title == self.test_title

    def test_get_title_null(self, tmp_page):
        test_title = process_notebooks.Page().get_title()
        assert test_title is None

    def test_get_title_no_output(self, tmp_page, capsys):
        process_notebooks.Page(tmp_page).get_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_title_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            process_notebooks.Page(tmp_page).get_title('extra parameter')

    def test_get_title_logbook(self, tmp_logbook_page):
        test_title = process_notebooks.LogbookPage(tmp_logbook_page).get_title()
        assert isinstance(test_title, str)
        assert test_title == self.temp_logbook

    def test_get_title_logbook_null(self):
        test_title = process_notebooks.LogbookPage().get_title()
        assert test_title is None

    def test_get_title_logbook_no_output(self, tmp_logbook_page, capsys):
        process_notebooks.LogbookPage(tmp_logbook_page).get_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_get_title_logbook_invalid_input(self, tmp_logbook_page):
        with pytest.raises(TypeError):
            process_notebooks.LogbookPage(tmp_logbook_page).get_title(
                'extra parameter')

    def test_convert_filename_to_title(self, tmp_page):
        test_title = process_notebooks.Page(tmp_page)._convert_filename_to_title()
        assert isinstance(test_title, str)
        expected = tmp_page.stem.replace('_', ' ').replace('-', ' ').strip()
        assert test_title == expected

    def test_convert_filename_to_title_null(self):
        test_title = process_notebooks.Page()._convert_filename_to_title()
        assert test_title is None

    def test_convert_filename_to_title_no_output(self, tmp_page, capsys):
        process_notebooks.Page(tmp_page)._convert_filename_to_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_convert_filename_to_title_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            (process_notebooks.Page(tmp_page)
                ._convert_filename_to_title('extra parameter'))

    def test_convert_filename_to_title_logbook(self, tmp_logbook_page):
        test_title = (process_notebooks.LogbookPage(tmp_logbook_page)
                        ._convert_filename_to_title())
        assert isinstance(test_title, str)
        expected = tmp_logbook_page.stem.strip()
        assert test_title == expected

    def test_convert_filename_to_title_logbook_null(self):
        test_title = (process_notebooks.LogbookPage()
                        ._convert_filename_to_title())
        assert test_title is None

    def test_convert_filename_to_title_logbook_no_output(self, tmp_logbook_page,
                                                         capsys):
        (process_notebooks.LogbookPage(tmp_logbook_page)
            ._convert_filename_to_title())
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_convert_filename_to_title_logbook_invalid_input(self,
                                                             tmp_logbook_page):
        with pytest.raises(TypeError):
            (process_notebooks.LogbookPage(tmp_logbook_page)
                ._convert_filename_to_title('extra parameter'))


    # Utility functions
    def test_is_blank_line_blank(self):
        assert process_notebooks._is_blank_line('') is True

    def test_is_blank_line_newline(self):
        assert process_notebooks._is_blank_line('\n') is True

    def test_is_blank_line_text(self):
        assert process_notebooks._is_blank_line('text') is False
        assert process_notebooks._is_blank_line('text\n') is False

    def test_is_blank_line_title(self):
        assert process_notebooks._is_blank_line('# Page title') is False
        assert process_notebooks._is_blank_line('# Page title\n') is False

    def test_is_blank_line_link(self):
        assert process_notebooks._is_blank_line('[link]: link') is False
        assert process_notebooks._is_blank_line('[link]: link\n') is False

    def test_is_blank_line_navigation(self):
        assert process_notebooks._is_blank_line('[page](link)') is False
        assert process_notebooks._is_blank_line('[page](link)\n') is False

    def test_is_blank_line_invalid_input(self):
        with pytest.raises(AttributeError):
            process_notebooks._is_blank_line(None)
        with pytest.raises(AttributeError):
            process_notebooks._is_blank_line(self.test_page)
        with pytest.raises(AttributeError):
            process_notebooks._is_blank_line(3.142)
        with pytest.raises(AttributeError):
            process_notebooks._is_blank_line(['1', '2'])

    def test_is_navigation_line_blank(self):
        assert process_notebooks._is_navigation_line('') is False

    def test_is_navigation_line_newline(self):
        assert process_notebooks._is_navigation_line('\n') is False

    def test_is_navigation_line_text(self):
        assert process_notebooks._is_navigation_line('text') is False
        assert process_notebooks._is_navigation_line('text\n') is False

    def test_is_navigation_line_title(self):
        assert process_notebooks._is_navigation_line('# Page title') is False
        assert process_notebooks._is_navigation_line('# Page title\n') is False

    def test_is_navigation_line_link(self):
        assert process_notebooks._is_navigation_line('[link]: link') is False
        assert process_notebooks._is_navigation_line('[link]: link\n') is False

    def test_is_navigation_line_navigation(self):
        assert process_notebooks._is_navigation_line('[page](link)') is True
        assert process_notebooks._is_navigation_line('[page](link)\n') is True

    def test_is_navigation_line_invalid_input(self):
        with pytest.raises(TypeError):
            process_notebooks._is_navigation_line(None)
        with pytest.raises(TypeError):
            process_notebooks._is_navigation_line(self.test_page)
        with pytest.raises(TypeError):
            process_notebooks._is_navigation_line(3.142)
        with pytest.raises(TypeError):
            process_notebooks._is_navigation_line(['1', '2'])

    def test_is_title_line_blank(self):
        assert process_notebooks._is_title_line('') is False

    def test_is_title_line_newline(self):
        assert process_notebooks._is_title_line('\n') is False

    def test_is_title_line_text(self):
        assert process_notebooks._is_title_line('text') is False
        assert process_notebooks._is_title_line('text\n') is False

    def test_is_title_line_title(self):
        assert process_notebooks._is_title_line('# Page title') is True
        assert process_notebooks._is_title_line('# Page title\n') is True

    def test_is_title_line_link(self):
        assert process_notebooks._is_title_line('[link]: link') is False
        assert process_notebooks._is_title_line('[link]: link\n') is False

    def test_is_title_line_navigation(self):
        assert process_notebooks._is_title_line('[page](link)') is False
        assert process_notebooks._is_title_line('[page](link)\n') is False

    def test_is_title_line_invalid_input(self):
        with pytest.raises(AttributeError):
            process_notebooks._is_title_line(None)
        with pytest.raises(AttributeError):
            process_notebooks._is_title_line(self.test_page)
        with pytest.raises(AttributeError):
            process_notebooks._is_title_line(3.142)
        with pytest.raises(AttributeError):
            process_notebooks._is_title_line(['1', '2'])
