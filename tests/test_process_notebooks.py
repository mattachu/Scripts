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
        self.test_logbook_page = (pathlib.Path(__file__).parent
                                    .joinpath('data/2020-01-01.md'))
        self.test_title = 'Page title'
        self.temp_notebook = 'temp_notebook'
        self.temp_page = 'temp_file'
        self.temp_pages = ['page1.md', 'page2.md', 'page3.md']
        self.temp_logbook = 'Logbook'
        self.temp_logbook_page = '2020-01-01'
        self.temp_logbook_pages = ['2020-01-01.md',
                                   '2020-01-02.md',
                                   '2020-01-03.md']
        self.test_message = 'Hello world'


    # Fixtures
    @pytest.fixture
    def tmp_file_factory(self, tmp_path):
        created_files = []
        def _new_temp_file(filename):
            tempfile = tmp_path.joinpath(filename)
            with open(tempfile, 'w') as f:
                f.write(self.test_message)
            created_files.append(tempfile)
            return tempfile
        yield _new_temp_file
        for file in created_files:
            if file.is_file():
                file.unlink()

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
        tempfile = tmp_path.joinpath(f'{self.temp_logbook_page}.md')
        shutil.copyfile(self.test_logbook_page, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_notebook(self, tmp_path):
        """Create a temporary notebook folder and add some pages."""
        notebook_folder = tmp_path.joinpath(self.temp_notebook)
        self.create_and_fill_folder(notebook_folder,
                                    self.temp_pages,
                                    self.test_page)
        yield notebook_folder
        shutil.rmtree(notebook_folder)

    @pytest.fixture
    def tmp_logbook(self, tmp_path):
        """Create a temporary logbook folder and add some pages."""
        logbook_folder = tmp_path.joinpath(self.temp_logbook)
        self.create_and_fill_folder(logbook_folder,
                                    self.temp_logbook_pages,
                                    self.test_logbook_page)
        yield logbook_folder
        shutil.rmtree(logbook_folder)

    @pytest.fixture
    def tmp_nested(self, tmp_path):
        """Create a temporary notebook folder and add pages and subfolders."""
        notebook_folder = tmp_path.joinpath(self.temp_notebook)
        self.create_and_fill_folder(notebook_folder,
                                    self.temp_pages,
                                    self.test_page)
        subfolder1 = notebook_folder.joinpath(self.temp_notebook)
        self.create_and_fill_folder(subfolder1,
                                    self.temp_pages,
                                    self.test_page)
        subfolder2 = notebook_folder.joinpath(self.temp_logbook)
        self.create_and_fill_folder(subfolder2,
                                    self.temp_logbook_pages,
                                    self.test_logbook_page)
        yield notebook_folder
        shutil.rmtree(notebook_folder)

    @pytest.fixture(scope="class")
    def cloned_repo(self, tmp_path_factory):
        """Create a complete clone of the Notebooks repo in a temp folder."""
        source_repo = git.Repo(self.notebook_path)
        destination_path = tmp_path_factory.mktemp('Notebooks', numbered=False)
        cloned_repo = source_repo.clone(destination_path)
        cloned_repo.head.reference = cloned_repo.heads.master
        cloned_repo.head.reset(index=True, working_tree=True)
        yield cloned_repo
        shutil.rmtree(destination_path)


    # Functions
    def create_and_fill_folder(self, folder_path, file_list, file_template):
        folder_path.mkdir()
        for filename in file_list:
            new_file = folder_path.joinpath(filename)
            shutil.copyfile(file_template, new_file)

    def repo_unchanged(self, cloned_repo):
        """Make sure no files are changed within the cloned repo."""
        if not cloned_repo.head.reference == cloned_repo.heads.master:
            return False
        elif cloned_repo.is_dirty():
            return False
        elif len(cloned_repo.untracked_files) > 0:
            return False
        else:
            return True


    # Creating page objects
    def test_create_page(self, tmp_page):
        test_page = process_notebooks.Page(tmp_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert isinstance(test_page.content, list)
        assert test_page.path == tmp_page
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def test_create_page_null(self):
        test_page = process_notebooks.Page()
        assert test_page.path is None
        assert test_page.content is None

    def test_create_page_no_output(self, tmp_page, capsys):
        process_notebooks.Page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_create_page_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            process_notebooks.Page(tmp_page, 'extra parameter')
        with pytest.raises(AttributeError):
            process_notebooks.Page('string')
        with pytest.raises(AttributeError):
            process_notebooks.Page(3.142)
        with pytest.raises(AttributeError):
            process_notebooks.Page([tmp_page, tmp_page])

    def test_create_page_invalid_file_types(self, tmp_file_factory):
        with pytest.raises(ValueError):
            process_notebooks.Page(tmp_file_factory('test.xlsx'))
        with pytest.raises(ValueError):
            process_notebooks.Page(tmp_file_factory('test.png'))
        with pytest.raises(ValueError):
            process_notebooks.Page(tmp_file_factory('.DS_Store'))

    def test_create_logbook_page(self, tmp_logbook_page):
        test_page = process_notebooks.LogbookPage(tmp_logbook_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert isinstance(test_page.content, list)
        assert test_page.path == tmp_logbook_page
        with open(self.test_logbook_page, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def test_create_logbook_page_null(self):
        test_page = process_notebooks.LogbookPage()
        assert test_page.path is None
        assert test_page.content is None

    def test_create_logbook_page_no_output(self, tmp_logbook_page, capsys):
        process_notebooks.LogbookPage(tmp_logbook_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_create_logbook_page_invalid_input(self, tmp_logbook_page):
        with pytest.raises(TypeError):
            process_notebooks.LogbookPage(tmp_logbook_page, 'extra parameter')
        with pytest.raises(AttributeError):
            process_notebooks.LogbookPage('string')
        with pytest.raises(AttributeError):
            process_notebooks.LogbookPage(3.142)
        with pytest.raises(AttributeError):
            process_notebooks.LogbookPage([tmp_logbook_page, tmp_logbook_page])
        with pytest.raises(OSError):
            process_notebooks.LogbookPage(pathlib.Path('/not/a/path'))

    def test_create_logbook_page_invalid_file_types(self, tmp_file_factory):
        with pytest.raises(ValueError):
            process_notebooks.LogbookPage(tmp_file_factory('test.xlsx'))
        with pytest.raises(ValueError):
            process_notebooks.LogbookPage(tmp_file_factory('test.png'))
        with pytest.raises(ValueError):
            process_notebooks.LogbookPage(tmp_file_factory('.DS_Store'))


    # Loading data to page objects
    def test_page_load_content(self, tmp_page):
        test_page = process_notebooks.Page()
        test_page.path = tmp_page
        test_page.load_content()
        assert isinstance(test_page.content, list)
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def test_page_load_content_null(self):
        test_page = process_notebooks.Page()
        test_page.path = None
        test_page.load_content()
        assert test_page.content is None

    def test_page_load_content_no_output(self, tmp_page, capsys):
        test_page = process_notebooks.Page()
        test_page.path = tmp_page
        test_page.load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_page_load_content_null_no_output(self, capsys):
        process_notebooks.Page().load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_page_load_content_invalid_input(self, tmp_page):
        test_page = process_notebooks.Page()
        with pytest.raises(TypeError):
            test_page.load_content('extra parameter')

    def test_page_load_content_invalid_file_types(self, tmp_file_factory):
        test_page = process_notebooks.Page()
        test_page.path = tmp_file_factory('test.xlsx')
        with pytest.raises(ValueError):
            test_page.load_content()
        test_page.path = tmp_file_factory('test.png')
        with pytest.raises(ValueError):
            test_page.load_content()
        test_page.path = tmp_file_factory('.DS_Store')
        with pytest.raises(ValueError):
            test_page.load_content()

    def test_logbook_page_load_content(self, tmp_logbook_page):
        test_logbook_page = process_notebooks.LogbookPage()
        test_logbook_page.path = tmp_logbook_page
        test_logbook_page.load_content()
        assert isinstance(test_logbook_page.content, list)
        with open(self.test_logbook_page, 'r')  as f:
            test_content = f.readlines()
        assert test_logbook_page.content == test_content

    def test_logbook_page_load_content_null(self):
        test_logbook_page = process_notebooks.LogbookPage()
        test_logbook_page.path = None
        test_logbook_page.load_content()
        assert test_logbook_page.content is None

    def test_logbook_page_load_content_no_output(self, capsys):
        process_notebooks.LogbookPage().load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_page_load_content_null_no_output(self, tmp_logbook_page,
                                                      capsys):
        test_logbook_page = process_notebooks.LogbookPage()
        test_logbook_page.path = tmp_logbook_page
        test_logbook_page.load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_page_load_content_invalid_input(self, tmp_logbook_page):
        test_logbook_page = process_notebooks.LogbookPage()
        with pytest.raises(TypeError):
            test_logbook_page.load_content('extra parameter')

    def test_logbook_page_load_content_invalid_file_types(self, tmp_path):
        test_page = process_notebooks.LogbookPage()
        temp_file = tmp_path.joinpath('test.xlsx')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        test_page.path = temp_file
        with pytest.raises(ValueError):
            test_page.load_content()
        temp_file = tmp_path.joinpath('test.png')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        test_page.path = temp_file
        with pytest.raises(ValueError):
            test_page.load_content()
        temp_file = tmp_path.joinpath('.DS_Store')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        test_page.path = temp_file
        with pytest.raises(ValueError):
            test_page.load_content()
        temp_file = tmp_path.joinpath('2020-01-01-Meeting.md')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        test_page.path = temp_file
        with pytest.raises(ValueError):
            test_page.load_content()


    # Getting information from page objects
    def test_page_get_title(self, tmp_page):
        test_title = process_notebooks.Page(tmp_page).get_title()
        assert isinstance(test_title, str)
        assert test_title == self.test_title

    def test_page_get_title_null(self, tmp_page):
        test_title = process_notebooks.Page().get_title()
        assert test_title is None

    def test_page_get_title_no_output(self, tmp_page, capsys):
        process_notebooks.Page(tmp_page).get_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_page_get_title_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            process_notebooks.Page(tmp_page).get_title('extra parameter')

    def test_logbook_page_get_title(self, tmp_logbook_page):
        test_title = process_notebooks.LogbookPage(tmp_logbook_page).get_title()
        assert isinstance(test_title, str)
        assert test_title == self.temp_logbook_page.strip()

    def test_logbook_page_get_title_null(self):
        test_title = process_notebooks.LogbookPage().get_title()
        assert test_title is None

    def test_logbook_page_get_title_no_output(self, tmp_logbook_page, capsys):
        process_notebooks.LogbookPage(tmp_logbook_page).get_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_page_get_title_invalid_input(self, tmp_logbook_page):
        with pytest.raises(TypeError):
            process_notebooks.LogbookPage(tmp_logbook_page).get_title(
                'extra parameter')

    def test_page_is_valid_page(self, tmp_page):
        test_page = process_notebooks.Page()
        assert test_page._is_valid_page(tmp_page) is True

    def test_page_is_valid_page_logbook_page(self, tmp_logbook_page):
        test_page = process_notebooks.Page()
        assert test_page._is_valid_page(tmp_logbook_page) is True

    def test_page_is_valid_page_fail(self, tmp_file_factory):
        test_page = process_notebooks.Page()
        assert test_page._is_valid_page(tmp_file_factory('test.xlsx')) is False
        assert test_page._is_valid_page(tmp_file_factory('test.png')) is False
        assert test_page._is_valid_page(tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory('is-a-file.md')
        with pytest.raises(OSError):
            test_page._is_valid_page(tmp_file.parent.joinpath('not-a-file.md'))

    def test_page_is_valid_page_no_output(self, tmp_page, capsys):
        process_notebooks.Page()._is_valid_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_page_is_valid_page_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            process_notebooks.Page()._is_valid_page(tmp_page, 'extra parameter')
        with pytest.raises(AttributeError):
            process_notebooks.Page()._is_valid_page('string')
        with pytest.raises(AttributeError):
            process_notebooks.Page()._is_valid_page(3.142)
        with pytest.raises(AttributeError):
            process_notebooks.Page()._is_valid_page([tmp_page, tmp_page])
        with pytest.raises(OSError):
            process_notebooks.Page()._is_valid_page(pathlib.Path('/not/a/path'))

    def test_logbook_page_is_valid_page(self, tmp_logbook_page):
        test_page = process_notebooks.LogbookPage()
        assert test_page._is_valid_page(tmp_logbook_page) is True

    def test_logbook_page_is_valid_page_notebook_page(self, tmp_page):
        test_page = process_notebooks.LogbookPage()
        assert test_page._is_valid_page(tmp_page) is False

    def test_logbook_page_is_valid_page_fail(self, tmp_file_factory):
        test_page = process_notebooks.LogbookPage()
        assert test_page._is_valid_page(tmp_file_factory('test.xlsx')) is False
        assert test_page._is_valid_page(tmp_file_factory('test.png')) is False
        assert test_page._is_valid_page(tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory('is-a-file.md')
        with pytest.raises(OSError):
            test_page._is_valid_page(tmp_file.parent.joinpath('not-a-file.md'))
        assert test_page._is_valid_page(
            tmp_file_factory('2020-01-01-Meeting.md')) is False
        assert test_page._is_valid_page(tmp_file_factory('page1.md')) is False

    def test_logbook_page_is_valid_page_no_output(self, tmp_logbook_page, capsys):
        process_notebooks.LogbookPage()._is_valid_page(tmp_logbook_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_page_is_valid_page_invalid_input(self, tmp_logbook_page):
        with pytest.raises(TypeError):
            process_notebooks.LogbookPage()._is_valid_page(tmp_logbook_page,
                                                           'extra parameter')
        with pytest.raises(AttributeError):
            process_notebooks.LogbookPage()._is_valid_page('string')
        with pytest.raises(AttributeError):
            process_notebooks.LogbookPage()._is_valid_page(3.142)
        with pytest.raises(AttributeError):
            process_notebooks.LogbookPage()._is_valid_page([tmp_logbook_page,
                                                            tmp_logbook_page])
        with pytest.raises(OSError):
            process_notebooks.LogbookPage()._is_valid_page(
                pathlib.Path('/not/a/path'))

    def test_page_convert_filename_to_title(self, tmp_page):
        test_title = process_notebooks.Page(tmp_page)._convert_filename_to_title()
        assert isinstance(test_title, str)
        expected = tmp_page.stem.replace('_', ' ').replace('-', ' ').strip()
        assert test_title == expected

    def test_page_convert_filename_to_title_null(self):
        test_title = process_notebooks.Page()._convert_filename_to_title()
        assert test_title is None

    def test_page_convert_filename_to_title_no_output(self, tmp_page, capsys):
        process_notebooks.Page(tmp_page)._convert_filename_to_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_page_convert_filename_to_title_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            (process_notebooks.Page(tmp_page)
                ._convert_filename_to_title('extra parameter'))

    def test_logbook_page_convert_filename_to_title(self, tmp_logbook_page):
        test_title = (process_notebooks.LogbookPage(tmp_logbook_page)
                        ._convert_filename_to_title())
        assert isinstance(test_title, str)
        expected = tmp_logbook_page.stem.strip()
        assert test_title == expected

    def test_logbook_page_convert_filename_to_title_null(self):
        test_title = (process_notebooks.LogbookPage()
                        ._convert_filename_to_title())
        assert test_title is None

    def test_logbook_page_convert_filename_to_title_no_output(self, tmp_logbook_page,
                                                         capsys):
        (process_notebooks.LogbookPage(tmp_logbook_page)
            ._convert_filename_to_title())
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_page_convert_filename_to_title_invalid_input(self,
                                                             tmp_logbook_page):
        with pytest.raises(TypeError):
            (process_notebooks.LogbookPage(tmp_logbook_page)
                ._convert_filename_to_title('extra parameter'))


    # Creating notebook objects
    def test_create_notebook(self, tmp_notebook):
        test_notebook = process_notebooks.Notebook(tmp_notebook)
        assert isinstance(test_notebook.path, pathlib.Path)
        assert test_notebook.path == tmp_notebook

    def test_create_notebook_contents(self, tmp_notebook):
        test_notebook = process_notebooks.Notebook(tmp_notebook)
        for filename in self.temp_pages:
            this_path = tmp_notebook.joinpath(filename)
            assert this_path in [this_page.path
                                 for this_page in test_notebook.contents]
        for this_page in test_notebook.contents:
            assert isinstance(this_page, process_notebooks.Page)
            with open(self.test_page, 'r')  as f:
                test_content = f.readlines()
            assert this_page.content == test_content

    def test_create_notebook_no_changes(self, cloned_repo):
        process_notebooks.Notebook(pathlib.Path(cloned_repo.working_dir))
        assert self.repo_unchanged(cloned_repo)

    def test_create_notebook_null(self):
        test_notebook = process_notebooks.Notebook()
        assert test_notebook.path is None
        assert test_notebook.contents == []

    def test_create_notebook_no_output(self, tmp_notebook, capsys):
        process_notebooks.Notebook(tmp_notebook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_create_notebook_invalid_input(self, tmp_notebook):
        with pytest.raises(TypeError):
            process_notebooks.Notebook(tmp_notebook, 'extra parameter')
        with pytest.raises(AttributeError):
            process_notebooks.Notebook('string')
        with pytest.raises(AttributeError):
            process_notebooks.Notebook(3.142)
        with pytest.raises(AttributeError):
            process_notebooks.Notebook([tmp_notebook, tmp_notebook])
        with pytest.raises(OSError):
            process_notebooks.Notebook(pathlib.Path('/not/a/path'))

    def test_create_logbook(self, tmp_logbook):
        test_logbook = process_notebooks.Logbook(tmp_logbook)
        assert isinstance(test_logbook.path, pathlib.Path)
        assert test_logbook.path == tmp_logbook

    def test_create_logbook_contents(self, tmp_logbook):
        test_logbook = process_notebooks.Logbook(tmp_logbook)
        for filename in self.temp_logbook_pages:
            this_path = tmp_logbook.joinpath(filename)
            assert this_path in [this_page.path
                                 for this_page in test_logbook.contents]
        for this_page in test_logbook.contents:
            assert isinstance(this_page, process_notebooks.LogbookPage)
            with open(self.test_logbook_page, 'r')  as f:
                test_content = f.readlines()
            assert this_page.content == test_content

    def test_create_logbook_null(self):
        test_logbook = process_notebooks.Logbook()
        assert test_logbook.path is None
        assert test_logbook.contents == []

    def test_create_logbook_no_output(self, tmp_logbook, capsys):
        process_notebooks.Logbook(tmp_logbook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_create_logbook_invalid_input(self, tmp_logbook):
        with pytest.raises(TypeError):
            process_notebooks.Logbook(tmp_logbook, 'extra parameter')
        with pytest.raises(AttributeError):
            process_notebooks.Logbook('string')
        with pytest.raises(AttributeError):
            process_notebooks.Logbook(3.142)
        with pytest.raises(AttributeError):
            process_notebooks.Logbook([tmp_logbook, tmp_logbook])
        with pytest.raises(OSError):
            process_notebooks.Logbook(pathlib.Path('/not/a/path'))

    def test_create_notebook_nested(self, tmp_nested):
        test_notebook = process_notebooks.Notebook(tmp_nested)
        assert isinstance(test_notebook.path, pathlib.Path)
        assert test_notebook.path == tmp_nested

    def test_create_notebook_nested_contents(self, tmp_nested):
        test_notebook = process_notebooks.Notebook(tmp_nested)
        notebook_contents = [item.path for item in test_notebook.contents]
        for filename in self.temp_pages:
            this_path = tmp_nested.joinpath(filename)
            assert this_path in notebook_contents
        assert tmp_nested.joinpath(self.temp_notebook) in notebook_contents
        assert tmp_nested.joinpath(self.temp_logbook) in notebook_contents


    # Loading data to notebook objects
    def test_notebook_add_page(self, tmp_page):
        test_notebook = process_notebooks.Notebook()
        test_notebook.add_page(tmp_page)
        assert isinstance(test_notebook.contents, list)
        assert tmp_page in [this_page.path
                            for this_page in test_notebook.contents]
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, process_notebooks.Page)
        assert last_item.path == tmp_page
        assert isinstance(last_item.content, list)
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert last_item.content == test_content

    def test_notebook_add_page_null(self):
        test_notebook = process_notebooks.Notebook()
        test_notebook.add_page()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, process_notebooks.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_notebook_add_page_no_output(self, tmp_page, capsys):
        process_notebooks.Notebook().add_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_page_null_no_output(self, capsys):
        process_notebooks.Notebook().add_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_page_invalid_input(self, tmp_page):
        test_notebook = process_notebooks.Notebook()
        with pytest.raises(TypeError):
            test_notebook.add_page(tmp_page, 'extra parameter')
        with pytest.raises(AttributeError):
            test_notebook.add_page('string')
        with pytest.raises(AttributeError):
            test_notebook.add_page(3.142)
        with pytest.raises(AttributeError):
            test_notebook.add_page([tmp_page, tmp_page])
        with pytest.raises(OSError):
            test_notebook.add_page(pathlib.Path('/not/a/path'))

    def test_notebook_add_page_invalid_file_types(self, tmp_path):
        test_notebook = process_notebooks.Notebook()
        temp_file = tmp_path.joinpath('test.xlsx')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_notebook.add_page(temp_file)
        temp_file = tmp_path.joinpath('test.png')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_notebook.add_page(temp_file)
        temp_file = tmp_path.joinpath('.DS_Store')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_notebook.add_page(temp_file)

    def test_logbook_add_page(self, tmp_logbook_page):
        test_logbook = process_notebooks.Logbook()
        test_logbook.add_page(tmp_logbook_page)
        assert isinstance(test_logbook.contents, list)
        assert tmp_logbook_page in [this_page.path
                                    for this_page in test_logbook.contents]
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, process_notebooks.LogbookPage)
        assert last_item.path == tmp_logbook_page
        assert isinstance(last_item.content, list)
        with open(self.test_logbook_page, 'r')  as f:
            test_content = f.readlines()
        assert last_item.content == test_content

    def test_logbook_add_page_null(self):
        test_logbook = process_notebooks.Logbook()
        test_logbook.add_page()
        assert isinstance(test_logbook.contents, list)
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, process_notebooks.LogbookPage)
        assert last_item.path is None
        assert last_item.content is None

    def test_logbook_add_page_no_output(self, tmp_logbook_page, capsys):
        process_notebooks.Logbook().add_page(tmp_logbook_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_page_null_no_output(self, capsys):
        process_notebooks.Logbook().add_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_page_invalid_input(self, tmp_logbook_page):
        test_logbook = process_notebooks.Logbook()
        with pytest.raises(TypeError):
            test_logbook.add_page(tmp_logbook_page, 'extra parameter')
        with pytest.raises(AttributeError):
            test_logbook.add_page('string')
        with pytest.raises(AttributeError):
            test_logbook.add_page(3.142)
        with pytest.raises(AttributeError):
            test_logbook.add_page([tmp_logbook_page, tmp_logbook_page])
        with pytest.raises(OSError):
            test_logbook.add_page(pathlib.Path('/not/a/path'))

    def test_logbook_add_page_invalid_file_types(self, tmp_path):
        test_logbook = process_notebooks.Logbook()
        temp_file = tmp_path.joinpath('test.xlsx')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_logbook.add_page(temp_file)
        temp_file = tmp_path.joinpath('test.png')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_logbook.add_page(temp_file)
        temp_file = tmp_path.joinpath('.DS_Store')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_logbook.add_page(temp_file)

    def test_logbook_add_page_not_logbook_page(self, tmp_path):
        test_logbook = process_notebooks.Logbook()
        temp_file = tmp_path.joinpath('test.md')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_logbook.add_page(temp_file)

    def test_notebook_add_notebook(self, tmp_notebook):
        test_notebook = process_notebooks.Notebook()
        test_notebook.add_notebook(tmp_notebook)
        assert isinstance(test_notebook.contents, list)
        assert tmp_notebook in [this_item.path
                                for this_item in test_notebook.contents]
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, process_notebooks.Notebook)
        assert last_item.path == tmp_notebook
        assert isinstance(last_item.contents, list)
        for filename in self.temp_pages:
            this_path = tmp_notebook.joinpath(filename)
            assert this_path in [this_page.path
                                 for this_page in last_item.contents]
        for this_page in last_item.contents:
            assert isinstance(this_page, process_notebooks.Page)
            with open(self.test_page, 'r')  as f:
                test_content = f.readlines()
            assert this_page.content == test_content

    def test_notebook_add_notebook_null(self):
        test_notebook = process_notebooks.Notebook()
        test_notebook.add_notebook()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, process_notebooks.Notebook)
        assert last_item.path is None
        assert last_item.contents == []

    def test_notebook_add_notebook_no_output(self, tmp_notebook, capsys):
        process_notebooks.Notebook().add_notebook(tmp_notebook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_notebook_null_no_output(self, capsys):
        process_notebooks.Notebook().add_notebook()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_notebook_invalid_input(self, tmp_notebook):
        test_notebook = process_notebooks.Notebook()
        with pytest.raises(TypeError):
            test_notebook.add_notebook(tmp_notebook, 'extra parameter')
        with pytest.raises(AttributeError):
            test_notebook.add_notebook('string')
        with pytest.raises(AttributeError):
            test_notebook.add_notebook(3.142)
        with pytest.raises(AttributeError):
            test_notebook.add_notebook([tmp_notebook, tmp_notebook])
        with pytest.raises(OSError):
            test_notebook.add_notebook(pathlib.Path('/not/a/path'))

    def test_logbook_add_notebook_fail(self, tmp_notebook):
        test_logbook = process_notebooks.Logbook()
        test_logbook.add_notebook(tmp_notebook)
        assert isinstance(test_logbook.contents, list)
        assert tmp_notebook not in [this_item.path
                                    for this_item in test_logbook.contents]

    def test_logbook_add_notebook_null(self):
        test_logbook = process_notebooks.Logbook()
        test_logbook.add_notebook()
        assert isinstance(test_logbook.contents, list)
        assert len(test_logbook.contents) == 0

    def test_logbook_add_notebook_no_output(self, tmp_notebook, capsys):
        process_notebooks.Logbook().add_notebook(tmp_notebook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_notebook_null_no_output(self, capsys):
        process_notebooks.Logbook().add_notebook()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_logbook(self, tmp_logbook):
        test_notebook = process_notebooks.Notebook()
        test_notebook.add_logbook(tmp_logbook)
        assert isinstance(test_notebook.contents, list)
        assert tmp_logbook in [this_item.path
                                for this_item in test_notebook.contents]
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, process_notebooks.Notebook)
        assert last_item.path == tmp_logbook
        assert isinstance(last_item.contents, list)
        for filename in self.temp_logbook_pages:
            this_path = tmp_logbook.joinpath(filename)
            assert this_path in [this_page.path
                                 for this_page in last_item.contents]
        for this_page in last_item.contents:
            assert isinstance(this_page, process_notebooks.Page)
            with open(self.test_logbook_page, 'r')  as f:
                test_content = f.readlines()
            assert this_page.content == test_content

    def test_notebook_add_logbook_null(self):
        test_notebook = process_notebooks.Notebook()
        test_notebook.add_logbook()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, process_notebooks.Notebook)
        assert last_item.path is None
        assert last_item.contents == []

    def test_notebook_add_logbook_no_output(self, tmp_logbook, capsys):
        process_notebooks.Notebook().add_logbook(tmp_logbook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_logbook_null_no_output(self, capsys):
        process_notebooks.Notebook().add_logbook()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_logbook_invalid_input(self, tmp_logbook):
        test_notebook = process_notebooks.Notebook()
        with pytest.raises(TypeError):
            test_notebook.add_logbook(tmp_logbook, 'extra parameter')
        with pytest.raises(AttributeError):
            test_notebook.add_logbook('string')
        with pytest.raises(AttributeError):
            test_notebook.add_logbook(3.142)
        with pytest.raises(AttributeError):
            test_notebook.add_logbook([tmp_logbook, tmp_logbook])
        with pytest.raises(OSError):
            test_notebook.add_logbook(pathlib.Path('/not/a/path'))

    def test_logbook_add_logbook_fail(self, tmp_logbook):
        test_logbook = process_notebooks.Logbook()
        test_logbook.add_logbook(tmp_logbook)
        assert isinstance(test_logbook.contents, list)
        assert tmp_logbook not in [this_item.path
                                   for this_item in test_logbook.contents]

    def test_logbook_add_logbook_null(self):
        test_logbook = process_notebooks.Logbook()
        test_logbook.add_logbook()
        assert isinstance(test_logbook.contents, list)
        assert len(test_logbook.contents) == 0

    def test_logbook_add_logbook_no_output(self, tmp_logbook, capsys):
        process_notebooks.Logbook().add_logbook(tmp_logbook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_logbook_null_no_output(self, capsys):
        process_notebooks.Logbook().add_logbook()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_load_contents(self, tmp_notebook):
        test_notebook = process_notebooks.Notebook()
        test_notebook.path = tmp_notebook
        test_notebook.load_contents()
        for filename in self.temp_pages:
            this_path = tmp_notebook.joinpath(filename)
            assert this_path in [this_page.path
                                 for this_page in test_notebook.contents]
        for this_page in test_notebook.contents:
            assert isinstance(this_page, process_notebooks.Page)
            with open(self.test_page, 'r')  as f:
                test_content = f.readlines()
            assert this_page.content == test_content

    def test_notebook_load_contents_no_changes(self, cloned_repo):
        test_notebook = process_notebooks.Notebook()
        test_notebook.path = pathlib.Path(cloned_repo.working_dir)
        test_notebook.load_contents()
        assert self.repo_unchanged(cloned_repo)

    def test_notebook_load_contents_null(self):
        test_notebook = process_notebooks.Notebook()
        test_notebook.path = None
        test_notebook.load_contents()
        assert test_notebook.contents == []

    def test_notebook_load_contents_no_output(self, tmp_notebook, capsys):
        test_notebook = process_notebooks.Notebook()
        test_notebook.path = tmp_notebook
        test_notebook.load_contents()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_load_contents_null_no_output(self, capsys):
        process_notebooks.Notebook().load_contents()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_load_contents_invalid_input(self, tmp_logbook_page):
        test_notebook = process_notebooks.Notebook()
        with pytest.raises(TypeError):
            test_notebook.load_contents('extra parameter')

    def test_logbook_load_contents(self, tmp_logbook):
        test_logbook = process_notebooks.Logbook()
        test_logbook.path = tmp_logbook
        test_logbook.load_contents()
        for filename in self.temp_logbook_pages:
            this_path = tmp_logbook.joinpath(filename)
            assert this_path in [this_page.path
                                 for this_page in test_logbook.contents]
        for this_page in test_logbook.contents:
            assert isinstance(this_page, process_notebooks.LogbookPage)
            with open(self.test_logbook_page, 'r')  as f:
                test_content = f.readlines()
            assert this_page.content == test_content

    def test_logbook_load_contents_null(self):
        test_logbook = process_notebooks.Logbook()
        test_logbook.path = None
        test_logbook.load_contents()
        assert test_logbook.contents == []

    def test_logbook_load_contents_no_output(self, tmp_logbook, capsys):
        test_logbook = process_notebooks.Logbook()
        test_logbook.path = tmp_logbook
        test_logbook.load_contents()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_load_contents_null_no_output(self, capsys):
        process_notebooks.Logbook().load_contents()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_load_contents_invalid_input(self, tmp_logbook_page):
        test_logbook = process_notebooks.Logbook()
        with pytest.raises(TypeError):
            test_logbook.load_contents('extra parameter')


    # Getting information from notebook objects
    def test_notebook_is_valid_page(self, tmp_page):
        test_notebook = process_notebooks.Notebook()
        assert test_notebook._is_valid_page(tmp_page) is True

    def test_notebook_is_valid_page_logbook_page(self, tmp_logbook_page):
        test_notebook = process_notebooks.Notebook()
        assert test_notebook._is_valid_page(tmp_logbook_page) is True

    def test_notebook_is_valid_page_fail(self, tmp_file_factory):
        test_notebook = process_notebooks.Notebook()
        assert test_notebook._is_valid_page(
            tmp_file_factory('test.xlsx')) is False
        assert test_notebook._is_valid_page(
            tmp_file_factory('test.png')) is False
        assert test_notebook._is_valid_page(
            tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory('is-a-file.md')
        with pytest.raises(OSError):
            test_notebook._is_valid_page(
                tmp_file.parent.joinpath('not-a-file.md'))

    def test_notebook_is_valid_page_no_output(self, tmp_page, capsys):
        process_notebooks.Notebook()._is_valid_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_is_valid_page_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            process_notebooks.Notebook()._is_valid_page(tmp_page,
                                                        'extra parameter')
        with pytest.raises(AttributeError):
            process_notebooks.Notebook()._is_valid_page('string')
        with pytest.raises(AttributeError):
            process_notebooks.Notebook()._is_valid_page(3.142)
        with pytest.raises(AttributeError):
            process_notebooks.Notebook()._is_valid_page([tmp_page, tmp_page])
        with pytest.raises(OSError):
            process_notebooks.Notebook()._is_valid_page(
                pathlib.Path('/not/a/path'))

    def test_logbook_is_valid_page(self, tmp_logbook_page):
        test_logbook = process_notebooks.Logbook()
        assert test_logbook._is_valid_page(tmp_logbook_page) is True

    def test_logbook_is_valid_page_notebook_page(self, tmp_page):
        test_logbook = process_notebooks.Logbook()
        assert test_logbook._is_valid_page(tmp_page) is False

    def test_logbook_is_valid_page_fail(self, tmp_file_factory):
        test_logbook = process_notebooks.Logbook()
        assert test_logbook._is_valid_page(
            tmp_file_factory('test.xlsx')) is False
        assert test_logbook._is_valid_page(
            tmp_file_factory('test.png')) is False
        assert test_logbook._is_valid_page(
            tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory('is-a-file.md')
        with pytest.raises(OSError):
            test_logbook._is_valid_page(
                tmp_file.parent.joinpath('not-a-file.md'))

    def test_logbook_is_valid_page_no_output(self, tmp_page, capsys):
        process_notebooks.Logbook()._is_valid_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_is_valid_page_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            process_notebooks.Logbook()._is_valid_page(tmp_page,
                                                        'extra parameter')
        with pytest.raises(AttributeError):
            process_notebooks.Logbook()._is_valid_page('string')
        with pytest.raises(AttributeError):
            process_notebooks.Logbook()._is_valid_page(3.142)
        with pytest.raises(AttributeError):
            process_notebooks.Logbook()._is_valid_page([tmp_page, tmp_page])
        with pytest.raises(OSError):
            process_notebooks.Logbook()._is_valid_page(
                pathlib.Path('/not/a/path'))

    def test_notebook_is_valid_folder(self, tmp_path):
        assert process_notebooks.Notebook()._is_valid_folder(
            tmp_path) is True

    def test_notebook_is_valid_folder_notebook(self, tmp_notebook):
        assert process_notebooks.Notebook()._is_valid_folder(
            tmp_notebook) is True

    def test_notebook_is_valid_folder_logbook(self, tmp_logbook):
        assert process_notebooks.Notebook()._is_valid_folder(
            tmp_logbook) is True

    def test_notebook_is_valid_folder_fail(self, tmp_path_factory, tmp_page):
        assert process_notebooks.Notebook()._is_valid_folder(
            tmp_path_factory.mktemp('.vscode')) is False
        assert process_notebooks.Notebook()._is_valid_folder(
            tmp_path_factory.mktemp('.config')) is False

    def test_notebook_is_valid_folder_no_output(self, tmp_path, capsys):
        process_notebooks.Notebook()._is_valid_folder(tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_is_valid_folder_invalid_input(self, tmp_path, tmp_page):
        with pytest.raises(TypeError):
            process_notebooks.Notebook()._is_valid_folder()
        with pytest.raises(TypeError):
            process_notebooks.Notebook()._is_valid_folder(tmp_path,
                                                          'extra parameter')
        with pytest.raises(AttributeError):
            process_notebooks.Notebook()._is_valid_folder('string')
        with pytest.raises(AttributeError):
            process_notebooks.Notebook()._is_valid_folder(3.142)
        with pytest.raises(AttributeError):
            process_notebooks.Notebook()._is_valid_folder([tmp_path, tmp_path])
        with pytest.raises(OSError):
            process_notebooks.Notebook()._is_valid_folder(
                pathlib.Path('/not/a/path'))
        with pytest.raises(OSError):
            process_notebooks.Notebook()._is_valid_folder(tmp_page)
        with pytest.raises(OSError):
            process_notebooks.Notebook()._is_valid_folder(
                tmp_path.joinpath('not-a-path'))

    def test_logbook_is_valid_folder(self, tmp_path):
        assert process_notebooks.Logbook()._is_valid_folder(
            tmp_path) is False

    def test_logbook_is_valid_folder_notebook(self, tmp_notebook):
        assert process_notebooks.Logbook()._is_valid_folder(
            tmp_notebook) is False

    def test_logbook_is_valid_folder_logbook(self, tmp_logbook):
        assert process_notebooks.Logbook()._is_valid_folder(
            tmp_logbook) is True

    def test_logbook_is_valid_folder_fail(self, tmp_path_factory, tmp_page):
        assert process_notebooks.Logbook()._is_valid_folder(
            tmp_path_factory.mktemp('.vscode')) is False
        assert process_notebooks.Logbook()._is_valid_folder(
            tmp_path_factory.mktemp('.config')) is False

    def test_logbook_is_valid_folder_no_output(self, tmp_path, capsys):
        process_notebooks.Logbook()._is_valid_folder(tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_is_valid_folder_invalid_input(self, tmp_path, tmp_page):
        with pytest.raises(TypeError):
            process_notebooks.Logbook()._is_valid_folder()
        with pytest.raises(TypeError):
            process_notebooks.Logbook()._is_valid_folder(tmp_path,
                                                          'extra parameter')
        with pytest.raises(AttributeError):
            process_notebooks.Logbook()._is_valid_folder('string')
        with pytest.raises(AttributeError):
            process_notebooks.Logbook()._is_valid_folder(3.142)
        with pytest.raises(AttributeError):
            process_notebooks.Logbook()._is_valid_folder([tmp_path, tmp_path])
        with pytest.raises(OSError):
            process_notebooks.Logbook()._is_valid_folder(
                pathlib.Path('/not/a/path'))
        with pytest.raises(OSError):
            process_notebooks.Logbook()._is_valid_folder(tmp_page)
        with pytest.raises(OSError):
            process_notebooks.Logbook()._is_valid_folder(
                tmp_path.joinpath('not-a-path'))


    # Utility functions
    def test_is_valid_page(self, tmp_page):
        assert process_notebooks._is_valid_page(tmp_page) is True

    def test_is_valid_page_logbook_page(self, tmp_logbook_page):
        assert process_notebooks._is_valid_page(tmp_logbook_page) is True

    def test_is_valid_page_fail(self, tmp_file_factory):
        assert process_notebooks._is_valid_page(
            tmp_file_factory('test.xlsx')) is False
        assert process_notebooks._is_valid_page(
            tmp_file_factory('test.png')) is False
        assert process_notebooks._is_valid_page(
            tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory('is-a-file.md')
        with pytest.raises(OSError):
            process_notebooks._is_valid_page(
                tmp_file.parent.joinpath('not-a-file.md'))

    def test_is_valid_page_no_output(self, tmp_page, capsys):
        process_notebooks._is_valid_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_is_valid_page_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            process_notebooks._is_valid_page(tmp_page, 'extra parameter')
        with pytest.raises(AttributeError):
            process_notebooks._is_valid_page('string')
        with pytest.raises(AttributeError):
            process_notebooks._is_valid_page(3.142)
        with pytest.raises(AttributeError):
            process_notebooks._is_valid_page([tmp_page, tmp_page])
        with pytest.raises(OSError):
            process_notebooks._is_valid_page(pathlib.Path('/not/a/path'))

    def test_is_valid_logbook_page(self, tmp_logbook_page):
        assert process_notebooks._is_valid_logbook_page(
            tmp_logbook_page) is True

    def test_is_valid_logbook_page_notebook_page(self, tmp_page):
        assert process_notebooks._is_valid_logbook_page(
            tmp_page) is False

    def test_is_valid_logbook_page_fail(self, tmp_file_factory):
        assert process_notebooks._is_valid_logbook_page(
            tmp_file_factory('test.xlsx')) is False
        assert process_notebooks._is_valid_logbook_page(
            tmp_file_factory('test.png')) is False
        assert process_notebooks._is_valid_logbook_page(
            tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory('is-a-file.md')
        with pytest.raises(OSError):
            process_notebooks._is_valid_logbook_page(
                tmp_file.parent.joinpath('not-a-file.md'))
        assert process_notebooks._is_valid_logbook_page(
            tmp_file_factory('2020-01-01-Meeting.md')) is False
        assert process_notebooks._is_valid_logbook_page(
            tmp_file_factory('page1.md')) is False

    def test_is_valid_logbook_page_no_output(self, tmp_logbook_page, capsys):
        process_notebooks._is_valid_logbook_page(tmp_logbook_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_is_valid_logbook_page_invalid_input(self, tmp_logbook_page):
        with pytest.raises(TypeError):
            process_notebooks._is_valid_logbook_page(tmp_logbook_page,
                                                     'extra parameter')
        with pytest.raises(AttributeError):
            process_notebooks._is_valid_logbook_page('string')
        with pytest.raises(AttributeError):
            process_notebooks._is_valid_logbook_page(3.142)
        with pytest.raises(AttributeError):
            process_notebooks._is_valid_logbook_page([tmp_logbook_page,
                                                      tmp_logbook_page])
        with pytest.raises(OSError):
            process_notebooks._is_valid_logbook_page(
                pathlib.Path('/not/a/path'))

    def test_is_valid_folder(self, tmp_path):
        assert process_notebooks._is_valid_folder(tmp_path) is True

    def test_is_valid_folder_notebook(self, tmp_notebook):
        assert process_notebooks._is_valid_folder(tmp_notebook) is True

    def test_is_valid_folder_logbook(self, tmp_logbook):
        assert process_notebooks._is_valid_folder(tmp_logbook) is True

    def test_is_valid_folder_fail(self, tmp_path_factory, tmp_page):
        assert process_notebooks._is_valid_folder(
            tmp_path_factory.mktemp('.vscode')) is False
        assert process_notebooks._is_valid_folder(
            tmp_path_factory.mktemp('.config')) is False

    def test_is_valid_folder_no_output(self, tmp_path, capsys):
        process_notebooks._is_valid_folder(tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_is_valid_folder_invalid_input(self, tmp_path, tmp_page):
        with pytest.raises(TypeError):
            process_notebooks._is_valid_folder()
        with pytest.raises(TypeError):
            process_notebooks._is_valid_folder(tmp_path, 'extra parameter')
        with pytest.raises(AttributeError):
            process_notebooks._is_valid_folder('string')
        with pytest.raises(AttributeError):
            process_notebooks._is_valid_folder(3.142)
        with pytest.raises(AttributeError):
            process_notebooks._is_valid_folder([tmp_path, tmp_path])
        with pytest.raises(OSError):
            process_notebooks._is_valid_folder(pathlib.Path('/not/a/path'))
        with pytest.raises(OSError):
            process_notebooks._is_valid_folder(tmp_page)
        with pytest.raises(OSError):
            process_notebooks._is_valid_folder(tmp_path.joinpath('not-a-path'))

    def test_is_valid_logbook_folder(self, tmp_path):
        assert process_notebooks._is_valid_logbook_folder(tmp_path) is False

    def test_is_valid_logbook_folder_notebook(self, tmp_notebook):
        assert process_notebooks._is_valid_logbook_folder(tmp_notebook) is False

    def test_is_valid_logbook_folder_logbook(self, tmp_logbook):
        assert process_notebooks._is_valid_logbook_folder(tmp_logbook) is True

    def test_is_valid_logbook_folder_fail(self, tmp_path_factory, tmp_page):
        assert process_notebooks._is_valid_logbook_folder(
            tmp_path_factory.mktemp('.vscode')) is False
        assert process_notebooks._is_valid_logbook_folder(
            tmp_path_factory.mktemp('.config')) is False

    def test_is_valid_logbook_folder_no_output(self, tmp_path, capsys):
        process_notebooks._is_valid_logbook_folder(tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_is_valid_logbook_folder_invalid_input(self, tmp_path, tmp_page):
        with pytest.raises(TypeError):
            process_notebooks._is_valid_logbook_folder()
        with pytest.raises(TypeError):
            process_notebooks._is_valid_logbook_folder(tmp_path, 'extra parameter')
        with pytest.raises(AttributeError):
            process_notebooks._is_valid_logbook_folder('string')
        with pytest.raises(AttributeError):
            process_notebooks._is_valid_logbook_folder(3.142)
        with pytest.raises(AttributeError):
            process_notebooks._is_valid_logbook_folder([tmp_path, tmp_path])
        with pytest.raises(OSError):
            process_notebooks._is_valid_logbook_folder(pathlib.Path('/not/a/path'))
        with pytest.raises(OSError):
            process_notebooks._is_valid_logbook_folder(tmp_page)
        with pytest.raises(OSError):
            process_notebooks._is_valid_logbook_folder(tmp_path.joinpath('not-a-path'))

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
