# Tests process_notebooks.py

import pytest
import pathlib
import git
import shutil

import process_notebooks as pn

class TestProcessNotebooks:

    # Setup before testing
    def setup_class(self):
        """Settings and variables shared for all tests."""
        self.notebook_path = (pathlib.Path.home()
                              .joinpath('OneDrive/Documents/Notebooks'))
        self.test_page = (pathlib.Path(__file__).parent
                          .joinpath('data/notebook_page.md'))
        self.test_logbook_page = (pathlib.Path(__file__).parent
                                  .joinpath('data/logbook_page.md'))
        self.test_home_page = (pathlib.Path(__file__).parent
                               .joinpath('data/homepage.md'))
        self.test_contents_page = (pathlib.Path(__file__).parent
                                   .joinpath('data/notebook_contents.md'))
        self.test_logbook_contents_page = (pathlib.Path(__file__).parent
                                           .joinpath('data/logbook_contents.md'))
        self.test_logbook_month_page = (pathlib.Path(__file__).parent
                                        .joinpath('data/logbook_month.md'))
        self.test_readme_page = (pathlib.Path(__file__).parent
                                 .joinpath('data/notebook_readme.md'))
        self.test_logbook_readme_page = (pathlib.Path(__file__).parent
                                         .joinpath('data/logbook_readme.md'))
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
        self.page_suffix = '.md'
        self.homepage_descriptor = 'Home'
        self.homepage_filename = 'Home'
        self.contents_descriptor = 'Contents'
        self.contents_filename = 'Contents'
        self.readme_filename = 'Readme'
        self.readme_descriptor = 'Readme'
        self.logbook_folder_name = 'Logbook'
        self.unknown_descriptor = 'Unknown'


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
        tempfile = tmp_path.joinpath(f'{self.temp_page}{self.page_suffix}')
        shutil.copyfile(self.test_page, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_logbook_page(self, tmp_path):
        """Create a new logbook page in a temp folder and return its path."""
        tempfile = tmp_path.joinpath(f'{self.temp_logbook_page}'
                                     f'{self.page_suffix}')
        shutil.copyfile(self.test_logbook_page, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_contents_page(self, tmp_path):
        """Create a new contents page in a temp folder and return its path."""
        tempfile = tmp_path.joinpath(f'{self.contents_filename}'
                                     f'{self.page_suffix}')
        shutil.copyfile(self.test_page, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_home_page(self, tmp_path):
        """Create a new home page in a temp folder and return its path."""
        tempfile = tmp_path.joinpath(f'{self.homepage_filename}'
                                     f'{self.page_suffix}')
        shutil.copyfile(self.test_page, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_readme_page(self, tmp_path):
        """Create a new readme page in a temp folder and return its path."""
        tempfile = tmp_path.joinpath(f'{self.readme_filename}'
                                     f'{self.page_suffix}')
        shutil.copyfile(self.test_page, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_notebook(self, tmp_path):
        """Create a temporary notebook folder and add some pages."""
        notebook_folder = tmp_path.joinpath(self.temp_notebook)
        self.create_and_fill_folder(
            notebook_folder,
            self.temp_pages,
            self.test_page,
            contents_page=self.test_contents_page,
            readme_page=self.test_readme_page)
        yield notebook_folder
        shutil.rmtree(notebook_folder)

    @pytest.fixture
    def tmp_logbook(self, tmp_path):
        """Create a temporary logbook folder and add some pages."""
        logbook_folder = tmp_path.joinpath(self.temp_logbook)
        self.create_and_fill_folder(
            logbook_folder,
            self.temp_logbook_pages,
            self.test_logbook_page,
            contents_page=self.test_logbook_contents_page,
            readme_page=self.test_logbook_readme_page)
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
    def create_and_fill_folder(
            self, folder_path, file_list, file_template,
            home_page=None, contents_page=None, readme_page=None):
        folder_path.mkdir()
        for filename in file_list:
            new_file = folder_path.joinpath(filename)
            shutil.copyfile(file_template, new_file)
        if home_page is not None:
            new_file = folder_path.joinpath(f'{self.homepage_filename}'
                                            f'{self.page_suffix}')
            shutil.copyfile(home_page, new_file)
        if contents_page is not None:
            new_file = folder_path.joinpath(f'{self.contents_filename}'
                                            f'{self.page_suffix}')
            shutil.copyfile(contents_page, new_file)
        if readme_page is not None:
            new_file = folder_path.joinpath(f'{self.readme_filename}'
                                            f'{self.page_suffix}')
            shutil.copyfile(readme_page, new_file)

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


    # Constants
    def test_constant_contents_filename(self):
        assert pn.PAGE_SUFFIX == self.page_suffix
        assert pn.HOME_DESCRIPTOR == self.homepage_descriptor
        assert pn.HOMEPAGE_FILENAME == self.homepage_filename
        assert pn.CONTENTS_DESCRIPTOR == self.contents_descriptor
        assert pn.CONTENTS_FILENAME == self.contents_filename
        assert pn.README_DESCRIPTOR == self.readme_descriptor
        assert pn.README_FILENAME == self.readme_filename
        assert pn.LOGBOOK_FOLDER_NAME == self.logbook_folder_name
        assert pn.UNKNOWN_DESCRIPTOR == self.unknown_descriptor


    # Creating page objects
    def test_create_page(self, tmp_page):
        test_page = pn.Page(tmp_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert isinstance(test_page.content, list)
        assert test_page.path == tmp_page
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def test_create_page_null(self):
        test_page = pn.Page()
        assert test_page.path is None
        assert test_page.content is None

    def test_create_page_no_output(self, tmp_page, capsys):
        pn.Page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_create_page_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            pn.Page(tmp_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.Page('string')
        with pytest.raises(AttributeError):
            pn.Page(3.142)
        with pytest.raises(AttributeError):
            pn.Page([tmp_page, tmp_page])

    def test_create_page_invalid_file_types(self, tmp_file_factory):
        with pytest.raises(ValueError):
            pn.Page(tmp_file_factory('test.xlsx'))
        with pytest.raises(ValueError):
            pn.Page(tmp_file_factory('test.png'))
        with pytest.raises(ValueError):
            pn.Page(tmp_file_factory('.DS_Store'))

    def test_create_logbook_page(self, tmp_logbook_page):
        test_page = pn.LogbookPage(tmp_logbook_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert isinstance(test_page.content, list)
        assert test_page.path == tmp_logbook_page
        with open(self.test_logbook_page, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def test_create_logbook_page_null(self):
        test_page = pn.LogbookPage()
        assert test_page.path is None
        assert test_page.content is None

    def test_create_logbook_page_no_output(self, tmp_logbook_page, capsys):
        pn.LogbookPage(tmp_logbook_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_create_logbook_page_invalid_input(self, tmp_logbook_page):
        with pytest.raises(TypeError):
            pn.LogbookPage(tmp_logbook_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.LogbookPage('string')
        with pytest.raises(AttributeError):
            pn.LogbookPage(3.142)
        with pytest.raises(AttributeError):
            pn.LogbookPage([tmp_logbook_page, tmp_logbook_page])
        with pytest.raises(OSError):
            pn.LogbookPage(pathlib.Path('/not/a/path'))

    def test_create_logbook_page_invalid_file_types(self, tmp_file_factory):
        with pytest.raises(ValueError):
            pn.LogbookPage(tmp_file_factory('test.xlsx'))
        with pytest.raises(ValueError):
            pn.LogbookPage(tmp_file_factory('test.png'))
        with pytest.raises(ValueError):
            pn.LogbookPage(tmp_file_factory('.DS_Store'))

    def test_create_contents_page(self, tmp_contents_page):
        test_page = pn.ContentsPage(tmp_contents_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert isinstance(test_page.content, list)
        assert test_page.path == tmp_contents_page
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def test_create_contents_page_null(self):
        test_page = pn.ContentsPage()
        assert test_page.path is None
        assert test_page.content is None

    def test_create_contents_page_no_output(self, tmp_contents_page, capsys):
        pn.ContentsPage(tmp_contents_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_create_contents_page_invalid_input(self, tmp_contents_page):
        with pytest.raises(TypeError):
            pn.ContentsPage(tmp_contents_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.ContentsPage('string')
        with pytest.raises(AttributeError):
            pn.ContentsPage(3.142)
        with pytest.raises(AttributeError):
            pn.ContentsPage([tmp_contents_page, tmp_contents_page])

    def test_create_contents_page_invalid_filename(self, tmp_page):
        with pytest.raises(ValueError):
            pn.ContentsPage(tmp_page)

    def test_create_contents_page_invalid_file_types(self, tmp_file_factory):
        with pytest.raises(ValueError):
            pn.ContentsPage(tmp_file_factory('test.xlsx'))
        with pytest.raises(ValueError):
            pn.ContentsPage(tmp_file_factory('test.png'))
        with pytest.raises(ValueError):
            pn.ContentsPage(tmp_file_factory('.DS_Store'))

    def test_create_home_page(self, tmp_home_page):
        test_page = pn.HomePage(tmp_home_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert isinstance(test_page.content, list)
        assert test_page.path == tmp_home_page
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def test_create_home_page_null(self):
        test_page = pn.HomePage()
        assert test_page.path is None
        assert test_page.content is None

    def test_create_home_page_no_output(self, tmp_home_page, capsys):
        pn.HomePage(tmp_home_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_create_home_page_invalid_input(self, tmp_home_page):
        with pytest.raises(TypeError):
            pn.HomePage(tmp_home_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.HomePage('string')
        with pytest.raises(AttributeError):
            pn.HomePage(3.142)
        with pytest.raises(AttributeError):
            pn.HomePage([tmp_home_page, tmp_home_page])

    def test_create_home_page_invalid_filename(self, tmp_page):
        with pytest.raises(ValueError):
            pn.HomePage(tmp_page)

    def test_create_home_page_invalid_file_types(self, tmp_file_factory):
        with pytest.raises(ValueError):
            pn.HomePage(tmp_file_factory('test.xlsx'))
        with pytest.raises(ValueError):
            pn.HomePage(tmp_file_factory('test.png'))
        with pytest.raises(ValueError):
            pn.HomePage(tmp_file_factory('.DS_Store'))

    def test_create_readme_page(self, tmp_readme_page):
        test_page = pn.ReadmePage(tmp_readme_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert isinstance(test_page.content, list)
        assert test_page.path == tmp_readme_page
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def test_create_readme_page_null(self):
        test_page = pn.ReadmePage()
        assert test_page.path is None
        assert test_page.content is None

    def test_create_readme_page_no_output(self, tmp_readme_page, capsys):
        pn.ReadmePage(tmp_readme_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_create_readme_page_invalid_input(self, tmp_readme_page):
        with pytest.raises(TypeError):
            pn.ReadmePage(tmp_readme_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.ReadmePage('string')
        with pytest.raises(AttributeError):
            pn.ReadmePage(3.142)
        with pytest.raises(AttributeError):
            pn.ReadmePage([tmp_readme_page, tmp_readme_page])

    def test_create_readme_page_invalid_filename(self, tmp_page):
        with pytest.raises(ValueError):
            pn.ReadmePage(tmp_page)

    def test_create_readme_page_invalid_file_types(self, tmp_file_factory):
        with pytest.raises(ValueError):
            pn.ReadmePage(tmp_file_factory('test.xlsx'))
        with pytest.raises(ValueError):
            pn.ReadmePage(tmp_file_factory('test.png'))
        with pytest.raises(ValueError):
            pn.ReadmePage(tmp_file_factory('.DS_Store'))


    # Loading data to page objects
    def test_page_load_content(self, tmp_page):
        test_page = pn.Page()
        test_page.path = tmp_page
        test_page.load_content()
        assert isinstance(test_page.content, list)
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def test_page_load_content_null(self):
        test_page = pn.Page()
        test_page.path = None
        test_page.load_content()
        assert test_page.content is None

    def test_page_load_content_no_output(self, tmp_page, capsys):
        test_page = pn.Page()
        test_page.path = tmp_page
        test_page.load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_page_load_content_null_no_output(self, capsys):
        pn.Page().load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_page_load_content_invalid_input(self, tmp_page):
        test_page = pn.Page()
        with pytest.raises(TypeError):
            test_page.load_content('extra parameter')

    def test_page_load_content_invalid_file_types(self, tmp_file_factory):
        test_page = pn.Page()
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
        test_logbook_page = pn.LogbookPage()
        test_logbook_page.path = tmp_logbook_page
        test_logbook_page.load_content()
        assert isinstance(test_logbook_page.content, list)
        with open(self.test_logbook_page, 'r')  as f:
            test_content = f.readlines()
        assert test_logbook_page.content == test_content

    def test_logbook_page_load_content_null(self):
        test_logbook_page = pn.LogbookPage()
        test_logbook_page.path = None
        test_logbook_page.load_content()
        assert test_logbook_page.content is None

    def test_logbook_page_load_content_no_output(self, capsys):
        pn.LogbookPage().load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_page_load_content_null_no_output(
            self, tmp_logbook_page, capsys):
        test_logbook_page = pn.LogbookPage()
        test_logbook_page.path = tmp_logbook_page
        test_logbook_page.load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_page_load_content_invalid_input(self, tmp_logbook_page):
        test_logbook_page = pn.LogbookPage()
        with pytest.raises(TypeError):
            test_logbook_page.load_content('extra parameter')

    def test_logbook_page_load_content_invalid_file_types(self, tmp_path):
        test_page = pn.LogbookPage()
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
        temp_file = tmp_path.joinpath(f'2020-01-01-Meeting{self.page_suffix}')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        test_page.path = temp_file
        with pytest.raises(ValueError):
            test_page.load_content()

    def test_contents_page_load_content(self, tmp_contents_page):
        test_page = pn.ContentsPage()
        test_page.path = tmp_contents_page
        test_page.load_content()
        assert isinstance(test_page.path, pathlib.Path)
        assert isinstance(test_page.content, list)
        assert test_page.path == tmp_contents_page
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def test_contents_page_load_content_null(self):
        test_page = pn.ContentsPage()
        test_page.path = None
        test_page.load_content()
        assert test_page.path is None
        assert test_page.content is None

    def test_contents_page_load_content_no_output(
            self, tmp_contents_page, capsys):
        test_page = pn.ContentsPage()
        test_page.path = tmp_contents_page
        test_page.load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_contents_page_load_content_invalid_input(self, tmp_contents_page):
        test_page = pn.ContentsPage()
        test_page.path = tmp_contents_page
        with pytest.raises(TypeError):
            test_page.load_content('extra parameter')

    def test_contents_page_load_content_invalid_filename(self, tmp_page):
        test_page = pn.ContentsPage()
        test_page.path = tmp_page
        with pytest.raises(ValueError):
            test_page.load_content()

    def test_contents_page_load_content_invalid_file_types(
            self, tmp_file_factory):
        test_page = pn.ContentsPage()
        with pytest.raises(ValueError):
            test_page.path = tmp_file_factory('test.xlsx')
            test_page.load_content()
        with pytest.raises(ValueError):
            test_page.path = tmp_file_factory('test.png')
            test_page.load_content()
        with pytest.raises(ValueError):
            test_page.path = tmp_file_factory('.DS_Store')
            test_page.load_content()

    def test_home_page_load_content(self, tmp_home_page):
        test_page = pn.HomePage()
        test_page.path = tmp_home_page
        test_page.load_content()
        assert isinstance(test_page.path, pathlib.Path)
        assert isinstance(test_page.content, list)
        assert test_page.path == tmp_home_page
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def test_home_page_load_content_null(self):
        test_page = pn.HomePage()
        test_page.path = None
        test_page.load_content()
        assert test_page.path is None
        assert test_page.content is None

    def test_home_page_load_content_no_output(self, tmp_home_page, capsys):
        test_page = pn.HomePage()
        test_page.path = tmp_home_page
        test_page.load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_home_page_load_content_invalid_input(self, tmp_home_page):
        test_page = pn.HomePage()
        test_page.path = tmp_home_page
        with pytest.raises(TypeError):
            test_page.load_content('extra parameter')

    def test_home_page_load_content_invalid_filename(self, tmp_page):
        test_page = pn.HomePage()
        test_page.path = tmp_page
        with pytest.raises(ValueError):
            test_page.load_content()

    def test_home_page_load_content_invalid_file_types(self, tmp_file_factory):
        test_page = pn.HomePage()
        with pytest.raises(ValueError):
            test_page.path = tmp_file_factory('test.xlsx')
            test_page.load_content()
        with pytest.raises(ValueError):
            test_page.path = tmp_file_factory('test.png')
            test_page.load_content()
        with pytest.raises(ValueError):
            test_page.path = tmp_file_factory('.DS_Store')
            test_page.load_content()

    def test_readme_page_load_content(self, tmp_readme_page):
        test_page = pn.ReadmePage()
        test_page.path = tmp_readme_page
        test_page.load_content()
        assert isinstance(test_page.path, pathlib.Path)
        assert isinstance(test_page.content, list)
        assert test_page.path == tmp_readme_page
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def test_readme_page_load_content_null(self):
        test_page = pn.ReadmePage()
        test_page.path = None
        test_page.load_content()
        assert test_page.path is None
        assert test_page.content is None

    def test_readme_page_load_content_no_output(self, tmp_readme_page, capsys):
        test_page = pn.ReadmePage()
        test_page.path = tmp_readme_page
        test_page.load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_readme_page_load_content_invalid_input(self, tmp_readme_page):
        test_page = pn.ReadmePage()
        test_page.path = tmp_readme_page
        with pytest.raises(TypeError):
            test_page.load_content('extra parameter')

    def test_readme_page_load_content_invalid_filename(self, tmp_page):
        test_page = pn.ReadmePage()
        test_page.path = tmp_page
        with pytest.raises(ValueError):
            test_page.load_content()

    def test_readme_page_load_content_invalid_file_types(
            self, tmp_file_factory):
        test_page = pn.ReadmePage()
        with pytest.raises(ValueError):
            test_page.path = tmp_file_factory('test.xlsx')
            test_page.load_content()
        with pytest.raises(ValueError):
            test_page.path = tmp_file_factory('test.png')
            test_page.load_content()
        with pytest.raises(ValueError):
            test_page.path = tmp_file_factory('.DS_Store')
            test_page.load_content()


    # Getting information from page objects
    def test_page_get_title(self, tmp_page):
        test_title = pn.Page(tmp_page).get_title()
        assert isinstance(test_title, str)
        assert test_title == self.test_title

    def test_page_get_title_null(self, tmp_page):
        test_title = pn.Page().get_title()
        assert test_title is None

    def test_page_get_title_no_output(self, tmp_page, capsys):
        pn.Page(tmp_page).get_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_page_get_title_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            pn.Page(tmp_page).get_title('extra parameter')

    def test_logbook_page_get_title(self, tmp_logbook_page):
        test_title = pn.LogbookPage(tmp_logbook_page).get_title()
        assert isinstance(test_title, str)
        assert test_title == self.temp_logbook_page.strip()

    def test_logbook_page_get_title_null(self):
        test_title = pn.LogbookPage().get_title()
        assert test_title is None

    def test_logbook_page_get_title_no_output(self, tmp_logbook_page, capsys):
        pn.LogbookPage(tmp_logbook_page).get_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_page_get_title_invalid_input(self, tmp_logbook_page):
        with pytest.raises(TypeError):
            pn.LogbookPage(tmp_logbook_page).get_title('extra parameter')

    def test_contents_page_get_title(self, tmp_contents_page):
        test_title = pn.ContentsPage(tmp_contents_page).get_title()
        assert isinstance(test_title, str)
        assert test_title == self.contents_filename

    def test_contents_page_get_title_null(self):
        test_title = pn.ContentsPage().get_title()
        assert test_title == self.contents_filename

    def test_contents_page_get_title_no_output(self, tmp_contents_page, capsys):
        pn.ContentsPage(tmp_contents_page).get_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_contents_page_get_title_invalid_input(self, tmp_contents_page):
        with pytest.raises(TypeError):
            pn.ContentsPage(tmp_contents_page).get_title('extra parameter')

    def test_home_page_get_title(self, tmp_home_page):
        test_title = pn.HomePage(tmp_home_page).get_title()
        assert isinstance(test_title, str)
        assert test_title == self.homepage_filename

    def test_home_page_get_title_null(self):
        test_title = pn.HomePage().get_title()
        assert test_title == self.homepage_filename

    def test_home_page_get_title_no_output(self, tmp_home_page, capsys):
        pn.HomePage(tmp_home_page).get_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_home_page_get_title_invalid_input(self, tmp_home_page):
        with pytest.raises(TypeError):
            pn.HomePage(tmp_home_page).get_title('extra parameter')

    def test_readme_page_get_title(self, tmp_readme_page):
        test_title = pn.ReadmePage(tmp_readme_page).get_title()
        assert isinstance(test_title, str)
        assert test_title == self.readme_filename

    def test_readme_page_get_title_null(self):
        test_title = pn.ReadmePage().get_title()
        assert test_title == self.readme_filename

    def test_readme_page_get_title_no_output(self, tmp_readme_page, capsys):
        pn.ReadmePage(tmp_readme_page).get_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_readme_page_get_title_invalid_input(self, tmp_readme_page):
        with pytest.raises(TypeError):
            pn.ReadmePage(tmp_readme_page).get_title('extra parameter')

    def test_page_is_valid_page(self, tmp_page):
        test_page = pn.Page()
        assert test_page._is_valid_page(tmp_page) is True

    def test_page_is_valid_page_logbook_page(self, tmp_logbook_page):
        test_page = pn.Page()
        assert test_page._is_valid_page(tmp_logbook_page) is True

    def test_page_is_valid_page_contents_page(self, tmp_contents_page):
        test_page = pn.Page()
        assert test_page._is_valid_page(tmp_contents_page) is True

    def test_page_is_valid_page_home_page(self, tmp_home_page):
        test_page = pn.Page()
        assert test_page._is_valid_page(tmp_home_page) is True

    def test_page_is_valid_page_readme_page(self, tmp_readme_page):
        test_page = pn.Page()
        assert test_page._is_valid_page(tmp_readme_page) is True

    def test_page_is_valid_page_fail(self, tmp_file_factory):
        test_page = pn.Page()
        assert test_page._is_valid_page(tmp_file_factory('test.xlsx')) is False
        assert test_page._is_valid_page(tmp_file_factory('test.png')) is False
        assert test_page._is_valid_page(tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            test_page._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))

    def test_page_is_valid_page_no_output(self, tmp_page, capsys):
        pn.Page()._is_valid_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_page_is_valid_page_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            pn.Page()._is_valid_page(tmp_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.Page()._is_valid_page('string')
        with pytest.raises(AttributeError):
            pn.Page()._is_valid_page(3.142)
        with pytest.raises(AttributeError):
            pn.Page()._is_valid_page([tmp_page, tmp_page])
        with pytest.raises(OSError):
            pn.Page()._is_valid_page(pathlib.Path('/not/a/path'))

    def test_logbook_page_is_valid_page(self, tmp_logbook_page):
        test_page = pn.LogbookPage()
        assert test_page._is_valid_page(tmp_logbook_page) is True

    def test_logbook_page_is_valid_page_notebook_page(self, tmp_page):
        test_page = pn.LogbookPage()
        assert test_page._is_valid_page(tmp_page) is False

    def test_logbook_page_is_valid_page_logbook_page(self, tmp_logbook_page):
        test_page = pn.LogbookPage()
        assert test_page._is_valid_page(tmp_logbook_page) is True

    def test_logbook_page_is_valid_page_contents_page(self, tmp_contents_page):
        test_page = pn.LogbookPage()
        assert test_page._is_valid_page(tmp_contents_page) is False

    def test_logbook_page_is_valid_page_home_page(self, tmp_home_page):
        test_page = pn.LogbookPage()
        assert test_page._is_valid_page(tmp_home_page) is False

    def test_logbook_page_is_valid_page_readme_page(self, tmp_readme_page):
        test_page = pn.LogbookPage()
        assert test_page._is_valid_page(tmp_readme_page) is False

    def test_logbook_page_is_valid_page_fail(self, tmp_file_factory):
        test_page = pn.LogbookPage()
        assert test_page._is_valid_page(tmp_file_factory('test.xlsx')) is False
        assert test_page._is_valid_page(tmp_file_factory('test.png')) is False
        assert test_page._is_valid_page(tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory('is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            test_page._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))
        assert test_page._is_valid_page(
            tmp_file_factory(f'2020-01-01-Meeting{self.page_suffix}')) is False
        assert test_page._is_valid_page(
            tmp_file_factory(f'page1{self.page_suffix}')) is False

    def test_logbook_page_is_valid_page_no_output(
            self, tmp_logbook_page, capsys):
        pn.LogbookPage()._is_valid_page(tmp_logbook_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_page_is_valid_page_invalid_input(self, tmp_logbook_page):
        with pytest.raises(TypeError):
            pn.LogbookPage()._is_valid_page(tmp_logbook_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.LogbookPage()._is_valid_page('string')
        with pytest.raises(AttributeError):
            pn.LogbookPage()._is_valid_page(3.142)
        with pytest.raises(AttributeError):
            pn.LogbookPage()._is_valid_page([tmp_logbook_page, tmp_logbook_page])
        with pytest.raises(OSError):
            pn.LogbookPage()._is_valid_page(
                pathlib.Path('/not/a/path'))

    def test_contents_page_is_valid_page(self, tmp_contents_page):
        test_page = pn.ContentsPage()
        assert test_page._is_valid_page(tmp_contents_page) is True

    def test_contents_page_is_valid_page_notebook_page(self, tmp_page):
        test_page = pn.ContentsPage()
        assert test_page._is_valid_page(tmp_page) is False

    def test_contents_page_is_valid_page_logbook_page(self, tmp_logbook_page):
        test_page = pn.ContentsPage()
        assert test_page._is_valid_page(tmp_logbook_page) is False

    def test_contents_page_is_valid_page_contents_page(self, tmp_contents_page):
        test_page = pn.ContentsPage()
        assert test_page._is_valid_page(tmp_contents_page) is True

    def test_contents_page_is_valid_page_home_page(self, tmp_home_page):
        test_page = pn.ContentsPage()
        assert test_page._is_valid_page(tmp_home_page) is False

    def test_contents_page_is_valid_page_readme_page(self, tmp_readme_page):
        test_page = pn.ContentsPage()
        assert test_page._is_valid_page(tmp_readme_page) is False

    def test_contents_page_is_valid_page_fail(self, tmp_file_factory):
        test_page = pn.ContentsPage()
        assert test_page._is_valid_page(tmp_file_factory('test.xlsx')) is False
        assert test_page._is_valid_page(tmp_file_factory('test.png')) is False
        assert test_page._is_valid_page(tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            test_page._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))

    def test_contents_page_is_valid_page_no_output(
            self, tmp_contents_page, capsys):
        pn.ContentsPage()._is_valid_page(tmp_contents_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_contents_page_is_valid_page_invalid_input(self, tmp_contents_page):
        with pytest.raises(TypeError):
            pn.ContentsPage()._is_valid_page(tmp_contents_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.ContentsPage()._is_valid_page('string')
        with pytest.raises(AttributeError):
            pn.ContentsPage()._is_valid_page(3.142)
        with pytest.raises(AttributeError):
            pn.ContentsPage()._is_valid_page(
                [tmp_contents_page, tmp_contents_page])
        with pytest.raises(OSError):
            pn.ContentsPage()._is_valid_page(pathlib.Path('/not/a/path'))

    def test_home_page_is_valid_page(self, tmp_home_page):
        test_page = pn.HomePage()
        assert test_page._is_valid_page(tmp_home_page) is True

    def test_home_page_is_valid_page_notebook_page(self, tmp_page):
        test_page = pn.HomePage()
        assert test_page._is_valid_page(tmp_page) is False

    def test_home_page_is_valid_page_logbook_page(self, tmp_logbook_page):
        test_page = pn.HomePage()
        assert test_page._is_valid_page(tmp_logbook_page) is False

    def test_home_page_is_valid_page_contents_page(self, tmp_contents_page):
        test_page = pn.HomePage()
        assert test_page._is_valid_page(tmp_contents_page) is False

    def test_home_page_is_valid_page_home_page(self, tmp_home_page):
        test_page = pn.HomePage()
        assert test_page._is_valid_page(tmp_home_page) is True

    def test_home_page_is_valid_page_readme_page(self, tmp_readme_page):
        test_page = pn.HomePage()
        assert test_page._is_valid_page(tmp_readme_page) is False

    def test_home_page_is_valid_page_fail(self, tmp_file_factory):
        test_page = pn.HomePage()
        assert test_page._is_valid_page(tmp_file_factory('test.xlsx')) is False
        assert test_page._is_valid_page(tmp_file_factory('test.png')) is False
        assert test_page._is_valid_page(tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            test_page._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))

    def test_home_page_is_valid_page_no_output(self, tmp_home_page, capsys):
        pn.HomePage()._is_valid_page(tmp_home_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_home_page_is_valid_page_invalid_input(self, tmp_home_page):
        with pytest.raises(TypeError):
            pn.HomePage()._is_valid_page(tmp_home_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.HomePage()._is_valid_page('string')
        with pytest.raises(AttributeError):
            pn.HomePage()._is_valid_page(3.142)
        with pytest.raises(AttributeError):
            pn.HomePage()._is_valid_page([tmp_home_page, tmp_home_page])
        with pytest.raises(OSError):
            pn.HomePage()._is_valid_page(pathlib.Path('/not/a/path'))

    def test_readme_page_is_valid_page(self, tmp_readme_page):
        test_page = pn.ReadmePage()
        assert test_page._is_valid_page(tmp_readme_page) is True

    def test_readme_page_is_valid_page_notebook_page(self, tmp_page):
        test_page = pn.ReadmePage()
        assert test_page._is_valid_page(tmp_page) is False

    def test_readme_page_is_valid_page_logbook_page(self, tmp_logbook_page):
        test_page = pn.ReadmePage()
        assert test_page._is_valid_page(tmp_logbook_page) is False

    def test_readme_page_is_valid_page_contents_page(self, tmp_contents_page):
        test_page = pn.ReadmePage()
        assert test_page._is_valid_page(tmp_contents_page) is False

    def test_readme_page_is_valid_page_home_page(self, tmp_home_page):
        test_page = pn.ReadmePage()
        assert test_page._is_valid_page(tmp_home_page) is False

    def test_readme_page_is_valid_page_readme_page(self, tmp_readme_page):
        test_page = pn.ReadmePage()
        assert test_page._is_valid_page(tmp_readme_page) is True

    def test_readme_page_is_valid_page_fail(self, tmp_file_factory):
        test_page = pn.ReadmePage()
        assert test_page._is_valid_page(tmp_file_factory('test.xlsx')) is False
        assert test_page._is_valid_page(tmp_file_factory('test.png')) is False
        assert test_page._is_valid_page(tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            test_page._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))

    def test_readme_page_is_valid_page_no_output(
            self, tmp_readme_page, capsys):
        pn.ReadmePage()._is_valid_page(tmp_readme_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_readme_page_is_valid_page_invalid_input(self, tmp_readme_page):
        with pytest.raises(TypeError):
            pn.ReadmePage()._is_valid_page(tmp_readme_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.ReadmePage()._is_valid_page('string')
        with pytest.raises(AttributeError):
            pn.ReadmePage()._is_valid_page(3.142)
        with pytest.raises(AttributeError):
            pn.ReadmePage()._is_valid_page([tmp_readme_page, tmp_readme_page])
        with pytest.raises(OSError):
            pn.ReadmePage()._is_valid_page(pathlib.Path('/not/a/path'))

    def test_page_convert_filename_to_title(self, tmp_page):
        test_title = pn.Page(tmp_page)._convert_filename_to_title()
        assert isinstance(test_title, str)
        expected = tmp_page.stem.replace('_', ' ').replace('-', ' ').strip()
        assert test_title == expected

    def test_page_convert_filename_to_title_null(self):
        test_title = pn.Page()._convert_filename_to_title()
        assert test_title is None

    def test_page_convert_filename_to_title_no_output(self, tmp_page, capsys):
        pn.Page(tmp_page)._convert_filename_to_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_page_convert_filename_to_title_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            pn.Page(tmp_page)._convert_filename_to_title('extra parameter')

    def test_logbook_page_convert_filename_to_title(self, tmp_logbook_page):
        test_title = pn.LogbookPage(tmp_logbook_page)._convert_filename_to_title()
        assert isinstance(test_title, str)
        expected = tmp_logbook_page.stem.strip()
        assert test_title == expected

    def test_logbook_page_convert_filename_to_title_null(self):
        test_title = pn.LogbookPage()._convert_filename_to_title()
        assert test_title is None

    def test_logbook_page_convert_filename_to_title_no_output(
            self, tmp_logbook_page, capsys):
        pn.LogbookPage(tmp_logbook_page)._convert_filename_to_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_page_convert_filename_to_title_invalid_input(
            self, tmp_logbook_page):
        with pytest.raises(TypeError):
            (pn.LogbookPage(tmp_logbook_page)
               ._convert_filename_to_title('extra parameter'))

    def test_contents_page_convert_filename_to_title(self, tmp_contents_page):
        test_title = (pn.ContentsPage(tmp_contents_page)
                        ._convert_filename_to_title())
        assert isinstance(test_title, str)
        expected = tmp_contents_page.stem.strip()
        assert test_title == expected

    def test_contents_page_convert_filename_to_title_null(self):
        test_title = pn.ContentsPage()._convert_filename_to_title()
        assert test_title is None

    def test_contents_page_convert_filename_to_title_no_output(
            self, tmp_contents_page, capsys):
        pn.ContentsPage(tmp_contents_page)._convert_filename_to_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_contents_page_convert_filename_to_title_invalid_input(
            self, tmp_contents_page):
        with pytest.raises(TypeError):
            (pn.ContentsPage(tmp_contents_page)
                ._convert_filename_to_title('extra parameter'))

    def test_home_page_convert_filename_to_title(self, tmp_home_page):
        test_title = pn.HomePage(tmp_home_page)._convert_filename_to_title()
        assert isinstance(test_title, str)
        expected = tmp_home_page.stem.strip()
        assert test_title == expected

    def test_home_page_convert_filename_to_title_null(self):
        test_title = pn.HomePage()._convert_filename_to_title()
        assert test_title is None

    def test_home_page_convert_filename_to_title_no_output(
            self, tmp_home_page, capsys):
        pn.HomePage(tmp_home_page)._convert_filename_to_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_home_page_convert_filename_to_title_invalid_input(
            self, tmp_home_page):
        with pytest.raises(TypeError):
            (pn.HomePage(tmp_home_page)
                ._convert_filename_to_title('extra parameter'))

    def test_readme_page_convert_filename_to_title(self, tmp_readme_page):
        test_title = pn.ReadmePage(tmp_readme_page)._convert_filename_to_title()
        assert isinstance(test_title, str)
        expected = tmp_readme_page.stem.strip()
        assert test_title == expected

    def test_readme_page_convert_filename_to_title_null(self):
        test_title = pn.ReadmePage()._convert_filename_to_title()
        assert test_title is None

    def test_readme_page_convert_filename_to_title_no_output(
            self, tmp_readme_page, capsys):
        pn.ReadmePage(tmp_readme_page)._convert_filename_to_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_readme_page_convert_filename_to_title_invalid_input(
            self, tmp_readme_page):
        with pytest.raises(TypeError):
            (pn.ReadmePage(tmp_readme_page)
                ._convert_filename_to_title('extra parameter'))


    # Creating notebook objects
    def test_create_notebook(self, tmp_notebook):
        test_notebook = pn.Notebook(tmp_notebook)
        assert isinstance(test_notebook.path, pathlib.Path)
        assert test_notebook.path == tmp_notebook

    def test_create_notebook_contents(self, tmp_notebook):
        test_notebook = pn.Notebook(tmp_notebook)
        for filename in self.temp_pages:
            this_path = tmp_notebook.joinpath(filename)
            assert this_path in [this_page.path
                                 for this_page in test_notebook.contents]
        for this_page in test_notebook.contents:
            assert isinstance(this_page, pn.Page)
            if this_page.get_title() not in [self.homepage_descriptor,
                                             self.contents_descriptor,
                                             self.readme_descriptor]:
                with open(self.test_page, 'r')  as f:
                    test_content = f.readlines()
                assert this_page.content == test_content

    def test_create_notebook_no_changes(self, cloned_repo):
        pn.Notebook(pathlib.Path(cloned_repo.working_dir))
        assert self.repo_unchanged(cloned_repo)

    def test_create_notebook_null(self):
        test_notebook = pn.Notebook()
        assert test_notebook.path is None
        assert test_notebook.contents == []

    def test_create_notebook_no_output(self, tmp_notebook, capsys):
        pn.Notebook(tmp_notebook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_create_notebook_invalid_input(self, tmp_notebook):
        with pytest.raises(TypeError):
            pn.Notebook(tmp_notebook, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.Notebook('string')
        with pytest.raises(AttributeError):
            pn.Notebook(3.142)
        with pytest.raises(AttributeError):
            pn.Notebook([tmp_notebook, tmp_notebook])
        with pytest.raises(OSError):
            pn.Notebook(pathlib.Path('/not/a/path'))

    def test_create_logbook(self, tmp_logbook):
        test_logbook = pn.Logbook(tmp_logbook)
        assert isinstance(test_logbook.path, pathlib.Path)
        assert test_logbook.path == tmp_logbook

    def test_create_logbook_contents(self, tmp_logbook):
        test_logbook = pn.Logbook(tmp_logbook)
        for filename in self.temp_logbook_pages:
            this_path = tmp_logbook.joinpath(filename)
            assert this_path in [this_page.path
                                 for this_page in test_logbook.contents]
        for this_page in test_logbook.contents:
            assert isinstance(this_page, pn.Page)
            if this_page.get_title() not in [self.homepage_descriptor,
                                             self.contents_descriptor,
                                             self.readme_descriptor]:
                assert isinstance(this_page, pn.LogbookPage)
                with open(self.test_logbook_page, 'r')  as f:
                    test_content = f.readlines()
                assert this_page.content == test_content

    def test_create_logbook_null(self):
        test_logbook = pn.Logbook()
        assert test_logbook.path is None
        assert test_logbook.contents == []

    def test_create_logbook_no_output(self, tmp_logbook, capsys):
        pn.Logbook(tmp_logbook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_create_logbook_invalid_input(self, tmp_logbook):
        with pytest.raises(TypeError):
            pn.Logbook(tmp_logbook, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.Logbook('string')
        with pytest.raises(AttributeError):
            pn.Logbook(3.142)
        with pytest.raises(AttributeError):
            pn.Logbook([tmp_logbook, tmp_logbook])
        with pytest.raises(OSError):
            pn.Logbook(pathlib.Path('/not/a/path'))

    def test_create_notebook_nested(self, tmp_nested):
        test_notebook = pn.Notebook(tmp_nested)
        assert isinstance(test_notebook.path, pathlib.Path)
        assert test_notebook.path == tmp_nested

    def test_create_notebook_nested_contents(self, tmp_nested):
        test_notebook = pn.Notebook(tmp_nested)
        notebook_contents = [item.path for item in test_notebook.contents]
        for filename in self.temp_pages:
            this_path = tmp_nested.joinpath(filename)
            assert this_path in notebook_contents
        assert tmp_nested.joinpath(self.temp_notebook) in notebook_contents
        assert tmp_nested.joinpath(self.temp_logbook) in notebook_contents


    # Loading data to notebook objects
    def test_notebook_add_page(self, tmp_page):
        test_notebook = pn.Notebook()
        test_notebook.add_page(tmp_page)
        assert isinstance(test_notebook.contents, list)
        assert tmp_page in [this_page.path
                            for this_page in test_notebook.contents]
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path == tmp_page
        assert isinstance(last_item.content, list)
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert last_item.content == test_content

    def test_notebook_add_page_null(self):
        test_notebook = pn.Notebook()
        test_notebook.add_page()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_notebook_add_page_no_output(self, tmp_page, capsys):
        pn.Notebook().add_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_page_null_no_output(self, capsys):
        pn.Notebook().add_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_page_invalid_input(self, tmp_page):
        test_notebook = pn.Notebook()
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
        test_notebook = pn.Notebook()
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
        test_logbook = pn.Logbook()
        test_logbook.add_page(tmp_logbook_page)
        assert isinstance(test_logbook.contents, list)
        assert tmp_logbook_page in [this_page.path
                                    for this_page in test_logbook.contents]
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.LogbookPage)
        assert last_item.path == tmp_logbook_page
        assert isinstance(last_item.content, list)
        with open(self.test_logbook_page, 'r')  as f:
            test_content = f.readlines()
        assert last_item.content == test_content

    def test_logbook_add_page_null(self):
        test_logbook = pn.Logbook()
        test_logbook.add_page()
        assert isinstance(test_logbook.contents, list)
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.LogbookPage)
        assert last_item.path is None
        assert last_item.content is None

    def test_logbook_add_page_no_output(self, tmp_logbook_page, capsys):
        pn.Logbook().add_page(tmp_logbook_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_page_null_no_output(self, capsys):
        pn.Logbook().add_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_page_invalid_input(self, tmp_logbook_page):
        test_logbook = pn.Logbook()
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
        test_logbook = pn.Logbook()
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
        test_logbook = pn.Logbook()
        temp_file = tmp_path.joinpath(f'test{self.page_suffix}')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_logbook.add_page(temp_file)

    def test_notebook_add_contents_page(self, tmp_contents_page):
        test_notebook = pn.Notebook()
        test_notebook.add_contents_page(tmp_contents_page)
        assert isinstance(test_notebook.contents, list)
        assert tmp_contents_page in [this_page.path
                            for this_page in test_notebook.contents]
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path == tmp_contents_page
        assert isinstance(last_item.content, list)
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert last_item.content == test_content

    def test_notebook_add_contents_page_null(self):
        test_notebook = pn.Notebook()
        test_notebook.add_contents_page()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_notebook_add_contents_page_no_output(self, tmp_contents_page, capsys):
        pn.Notebook().add_contents_page(tmp_contents_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_contents_page_null_no_output(self, capsys):
        pn.Notebook().add_contents_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_contents_page_invalid_input(self, tmp_contents_page):
        test_notebook = pn.Notebook()
        with pytest.raises(TypeError):
            test_notebook.add_contents_page(tmp_contents_page, 'extra parameter')
        with pytest.raises(AttributeError):
            test_notebook.add_contents_page('string')
        with pytest.raises(AttributeError):
            test_notebook.add_contents_page(3.142)
        with pytest.raises(AttributeError):
            test_notebook.add_contents_page([tmp_contents_page, tmp_contents_page])
        with pytest.raises(OSError):
            test_notebook.add_contents_page(pathlib.Path('/not/a/path'))

    def test_notebook_add_contents_page_invalid_file_types(self, tmp_path):
        test_notebook = pn.Notebook()
        temp_file = tmp_path.joinpath('test.xlsx')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_notebook.add_contents_page(temp_file)
        temp_file = tmp_path.joinpath('test.png')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_notebook.add_contents_page(temp_file)
        temp_file = tmp_path.joinpath('.DS_Store')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_notebook.add_contents_page(temp_file)

    def test_logbook_add_contents_page(self, tmp_contents_page):
        test_logbook = pn.Logbook()
        test_logbook.add_contents_page(tmp_contents_page)
        assert isinstance(test_logbook.contents, list)
        assert tmp_contents_page in [this_page.path
                            for this_page in test_logbook.contents]
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path == tmp_contents_page
        assert isinstance(last_item.content, list)
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert last_item.content == test_content

    def test_logbook_add_contents_page_null(self):
        test_logbook = pn.Logbook()
        test_logbook.add_contents_page()
        assert isinstance(test_logbook.contents, list)
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_logbook_add_contents_page_no_output(self, tmp_contents_page, capsys):
        pn.Logbook().add_contents_page(tmp_contents_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_contents_page_null_no_output(self, capsys):
        pn.Logbook().add_contents_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_contents_page_invalid_input(self, tmp_contents_page):
        test_logbook = pn.Logbook()
        with pytest.raises(TypeError):
            test_logbook.add_contents_page(tmp_contents_page, 'extra parameter')
        with pytest.raises(AttributeError):
            test_logbook.add_contents_page('string')
        with pytest.raises(AttributeError):
            test_logbook.add_contents_page(3.142)
        with pytest.raises(AttributeError):
            test_logbook.add_contents_page([tmp_contents_page, tmp_contents_page])
        with pytest.raises(OSError):
            test_logbook.add_contents_page(pathlib.Path('/not/a/path'))

    def test_logbook_add_contents_page_invalid_file_types(self, tmp_path):
        test_logbook = pn.Logbook()
        temp_file = tmp_path.joinpath('test.xlsx')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_logbook.add_contents_page(temp_file)
        temp_file = tmp_path.joinpath('test.png')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_logbook.add_contents_page(temp_file)
        temp_file = tmp_path.joinpath('.DS_Store')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_logbook.add_contents_page(temp_file)

    def test_notebook_add_home_page(self, tmp_home_page):
        test_notebook = pn.Notebook()
        test_notebook.add_home_page(tmp_home_page)
        assert isinstance(test_notebook.contents, list)
        assert tmp_home_page in [this_page.path
                            for this_page in test_notebook.contents]
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path == tmp_home_page
        assert isinstance(last_item.content, list)
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert last_item.content == test_content

    def test_notebook_add_home_page_null(self):
        test_notebook = pn.Notebook()
        test_notebook.add_home_page()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_notebook_add_home_page_no_output(self, tmp_home_page, capsys):
        pn.Notebook().add_home_page(tmp_home_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_home_page_null_no_output(self, capsys):
        pn.Notebook().add_home_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_home_page_invalid_input(self, tmp_home_page):
        test_notebook = pn.Notebook()
        with pytest.raises(TypeError):
            test_notebook.add_home_page(tmp_home_page, 'extra parameter')
        with pytest.raises(AttributeError):
            test_notebook.add_home_page('string')
        with pytest.raises(AttributeError):
            test_notebook.add_home_page(3.142)
        with pytest.raises(AttributeError):
            test_notebook.add_home_page([tmp_home_page, tmp_home_page])
        with pytest.raises(OSError):
            test_notebook.add_home_page(pathlib.Path('/not/a/path'))

    def test_notebook_add_home_page_invalid_file_types(self, tmp_path):
        test_notebook = pn.Notebook()
        temp_file = tmp_path.joinpath('test.xlsx')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_notebook.add_home_page(temp_file)
        temp_file = tmp_path.joinpath('test.png')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_notebook.add_home_page(temp_file)
        temp_file = tmp_path.joinpath('.DS_Store')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_notebook.add_home_page(temp_file)

    def test_logbook_add_home_page(self, tmp_home_page):
        test_logbook = pn.Logbook()
        test_logbook.add_home_page(tmp_home_page)
        assert isinstance(test_logbook.contents, list)
        assert tmp_home_page in [this_page.path
                            for this_page in test_logbook.contents]
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path == tmp_home_page
        assert isinstance(last_item.content, list)
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert last_item.content == test_content

    def test_logbook_add_home_page_null(self):
        test_logbook = pn.Logbook()
        test_logbook.add_home_page()
        assert isinstance(test_logbook.contents, list)
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_logbook_add_home_page_no_output(self, tmp_home_page, capsys):
        pn.Logbook().add_home_page(tmp_home_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_home_page_null_no_output(self, capsys):
        pn.Logbook().add_home_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_home_page_invalid_input(self, tmp_home_page):
        test_logbook = pn.Logbook()
        with pytest.raises(TypeError):
            test_logbook.add_home_page(tmp_home_page, 'extra parameter')
        with pytest.raises(AttributeError):
            test_logbook.add_home_page('string')
        with pytest.raises(AttributeError):
            test_logbook.add_home_page(3.142)
        with pytest.raises(AttributeError):
            test_logbook.add_home_page([tmp_home_page, tmp_home_page])
        with pytest.raises(OSError):
            test_logbook.add_home_page(pathlib.Path('/not/a/path'))

    def test_logbook_add_home_page_invalid_file_types(self, tmp_path):
        test_logbook = pn.Logbook()
        temp_file = tmp_path.joinpath('test.xlsx')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_logbook.add_home_page(temp_file)
        temp_file = tmp_path.joinpath('test.png')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_logbook.add_home_page(temp_file)
        temp_file = tmp_path.joinpath('.DS_Store')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_logbook.add_home_page(temp_file)

    def test_notebook_add_readme_page(self, tmp_readme_page):
        test_notebook = pn.Notebook()
        test_notebook.add_readme_page(tmp_readme_page)
        assert isinstance(test_notebook.contents, list)
        assert tmp_readme_page in [this_page.path
                            for this_page in test_notebook.contents]
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path == tmp_readme_page
        assert isinstance(last_item.content, list)
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert last_item.content == test_content

    def test_notebook_add_readme_page_null(self):
        test_notebook = pn.Notebook()
        test_notebook.add_readme_page()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_notebook_add_readme_page_no_output(self, tmp_readme_page, capsys):
        pn.Notebook().add_readme_page(tmp_readme_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_readme_page_null_no_output(self, capsys):
        pn.Notebook().add_readme_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_readme_page_invalid_input(self, tmp_readme_page):
        test_notebook = pn.Notebook()
        with pytest.raises(TypeError):
            test_notebook.add_readme_page(tmp_readme_page, 'extra parameter')
        with pytest.raises(AttributeError):
            test_notebook.add_readme_page('string')
        with pytest.raises(AttributeError):
            test_notebook.add_readme_page(3.142)
        with pytest.raises(AttributeError):
            test_notebook.add_readme_page([tmp_readme_page, tmp_readme_page])
        with pytest.raises(OSError):
            test_notebook.add_readme_page(pathlib.Path('/not/a/path'))

    def test_notebook_add_readme_page_invalid_file_types(self, tmp_path):
        test_notebook = pn.Notebook()
        temp_file = tmp_path.joinpath('test.xlsx')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_notebook.add_readme_page(temp_file)
        temp_file = tmp_path.joinpath('test.png')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_notebook.add_readme_page(temp_file)
        temp_file = tmp_path.joinpath('.DS_Store')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_notebook.add_readme_page(temp_file)

    def test_logbook_add_readme_page(self, tmp_readme_page):
        test_logbook = pn.Logbook()
        test_logbook.add_readme_page(tmp_readme_page)
        assert isinstance(test_logbook.contents, list)
        assert tmp_readme_page in [this_page.path
                            for this_page in test_logbook.contents]
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path == tmp_readme_page
        assert isinstance(last_item.content, list)
        with open(self.test_page, 'r')  as f:
            test_content = f.readlines()
        assert last_item.content == test_content

    def test_logbook_add_readme_page_null(self):
        test_logbook = pn.Logbook()
        test_logbook.add_readme_page()
        assert isinstance(test_logbook.contents, list)
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_logbook_add_readme_page_no_output(self, tmp_readme_page, capsys):
        pn.Logbook().add_readme_page(tmp_readme_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_readme_page_null_no_output(self, capsys):
        pn.Logbook().add_readme_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_readme_page_invalid_input(self, tmp_readme_page):
        test_logbook = pn.Logbook()
        with pytest.raises(TypeError):
            test_logbook.add_readme_page(tmp_readme_page, 'extra parameter')
        with pytest.raises(AttributeError):
            test_logbook.add_readme_page('string')
        with pytest.raises(AttributeError):
            test_logbook.add_readme_page(3.142)
        with pytest.raises(AttributeError):
            test_logbook.add_readme_page([tmp_readme_page, tmp_readme_page])
        with pytest.raises(OSError):
            test_logbook.add_readme_page(pathlib.Path('/not/a/path'))

    def test_logbook_add_readme_page_invalid_file_types(self, tmp_path):
        test_logbook = pn.Logbook()
        temp_file = tmp_path.joinpath('test.xlsx')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_logbook.add_readme_page(temp_file)
        temp_file = tmp_path.joinpath('test.png')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_logbook.add_readme_page(temp_file)
        temp_file = tmp_path.joinpath('.DS_Store')
        with open(temp_file, 'w') as f:
            f.write('Hello world')
        with pytest.raises(ValueError):
            test_logbook.add_readme_page(temp_file)

    def test_notebook_add_notebook(self, tmp_notebook):
        test_notebook = pn.Notebook()
        test_notebook.add_notebook(tmp_notebook)
        assert isinstance(test_notebook.contents, list)
        assert tmp_notebook in [this_item.path
                                for this_item in test_notebook.contents]
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Notebook)
        assert last_item.path == tmp_notebook
        assert isinstance(last_item.contents, list)
        for filename in self.temp_pages:
            this_path = tmp_notebook.joinpath(filename)
            assert this_path in [this_page.path
                                 for this_page in last_item.contents]
        for this_page in last_item.contents:
            assert isinstance(this_page, pn.Page)
            if this_page.get_title() not in [self.homepage_descriptor,
                                             self.contents_descriptor,
                                             self.readme_descriptor]:
                with open(self.test_page, 'r')  as f:
                    test_content = f.readlines()
                assert this_page.content == test_content

    def test_notebook_add_notebook_null(self):
        test_notebook = pn.Notebook()
        test_notebook.add_notebook()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Notebook)
        assert last_item.path is None
        assert last_item.contents == []

    def test_notebook_add_notebook_no_output(self, tmp_notebook, capsys):
        pn.Notebook().add_notebook(tmp_notebook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_notebook_null_no_output(self, capsys):
        pn.Notebook().add_notebook()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_notebook_invalid_input(self, tmp_notebook):
        test_notebook = pn.Notebook()
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
        test_logbook = pn.Logbook()
        test_logbook.add_notebook(tmp_notebook)
        assert isinstance(test_logbook.contents, list)
        assert tmp_notebook not in [this_item.path
                                    for this_item in test_logbook.contents]

    def test_logbook_add_notebook_null(self):
        test_logbook = pn.Logbook()
        test_logbook.add_notebook()
        assert isinstance(test_logbook.contents, list)
        assert len(test_logbook.contents) == 0

    def test_logbook_add_notebook_no_output(self, tmp_notebook, capsys):
        pn.Logbook().add_notebook(tmp_notebook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_notebook_null_no_output(self, capsys):
        pn.Logbook().add_notebook()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_logbook(self, tmp_logbook):
        test_notebook = pn.Notebook()
        test_notebook.add_logbook(tmp_logbook)
        assert isinstance(test_notebook.contents, list)
        assert tmp_logbook in [this_item.path
                                for this_item in test_notebook.contents]
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Logbook)
        assert last_item.path == tmp_logbook
        assert isinstance(last_item.contents, list)
        for filename in self.temp_logbook_pages:
            this_path = tmp_logbook.joinpath(filename)
            assert this_path in [this_page.path
                                 for this_page in last_item.contents]
        for this_page in last_item.contents:
            assert isinstance(this_page, pn.Page)
            if this_page.get_title() not in [self.homepage_descriptor,
                                             self.contents_descriptor,
                                             self.readme_descriptor]:
                assert isinstance(this_page, pn.LogbookPage)
                with open(self.test_logbook_page, 'r')  as f:
                    test_content = f.readlines()
                assert this_page.content == test_content

    def test_notebook_add_logbook_null(self):
        test_notebook = pn.Notebook()
        test_notebook.add_logbook()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Notebook)
        assert last_item.path is None
        assert last_item.contents == []

    def test_notebook_add_logbook_no_output(self, tmp_logbook, capsys):
        pn.Notebook().add_logbook(tmp_logbook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_logbook_null_no_output(self, capsys):
        pn.Notebook().add_logbook()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_logbook_invalid_input(self, tmp_logbook):
        test_notebook = pn.Notebook()
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
        test_logbook = pn.Logbook()
        test_logbook.add_logbook(tmp_logbook)
        assert isinstance(test_logbook.contents, list)
        assert tmp_logbook not in [this_item.path
                                   for this_item in test_logbook.contents]

    def test_logbook_add_logbook_null(self):
        test_logbook = pn.Logbook()
        test_logbook.add_logbook()
        assert isinstance(test_logbook.contents, list)
        assert len(test_logbook.contents) == 0

    def test_logbook_add_logbook_no_output(self, tmp_logbook, capsys):
        pn.Logbook().add_logbook(tmp_logbook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_logbook_null_no_output(self, capsys):
        pn.Logbook().add_logbook()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_load_contents(self, tmp_notebook):
        test_notebook = pn.Notebook()
        test_notebook.path = tmp_notebook
        test_notebook.load_contents()
        for filename in self.temp_pages:
            this_path = tmp_notebook.joinpath(filename)
            assert this_path in [this_page.path
                                 for this_page in test_notebook.contents]
        for this_page in test_notebook.contents:
            assert isinstance(this_page, pn.Page)
            if this_page.get_title() not in [self.homepage_descriptor,
                                             self.contents_descriptor,
                                             self.readme_descriptor]:
                with open(self.test_page, 'r')  as f:
                    test_content = f.readlines()
                assert this_page.content == test_content

    def test_notebook_load_contents_no_changes(self, cloned_repo):
        test_notebook = pn.Notebook()
        test_notebook.path = pathlib.Path(cloned_repo.working_dir)
        test_notebook.load_contents()
        assert self.repo_unchanged(cloned_repo)

    def test_notebook_load_contents_null(self):
        test_notebook = pn.Notebook()
        test_notebook.path = None
        test_notebook.load_contents()
        assert test_notebook.contents == []

    def test_notebook_load_contents_no_output(self, tmp_notebook, capsys):
        test_notebook = pn.Notebook()
        test_notebook.path = tmp_notebook
        test_notebook.load_contents()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_load_contents_null_no_output(self, capsys):
        pn.Notebook().load_contents()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_load_contents_invalid_input(self, tmp_logbook_page):
        test_notebook = pn.Notebook()
        with pytest.raises(TypeError):
            test_notebook.load_contents('extra parameter')

    def test_logbook_load_contents(self, tmp_logbook):
        test_logbook = pn.Logbook()
        test_logbook.path = tmp_logbook
        test_logbook.load_contents()
        for filename in self.temp_logbook_pages:
            this_path = tmp_logbook.joinpath(filename)
            assert this_path in [this_page.path
                                 for this_page in test_logbook.contents]
        for this_page in test_logbook.contents:
            assert isinstance(this_page, pn.Page)
            if this_page.get_title() not in [self.homepage_descriptor,
                                             self.contents_descriptor,
                                             self.readme_descriptor]:
                assert isinstance(this_page, pn.LogbookPage)
                with open(self.test_logbook_page, 'r')  as f:
                    test_content = f.readlines()
                assert this_page.content == test_content

    def test_logbook_load_contents_null(self):
        test_logbook = pn.Logbook()
        test_logbook.path = None
        test_logbook.load_contents()
        assert test_logbook.contents == []

    def test_logbook_load_contents_no_output(self, tmp_logbook, capsys):
        test_logbook = pn.Logbook()
        test_logbook.path = tmp_logbook
        test_logbook.load_contents()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_load_contents_null_no_output(self, capsys):
        pn.Logbook().load_contents()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_load_contents_invalid_input(self, tmp_logbook_page):
        test_logbook = pn.Logbook()
        with pytest.raises(TypeError):
            test_logbook.load_contents('extra parameter')


    # Getting information from notebook objects
    def test_notebook_is_valid_page(self, tmp_page):
        test_notebook = pn.Notebook()
        assert test_notebook._is_valid_page(tmp_page) is True

    def test_notebook_is_valid_page_logbook_page(self, tmp_logbook_page):
        test_notebook = pn.Notebook()
        assert test_notebook._is_valid_page(tmp_logbook_page) is True

    def test_notebook_is_valid_page_fail(self, tmp_file_factory):
        test_notebook = pn.Notebook()
        assert test_notebook._is_valid_page(
            tmp_file_factory('test.xlsx')) is False
        assert test_notebook._is_valid_page(
            tmp_file_factory('test.png')) is False
        assert test_notebook._is_valid_page(
            tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            test_notebook._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))

    def test_notebook_is_valid_page_no_output(self, tmp_page, capsys):
        pn.Notebook()._is_valid_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_is_valid_page_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            pn.Notebook()._is_valid_page(tmp_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.Notebook()._is_valid_page('string')
        with pytest.raises(AttributeError):
            pn.Notebook()._is_valid_page(3.142)
        with pytest.raises(AttributeError):
            pn.Notebook()._is_valid_page([tmp_page, tmp_page])
        with pytest.raises(OSError):
            pn.Notebook()._is_valid_page(pathlib.Path('/not/a/path'))

    def test_logbook_is_valid_page(self, tmp_logbook_page):
        test_logbook = pn.Logbook()
        assert test_logbook._is_valid_page(tmp_logbook_page) is True

    def test_logbook_is_valid_page_notebook_page(self, tmp_page):
        test_logbook = pn.Logbook()
        assert test_logbook._is_valid_page(tmp_page) is False

    def test_logbook_is_valid_page_fail(self, tmp_file_factory):
        test_logbook = pn.Logbook()
        assert test_logbook._is_valid_page(
            tmp_file_factory('test.xlsx')) is False
        assert test_logbook._is_valid_page(
            tmp_file_factory('test.png')) is False
        assert test_logbook._is_valid_page(
            tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            test_logbook._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))

    def test_logbook_is_valid_page_no_output(self, tmp_page, capsys):
        pn.Logbook()._is_valid_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_is_valid_page_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            pn.Logbook()._is_valid_page(tmp_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.Logbook()._is_valid_page('string')
        with pytest.raises(AttributeError):
            pn.Logbook()._is_valid_page(3.142)
        with pytest.raises(AttributeError):
            pn.Logbook()._is_valid_page([tmp_page, tmp_page])
        with pytest.raises(OSError):
            pn.Logbook()._is_valid_page(pathlib.Path('/not/a/path'))

    def test_notebook_is_valid_folder(self, tmp_path):
        assert pn.Notebook()._is_valid_folder(
            tmp_path) is True

    def test_notebook_is_valid_folder_notebook(self, tmp_notebook):
        assert pn.Notebook()._is_valid_folder(
            tmp_notebook) is True

    def test_notebook_is_valid_folder_logbook(self, tmp_logbook):
        assert pn.Notebook()._is_valid_folder(
            tmp_logbook) is True

    def test_notebook_is_valid_folder_fail(self, tmp_path_factory, tmp_page):
        assert pn.Notebook()._is_valid_folder(
            tmp_path_factory.mktemp('.vscode')) is False
        assert pn.Notebook()._is_valid_folder(
            tmp_path_factory.mktemp('.config')) is False

    def test_notebook_is_valid_folder_no_output(self, tmp_path, capsys):
        pn.Notebook()._is_valid_folder(tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_is_valid_folder_invalid_input(self, tmp_path, tmp_page):
        with pytest.raises(TypeError):
            pn.Notebook()._is_valid_folder()
        with pytest.raises(TypeError):
            pn.Notebook()._is_valid_folder(tmp_path, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.Notebook()._is_valid_folder('string')
        with pytest.raises(AttributeError):
            pn.Notebook()._is_valid_folder(3.142)
        with pytest.raises(AttributeError):
            pn.Notebook()._is_valid_folder([tmp_path, tmp_path])
        with pytest.raises(OSError):
            pn.Notebook()._is_valid_folder(pathlib.Path('/not/a/path'))
        with pytest.raises(OSError):
            pn.Notebook()._is_valid_folder(tmp_page)
        with pytest.raises(OSError):
            pn.Notebook()._is_valid_folder(tmp_path.joinpath('not-a-path'))

    def test_logbook_is_valid_folder(self, tmp_path):
        assert pn.Logbook()._is_valid_folder(tmp_path) is False

    def test_logbook_is_valid_folder_notebook(self, tmp_notebook):
        assert pn.Logbook()._is_valid_folder(tmp_notebook) is False

    def test_logbook_is_valid_folder_logbook(self, tmp_logbook):
        assert pn.Logbook()._is_valid_folder(tmp_logbook) is True

    def test_logbook_is_valid_folder_fail(self, tmp_path_factory, tmp_page):
        assert pn.Logbook()._is_valid_folder(
            tmp_path_factory.mktemp('.vscode')) is False
        assert pn.Logbook()._is_valid_folder(
            tmp_path_factory.mktemp('.config')) is False

    def test_logbook_is_valid_folder_no_output(self, tmp_path, capsys):
        pn.Logbook()._is_valid_folder(tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_is_valid_folder_invalid_input(self, tmp_path, tmp_page):
        with pytest.raises(TypeError):
            pn.Logbook()._is_valid_folder()
        with pytest.raises(TypeError):
            pn.Logbook()._is_valid_folder(tmp_path, 'extra parameter')
        with pytest.raises(AttributeError):
            pn.Logbook()._is_valid_folder('string')
        with pytest.raises(AttributeError):
            pn.Logbook()._is_valid_folder(3.142)
        with pytest.raises(AttributeError):
            pn.Logbook()._is_valid_folder([tmp_path, tmp_path])
        with pytest.raises(OSError):
            pn.Logbook()._is_valid_folder(pathlib.Path('/not/a/path'))
        with pytest.raises(OSError):
            pn.Logbook()._is_valid_folder(tmp_page)
        with pytest.raises(OSError):
            pn.Logbook()._is_valid_folder(tmp_path.joinpath('not-a-path'))

    def test_notebook_get_pages(self, tmp_notebook):
        test_notebook = pn.Notebook(tmp_notebook)
        test_pages = test_notebook.get_pages()
        assert isinstance(test_pages, list)
        assert len(test_pages) == len(self.temp_pages)

    def test_notebook_get_pages_contents(self, tmp_notebook):
        test_notebook = pn.Notebook(tmp_notebook)
        test_pages = test_notebook.get_pages()
        for filename in self.temp_pages:
            this_path = tmp_notebook.joinpath(filename)
            assert this_path in [this_page.path for this_page in test_pages]
        for this_page in test_pages:
            assert isinstance(this_page, pn.Page)
            with open(self.test_page, 'r')  as f:
                test_content = f.readlines()
            assert this_page.content == test_content

    def test_notebook_get_pages_selective(self, tmp_page):
        test_notebook = pn.Notebook()
        test_notebook.add_page()
        test_notebook.add_page(tmp_page)
        test_notebook.add_notebook()
        test_notebook.add_logbook()
        test_pages = test_notebook.get_pages()
        assert isinstance(test_pages, list)
        assert len(test_pages) == 2
        assert tmp_page in [page.path for page in test_pages]

    def test_notebook_get_pages_null(self):
        test_notebook = pn.Notebook()
        test_pages = test_notebook.get_pages()
        assert test_pages == []

    def test_notebook_get_pages_no_output(self, capsys):
        pn.Notebook().get_pages()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_get_pages_invalid_input(self):
        with pytest.raises(TypeError):
            pn.Notebook().get_pages('extra parameter')

    def test_logbook_get_pages(self, tmp_logbook):
        test_logbook = pn.Logbook(tmp_logbook)
        test_pages = test_logbook.get_pages()
        assert isinstance(test_pages, list)
        assert len(test_pages) == len(self.temp_logbook_pages)

    def test_logbook_get_pages_contents(self, tmp_logbook):
        test_logbook = pn.Logbook(tmp_logbook)
        test_pages = test_logbook.get_pages()
        for filename in self.temp_logbook_pages:
            this_path = tmp_logbook.joinpath(filename)
            assert this_path in [this_page.path for this_page in test_pages]
        for this_page in test_pages:
            assert isinstance(this_page, pn.Page)
            with open(self.test_logbook_page, 'r')  as f:
                test_content = f.readlines()
            assert this_page.content == test_content

    def test_logbook_get_pages_selective(self, tmp_logbook_page):
        test_logbook = pn.Logbook()
        test_logbook.add_page()
        test_logbook.add_page(tmp_logbook_page)
        test_logbook.add_notebook()
        test_logbook.add_logbook()
        test_pages = test_logbook.get_pages()
        assert isinstance(test_pages, list)
        assert len(test_pages) == 2
        assert tmp_logbook_page in [page.path for page in test_pages]

    def test_logbook_get_pages_null(self):
        test_logbook = pn.Logbook()
        test_pages = test_logbook.get_pages()
        assert test_pages == []

    def test_logbook_get_pages_no_output(self, capsys):
        pn.Logbook().get_pages()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_get_pages_invalid_input(self):
        with pytest.raises(TypeError):
            pn.Logbook().get_pages('extra parameter')

    def test_notebook_get_notebooks(self, tmp_notebook):
        test_notebook = pn.Notebook()
        test_notebook.add_notebook(tmp_notebook)
        notebook_list = test_notebook.get_notebooks()
        assert isinstance(notebook_list, list)
        assert len(notebook_list) == 1

    def test_notebook_get_notebooks_contents(self, tmp_notebook):
        test_notebook = pn.Notebook()
        test_notebook.add_notebook(tmp_notebook)
        notebook_list = test_notebook.get_notebooks()
        nested_notebook = notebook_list[0]
        for filename in self.temp_pages:
            this_path = tmp_notebook.joinpath(filename)
            assert this_path in [this_page.path
                                 for this_page in nested_notebook.contents]
        for this_page in nested_notebook.contents:
            assert isinstance(this_page, pn.Page)
            if this_page.get_title() not in [self.homepage_descriptor,
                                             self.contents_descriptor,
                                             self.readme_descriptor]:
                with open(self.test_page, 'r')  as f:
                    test_content = f.readlines()
                assert this_page.content == test_content

    def test_notebook_get_notebooks_selective(self, tmp_notebook, tmp_logbook):
        test_notebook = pn.Notebook()
        test_notebook.add_page()
        test_notebook.add_notebook()
        test_notebook.add_notebook(tmp_notebook)
        test_notebook.add_logbook()
        test_notebook.add_logbook(tmp_logbook)
        notebook_list = test_notebook.get_notebooks()
        assert isinstance(notebook_list, list)
        assert len(notebook_list) == 2
        assert tmp_notebook in [item.path for item in notebook_list]
        assert tmp_logbook not in [item.path for item in notebook_list]

    def test_notebook_get_notebooks_null(self):
        test_notebook = pn.Notebook()
        notebook_list = test_notebook.get_notebooks()
        assert notebook_list == []

    def test_notebook_get_notebooks_no_output(self, capsys):
        pn.Notebook().get_notebooks()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_get_notebooks_invalid_input(self):
        include_logbooks = True
        with pytest.raises(TypeError):
            pn.Notebook().get_notebooks(include_logbooks, 'extra parameter')

    def test_logbook_get_notebooks(self, tmp_notebook):
        test_logbook = pn.Logbook()
        test_logbook.add_notebook(tmp_notebook)
        notebook_list = test_logbook.get_notebooks()
        assert isinstance(notebook_list, list)
        assert len(notebook_list) == 0

    def test_logbook_get_notebooks_selective(self, tmp_notebook, tmp_logbook):
        test_logbook = pn.Logbook()
        test_logbook.add_page()
        test_logbook.add_notebook()
        test_logbook.add_notebook(tmp_notebook)
        test_logbook.add_logbook()
        test_logbook.add_logbook(tmp_logbook)
        notebook_list = test_logbook.get_notebooks()
        assert isinstance(notebook_list, list)
        assert len(notebook_list) == 0

    def test_logbook_get_notebooks_null(self):
        test_logbook = pn.Logbook()
        notebook_list = test_logbook.get_notebooks()
        assert notebook_list == []

    def test_logbook_get_notebooks_no_output(self, capsys):
        pn.Logbook().get_notebooks()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_get_notebooks_invalid_input(self):
        include_logbooks = True
        with pytest.raises(TypeError):
            pn.Logbook().get_notebooks(include_logbooks, 'extra parameter')

    def test_notebook_get_logbooks(self, tmp_logbook):
        test_notebook = pn.Notebook()
        test_notebook.add_logbook(tmp_logbook)
        logbook_list = test_notebook.get_logbooks()
        assert isinstance(logbook_list, list)
        assert len(logbook_list) == 1

    def test_notebook_get_logbooks_contents(self, tmp_logbook):
        test_notebook = pn.Notebook()
        test_notebook.add_logbook(tmp_logbook)
        logbook_list = test_notebook.get_logbooks()
        nested_logbook = logbook_list[0]
        for filename in self.temp_logbook_pages:
            this_path = tmp_logbook.joinpath(filename)
            assert this_path in [this_page.path
                                 for this_page in nested_logbook.contents]
        for this_page in nested_logbook.contents:
            assert isinstance(this_page, pn.Page)
            if this_page.get_title() not in [self.homepage_descriptor,
                                             self.contents_descriptor,
                                             self.readme_descriptor]:
                assert isinstance(this_page, pn.LogbookPage)
                with open(self.test_logbook_page, 'r')  as f:
                    test_content = f.readlines()
                assert this_page.content == test_content

    def test_notebook_get_logbooks_selective(self, tmp_notebook, tmp_logbook):
        test_notebook = pn.Notebook()
        test_notebook.add_page()
        test_notebook.add_notebook()
        test_notebook.add_notebook(tmp_notebook)
        test_notebook.add_logbook()
        test_notebook.add_logbook(tmp_logbook)
        logbook_list = test_notebook.get_logbooks()
        assert isinstance(logbook_list, list)
        assert len(logbook_list) == 2
        assert tmp_logbook in [item.path for item in logbook_list]
        assert tmp_notebook not in [item.path for item in logbook_list]

    def test_notebook_get_logbooks_null(self):
        test_notebook = pn.Notebook()
        logbook_list = test_notebook.get_logbooks()
        assert logbook_list == []

    def test_notebook_get_logbooks_no_output(self, capsys):
        pn.Notebook().get_logbooks()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_get_logbooks_invalid_input(self):
        include_logbooks = True
        with pytest.raises(TypeError):
            pn.Notebook().get_logbooks('extra parameter')

    def test_logbook_get_logbooks(self, tmp_logbook):
        test_logbook = pn.Logbook()
        test_logbook.add_logbook(tmp_logbook)
        logbook_list = test_logbook.get_logbooks()
        assert isinstance(logbook_list, list)
        assert len(logbook_list) == 0

    def test_logbook_get_logbooks_selective(self, tmp_notebook, tmp_logbook):
        test_logbook = pn.Logbook()
        test_logbook.add_page()
        test_logbook.add_notebook()
        test_logbook.add_notebook(tmp_notebook)
        test_logbook.add_logbook()
        test_logbook.add_logbook(tmp_logbook)
        logbook_list = test_logbook.get_logbooks()
        assert isinstance(logbook_list, list)
        assert len(logbook_list) == 0

    def test_logbook_get_logbooks_null(self):
        test_logbook = pn.Logbook()
        logbook_list = test_logbook.get_logbooks()
        assert logbook_list == []

    def test_logbook_get_logbooks_no_output(self, capsys):
        pn.Logbook().get_logbooks()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_get_logbooks_invalid_input(self):
        include_logbooks = True
        with pytest.raises(TypeError):
            pn.Logbook().get_logbooks('extra parameter')


    # Utility functions
    def test_is_valid_page(self, tmp_page):
        assert pn._is_valid_page(tmp_page) is True

    def test_is_valid_page_notebook_page(self, tmp_page):
        assert pn._is_valid_page(tmp_page) is True

    def test_is_valid_page_logbook_page(self, tmp_logbook_page):
        assert pn._is_valid_page(tmp_logbook_page) is True

    def test_is_valid_page_contents_page(self, tmp_contents_page):
        assert pn._is_valid_page(tmp_contents_page) is True

    def test_is_valid_page_home_page(self, tmp_home_page):
        assert pn._is_valid_page(tmp_home_page) is True

    def test_is_valid_page_readme_page(self, tmp_readme_page):
        assert pn._is_valid_page(tmp_readme_page) is True

    def test_is_valid_page_fail(self, tmp_file_factory):
        assert pn._is_valid_page(tmp_file_factory('test.xlsx')) is False
        assert pn._is_valid_page(tmp_file_factory('test.png')) is False
        assert pn._is_valid_page(tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            pn._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))

    def test_is_valid_page_no_output(self, tmp_page, capsys):
        pn._is_valid_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_is_valid_page_invalid_input(self, tmp_page):
        with pytest.raises(TypeError):
            pn._is_valid_page(tmp_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn._is_valid_page('string')
        with pytest.raises(AttributeError):
            pn._is_valid_page(3.142)
        with pytest.raises(AttributeError):
            pn._is_valid_page([tmp_page, tmp_page])
        with pytest.raises(OSError):
            pn._is_valid_page(pathlib.Path('/not/a/path'))

    def test_is_valid_logbook_page(self, tmp_logbook_page):
        assert pn._is_valid_logbook_page(tmp_logbook_page) is True

    def test_is_valid_logbook_page_notebook_page(self, tmp_page):
        assert pn._is_valid_logbook_page(tmp_page) is False

    def test_is_valid_logbook_page_logbook_page(self, tmp_logbook_page):
        assert pn._is_valid_logbook_page(tmp_logbook_page) is True

    def test_is_valid_logbook_page_contents_page(self, tmp_contents_page):
        assert pn._is_valid_logbook_page(tmp_contents_page) is False

    def test_is_valid_logbook_page_home_page(self, tmp_home_page):
        assert pn._is_valid_logbook_page(tmp_home_page) is False

    def test_is_valid_logbook_page_readme_page(self, tmp_readme_page):
        assert pn._is_valid_logbook_page(tmp_readme_page) is False

    def test_is_valid_logbook_page_fail(self, tmp_file_factory):
        assert pn._is_valid_logbook_page(tmp_file_factory('test.xlsx')) is False
        assert pn._is_valid_logbook_page(tmp_file_factory('test.png')) is False
        assert pn._is_valid_logbook_page(tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            pn._is_valid_logbook_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))
        assert pn._is_valid_logbook_page(
            tmp_file_factory(f'2020-01-01-Meeting{self.page_suffix}')) is False
        assert pn._is_valid_logbook_page(
            tmp_file_factory(f'page1{self.page_suffix}')) is False

    def test_is_valid_logbook_page_no_output(self, tmp_logbook_page, capsys):
        pn._is_valid_logbook_page(tmp_logbook_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_is_valid_logbook_page_invalid_input(self, tmp_logbook_page):
        with pytest.raises(TypeError):
            pn._is_valid_logbook_page(tmp_logbook_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn._is_valid_logbook_page('string')
        with pytest.raises(AttributeError):
            pn._is_valid_logbook_page(3.142)
        with pytest.raises(AttributeError):
            pn._is_valid_logbook_page([tmp_logbook_page, tmp_logbook_page])
        with pytest.raises(OSError):
            pn._is_valid_logbook_page(pathlib.Path('/not/a/path'))

    def test_is_valid_contents_page(self, tmp_contents_page):
        assert pn._is_valid_contents_page(tmp_contents_page) is True

    def test_is_valid_contents_page_notebook_page(self, tmp_page):
        assert pn._is_valid_contents_page(tmp_page) is False

    def test_is_valid_contents_page_logbook_page(self, tmp_logbook_page):
        assert pn._is_valid_contents_page(tmp_logbook_page) is False

    def test_is_valid_contents_page_contents_page(self, tmp_contents_page):
        assert pn._is_valid_contents_page(tmp_contents_page) is True

    def test_is_valid_contents_page_home_page(self, tmp_home_page):
        assert pn._is_valid_contents_page(tmp_home_page) is False

    def test_is_valid_contents_page_readme_page(self, tmp_readme_page):
        assert pn._is_valid_contents_page(tmp_readme_page) is False

    def test_is_valid_contents_page_fail(self, tmp_file_factory):
        assert pn._is_valid_contents_page(tmp_file_factory('test.xlsx')) is False
        assert pn._is_valid_contents_page(tmp_file_factory('test.png')) is False
        assert pn._is_valid_contents_page(tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            pn._is_valid_contents_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))
        assert pn._is_valid_contents_page(
            tmp_file_factory(f'2020-01-01-Meeting{self.page_suffix}')) is False
        assert pn._is_valid_contents_page(
            tmp_file_factory(f'page1{self.page_suffix}')) is False

    def test_is_valid_contents_page_no_output(self, tmp_contents_page, capsys):
        pn._is_valid_contents_page(tmp_contents_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_is_valid_contents_page_invalid_input(self, tmp_contents_page):
        with pytest.raises(TypeError):
            pn._is_valid_contents_page(tmp_contents_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn._is_valid_contents_page('string')
        with pytest.raises(AttributeError):
            pn._is_valid_contents_page(3.142)
        with pytest.raises(AttributeError):
            pn._is_valid_contents_page([tmp_contents_page, tmp_contents_page])
        with pytest.raises(OSError):
            pn._is_valid_contents_page(pathlib.Path('/not/a/path'))

    def test_is_valid_home_page(self, tmp_home_page):
        assert pn._is_valid_home_page(tmp_home_page) is True

    def test_is_valid_home_page_notebook_page(self, tmp_page):
        assert pn._is_valid_home_page(tmp_page) is False

    def test_is_valid_home_page_logbook_page(self, tmp_logbook_page):
        assert pn._is_valid_home_page(tmp_logbook_page) is False

    def test_is_valid_home_page_contents_page(self, tmp_contents_page):
        assert pn._is_valid_home_page(tmp_contents_page) is False

    def test_is_valid_home_page_home_page(self, tmp_home_page):
        assert pn._is_valid_home_page(tmp_home_page) is True

    def test_is_valid_home_page_readme_page(self, tmp_readme_page):
        assert pn._is_valid_home_page(tmp_readme_page) is False

    def test_is_valid_home_page_fail(self, tmp_file_factory):
        assert pn._is_valid_home_page(tmp_file_factory('test.xlsx')) is False
        assert pn._is_valid_home_page(tmp_file_factory('test.png')) is False
        assert pn._is_valid_home_page(tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            pn._is_valid_home_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))
        assert pn._is_valid_home_page(
            tmp_file_factory(f'2020-01-01-Meeting{self.page_suffix}')) is False
        assert pn._is_valid_home_page(
            tmp_file_factory(f'page1{self.page_suffix}')) is False

    def test_is_valid_home_page_no_output(self, tmp_home_page, capsys):
        pn._is_valid_home_page(tmp_home_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_is_valid_home_page_invalid_input(self, tmp_home_page):
        with pytest.raises(TypeError):
            pn._is_valid_home_page(tmp_home_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn._is_valid_home_page('string')
        with pytest.raises(AttributeError):
            pn._is_valid_home_page(3.142)
        with pytest.raises(AttributeError):
            pn._is_valid_home_page([tmp_home_page, tmp_home_page])
        with pytest.raises(OSError):
            pn._is_valid_home_page(pathlib.Path('/not/a/path'))

    def test_is_valid_readme_page(self, tmp_readme_page):
        assert pn._is_valid_readme_page(tmp_readme_page) is True

    def test_is_valid_readme_page_notebook_page(self, tmp_page):
        assert pn._is_valid_readme_page(tmp_page) is False

    def test_is_valid_readme_page_logbook_page(self, tmp_logbook_page):
        assert pn._is_valid_readme_page(tmp_logbook_page) is False

    def test_is_valid_readme_page_contents_page(self, tmp_contents_page):
        assert pn._is_valid_readme_page(tmp_contents_page) is False

    def test_is_valid_readme_page_home_page(self, tmp_home_page):
        assert pn._is_valid_readme_page(tmp_home_page) is False

    def test_is_valid_readme_page_readme_page(self, tmp_readme_page):
        assert pn._is_valid_readme_page(tmp_readme_page) is True

    def test_is_valid_readme_page_fail(self, tmp_file_factory):
        assert pn._is_valid_readme_page(tmp_file_factory('test.xlsx')) is False
        assert pn._is_valid_readme_page(tmp_file_factory('test.png')) is False
        assert pn._is_valid_readme_page(tmp_file_factory('.DS_Store')) is False
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            pn._is_valid_readme_page(tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))
        assert pn._is_valid_readme_page(
            tmp_file_factory(f'2020-01-01-Meeting{self.page_suffix}')) is False
        assert pn._is_valid_readme_page(
            tmp_file_factory(f'page1{self.page_suffix}')) is False

    def test_is_valid_readme_page_no_output(self, tmp_readme_page, capsys):
        pn._is_valid_readme_page(tmp_readme_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_is_valid_readme_page_invalid_input(self, tmp_readme_page):
        with pytest.raises(TypeError):
            pn._is_valid_readme_page(tmp_readme_page, 'extra parameter')
        with pytest.raises(AttributeError):
            pn._is_valid_readme_page('string')
        with pytest.raises(AttributeError):
            pn._is_valid_readme_page(3.142)
        with pytest.raises(AttributeError):
            pn._is_valid_readme_page([tmp_readme_page, tmp_readme_page])
        with pytest.raises(OSError):
            pn._is_valid_readme_page(pathlib.Path('/not/a/path'))

    def test_is_valid_folder(self, tmp_path):
        assert pn._is_valid_folder(tmp_path) is True

    def test_is_valid_folder_notebook(self, tmp_notebook):
        assert pn._is_valid_folder(tmp_notebook) is True

    def test_is_valid_folder_logbook(self, tmp_logbook):
        assert pn._is_valid_folder(tmp_logbook) is True

    def test_is_valid_folder_fail(self, tmp_path_factory, tmp_page):
        assert pn._is_valid_folder(tmp_path_factory.mktemp('.vscode')) is False
        assert pn._is_valid_folder(tmp_path_factory.mktemp('.config')) is False

    def test_is_valid_folder_no_output(self, tmp_path, capsys):
        pn._is_valid_folder(tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_is_valid_folder_invalid_input(self, tmp_path, tmp_page):
        with pytest.raises(TypeError):
            pn._is_valid_folder()
        with pytest.raises(TypeError):
            pn._is_valid_folder(tmp_path, 'extra parameter')
        with pytest.raises(AttributeError):
            pn._is_valid_folder('string')
        with pytest.raises(AttributeError):
            pn._is_valid_folder(3.142)
        with pytest.raises(AttributeError):
            pn._is_valid_folder([tmp_path, tmp_path])
        with pytest.raises(OSError):
            pn._is_valid_folder(pathlib.Path('/not/a/path'))
        with pytest.raises(OSError):
            pn._is_valid_folder(tmp_page)
        with pytest.raises(OSError):
            pn._is_valid_folder(tmp_path.joinpath('not-a-path'))

    def test_is_valid_logbook_folder(self, tmp_path):
        assert pn._is_valid_logbook_folder(tmp_path) is False

    def test_is_valid_logbook_folder_notebook(self, tmp_notebook):
        assert pn._is_valid_logbook_folder(tmp_notebook) is False

    def test_is_valid_logbook_folder_logbook(self, tmp_logbook):
        assert pn._is_valid_logbook_folder(tmp_logbook) is True

    def test_is_valid_logbook_folder_fail(self, tmp_path_factory, tmp_page):
        assert pn._is_valid_logbook_folder(
            tmp_path_factory.mktemp('.vscode')) is False
        assert pn._is_valid_logbook_folder(
            tmp_path_factory.mktemp('.config')) is False

    def test_is_valid_logbook_folder_no_output(self, tmp_path, capsys):
        pn._is_valid_logbook_folder(tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_is_valid_logbook_folder_invalid_input(self, tmp_path, tmp_page):
        with pytest.raises(TypeError):
            pn._is_valid_logbook_folder()
        with pytest.raises(TypeError):
            pn._is_valid_logbook_folder(tmp_path, 'extra parameter')
        with pytest.raises(AttributeError):
            pn._is_valid_logbook_folder('string')
        with pytest.raises(AttributeError):
            pn._is_valid_logbook_folder(3.142)
        with pytest.raises(AttributeError):
            pn._is_valid_logbook_folder([tmp_path, tmp_path])
        with pytest.raises(OSError):
            pn._is_valid_logbook_folder(pathlib.Path('/not/a/path'))
        with pytest.raises(OSError):
            pn._is_valid_logbook_folder(tmp_page)
        with pytest.raises(OSError):
            pn._is_valid_logbook_folder(tmp_path.joinpath('not-a-path'))

    def test_is_blank_line_blank(self):
        assert pn._is_blank_line('') is True

    def test_is_blank_line_newline(self):
        assert pn._is_blank_line('\n') is True

    def test_is_blank_line_text(self):
        assert pn._is_blank_line('text') is False
        assert pn._is_blank_line('text\n') is False

    def test_is_blank_line_title(self):
        assert pn._is_blank_line('# Page title') is False
        assert pn._is_blank_line('# Page title\n') is False

    def test_is_blank_line_link(self):
        assert pn._is_blank_line('[link]: link') is False
        assert pn._is_blank_line('[link]: link\n') is False

    def test_is_blank_line_navigation(self):
        assert pn._is_blank_line('[page](link)') is False
        assert pn._is_blank_line('[page](link)\n') is False

    def test_is_blank_line_invalid_input(self):
        with pytest.raises(AttributeError):
            pn._is_blank_line(None)
        with pytest.raises(AttributeError):
            pn._is_blank_line(self.test_page)
        with pytest.raises(AttributeError):
            pn._is_blank_line(3.142)
        with pytest.raises(AttributeError):
            pn._is_blank_line(['1', '2'])

    def test_is_navigation_line_blank(self):
        assert pn._is_navigation_line('') is False

    def test_is_navigation_line_newline(self):
        assert pn._is_navigation_line('\n') is False

    def test_is_navigation_line_text(self):
        assert pn._is_navigation_line('text') is False
        assert pn._is_navigation_line('text\n') is False

    def test_is_navigation_line_title(self):
        assert pn._is_navigation_line('# Page title') is False
        assert pn._is_navigation_line('# Page title\n') is False

    def test_is_navigation_line_link(self):
        assert pn._is_navigation_line('[link]: link') is False
        assert pn._is_navigation_line('[link]: link\n') is False

    def test_is_navigation_line_navigation(self):
        assert pn._is_navigation_line('[page](link)') is True
        assert pn._is_navigation_line('[page](link)\n') is True

    def test_is_navigation_line_invalid_input(self):
        with pytest.raises(TypeError):
            pn._is_navigation_line(None)
        with pytest.raises(TypeError):
            pn._is_navigation_line(self.test_page)
        with pytest.raises(TypeError):
            pn._is_navigation_line(3.142)
        with pytest.raises(TypeError):
            pn._is_navigation_line(['1', '2'])

    def test_is_title_line_blank(self):
        assert pn._is_title_line('') is False

    def test_is_title_line_newline(self):
        assert pn._is_title_line('\n') is False

    def test_is_title_line_text(self):
        assert pn._is_title_line('text') is False
        assert pn._is_title_line('text\n') is False

    def test_is_title_line_title(self):
        assert pn._is_title_line('# Page title') is True
        assert pn._is_title_line('# Page title\n') is True

    def test_is_title_line_link(self):
        assert pn._is_title_line('[link]: link') is False
        assert pn._is_title_line('[link]: link\n') is False

    def test_is_title_line_navigation(self):
        assert pn._is_title_line('[page](link)') is False
        assert pn._is_title_line('[page](link)\n') is False

    def test_is_title_line_invalid_input(self):
        with pytest.raises(AttributeError):
            pn._is_title_line(None)
        with pytest.raises(AttributeError):
            pn._is_title_line(self.test_page)
        with pytest.raises(AttributeError):
            pn._is_title_line(3.142)
        with pytest.raises(AttributeError):
            pn._is_title_line(['1', '2'])
