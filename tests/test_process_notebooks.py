# Tests process_notebooks.py

import pytest
import pathlib
import git
import shutil

import process_notebooks as pn

# Invalid objects for parametrised testing
invalid_paths = [
        ('string', AttributeError),
        (3.142, AttributeError),
        ([1, 2, 3], AttributeError),
        (pathlib.Path('/not/a/path'), OSError)]

invalid_folders = ['.vscode', '.config']

invalid_logbook = invalid_folders + ['Notebooks', 'PKU-2019', 'Software']

invalid_lines = [
    None,
    3.142,
    [1, 2, 3],
    pathlib.Path('/not/a/path'),
    pathlib.Path.home(),
    pn.Page(),
    pn.Notebook()]

def invalid_filenames(object_type):
    filename_list = [
        'test.xlsx',
        'test.png',
        '.DS_Store']
    if object_type == 'page':
        return filename_list
    else:
        filename_list.append('Page1.md')
        filename_list.append('2020-01-01-meeting.md')
        if object_type != 'logbook page':
            filename_list.append('2020-01-01.md')
            filename_list.append('2020-01.md')
        if object_type != 'home':
            filename_list.append('Home.md')
        if object_type != 'contents':
            filename_list.append('Contents.md')
        if object_type != 'readme':
            filename_list.append('Readme.md')
        return filename_list


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
        self.cloned_home_page = 'Home.md'
        self.cloned_nested_notebook = 'PKU-2019'
        self.cloned_page = 'PKU-2019/Preparatory-research.md'
        self.cloned_contents_page = 'PKU-2019/Contents.md'
        self.cloned_readme_page = 'PKU-2019/Readme.md'
        self.cloned_logbook = 'PKU-2019/Logbook'
        self.cloned_logbook_page = 'PKU-2019/Logbook/2020-01-02.md'
        self.cloned_logbook_month_page = 'PKU-2019/Logbook/2020-01.md'
        self.cloned_logbook_contents_page = 'PKU-2019/Logbook/Contents.md'
        self.cloned_logbook_readme_page = 'PKU-2019/Logbook/Readme.md'
        self.test_title = 'Page title'
        self.temp_notebook = 'temp_notebook'
        self.temp_page = 'temp_file'
        self.temp_pages = ['page1.md', 'page2.md', 'page3.md']
        self.temp_logbook = 'Logbook'
        self.temp_logbook_page = '2020-01-01'
        self.temp_logbook_month = '2020-01'
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
        shutil.copyfile(self.test_contents_page, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_logbook_contents_page(self, tmp_path):
        """Create a new contents page in a temp folder and return its path."""
        tempfile = tmp_path.joinpath(f'{self.contents_filename}'
                                     f'{self.page_suffix}')
        shutil.copyfile(self.test_logbook_contents_page, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_logbook_month_page(self, tmp_path):
        """Create a new month contents page in a temp folder and return path."""
        tempfile = tmp_path.joinpath(f'{self.temp_logbook_month}'
                                     f'{self.page_suffix}')
        shutil.copyfile(self.test_logbook_month_page, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_home_page(self, tmp_path):
        """Create a new home page in a temp folder and return its path."""
        tempfile = tmp_path.joinpath(f'{self.homepage_filename}'
                                     f'{self.page_suffix}')
        shutil.copyfile(self.test_home_page, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_readme_page(self, tmp_path):
        """Create a new readme page in a temp folder and return its path."""
        tempfile = tmp_path.joinpath(f'{self.readme_filename}'
                                     f'{self.page_suffix}')
        shutil.copyfile(self.test_readme_page, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_logbook_readme_page(self, tmp_path):
        """Create a new readme page in a temp folder and return its path."""
        tempfile = tmp_path.joinpath(f'{self.readme_filename}'
                                     f'{self.page_suffix}')
        shutil.copyfile(self.test_logbook_readme_page, tempfile)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_notebook(self, tmp_path):
        """Create a temporary notebook folder and add some pages."""
        notebook_folder = tmp_path.joinpath(self.temp_notebook)
        self.create_and_fill_folder(notebook_folder)
        yield notebook_folder
        shutil.rmtree(notebook_folder)

    @pytest.fixture
    def tmp_logbook(self, tmp_path):
        """Create a temporary logbook folder and add some pages."""
        logbook_folder = tmp_path.joinpath(self.temp_logbook)
        self.create_and_fill_folder(logbook_folder, is_logbook=True)
        yield logbook_folder
        shutil.rmtree(logbook_folder)

    @pytest.fixture
    def tmp_nested(self, tmp_path):
        """Create a temporary notebook folder and add pages and subfolders."""
        notebook_folder = tmp_path.joinpath(self.temp_notebook)
        self.create_and_fill_folder(notebook_folder, add_home=True)
        subfolder1 = notebook_folder.joinpath(self.temp_notebook)
        self.create_and_fill_folder(subfolder1)
        subfolder2 = notebook_folder.joinpath(self.temp_logbook)
        self.create_and_fill_folder(subfolder2, is_logbook=True)
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
            self, folder_path, is_logbook=False,
            add_home=False, add_contents=True, add_readme=True):
        folder_path.mkdir()
        if is_logbook:
            file_list = self.temp_logbook_pages
            file_template = self.test_logbook_page
            contents_page = self.test_logbook_contents_page
            readme_page = self.test_logbook_readme_page
        else:
            file_list = self.temp_pages
            file_template = self.test_page
            contents_page = self.test_contents_page
            readme_page = self.test_readme_page
        home_page = self.test_home_page
        for filename in file_list:
            new_file = folder_path.joinpath(filename)
            shutil.copyfile(file_template, new_file)
        if add_home:
            new_file = folder_path.joinpath(f'{self.homepage_filename}'
                                            f'{self.page_suffix}')
            shutil.copyfile(home_page, new_file)
        if add_contents:
            new_file = folder_path.joinpath(f'{self.contents_filename}'
                                            f'{self.page_suffix}')
            shutil.copyfile(contents_page, new_file)
        if add_readme:
            new_file = folder_path.joinpath(f'{self.readme_filename}'
                                            f'{self.page_suffix}')
            shutil.copyfile(readme_page, new_file)


    # Custom assertions
    def assert_repo_unchanged(self, cloned_repo):
        """Assert that no files are changed within the cloned repo."""
        assert cloned_repo.head.reference == cloned_repo.heads.master
        assert not cloned_repo.is_dirty()
        assert len(cloned_repo.untracked_files) == 0

    def assert_page_contents_match(self, test_page, generator_page):
        """Assert that page contents match the generator page file."""
        with open(generator_page, 'r')  as f:
            test_content = f.readlines()
        assert test_page.content == test_content

    def assert_notebook_contents_match(self, test_notebook, tmp_notebook):
        """Assert that notebook contents match the generator folder."""
        for filename in self.temp_pages:
            this_path = tmp_notebook.joinpath(filename)
            assert this_path in [item.path for item in test_notebook.contents
                                 if isinstance(item, pn.Page)]
        for item in test_notebook.contents:
            if not isinstance(item, pn.Page):
                continue
            if isinstance(item, pn.HomePage):
                self.assert_page_contents_match(item, self.test_home_page)
            elif isinstance(item, pn.ContentsPage):
                self.assert_page_contents_match(item, self.test_contents_page)
            elif isinstance(item, pn.ReadmePage):
                self.assert_page_contents_match(item, self.test_readme_page)
            else:
                self.assert_page_contents_match(item, self.test_page)

    def assert_logbook_contents_match(self, test_logbook, tmp_logbook):
        """Assert that logbook contents match the generator folder."""
        for filename in self.temp_logbook_pages:
            this_path = tmp_logbook.joinpath(filename)
            assert this_path in [item.path for item in test_logbook.contents
                                 if isinstance(item, pn.Page)]
        for item in test_logbook.contents:
            if not isinstance(item, pn.Page):
                continue
            if isinstance(item, pn.ContentsPage):
                self.assert_page_contents_match(
                        item, self.test_logbook_contents_page)
            elif isinstance(item, pn.ReadmePage):
                self.assert_page_contents_match(
                        item, self.test_logbook_readme_page)
            else:
                assert isinstance(item, pn.LogbookPage)
                self.assert_page_contents_match(item, self.test_logbook_page)


    # Test constants
    @pytest.mark.parametrize('constant, value', [
        ('pn.PAGE_SUFFIX', 'self.page_suffix'),
        ('pn.HOME_DESCRIPTOR', 'self.homepage_descriptor'),
        ('pn.HOMEPAGE_FILENAME', 'self.homepage_filename'),
        ('pn.CONTENTS_DESCRIPTOR', 'self.contents_descriptor'),
        ('pn.CONTENTS_FILENAME', 'self.contents_filename'),
        ('pn.README_DESCRIPTOR', 'self.readme_descriptor'),
        ('pn.README_FILENAME', 'self.readme_filename'),
        ('pn.LOGBOOK_FOLDER_NAME', 'self.logbook_folder_name'),
        ('pn.UNKNOWN_DESCRIPTOR', 'self.unknown_descriptor')])
    def test_constant_value(self, constant, value):
        assert eval(constant) == eval(value)


    # Creating page objects
    def test_create_page(self, tmp_page):
        test_page = pn.Page(tmp_page)
        assert isinstance(test_page, pn.Page)

    def test_create_page_path(self, tmp_page):
        test_page = pn.Page(tmp_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert test_page.path == tmp_page

    def test_create_page_content(self, tmp_page):
        test_page = pn.Page(tmp_page)
        assert isinstance(test_page.content, list)
        self.assert_page_contents_match(test_page, tmp_page)

    def test_create_page_null(self):
        test_page = pn.Page()
        assert test_page.path is None
        assert test_page.content is None

    def test_create_page_no_changes(self, cloned_repo):
        pn.Page(pathlib.Path(cloned_repo.working_dir)
                .joinpath(self.cloned_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_create_page_no_output(self, tmp_page, capsys):
        pn.Page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_create_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Page(path)

    def test_create_page_extra_parameter(self, tmp_page):
        with pytest.raises(TypeError):
            pn.Page(tmp_page, 'extra parameter')

    @pytest.mark.parametrize('filename', invalid_filenames('page'))
    def test_create_page_invalid_file_types(self, tmp_file_factory, filename):
        with pytest.raises(ValueError):
            pn.Page(tmp_file_factory(filename))

    def test_create_logbook_page(self, tmp_logbook_page):
        test_page = pn.LogbookPage(tmp_logbook_page)
        assert isinstance(test_page, pn.LogbookPage)

    def test_create_logbook_page_path(self, tmp_logbook_page):
        test_page = pn.LogbookPage(tmp_logbook_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert test_page.path == tmp_logbook_page

    def test_create_logbook_page_content(self, tmp_logbook_page):
        test_page = pn.LogbookPage(tmp_logbook_page)
        assert isinstance(test_page.content, list)
        self.assert_page_contents_match(test_page, tmp_logbook_page)

    def test_create_logbook_page_null(self):
        test_page = pn.LogbookPage()
        assert test_page.path is None
        assert test_page.content is None

    def test_create_logbook_page_no_changes(self, cloned_repo):
        pn.LogbookPage(pathlib.Path(cloned_repo.working_dir)
                       .joinpath(self.cloned_logbook_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_create_logbook_page_no_output(self, tmp_logbook_page, capsys):
        pn.LogbookPage(tmp_logbook_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_create_logbook_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.LogbookPage(path)

    def test_create_logbook_page_extra_parameter(self, tmp_logbook_page):
        with pytest.raises(TypeError):
            pn.LogbookPage(tmp_logbook_page, 'extra parameter')

    @pytest.mark.parametrize('filename', invalid_filenames('logbook page'))
    def test_create_logbook_page_invalid_file_types(
            self, tmp_file_factory, filename):
        with pytest.raises(ValueError):
            pn.LogbookPage(tmp_file_factory(filename))

    def test_create_contents_page(self, tmp_contents_page):
        test_page = pn.ContentsPage(tmp_contents_page)
        assert isinstance(test_page, pn.ContentsPage)

    def test_create_contents_page_path(self, tmp_contents_page):
        test_page = pn.ContentsPage(tmp_contents_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert test_page.path == tmp_contents_page

    def test_create_contents_page_content(self, tmp_contents_page):
        test_page = pn.ContentsPage(tmp_contents_page)
        assert isinstance(test_page.content, list)
        self.assert_page_contents_match(test_page, tmp_contents_page)

    def test_create_contents_page_no_changes(self, cloned_repo):
        pn.ContentsPage(pathlib.Path(cloned_repo.working_dir)
                        .joinpath(self.cloned_contents_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_create_contents_page_null(self):
        test_page = pn.ContentsPage()
        assert test_page.path is None
        assert test_page.content is None

    def test_create_contents_page_no_output(self, tmp_contents_page, capsys):
        pn.ContentsPage(tmp_contents_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_create_contents_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.ContentsPage(path)

    def test_create_contents_page_invalid_extra_parameter(
            self, tmp_contents_page):
        with pytest.raises(TypeError):
            pn.ContentsPage(tmp_contents_page, 'extra parameter')

    def test_create_contents_page_invalid_filename(self, tmp_page):
        with pytest.raises(ValueError):
            pn.ContentsPage(tmp_page)

    @pytest.mark.parametrize('filename', invalid_filenames('contents'))
    def test_create_contents_page_invalid_file_types(
            self, tmp_file_factory, filename):
        with pytest.raises(ValueError):
            pn.ContentsPage(tmp_file_factory(filename))

    def test_create_logbook_contents_page(self, tmp_logbook_contents_page):
        test_page = pn.ContentsPage(tmp_logbook_contents_page)
        assert isinstance(test_page, pn.ContentsPage)

    def test_create_logbook_contents_page_path(self, tmp_logbook_contents_page):
        test_page = pn.ContentsPage(tmp_logbook_contents_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert test_page.path == tmp_logbook_contents_page

    def test_create_logbook_contents_page_content(
            self, tmp_logbook_contents_page):
        test_page = pn.ContentsPage(tmp_logbook_contents_page)
        assert isinstance(test_page.content, list)
        self.assert_page_contents_match(test_page, tmp_logbook_contents_page)

    def test_create_logbook_contents_page_no_changes(self, cloned_repo):
        pn.ContentsPage(pathlib.Path(cloned_repo.working_dir)
                        .joinpath(self.cloned_logbook_contents_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_create_logbook_contents_page_no_output(
            self, tmp_logbook_contents_page, capsys):
        pn.ContentsPage(tmp_logbook_contents_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_create_logbook_month_page(self, tmp_logbook_month_page):
        test_page = pn.LogbookPage(tmp_logbook_month_page)
        assert isinstance(test_page, pn.LogbookPage)

    def test_create_logbook_month_page_path(self, tmp_logbook_month_page):
        test_page = pn.LogbookPage(tmp_logbook_month_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert test_page.path == tmp_logbook_month_page

    def test_create_logbook_month_page_content(
            self, tmp_logbook_month_page):
        test_page = pn.LogbookPage(tmp_logbook_month_page)
        assert isinstance(test_page.content, list)
        self.assert_page_contents_match(test_page, tmp_logbook_month_page)

    def test_create_logbook_month_page_no_changes(self, cloned_repo):
        pn.LogbookPage(pathlib.Path(cloned_repo.working_dir)
                       .joinpath(self.cloned_logbook_month_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_create_logbook_month_page_no_output(
            self, tmp_logbook_month_page, capsys):
        pn.LogbookPage(tmp_logbook_month_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_create_home_page(self, tmp_home_page):
        test_page = pn.HomePage(tmp_home_page)
        assert isinstance(test_page, pn.HomePage)

    def test_create_home_page_path(self, tmp_home_page):
        test_page = pn.HomePage(tmp_home_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert test_page.path == tmp_home_page

    def test_create_home_page_content(self, tmp_home_page):
        test_page = pn.HomePage(tmp_home_page)
        assert isinstance(test_page.content, list)
        self.assert_page_contents_match(test_page, tmp_home_page)

    def test_create_home_page_null(self):
        test_page = pn.HomePage()
        assert test_page.path is None
        assert test_page.content is None

    def test_create_home_page_no_changes(self, cloned_repo):
        pn.HomePage(pathlib.Path(cloned_repo.working_dir)
                    .joinpath(self.cloned_home_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_create_home_page_no_output(self, tmp_home_page, capsys):
        pn.HomePage(tmp_home_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_create_home_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.HomePage(path)

    def test_create_home_page_extra_parameter(self, tmp_home_page):
        with pytest.raises(TypeError):
            pn.HomePage(tmp_home_page, 'extra parameter')

    def test_create_home_page_invalid_filename(self, tmp_page):
        with pytest.raises(ValueError):
            pn.HomePage(tmp_page)

    @pytest.mark.parametrize('filename', invalid_filenames('home'))
    def test_create_home_page_invalid_file_types(
            self, tmp_file_factory, filename):
        with pytest.raises(ValueError):
            pn.HomePage(tmp_file_factory(filename))

    def test_create_readme_page(self, tmp_readme_page):
        test_page = pn.ReadmePage(tmp_readme_page)
        assert isinstance(test_page, pn.ReadmePage)

    def test_create_readme_page_path(self, tmp_readme_page):
        test_page = pn.ReadmePage(tmp_readme_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert test_page.path == tmp_readme_page

    def test_create_readme_page_content(self, tmp_readme_page):
        test_page = pn.ReadmePage(tmp_readme_page)
        assert isinstance(test_page.content, list)
        self.assert_page_contents_match(test_page, tmp_readme_page)

    def test_create_readme_page_null(self):
        test_page = pn.ReadmePage()
        assert test_page.path is None
        assert test_page.content is None

    def test_create_readme_page_no_changes(self, cloned_repo):
        page_path = (pathlib.Path(cloned_repo.working_dir)
                     .joinpath(self.cloned_readme_page))
        pn.ReadmePage(page_path)
        self.assert_repo_unchanged(cloned_repo)

    def test_create_readme_page_no_output(self, tmp_readme_page, capsys):
        pn.ReadmePage(tmp_readme_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_create_readme_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.ReadmePage(path)

    def test_create_readme_page_extra_parameter(self, tmp_readme_page):
        with pytest.raises(TypeError):
            pn.ReadmePage(tmp_readme_page, 'extra parameter')

    def test_create_readme_page_invalid_filename(self, tmp_page):
        with pytest.raises(ValueError):
            pn.ReadmePage(tmp_page)

    @pytest.mark.parametrize('filename', invalid_filenames('readme'))
    def test_create_readme_page_invalid_file_types(
            self, tmp_file_factory, filename):
        with pytest.raises(ValueError):
            pn.ReadmePage(tmp_file_factory(filename))

    def test_create_logbook_readme_page(self, tmp_logbook_readme_page):
        test_page = pn.ReadmePage(tmp_logbook_readme_page)
        assert isinstance(test_page, pn.ReadmePage)

    def test_create_logbook_readme_page_path(self, tmp_logbook_readme_page):
        test_page = pn.ReadmePage(tmp_logbook_readme_page)
        assert isinstance(test_page.path, pathlib.Path)
        assert test_page.path == tmp_logbook_readme_page

    def test_create_logbook_readme_page_content(self, tmp_logbook_readme_page):
        test_page = pn.ReadmePage(tmp_logbook_readme_page)
        assert isinstance(test_page.content, list)
        self.assert_page_contents_match(test_page, tmp_logbook_readme_page)

    def test_create_logbook_readme_page_no_changes(self, cloned_repo):
        page_path = (pathlib.Path(cloned_repo.working_dir)
                     .joinpath(self.cloned_logbook_readme_page))
        pn.ReadmePage(page_path)
        self.assert_repo_unchanged(cloned_repo)

    def test_create_logbook_readme_page_no_output(
            self, tmp_logbook_readme_page, capsys):
        pn.ReadmePage(tmp_logbook_readme_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    # Loading data to page objects
    def test_page_load_content(self, tmp_page):
        test_page = pn.Page()
        test_page.path = tmp_page
        test_page.load_content()
        self.assert_page_contents_match(test_page, tmp_page)

    def test_page_load_content_null(self):
        test_page = pn.Page()
        test_page.path = None
        test_page.load_content()
        assert test_page.content is None

    def test_page_load_contents_no_changes(self, cloned_repo):
        test_page = pn.Page()
        test_page.path = (pathlib.Path(cloned_repo.working_dir)
                          .joinpath(self.cloned_page))
        test_page.load_content()
        self.assert_repo_unchanged(cloned_repo)

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

    def test_page_load_content_extra_parameter(self, tmp_page):
        test_page = pn.Page()
        with pytest.raises(TypeError):
            test_page.load_content('extra parameter')

    @pytest.mark.parametrize('filename', invalid_filenames('page'))
    def test_page_load_content_invalid_file_types(
            self, tmp_file_factory, filename):
        test_page = pn.Page()
        test_page.path = tmp_file_factory(filename)
        with pytest.raises(ValueError):
            test_page.load_content()

    def test_logbook_page_load_content(self, tmp_logbook_page):
        test_logbook_page = pn.LogbookPage()
        test_logbook_page.path = tmp_logbook_page
        test_logbook_page.load_content()
        assert isinstance(test_logbook_page.content, list)
        self.assert_page_contents_match(test_logbook_page, tmp_logbook_page)

    def test_logbook_page_load_content_null(self):
        test_logbook_page = pn.LogbookPage()
        test_logbook_page.path = None
        test_logbook_page.load_content()
        assert test_logbook_page.content is None

    def test_logbook_page_load_contents_no_changes(self, cloned_repo):
        test_logbook_page = pn.LogbookPage()
        test_logbook_page.path = (pathlib.Path(cloned_repo.working_dir)
                                  .joinpath(self.cloned_logbook_page))
        test_logbook_page.load_content()
        self.assert_repo_unchanged(cloned_repo)

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

    def test_logbook_page_load_content_extra_parameter(self, tmp_logbook_page):
        test_logbook_page = pn.LogbookPage()
        with pytest.raises(TypeError):
            test_logbook_page.load_content('extra parameter')

    @pytest.mark.parametrize('filename', invalid_filenames('logbook page'))
    def test_logbook_page_load_content_invalid_file_types(
            self, tmp_file_factory, filename):
        test_page = pn.LogbookPage()
        test_page.path = tmp_file_factory(filename)
        with pytest.raises(ValueError):
            test_page.load_content()

    def test_contents_page_load_content(self, tmp_contents_page):
        test_page = pn.ContentsPage()
        test_page.path = tmp_contents_page
        test_page.load_content()
        assert isinstance(test_page.content, list)
        self.assert_page_contents_match(test_page, tmp_contents_page)

    def test_contents_page_load_content_null(self):
        test_page = pn.ContentsPage()
        test_page.path = None
        test_page.load_content()
        assert test_page.path is None
        assert test_page.content is None

    def test_contents_page_load_contents_no_changes(self, cloned_repo):
        test_page = pn.ContentsPage()
        test_page.path = (pathlib.Path(cloned_repo.working_dir)
                          .joinpath(self.cloned_contents_page))
        test_page.load_content()
        self.assert_repo_unchanged(cloned_repo)

    def test_contents_page_load_content_no_output(
            self, tmp_contents_page, capsys):
        test_page = pn.ContentsPage()
        test_page.path = tmp_contents_page
        test_page.load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_contents_page_load_content_extra_parameter(self, tmp_contents_page):
        test_page = pn.ContentsPage()
        test_page.path = tmp_contents_page
        with pytest.raises(TypeError):
            test_page.load_content('extra parameter')

    def test_contents_page_load_content_invalid_filename(self, tmp_page):
        test_page = pn.ContentsPage()
        test_page.path = tmp_page
        with pytest.raises(ValueError):
            test_page.load_content()

    @pytest.mark.parametrize('filename', invalid_filenames('contents'))
    def test_contents_page_load_content_invalid_file_types(
            self, tmp_file_factory, filename):
        test_page = pn.ContentsPage()
        test_page.path = tmp_file_factory(filename)
        with pytest.raises(ValueError):
            test_page.load_content()

    def test_logbook_contents_page_load_content(self, tmp_logbook_contents_page):
        test_page = pn.ContentsPage()
        test_page.path = tmp_logbook_contents_page
        test_page.load_content()
        assert isinstance(test_page.content, list)
        self.assert_page_contents_match(test_page, tmp_logbook_contents_page)

    def test_logbook_contents_page_load_contents_no_changes(self, cloned_repo):
        test_page = pn.ContentsPage()
        test_page.path = (pathlib.Path(cloned_repo.working_dir)
                          .joinpath(self.cloned_logbook_contents_page))
        test_page.load_content()
        self.assert_repo_unchanged(cloned_repo)

    def test_logbook_contents_page_load_content_no_output(
            self, tmp_logbook_contents_page, capsys):
        test_page = pn.ContentsPage()
        test_page.path = tmp_logbook_contents_page
        test_page.load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_contents_page_load_contents_extra_parameter(
            self, tmp_logbook_contents_page):
        test_page = pn.ContentsPage()
        test_page.path = tmp_logbook_contents_page
        with pytest.raises(TypeError):
            test_page.load_content('extra parameter')

    def test_home_page_load_content(self, tmp_home_page):
        test_page = pn.HomePage()
        test_page.path = tmp_home_page
        test_page.load_content()
        assert isinstance(test_page.content, list)
        self.assert_page_contents_match(test_page, tmp_home_page)

    def test_home_page_load_content_null(self):
        test_page = pn.HomePage()
        test_page.path = None
        test_page.load_content()
        assert test_page.path is None
        assert test_page.content is None

    def test_home_page_load_contents_no_changes(self, cloned_repo):
        test_page = pn.HomePage()
        test_page.path = (pathlib.Path(cloned_repo.working_dir)
                          .joinpath(self.cloned_home_page))
        test_page.load_content()
        self.assert_repo_unchanged(cloned_repo)

    def test_home_page_load_content_no_output(self, tmp_home_page, capsys):
        test_page = pn.HomePage()
        test_page.path = tmp_home_page
        test_page.load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_home_page_load_content_extra_parameter(self, tmp_home_page):
        test_page = pn.HomePage()
        test_page.path = tmp_home_page
        with pytest.raises(TypeError):
            test_page.load_content('extra parameter')

    def test_home_page_load_content_invalid_filename(self, tmp_page):
        test_page = pn.HomePage()
        test_page.path = tmp_page
        with pytest.raises(ValueError):
            test_page.load_content()

    @pytest.mark.parametrize('filename', invalid_filenames('home'))
    def test_home_page_load_content_invalid_file_types(
            self, tmp_file_factory, filename):
        test_page = pn.HomePage()
        test_page.path = tmp_file_factory(filename)
        with pytest.raises(ValueError):
            test_page.load_content()

    def test_readme_page_load_content(self, tmp_readme_page):
        test_page = pn.ReadmePage()
        test_page.path = tmp_readme_page
        test_page.load_content()
        assert isinstance(test_page.content, list)
        self.assert_page_contents_match(test_page, tmp_readme_page)

    def test_readme_page_load_content_null(self):
        test_page = pn.ReadmePage()
        test_page.path = None
        test_page.load_content()
        assert test_page.path is None
        assert test_page.content is None

    def test_readme_page_load_contents_no_changes(self, cloned_repo):
        test_page = pn.ReadmePage()
        test_page.path = (pathlib.Path(cloned_repo.working_dir)
                          .joinpath(self.cloned_readme_page))
        test_page.load_content()
        self.assert_repo_unchanged(cloned_repo)

    def test_readme_page_load_content_no_output(self, tmp_readme_page, capsys):
        test_page = pn.ReadmePage()
        test_page.path = tmp_readme_page
        test_page.load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_readme_page_load_content_extra_parameter(self, tmp_readme_page):
        test_page = pn.ReadmePage()
        test_page.path = tmp_readme_page
        with pytest.raises(TypeError):
            test_page.load_content('extra parameter')

    def test_readme_page_load_content_invalid_filename(self, tmp_page):
        test_page = pn.ReadmePage()
        test_page.path = tmp_page
        with pytest.raises(ValueError):
            test_page.load_content()

    @pytest.mark.parametrize('filename', invalid_filenames('readme'))
    def test_readme_page_load_content_invalid_file_types(
            self, tmp_file_factory, filename):
        test_page = pn.ReadmePage()
        test_page.path = tmp_file_factory(filename)
        with pytest.raises(ValueError):
            test_page.load_content()

    def test_logbook_readme_page_load_content(self, tmp_logbook_readme_page):
        test_page = pn.ReadmePage()
        test_page.path = tmp_logbook_readme_page
        test_page.load_content()
        assert isinstance(test_page.content, list)
        self.assert_page_contents_match(test_page, tmp_logbook_readme_page)

    def test_logbook_readme_page_load_contents_no_changes(self, cloned_repo):
        test_page = pn.ReadmePage()
        test_page.path = (pathlib.Path(cloned_repo.working_dir)
                          .joinpath(self.cloned_logbook_readme_page))
        test_page.load_content()
        self.assert_repo_unchanged(cloned_repo)

    def test_logbook_readme_page_load_content_no_output(
            self, tmp_logbook_readme_page, capsys):
        test_page = pn.ReadmePage()
        test_page.path = tmp_logbook_readme_page
        test_page.load_content()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_readme_page_load_content_extra_parameter(
            self, tmp_logbook_readme_page):
        test_page = pn.ReadmePage()
        test_page.path = tmp_logbook_readme_page
        with pytest.raises(TypeError):
            test_page.load_content('extra parameter')


    # Getting information from page objects
    def test_page_get_title(self, tmp_page):
        test_title = pn.Page(tmp_page).get_title()
        assert isinstance(test_title, str)
        assert test_title == self.test_title

    def test_page_get_title_null(self, tmp_page):
        test_title = pn.Page().get_title()
        assert test_title is None

    def test_page_get_title_no_changes(self, cloned_repo):
        test_page = pn.Page(pathlib.Path(cloned_repo.working_dir)
                            .joinpath(self.cloned_page))
        test_page.get_title()
        self.assert_repo_unchanged(cloned_repo)

    def test_page_get_title_no_output(self, tmp_page, capsys):
        pn.Page(tmp_page).get_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_page_get_title_extra_parameter(self, tmp_page):
        with pytest.raises(TypeError):
            pn.Page(tmp_page).get_title('extra parameter')

    def test_logbook_page_get_title(self, tmp_logbook_page):
        test_title = pn.LogbookPage(tmp_logbook_page).get_title()
        assert isinstance(test_title, str)
        assert test_title == self.temp_logbook_page.strip()

    def test_logbook_page_get_title_null(self):
        test_title = pn.LogbookPage().get_title()
        assert test_title is None

    def test_logbook_page_get_title_no_changes(self, cloned_repo):
        test_page = pn.LogbookPage(pathlib.Path(cloned_repo.working_dir)
                                   .joinpath(self.cloned_logbook_page))
        test_page.get_title()
        self.assert_repo_unchanged(cloned_repo)

    def test_logbook_page_get_title_no_output(self, tmp_logbook_page, capsys):
        pn.LogbookPage(tmp_logbook_page).get_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_page_get_title_extra_parameter(self, tmp_logbook_page):
        with pytest.raises(TypeError):
            pn.LogbookPage(tmp_logbook_page).get_title('extra parameter')

    def test_contents_page_get_title(self, tmp_contents_page):
        test_title = pn.ContentsPage(tmp_contents_page).get_title()
        assert isinstance(test_title, str)
        assert test_title == self.contents_filename

    def test_contents_page_get_title_null(self):
        test_title = pn.ContentsPage().get_title()
        assert test_title == self.contents_filename

    def test_contents_page_get_title_no_changes(self, cloned_repo):
        test_page = pn.ContentsPage(pathlib.Path(cloned_repo.working_dir)
                                    .joinpath(self.cloned_contents_page))
        test_page.get_title()
        self.assert_repo_unchanged(cloned_repo)

    def test_contents_page_get_title_no_output(self, tmp_contents_page, capsys):
        pn.ContentsPage(tmp_contents_page).get_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_contents_page_get_title_extra_parameter(self, tmp_contents_page):
        with pytest.raises(TypeError):
            pn.ContentsPage(tmp_contents_page).get_title('extra parameter')

    def test_home_page_get_title(self, tmp_home_page):
        test_title = pn.HomePage(tmp_home_page).get_title()
        assert isinstance(test_title, str)
        assert test_title == self.homepage_filename

    def test_home_page_get_title_null(self):
        test_title = pn.HomePage().get_title()
        assert test_title == self.homepage_filename

    def test_home_page_get_title_no_changes(self, cloned_repo):
        test_page = pn.HomePage(pathlib.Path(cloned_repo.working_dir)
                                .joinpath(self.cloned_home_page))
        test_page.get_title()
        self.assert_repo_unchanged(cloned_repo)

    def test_home_page_get_title_no_output(self, tmp_home_page, capsys):
        pn.HomePage(tmp_home_page).get_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_home_page_get_title_extra_parameter(self, tmp_home_page):
        with pytest.raises(TypeError):
            pn.HomePage(tmp_home_page).get_title('extra parameter')

    def test_readme_page_get_title(self, tmp_readme_page):
        test_title = pn.ReadmePage(tmp_readme_page).get_title()
        assert isinstance(test_title, str)
        assert test_title == self.readme_filename

    def test_readme_page_get_title_null(self):
        test_title = pn.ReadmePage().get_title()
        assert test_title == self.readme_filename

    def test_readme_page_get_title_no_changes(self, cloned_repo):
        test_page = pn.ReadmePage(pathlib.Path(cloned_repo.working_dir)
                                  .joinpath(self.cloned_readme_page))
        test_page.get_title()
        self.assert_repo_unchanged(cloned_repo)

    def test_readme_page_get_title_no_output(self, tmp_readme_page, capsys):
        pn.ReadmePage(tmp_readme_page).get_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_readme_page_get_title_extra_parameter(self, tmp_readme_page):
        with pytest.raises(TypeError):
            pn.ReadmePage(tmp_readme_page).get_title('extra parameter')

    def test_page_is_valid_page(self, tmp_page):
        assert pn.Page()._is_valid_page(tmp_page) is True

    def test_page_is_valid_page_logbook_page(self, tmp_logbook_page):
        assert pn.Page()._is_valid_page(tmp_logbook_page) is True

    def test_page_is_valid_page_contents_page(self, tmp_contents_page):
        assert pn.Page()._is_valid_page(tmp_contents_page) is True

    def test_page_is_valid_page_home_page(self, tmp_home_page):
        assert pn.Page()._is_valid_page(tmp_home_page) is True

    def test_page_is_valid_page_readme_page(self, tmp_readme_page):
        assert pn.Page()._is_valid_page(tmp_readme_page) is True

    @pytest.mark.parametrize('filename', invalid_filenames('page'))
    def test_page_is_valid_page_invalid_file_types(
            self, tmp_file_factory, filename):
        assert pn.Page()._is_valid_page(tmp_file_factory(filename)) is False

    def test_page_is_valid_page_invalid_file(self, tmp_file_factory):
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            pn.Page()._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))

    def test_page_is_valid_page_no_changes(self, cloned_repo):
        pn.Page()._is_valid_page(pathlib.Path(cloned_repo.working_dir)
                                 .joinpath(self.cloned_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_page_is_valid_page_no_output(self, tmp_page, capsys):
        pn.Page()._is_valid_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_page_is_valid_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Page()._is_valid_page(path)

    def test_page_is_valid_page_extra_parameter(self, tmp_page):
        with pytest.raises(TypeError):
            pn.Page()._is_valid_page(tmp_page, 'extra parameter')

    def test_logbook_page_is_valid_page(self, tmp_logbook_page):
        assert pn.LogbookPage()._is_valid_page(tmp_logbook_page) is True

    def test_logbook_page_is_valid_page_notebook_page(self, tmp_page):
        assert pn.LogbookPage()._is_valid_page(tmp_page) is False

    def test_logbook_page_is_valid_page_logbook_page(self, tmp_logbook_page):
        assert pn.LogbookPage()._is_valid_page(tmp_logbook_page) is True

    def test_logbook_page_is_valid_page_contents_page(self, tmp_contents_page):
        assert pn.LogbookPage()._is_valid_page(tmp_contents_page) is False

    def test_logbook_page_is_valid_page_home_page(self, tmp_home_page):
        assert pn.LogbookPage()._is_valid_page(tmp_home_page) is False

    def test_logbook_page_is_valid_page_readme_page(self, tmp_readme_page):
        assert pn.LogbookPage()._is_valid_page(tmp_readme_page) is False

    @pytest.mark.parametrize('filename', invalid_filenames('logbook page'))
    def test_logbook_page_is_valid_page_invalid_file_types(
            self, tmp_file_factory, filename):
        assert pn.LogbookPage()._is_valid_page(
            tmp_file_factory(filename)) is False

    def test_logbook_page_is_valid_page_invalid_file(self, tmp_file_factory):
        tmp_file = tmp_file_factory('is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            pn.LogbookPage()._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))

    def test_logbook_page_is_valid_page_no_changes(self, cloned_repo):
        test_page = pn.LogbookPage()
        test_page._is_valid_page(pathlib.Path(cloned_repo.working_dir)
                                 .joinpath(self.cloned_logbook_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_logbook_page_is_valid_page_no_output(
            self, tmp_logbook_page, capsys):
        pn.LogbookPage()._is_valid_page(tmp_logbook_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_logbook_page_is_valid_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.LogbookPage()._is_valid_page(path)

    def test_logbook_page_is_valid_page_extra_parameter(self, tmp_logbook_page):
        with pytest.raises(TypeError):
            pn.LogbookPage()._is_valid_page(tmp_logbook_page, 'extra parameter')

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

    @pytest.mark.parametrize('filename', invalid_filenames('contents'))
    def test_contents_page_is_valid_page_invalid_file_types(
            self, tmp_file_factory, filename):
        assert pn.ContentsPage()._is_valid_page(
            tmp_file_factory(filename)) is False

    def test_contents_page_is_valid_page_invalid_file(self, tmp_file_factory):
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            pn.ContentsPage()._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))

    def test_contents_page_is_valid_page_no_changes(self, cloned_repo):
        test_page = pn.ContentsPage()
        test_page._is_valid_page(pathlib.Path(cloned_repo.working_dir)
                                 .joinpath(self.cloned_contents_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_contents_page_is_valid_page_no_output(
            self, tmp_contents_page, capsys):
        pn.ContentsPage()._is_valid_page(tmp_contents_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_contents_page_is_valid_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.ContentsPage()._is_valid_page(path)

    def test_contents_page_is_valid_page_extra_parameter(
            self, tmp_contents_page):
        with pytest.raises(TypeError):
            pn.ContentsPage()._is_valid_page(
                tmp_contents_page, 'extra parameter')

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

    @pytest.mark.parametrize('filename', invalid_filenames('home'))
    def test_home_page_is_valid_page_invalid_file_types(
            self, tmp_file_factory, filename):
        assert pn.HomePage()._is_valid_page(tmp_file_factory(filename)) is False

    def test_home_page_is_valid_page_invalid_file(self, tmp_file_factory):
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            pn.HomePage()._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))

    def test_home_page_is_valid_page_no_changes(self, cloned_repo):
        test_page = pn.HomePage()
        test_page._is_valid_page(pathlib.Path(cloned_repo.working_dir)
                                 .joinpath(self.cloned_home_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_home_page_is_valid_page_no_output(self, tmp_home_page, capsys):
        pn.HomePage()._is_valid_page(tmp_home_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_home_page_is_valid_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.HomePage()._is_valid_page(path)

    def test_home_page_is_valid_page_extra_parameter(self, tmp_home_page):
        with pytest.raises(TypeError):
            pn.HomePage()._is_valid_page(tmp_home_page, 'extra parameter')

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

    @pytest.mark.parametrize('filename', invalid_filenames('readme'))
    def test_readme_page_is_valid_page_invalid_file_types(
            self, tmp_file_factory, filename):
        assert pn.ReadmePage()._is_valid_page(
            tmp_file_factory(filename)) is False

    def test_readme_page_is_valid_page_invalid_file(self, tmp_file_factory):
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            pn.ReadmePage()._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))

    def test_readme_page_is_valid_page_no_changes(self, cloned_repo):
        test_page = pn.ReadmePage()
        test_page._is_valid_page(pathlib.Path(cloned_repo.working_dir)
                                 .joinpath(self.cloned_readme_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_readme_page_is_valid_page_no_output(
            self, tmp_readme_page, capsys):
        pn.ReadmePage()._is_valid_page(tmp_readme_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_readme_page_is_valid_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.ReadmePage()._is_valid_page(path)

    def test_readme_page_is_valid_page_extra_parameter(self, tmp_readme_page):
        with pytest.raises(TypeError):
            pn.ReadmePage()._is_valid_page(tmp_readme_page, 'extra parameter')

    def test_page_convert_filename_to_title(self, tmp_page):
        test_title = pn.Page(tmp_page)._convert_filename_to_title()
        assert isinstance(test_title, str)
        expected = tmp_page.stem.replace('_', ' ').replace('-', ' ').strip()
        assert test_title == expected

    def test_page_convert_filename_to_title_null(self):
        test_title = pn.Page()._convert_filename_to_title()
        assert test_title is None

    def test_page_convert_filename_to_title_no_changes(self, cloned_repo):
        test_page = pn.Page(pathlib.Path(cloned_repo.working_dir)
                            .joinpath(self.cloned_page))
        test_page._convert_filename_to_title()
        self.assert_repo_unchanged(cloned_repo)

    def test_page_convert_filename_to_title_no_output(self, tmp_page, capsys):
        pn.Page(tmp_page)._convert_filename_to_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_page_convert_filename_to_title_extra_parameter(self, tmp_page):
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

    def test_logbook_page_convert_filename_to_title_no_changes(self, cloned_repo):
        test_page = pn.LogbookPage(pathlib.Path(cloned_repo.working_dir)
                                   .joinpath(self.cloned_logbook_page))
        test_page._convert_filename_to_title()
        self.assert_repo_unchanged(cloned_repo)

    def test_logbook_page_convert_filename_to_title_no_output(
            self, tmp_logbook_page, capsys):
        pn.LogbookPage(tmp_logbook_page)._convert_filename_to_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_page_convert_filename_to_title_extra_parameter(
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

    def test_contents_page_convert_filename_to_title_no_changes(self, cloned_repo):
        test_page = pn.ContentsPage(pathlib.Path(cloned_repo.working_dir)
                                   .joinpath(self.cloned_contents_page))
        test_page._convert_filename_to_title()
        self.assert_repo_unchanged(cloned_repo)

    def test_contents_page_convert_filename_to_title_no_output(
            self, tmp_contents_page, capsys):
        pn.ContentsPage(tmp_contents_page)._convert_filename_to_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_contents_page_convert_filename_to_title_extra_parameter(
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

    def test_home_page_convert_filename_to_title_no_changes(self, cloned_repo):
        test_page = pn.HomePage(pathlib.Path(cloned_repo.working_dir)
                                   .joinpath(self.cloned_home_page))
        test_page._convert_filename_to_title()
        self.assert_repo_unchanged(cloned_repo)

    def test_home_page_convert_filename_to_title_no_output(
            self, tmp_home_page, capsys):
        pn.HomePage(tmp_home_page)._convert_filename_to_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_home_page_convert_filename_to_title_extra_parameter(
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

    def test_readme_page_convert_filename_to_title_no_changes(self, cloned_repo):
        test_page = pn.ReadmePage(pathlib.Path(cloned_repo.working_dir)
                                   .joinpath(self.cloned_readme_page))
        test_page._convert_filename_to_title()
        self.assert_repo_unchanged(cloned_repo)

    def test_readme_page_convert_filename_to_title_no_output(
            self, tmp_readme_page, capsys):
        pn.ReadmePage(tmp_readme_page)._convert_filename_to_title()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_readme_page_convert_filename_to_title_extra_parameter(
            self, tmp_readme_page):
        with pytest.raises(TypeError):
            (pn.ReadmePage(tmp_readme_page)
                ._convert_filename_to_title('extra parameter'))


    # Creating notebook objects
    def test_create_notebook(self, tmp_notebook):
        test_notebook = pn.Notebook(tmp_notebook)
        assert isinstance(test_notebook, pn.Notebook)

    def test_create_notebook_path(self, tmp_notebook):
        test_notebook = pn.Notebook(tmp_notebook)
        assert isinstance(test_notebook.path, pathlib.Path)
        assert test_notebook.path == tmp_notebook

    def test_create_notebook_contents(self, tmp_notebook):
        test_notebook = pn.Notebook(tmp_notebook)
        self.assert_notebook_contents_match(test_notebook, tmp_notebook)

    def test_create_notebook_no_changes(self, cloned_repo):
        notebook_path = pathlib.Path(cloned_repo.working_dir)
        pn.Notebook(notebook_path)
        self.assert_repo_unchanged(cloned_repo)

    def test_create_notebook_null(self):
        test_notebook = pn.Notebook()
        assert isinstance(test_notebook, pn.Notebook)
        assert test_notebook.path is None
        assert test_notebook.contents == []

    def test_create_notebook_no_output(self, tmp_notebook, capsys):
        pn.Notebook(tmp_notebook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_create_notebook_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Notebook(path)

    def test_create_notebook_extra_parameter(self, tmp_notebook):
        with pytest.raises(TypeError):
            pn.Notebook(tmp_notebook, 'extra parameter')

    def test_create_logbook(self, tmp_logbook):
        test_logbook = pn.Logbook(tmp_logbook)
        assert isinstance(test_logbook, pn.Logbook)

    def test_create_logbook_path(self, tmp_logbook):
        test_logbook = pn.Logbook(tmp_logbook)
        assert isinstance(test_logbook.path, pathlib.Path)
        assert test_logbook.path == tmp_logbook

    def test_create_logbook_contents(self, tmp_logbook):
        test_logbook = pn.Logbook(tmp_logbook)
        self.assert_logbook_contents_match(test_logbook, tmp_logbook)

    def test_create_logbook_no_changes(self, cloned_repo):
        logbook_path = (pathlib.Path(cloned_repo.working_dir)
                        .joinpath('PKU-2019/Logbook'))
        pn.Logbook(logbook_path)
        self.assert_repo_unchanged(cloned_repo)

    def test_create_logbook_null(self):
        test_logbook = pn.Logbook()
        assert isinstance(test_logbook, pn.Logbook)
        assert test_logbook.path is None
        assert test_logbook.contents == []

    def test_create_logbook_no_output(self, tmp_logbook, capsys):
        pn.Logbook(tmp_logbook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_create_logbook_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Logbook(path)

    def test_create_logbook_extra_parameter(self, tmp_logbook):
        with pytest.raises(TypeError):
            pn.Logbook(tmp_logbook, 'extra parameter')

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
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Page)

    def test_notebook_add_page_path(self, tmp_page):
        test_notebook = pn.Notebook()
        test_notebook.add_page(tmp_page)
        assert tmp_page in [this_page.path
                            for this_page in test_notebook.contents]
        last_item = test_notebook.contents[-1]
        assert last_item.path == tmp_page

    def test_notebook_add_page_contents(self, tmp_page):
        test_notebook = pn.Notebook()
        test_notebook.add_page(tmp_page)
        last_item = test_notebook.contents[-1]
        self.assert_page_contents_match(last_item, tmp_page)

    def test_notebook_add_page_null(self):
        test_notebook = pn.Notebook()
        test_notebook.add_page()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_notebook_add_page_no_changes(self, cloned_repo):
        test_notebook = pn.Notebook()
        test_notebook.add_page(pathlib.Path(cloned_repo.working_dir)
                               .joinpath(self.cloned_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_notebook_add_page_no_output(self, tmp_page, capsys):
        pn.Notebook().add_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_page_null_no_output(self, capsys):
        pn.Notebook().add_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_notebook_add_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Notebook().add_page(path)

    def test_notebook_add_page_extra_parameter(self, tmp_page):
        with pytest.raises(TypeError):
            pn.Notebook().add_page(tmp_page, 'extra parameter')

    @pytest.mark.parametrize('filename', invalid_filenames('page'))
    def test_notebook_add_page_invalid_file_types(
            self, tmp_file_factory, filename):
        with pytest.raises(ValueError):
            pn.Notebook().add_page(tmp_file_factory(filename))

    def test_logbook_add_page(self, tmp_logbook_page):
        test_logbook = pn.Logbook()
        test_logbook.add_page(tmp_logbook_page)
        assert isinstance(test_logbook.contents, list)
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.LogbookPage)

    def test_logbook_add_page_path(self, tmp_logbook_page):
        test_logbook = pn.Logbook()
        test_logbook.add_page(tmp_logbook_page)
        last_item = test_logbook.contents[-1]
        assert last_item.path == tmp_logbook_page

    def test_logbook_add_page_content(self, tmp_logbook_page):
        test_logbook = pn.Logbook()
        test_logbook.add_page(tmp_logbook_page)
        last_item = test_logbook.contents[-1]
        self.assert_page_contents_match(last_item, tmp_logbook_page)

    def test_logbook_add_page_null(self):
        test_logbook = pn.Logbook()
        test_logbook.add_page()
        assert isinstance(test_logbook.contents, list)
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.LogbookPage)
        assert last_item.path is None
        assert last_item.content is None

    def test_logbook_add_page_no_changes(self, cloned_repo):
        test_logbook = pn.Logbook()
        test_logbook.add_page(pathlib.Path(cloned_repo.working_dir)
                              .joinpath(self.cloned_logbook_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_logbook_add_page_no_output(self, tmp_logbook_page, capsys):
        pn.Logbook().add_page(tmp_logbook_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_page_null_no_output(self, capsys):
        pn.Logbook().add_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_logbook_add_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Logbook().add_page(path)

    def test_logbook_add_page_extra_parameter(self, tmp_logbook_page):
        with pytest.raises(TypeError):
            pn.Logbook().add_page(tmp_logbook_page, 'extra parameter')

    @pytest.mark.parametrize('filename', invalid_filenames('logbook page'))
    def test_logbook_add_page_invalid_file_types(
            self, tmp_file_factory, filename):
        with pytest.raises(ValueError):
            pn.Logbook().add_page(tmp_file_factory(filename))

    def test_notebook_add_contents_page(self, tmp_contents_page):
        test_notebook = pn.Notebook()
        test_notebook.add_contents_page(tmp_contents_page)
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.ContentsPage)

    def test_notebook_add_contents_page_path(self, tmp_contents_page):
        test_notebook = pn.Notebook()
        test_notebook.add_contents_page(tmp_contents_page)
        assert tmp_contents_page in [this_page.path
                                     for this_page in test_notebook.contents]
        last_item = test_notebook.contents[-1]
        assert last_item.path == tmp_contents_page

    def test_notebook_add_contents_page_content(self, tmp_contents_page):
        test_notebook = pn.Notebook()
        test_notebook.add_contents_page(tmp_contents_page)
        last_item = test_notebook.contents[-1]
        self.assert_page_contents_match(last_item, tmp_contents_page)

    def test_notebook_add_contents_page_null(self):
        test_notebook = pn.Notebook()
        test_notebook.add_contents_page()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_notebook_add_contents_page_no_changes(self, cloned_repo):
        test_notebook = pn.Notebook()
        test_notebook.add_contents_page(pathlib.Path(cloned_repo.working_dir)
                                        .joinpath(self.cloned_contents_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_notebook_add_contents_page_no_output(self, tmp_contents_page, capsys):
        pn.Notebook().add_contents_page(tmp_contents_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_contents_page_null_no_output(self, capsys):
        pn.Notebook().add_contents_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_notebook_add_contents_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Notebook().add_contents_page(path)

    def test_notebook_add_contents_page_extra_parameter(self, tmp_contents_page):
        with pytest.raises(TypeError):
            pn.Notebook().add_contents_page(tmp_contents_page, 'extra parameter')

    @pytest.mark.parametrize('filename', invalid_filenames('contents'))
    def test_notebook_add_contents_page_invalid_file_types(
            self, tmp_file_factory, filename):
        with pytest.raises(ValueError):
            pn.Notebook().add_contents_page(tmp_file_factory(filename))

    def test_logbook_add_contents_page(self, tmp_logbook_contents_page):
        test_logbook = pn.Logbook()
        test_logbook.add_contents_page(tmp_logbook_contents_page)
        assert isinstance(test_logbook.contents, list)
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.ContentsPage)

    def test_logbook_add_contents_page_path(self, tmp_logbook_contents_page):
        test_logbook = pn.Logbook()
        test_logbook.add_contents_page(tmp_logbook_contents_page)
        assert tmp_logbook_contents_page in [this_page.path
                                             for this_page
                                             in test_logbook.contents]
        last_item = test_logbook.contents[-1]
        assert last_item.path == tmp_logbook_contents_page

    def test_logbook_add_contents_page_content(self, tmp_logbook_contents_page):
        test_logbook = pn.Logbook()
        test_logbook.add_contents_page(tmp_logbook_contents_page)
        last_item = test_logbook.contents[-1]
        self.assert_page_contents_match(last_item, tmp_logbook_contents_page)

    def test_logbook_add_contents_page_null(self):
        test_logbook = pn.Logbook()
        test_logbook.add_contents_page()
        assert isinstance(test_logbook.contents, list)
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_logbook_add_contents_page_no_changes(self, cloned_repo):
        test_logbook = pn.Logbook()
        test_logbook.add_contents_page(
            pathlib.Path(cloned_repo.working_dir)
            .joinpath(self.cloned_logbook_contents_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_logbook_add_contents_page_no_output(
            self, tmp_logbook_contents_page, capsys):
        pn.Logbook().add_contents_page(tmp_logbook_contents_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_contents_page_null_no_output(self, capsys):
        pn.Logbook().add_contents_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_logbook_add_contents_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Logbook().add_contents_page(path)

    def test_logbook_add_contents_page_extra_parameter(
            self, tmp_logbook_contents_page):
        with pytest.raises(TypeError):
            pn.Logbook().add_contents_page(
                tmp_logbook_contents_page, 'extra parameter')

    @pytest.mark.parametrize('filename', invalid_filenames('contents'))
    def test_logbook_add_contents_page_invalid_file_types(
            self, tmp_file_factory, filename):
        with pytest.raises(ValueError):
            pn.Logbook().add_contents_page(tmp_file_factory(filename))

    def test_notebook_add_home_page(self, tmp_home_page):
        test_notebook = pn.Notebook()
        test_notebook.add_home_page(tmp_home_page)
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.HomePage)

    def test_notebook_add_home_page_path(self, tmp_home_page):
        test_notebook = pn.Notebook()
        test_notebook.add_home_page(tmp_home_page)
        assert tmp_home_page in [this_page.path
                            for this_page in test_notebook.contents]
        last_item = test_notebook.contents[-1]
        assert last_item.path == tmp_home_page

    def test_notebook_add_home_page_content(self, tmp_home_page):
        test_notebook = pn.Notebook()
        test_notebook.add_home_page(tmp_home_page)
        last_item = test_notebook.contents[-1]
        self.assert_page_contents_match(last_item, tmp_home_page)

    def test_notebook_add_home_page_null(self):
        test_notebook = pn.Notebook()
        test_notebook.add_home_page()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_notebook_add_home_page_no_changes(self, cloned_repo):
        test_notebook = pn.Notebook()
        test_notebook.add_home_page(pathlib.Path(cloned_repo.working_dir)
                                    .joinpath(self.cloned_home_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_notebook_add_home_page_no_output(self, tmp_home_page, capsys):
        pn.Notebook().add_home_page(tmp_home_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_home_page_null_no_output(self, capsys):
        pn.Notebook().add_home_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_notebook_add_home_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Notebook().add_home_page(path)

    def test_notebook_add_home_page_extra_parameter(self, tmp_home_page):
        with pytest.raises(TypeError):
            pn.Notebook().add_home_page(tmp_home_page, 'extra parameter')

    @pytest.mark.parametrize('filename', invalid_filenames('home'))
    def test_notebook_add_home_page_invalid_file_types(
            self, tmp_file_factory, filename):
        with pytest.raises(ValueError):
            pn.Notebook().add_home_page(tmp_file_factory(filename))

    def test_logbook_add_home_page(self, tmp_home_page):
        test_logbook = pn.Logbook()
        test_logbook.add_home_page(tmp_home_page)
        assert isinstance(test_logbook.contents, list)
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.HomePage)

    def test_logbook_add_home_page_path(self, tmp_home_page):
        test_logbook = pn.Logbook()
        test_logbook.add_home_page(tmp_home_page)
        assert tmp_home_page in [this_page.path
                            for this_page in test_logbook.contents]
        last_item = test_logbook.contents[-1]
        assert last_item.path == tmp_home_page

    def test_logbook_add_home_page_contents(self, tmp_home_page):
        test_logbook = pn.Logbook()
        test_logbook.add_home_page(tmp_home_page)
        last_item = test_logbook.contents[-1]
        self.assert_page_contents_match(last_item, tmp_home_page)

    def test_logbook_add_home_page_null(self):
        test_logbook = pn.Logbook()
        test_logbook.add_home_page()
        assert isinstance(test_logbook.contents, list)
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_logbook_add_home_page_no_changes(self, cloned_repo):
        test_logbook = pn.Logbook()
        test_logbook.add_home_page(pathlib.Path(cloned_repo.working_dir)
                                   .joinpath(self.cloned_home_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_logbook_add_home_page_no_output(self, tmp_home_page, capsys):
        pn.Logbook().add_home_page(tmp_home_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_home_page_null_no_output(self, capsys):
        pn.Logbook().add_home_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_logbook_add_home_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Logbook().add_home_page(path)

    def test_logbook_add_home_page_extra_parameter(self, tmp_home_page):
        with pytest.raises(TypeError):
            pn.Logbook().add_home_page(tmp_home_page, 'extra parameter')

    @pytest.mark.parametrize('filename', invalid_filenames('home'))
    def test_logbook_add_home_page_invalid_file_types(
            self, tmp_file_factory, filename):
        with pytest.raises(ValueError):
            pn.Logbook().add_home_page(tmp_file_factory(filename))

    def test_notebook_add_readme_page(self, tmp_readme_page):
        test_notebook = pn.Notebook()
        test_notebook.add_readme_page(tmp_readme_page)
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.ReadmePage)

    def test_notebook_add_readme_page_path(self, tmp_readme_page):
        test_notebook = pn.Notebook()
        test_notebook.add_readme_page(tmp_readme_page)
        assert tmp_readme_page in [this_page.path
                            for this_page in test_notebook.contents]
        last_item = test_notebook.contents[-1]
        assert last_item.path == tmp_readme_page

    def test_notebook_add_readme_page_contents(self, tmp_readme_page):
        test_notebook = pn.Notebook()
        test_notebook.add_readme_page(tmp_readme_page)
        last_item = test_notebook.contents[-1]
        self.assert_page_contents_match(last_item, tmp_readme_page)

    def test_notebook_add_readme_page_null(self):
        test_notebook = pn.Notebook()
        test_notebook.add_readme_page()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_notebook_add_readme_page_no_changes(self, cloned_repo):
        test_notebook = pn.Notebook()
        test_notebook.add_readme_page(pathlib.Path(cloned_repo.working_dir)
                                      .joinpath(self.cloned_readme_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_notebook_add_readme_page_no_output(self, tmp_readme_page, capsys):
        pn.Notebook().add_readme_page(tmp_readme_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_readme_page_null_no_output(self, capsys):
        pn.Notebook().add_readme_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_notebook_add_readme_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Notebook().add_readme_page(path)

    def test_notebook_add_readme_page_extra_parameter(self, tmp_readme_page):
        with pytest.raises(TypeError):
            pn.Notebook().add_readme_page(tmp_readme_page, 'extra parameter')

    @pytest.mark.parametrize('filename', invalid_filenames('readme'))
    def test_notebook_add_readme_page_invalid_file_types(
            self, tmp_file_factory, filename):
        with pytest.raises(ValueError):
            pn.Notebook().add_readme_page(tmp_file_factory(filename))

    def test_logbook_add_readme_page(self, tmp_logbook_readme_page):
        test_logbook = pn.Logbook()
        test_logbook.add_readme_page(tmp_logbook_readme_page)
        assert isinstance(test_logbook.contents, list)
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.ReadmePage)

    def test_logbook_add_readme_page_path(self, tmp_logbook_readme_page):
        test_logbook = pn.Logbook()
        test_logbook.add_readme_page(tmp_logbook_readme_page)
        assert tmp_logbook_readme_page in [this_page.path
                                           for this_page
                                           in test_logbook.contents]
        last_item = test_logbook.contents[-1]
        assert last_item.path == tmp_logbook_readme_page

    def test_logbook_add_readme_page_contents(self, tmp_logbook_readme_page):
        test_logbook = pn.Logbook()
        test_logbook.add_readme_page(tmp_logbook_readme_page)
        last_item = test_logbook.contents[-1]
        self.assert_page_contents_match(last_item, tmp_logbook_readme_page)

    def test_logbook_add_readme_page_null(self):
        test_logbook = pn.Logbook()
        test_logbook.add_readme_page()
        assert isinstance(test_logbook.contents, list)
        last_item = test_logbook.contents[-1]
        assert isinstance(last_item, pn.Page)
        assert last_item.path is None
        assert last_item.content is None

    def test_logbook_add_readme_page_no_changes(self, cloned_repo):
        test_logbook = pn.Logbook()
        test_logbook.add_readme_page(pathlib.Path(cloned_repo.working_dir)
                                     .joinpath(self.cloned_logbook_readme_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_logbook_add_readme_page_no_output(
            self, tmp_logbook_readme_page, capsys):
        pn.Logbook().add_readme_page(tmp_logbook_readme_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_add_readme_page_null_no_output(self, capsys):
        pn.Logbook().add_readme_page()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_logbook_add_readme_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Logbook().add_readme_page(path)

    def test_logbook_add_readme_page_extra_parameter(
            self, tmp_logbook_readme_page):
        with pytest.raises(TypeError):
            pn.Logbook().add_readme_page(
                tmp_logbook_readme_page, 'extra parameter')

    @pytest.mark.parametrize('filename', invalid_filenames('readme'))
    def test_logbook_add_readme_page_invalid_file_types(
            self, tmp_file_factory, filename):
        with pytest.raises(ValueError):
            pn.Logbook().add_readme_page(tmp_file_factory(filename))

    def test_notebook_add_notebook(self, tmp_notebook):
        test_notebook = pn.Notebook()
        test_notebook.add_notebook(tmp_notebook)
        assert isinstance(test_notebook.contents, list)
        assert tmp_notebook in [this_item.path
                                for this_item in test_notebook.contents]

    def test_notebook_add_notebook_contents(self, tmp_notebook):
        test_notebook = pn.Notebook()
        test_notebook.add_notebook(tmp_notebook)
        last_item = test_notebook.contents[-1]
        self.assert_notebook_contents_match(last_item, tmp_notebook)

    def test_notebook_add_notebook_null(self):
        test_notebook = pn.Notebook()
        test_notebook.add_notebook()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Notebook)
        assert last_item.path is None
        assert last_item.contents == []

    def test_notebook_add_notebook_no_changes(self, cloned_repo):
        test_notebook = pn.Notebook()
        test_notebook.add_notebook(pathlib.Path(cloned_repo.working_dir)
                                   .joinpath(self.cloned_nested_notebook))
        self.assert_repo_unchanged(cloned_repo)

    def test_notebook_add_notebook_no_output(self, tmp_notebook, capsys):
        pn.Notebook().add_notebook(tmp_notebook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_notebook_null_no_output(self, capsys):
        pn.Notebook().add_notebook()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_notebook_add_notebook_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Notebook().add_notebook(path)

    def test_notebook_add_notebook_extra_parameter(self, tmp_notebook):
        with pytest.raises(TypeError):
            pn.Notebook().add_notebook(tmp_notebook, 'extra parameter')

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

    def test_logbook_add_notebook_no_changes(self, cloned_repo):
        test_logbook = pn.Logbook()
        test_logbook.add_notebook(pathlib.Path(cloned_repo.working_dir)
                                  .joinpath(self.cloned_nested_notebook))
        self.assert_repo_unchanged(cloned_repo)

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

    def test_notebook_add_logbook_contents(self, tmp_logbook):
        test_notebook = pn.Notebook()
        test_notebook.add_logbook(tmp_logbook)
        last_item = test_notebook.contents[-1]
        self.assert_logbook_contents_match(last_item, tmp_logbook)

    def test_notebook_add_logbook_null(self):
        test_notebook = pn.Notebook()
        test_notebook.add_logbook()
        assert isinstance(test_notebook.contents, list)
        last_item = test_notebook.contents[-1]
        assert isinstance(last_item, pn.Notebook)
        assert last_item.path is None
        assert last_item.contents == []

    def test_notebook_add_logbook_no_changes(self, cloned_repo):
        test_notebook = pn.Notebook()
        test_notebook.add_logbook(pathlib.Path(cloned_repo.working_dir)
                                  .joinpath(self.cloned_logbook))
        self.assert_repo_unchanged(cloned_repo)

    def test_notebook_add_logbook_no_output(self, tmp_logbook, capsys):
        pn.Notebook().add_logbook(tmp_logbook)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_add_logbook_null_no_output(self, capsys):
        pn.Notebook().add_logbook()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_notebook_add_logbook_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Notebook().add_logbook(path)

    def test_notebook_add_logbook_extra_parameter(self, tmp_logbook):
        with pytest.raises(TypeError):
            pn.Notebook().add_logbook(tmp_logbook, 'extra parameter')

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

    def test_logbook_add_logbook_no_changes(self, cloned_repo):
        test_logbook = pn.Logbook()
        test_logbook.add_logbook(pathlib.Path(cloned_repo.working_dir)
                                 .joinpath(self.cloned_logbook))
        self.assert_repo_unchanged(cloned_repo)

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
        self.assert_notebook_contents_match(test_notebook, tmp_notebook)

    def test_notebook_load_contents_null(self):
        test_notebook = pn.Notebook()
        test_notebook.path = None
        test_notebook.load_contents()
        assert test_notebook.contents == []

    def test_notebook_load_contents_no_changes(self, cloned_repo):
        test_notebook = pn.Notebook()
        test_notebook.path = pathlib.Path(cloned_repo.working_dir)
        test_notebook.load_contents()
        self.assert_repo_unchanged(cloned_repo)

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

    def test_notebook_load_contents_extra_parameter(self, tmp_logbook_page):
        test_notebook = pn.Notebook()
        with pytest.raises(TypeError):
            test_notebook.load_contents('extra parameter')

    def test_logbook_load_contents(self, tmp_logbook):
        test_logbook = pn.Logbook()
        test_logbook.path = tmp_logbook
        test_logbook.load_contents()
        self.assert_logbook_contents_match(test_logbook, tmp_logbook)

    def test_logbook_load_contents_null(self):
        test_logbook = pn.Logbook()
        test_logbook.path = None
        test_logbook.load_contents()
        assert test_logbook.contents == []

    def test_logbook_load_contents_no_changes(self, cloned_repo):
        test_logbook = pn.Logbook()
        test_logbook.path = (pathlib.Path(cloned_repo.working_dir)
                             .joinpath(self.cloned_logbook))
        test_logbook.load_contents()
        self.assert_repo_unchanged(cloned_repo)

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

    def test_logbook_load_contents_extra_parameter(self, tmp_logbook_page):
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

    @pytest.mark.parametrize('filename', invalid_filenames('page'))
    def test_notebook_is_valid_page_invalid_file_types(
            self, tmp_file_factory, filename):
        assert pn.Notebook()._is_valid_page(tmp_file_factory(filename)) is False

    def test_notebook_is_valid_page_invalid_file(self, tmp_file_factory):
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            pn.Notebook()._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))

    def test_notebook_is_valid_page_no_changes(self, cloned_repo):
        test_notebook = pn.Notebook()
        test_notebook._is_valid_page(pathlib.Path(cloned_repo.working_dir)
                                     .joinpath(self.cloned_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_notebook_is_valid_page_no_output(self, tmp_page, capsys):
        pn.Notebook()._is_valid_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_notebook_is_valid_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Notebook()._is_valid_page(path)

    def test_notebook_is_valid_page_extra_parameter(self, tmp_page):
        with pytest.raises(TypeError):
            pn.Notebook()._is_valid_page(tmp_page, 'extra parameter')

    def test_logbook_is_valid_page(self, tmp_logbook_page):
        test_logbook = pn.Logbook()
        assert test_logbook._is_valid_page(tmp_logbook_page) is True

    def test_logbook_is_valid_page_notebook_page(self, tmp_page):
        test_logbook = pn.Logbook()
        assert test_logbook._is_valid_page(tmp_page) is False

    @pytest.mark.parametrize('filename', invalid_filenames('logbook page'))
    def test_logbook_is_valid_page_invalid_file_types(
            self, tmp_file_factory, filename):
        assert pn.Logbook()._is_valid_page(
            tmp_file_factory(filename)) is False

    def test_logbook_is_valid_page_invalid_file(self, tmp_file_factory):
        tmp_file = tmp_file_factory(f'is-a-file{self.page_suffix}')
        with pytest.raises(OSError):
            pn.Logbook()._is_valid_page(
                tmp_file.parent.joinpath(f'not-a-file{self.page_suffix}'))

    def test_logbook_is_valid_page_no_changes(self, cloned_repo):
        test_logbook = pn.Logbook()
        test_logbook._is_valid_page(pathlib.Path(cloned_repo.working_dir)
                                    .joinpath(self.cloned_logbook_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_logbook_is_valid_page_no_output(self, tmp_page, capsys):
        pn.Logbook()._is_valid_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_logbook_is_valid_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Logbook()._is_valid_page(path)

    def test_logbook_is_valid_page_extra_parameter(self, tmp_page):
        with pytest.raises(TypeError):
            pn.Logbook()._is_valid_page(tmp_page, 'extra parameter')

    def test_notebook_is_valid_folder(self, tmp_path):
        assert pn.Notebook()._is_valid_folder(
            tmp_path) is True

    def test_notebook_is_valid_folder_notebook(self, tmp_notebook):
        assert pn.Notebook()._is_valid_folder(
            tmp_notebook) is True

    def test_notebook_is_valid_folder_logbook(self, tmp_logbook):
        assert pn.Notebook()._is_valid_folder(
            tmp_logbook) is True

    @pytest.mark.parametrize('folder_name', invalid_folders)
    def test_notebook_is_valid_folder_fail(self, tmp_path_factory, folder_name):
        assert pn.Notebook()._is_valid_folder(
            tmp_path_factory.mktemp(folder_name)) is False

    def test_notebook_is_valid_folder_no_changes(self, cloned_repo):
        test_notebook = pn.Notebook()
        test_notebook._is_valid_folder(pathlib.Path(cloned_repo.working_dir))
        self.assert_repo_unchanged(cloned_repo)

    def test_notebook_is_valid_folder_no_output(self, tmp_path, capsys):
        pn.Notebook()._is_valid_folder(tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_notebook_is_valid_folder_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Notebook()._is_valid_folder(path)

    def test_notebook_is_valid_folder_missing_parameter(self):
        with pytest.raises(TypeError):
            pn.Notebook()._is_valid_folder()

    def test_notebook_is_valid_folder_extra_parameter(self, tmp_path):
        with pytest.raises(TypeError):
            pn.Notebook()._is_valid_folder(tmp_path, 'extra parameter')

    def test_logbook_is_valid_folder(self, tmp_path):
        assert pn.Logbook()._is_valid_folder(tmp_path) is False

    def test_logbook_is_valid_folder_notebook(self, tmp_notebook):
        assert pn.Logbook()._is_valid_folder(tmp_notebook) is False

    def test_logbook_is_valid_folder_logbook(self, tmp_logbook):
        assert pn.Logbook()._is_valid_folder(tmp_logbook) is True

    @pytest.mark.parametrize('folder_name', invalid_logbook)
    def test_logbook_is_valid_folder_fail(self, tmp_path_factory, folder_name):
        assert pn.Logbook()._is_valid_folder(
            tmp_path_factory.mktemp(folder_name)) is False

    def test_logbook_is_valid_folder_no_changes(self, cloned_repo):
        test_logbook = pn.Logbook()
        test_logbook._is_valid_folder(pathlib.Path(cloned_repo.working_dir)
                                      .joinpath(self.cloned_logbook))
        self.assert_repo_unchanged(cloned_repo)

    def test_logbook_is_valid_folder_no_output(self, tmp_path, capsys):
        pn.Logbook()._is_valid_folder(tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_logbook_is_valid_folder_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn.Logbook()._is_valid_folder(path)

    def test_logbook_is_valid_folder_missing_parameter(self):
        with pytest.raises(TypeError):
            pn.Logbook()._is_valid_folder()

    def test_logbook_is_valid_folder_extra_parameter(self, tmp_logbook):
        with pytest.raises(TypeError):
            pn.Logbook()._is_valid_folder(tmp_logbook, 'extra parameter')

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
            assert this_path in [page.path for page in test_pages]
        for page in test_pages:
            assert isinstance(page, pn.Page)
            self.assert_page_contents_match(page, self.test_page)

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

    def test_notebook_get_pages_no_changes(self, cloned_repo):
        test_notebook = pn.Notebook(pathlib.Path(cloned_repo.working_dir))
        test_notebook.get_pages()
        self.assert_repo_unchanged(cloned_repo)

    def test_notebook_get_pages_no_output(self, capsys):
        pn.Notebook().get_pages()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_get_pages_extra_parameter(self):
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
            assert this_path in [page.path for page in test_pages]
        for page in test_pages:
            assert isinstance(page, pn.LogbookPage)
            self.assert_page_contents_match(page, self.test_logbook_page)

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

    def test_logbook_get_pages_no_changes(self, cloned_repo):
        test_logbook = pn.Logbook(pathlib.Path(cloned_repo.working_dir)
                                  .joinpath(self.cloned_logbook))
        test_logbook.get_pages()
        self.assert_repo_unchanged(cloned_repo)

    def test_logbook_get_pages_no_output(self, capsys):
        pn.Logbook().get_pages()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_get_pages_extra_parameter(self):
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
        self.assert_notebook_contents_match(nested_notebook, tmp_notebook)

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

    def test_notebook_get_notebooks_no_changes(self, cloned_repo):
        test_notebook = pn.Notebook(pathlib.Path(cloned_repo.working_dir))
        test_notebook.get_notebooks()
        self.assert_repo_unchanged(cloned_repo)

    def test_notebook_get_notebooks_no_output(self, capsys):
        pn.Notebook().get_notebooks()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_get_notebooks_extra_parameter(self):
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

    def test_logbook_get_notebooks_no_changes(self, cloned_repo):
        test_logbook = pn.Logbook(pathlib.Path(cloned_repo.working_dir)
                                  .joinpath(self.cloned_logbook))
        test_logbook.get_notebooks()
        self.assert_repo_unchanged(cloned_repo)

    def test_logbook_get_notebooks_no_output(self, capsys):
        pn.Logbook().get_notebooks()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_get_notebooks_extra_parameter(self):
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
        self.assert_logbook_contents_match(nested_logbook, tmp_logbook)

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

    def test_notebook_get_logbooks_no_changes(self, cloned_repo):
        test_notebook = pn.Notebook(pathlib.Path(cloned_repo.working_dir))
        test_notebook.get_logbooks()
        self.assert_repo_unchanged(cloned_repo)

    def test_notebook_get_logbooks_no_output(self, capsys):
        pn.Notebook().get_logbooks()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_notebook_get_logbooks_extra_parameter(self):
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

    def test_logbook_get_logbooks_no_changes(self, cloned_repo):
        test_logbook = pn.Logbook(pathlib.Path(cloned_repo.working_dir)
                                  .joinpath(self.cloned_logbook))
        test_logbook.get_logbooks()
        self.assert_repo_unchanged(cloned_repo)

    def test_logbook_get_logbooks_no_output(self, capsys):
        pn.Logbook().get_logbooks()
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_logbook_get_logbooks_extra_parameter(self):
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

    def test_is_valid_page_logbook_contents_page(
            self, tmp_logbook_contents_page):
        assert pn._is_valid_page(tmp_logbook_contents_page) is True

    def test_is_valid_page_logbook_month_page(self, tmp_logbook_month_page):
        assert pn._is_valid_page(tmp_logbook_month_page) is True

    def test_is_valid_page_home_page(self, tmp_home_page):
        assert pn._is_valid_page(tmp_home_page) is True

    def test_is_valid_page_readme_page(self, tmp_readme_page):
        assert pn._is_valid_page(tmp_readme_page) is True

    def test_is_valid_page_logbook_readme_page(self, tmp_logbook_readme_page):
        assert pn._is_valid_page(tmp_logbook_readme_page) is True

    @pytest.mark.parametrize('filename', invalid_filenames('page'))
    def test_is_valid_page_fail(self, tmp_file_factory, filename):
        assert pn._is_valid_page(tmp_file_factory(filename)) is False

    def test_is_valid_page_no_changes(self, cloned_repo):
        pn._is_valid_page(pathlib.Path(cloned_repo.working_dir)
                          .joinpath(self.cloned_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_is_valid_page_no_output(self, tmp_page, capsys):
        pn._is_valid_page(tmp_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_is_valid_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn._is_valid_page(path)

    def test_is_valid_page_extra_parameter(self, tmp_page):
        with pytest.raises(TypeError):
            pn._is_valid_page(tmp_page, 'extra parameter')

    def test_is_valid_logbook_page(self, tmp_logbook_page):
        assert pn._is_valid_logbook_page(tmp_logbook_page) is True

    def test_is_valid_logbook_page_notebook_page(self, tmp_page):
        assert pn._is_valid_logbook_page(tmp_page) is False

    def test_is_valid_logbook_page_logbook_page(self, tmp_logbook_page):
        assert pn._is_valid_logbook_page(tmp_logbook_page) is True

    def test_is_valid_logbook_page_contents_page(self, tmp_contents_page):
        assert pn._is_valid_logbook_page(tmp_contents_page) is False

    def test_is_valid_logbook_page_logbook_contents_page(
            self, tmp_logbook_contents_page):
        assert pn._is_valid_logbook_page(tmp_logbook_contents_page) is False

    def test_is_valid_logbook_page_logbook_month_page(
            self, tmp_logbook_month_page):
        assert pn._is_valid_logbook_page(tmp_logbook_month_page) is True

    def test_is_valid_logbook_page_home_page(self, tmp_home_page):
        assert pn._is_valid_logbook_page(tmp_home_page) is False

    def test_is_valid_logbook_page_readme_page(self, tmp_readme_page):
        assert pn._is_valid_logbook_page(tmp_readme_page) is False

    def test_is_valid_logbook_page_logbook_readme_page(
            self, tmp_logbook_readme_page):
        assert pn._is_valid_logbook_page(tmp_logbook_readme_page) is False

    @pytest.mark.parametrize('filename', invalid_filenames('logbook page'))
    def test_is_valid_logbook_page_fail(self, tmp_file_factory, filename):
        assert pn._is_valid_logbook_page(tmp_file_factory(filename)) is False

    def test_is_valid_logbook_page_no_changes(self, cloned_repo):
        pn._is_valid_logbook_page(pathlib.Path(cloned_repo.working_dir)
                                  .joinpath(self.cloned_logbook_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_is_valid_logbook_page_no_output(self, tmp_logbook_page, capsys):
        pn._is_valid_logbook_page(tmp_logbook_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_is_valid_logbook_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn._is_valid_logbook_page(path)

    def test_is_valid_logbook_page_extra_parameter(self, tmp_logbook_page):
        with pytest.raises(TypeError):
            pn._is_valid_logbook_page(tmp_logbook_page, 'extra parameter')

    def test_is_valid_contents_page(self, tmp_contents_page):
        assert pn._is_valid_contents_page(tmp_contents_page) is True

    def test_is_valid_contents_page_notebook_page(self, tmp_page):
        assert pn._is_valid_contents_page(tmp_page) is False

    def test_is_valid_contents_page_logbook_page(self, tmp_logbook_page):
        assert pn._is_valid_contents_page(tmp_logbook_page) is False

    def test_is_valid_contents_page_contents_page(self, tmp_contents_page):
        assert pn._is_valid_contents_page(tmp_contents_page) is True

    def test_is_valid_contents_page_logbook_contents_page(
            self, tmp_logbook_contents_page):
        assert pn._is_valid_contents_page(tmp_logbook_contents_page) is True

    def test_is_valid_contents_page_logbook_month_page(
            self, tmp_logbook_month_page):
        assert pn._is_valid_contents_page(tmp_logbook_month_page) is False

    def test_is_valid_contents_page_home_page(self, tmp_home_page):
        assert pn._is_valid_contents_page(tmp_home_page) is False

    def test_is_valid_contents_page_readme_page(self, tmp_readme_page):
        assert pn._is_valid_contents_page(tmp_readme_page) is False

    def test_is_valid_contents_page_logbook_readme_page(
            self, tmp_logbook_readme_page):
        assert pn._is_valid_contents_page(tmp_logbook_readme_page) is False

    @pytest.mark.parametrize('filename', invalid_filenames('contents'))
    def test_is_valid_contents_page_fail(self, tmp_file_factory, filename):
        assert pn._is_valid_contents_page(tmp_file_factory(filename)) is False

    def test_is_valid_contents_page_no_changes(self, cloned_repo):
        pn._is_valid_contents_page(pathlib.Path(cloned_repo.working_dir)
                                   .joinpath(self.cloned_contents_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_is_valid_contents_page_no_output(self, tmp_contents_page, capsys):
        pn._is_valid_contents_page(tmp_contents_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_is_valid_contents_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn._is_valid_contents_page(path)

    def test_is_valid_contents_page_extra_parameter(self, tmp_contents_page):
        with pytest.raises(TypeError):
            pn._is_valid_contents_page(tmp_contents_page, 'extra parameter')

    def test_is_valid_home_page(self, tmp_home_page):
        assert pn._is_valid_home_page(tmp_home_page) is True

    def test_is_valid_home_page_notebook_page(self, tmp_page):
        assert pn._is_valid_home_page(tmp_page) is False

    def test_is_valid_home_page_logbook_page(self, tmp_logbook_page):
        assert pn._is_valid_home_page(tmp_logbook_page) is False

    def test_is_valid_home_page_contents_page(self, tmp_contents_page):
        assert pn._is_valid_home_page(tmp_contents_page) is False

    def test_is_valid_home_page_logbook_contents_page(
            self, tmp_logbook_contents_page):
        assert pn._is_valid_home_page(tmp_logbook_contents_page) is False

    def test_is_valid_home_page_logbook_month_page(
            self, tmp_logbook_month_page):
        assert pn._is_valid_home_page(tmp_logbook_month_page) is False

    def test_is_valid_home_page_home_page(self, tmp_home_page):
        assert pn._is_valid_home_page(tmp_home_page) is True

    def test_is_valid_home_page_readme_page(self, tmp_readme_page):
        assert pn._is_valid_home_page(tmp_readme_page) is False

    def test_is_valid_home_page_logbook_readme_page(
            self, tmp_logbook_readme_page):
        assert pn._is_valid_home_page(tmp_logbook_readme_page) is False

    @pytest.mark.parametrize('filename', invalid_filenames('home'))
    def test_is_valid_home_page_fail(self, tmp_file_factory, filename):
        assert pn._is_valid_home_page(tmp_file_factory(filename)) is False

    def test_is_valid_home_page_no_changes(self, cloned_repo):
        pn._is_valid_home_page(pathlib.Path(cloned_repo.working_dir)
                               .joinpath(self.cloned_home_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_is_valid_home_page_no_output(self, tmp_home_page, capsys):
        pn._is_valid_home_page(tmp_home_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_is_valid_home_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn._is_valid_home_page(path)

    def test_is_valid_home_page_extra_parameter(self, tmp_home_page):
        with pytest.raises(TypeError):
            pn._is_valid_home_page(tmp_home_page, 'extra parameter')

    def test_is_valid_readme_page(self, tmp_readme_page):
        assert pn._is_valid_readme_page(tmp_readme_page) is True

    def test_is_valid_readme_page_notebook_page(self, tmp_page):
        assert pn._is_valid_readme_page(tmp_page) is False

    def test_is_valid_readme_page_logbook_page(self, tmp_logbook_page):
        assert pn._is_valid_readme_page(tmp_logbook_page) is False

    def test_is_valid_readme_page_contents_page(self, tmp_contents_page):
        assert pn._is_valid_readme_page(tmp_contents_page) is False

    def test_is_valid_readme_page_logbook_contents_page(
            self, tmp_logbook_contents_page):
        assert pn._is_valid_readme_page(tmp_logbook_contents_page) is False

    def test_is_valid_readme_page_logbook_month_page(
            self, tmp_logbook_month_page):
        assert pn._is_valid_readme_page(tmp_logbook_month_page) is False

    def test_is_valid_readme_page_home_page(self, tmp_home_page):
        assert pn._is_valid_readme_page(tmp_home_page) is False

    def test_is_valid_readme_page_readme_page(self, tmp_readme_page):
        assert pn._is_valid_readme_page(tmp_readme_page) is True

    def test_is_valid_readme_page_logbook_readme_page(
            self, tmp_logbook_readme_page):
        assert pn._is_valid_readme_page(tmp_logbook_readme_page) is True

    @pytest.mark.parametrize('filename', invalid_filenames('readme'))
    def test_is_valid_readme_page_fail(self, tmp_file_factory, filename):
        assert pn._is_valid_readme_page(tmp_file_factory(filename)) is False

    def test_is_valid_readme_page_no_changes(self, cloned_repo):
        pn._is_valid_readme_page(pathlib.Path(cloned_repo.working_dir)
                                 .joinpath(self.cloned_readme_page))
        self.assert_repo_unchanged(cloned_repo)

    def test_is_valid_readme_page_no_output(self, tmp_readme_page, capsys):
        pn._is_valid_readme_page(tmp_readme_page)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_is_valid_readme_page_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn._is_valid_readme_page(path)

    def test_is_valid_readme_page_extra_parameter(self, tmp_readme_page):
        with pytest.raises(TypeError):
            pn._is_valid_readme_page(tmp_readme_page, 'extra parameter')

    def test_is_valid_folder(self, tmp_path):
        assert pn._is_valid_folder(tmp_path) is True

    def test_is_valid_folder_notebook(self, tmp_notebook):
        assert pn._is_valid_folder(tmp_notebook) is True

    def test_is_valid_folder_logbook(self, tmp_logbook):
        assert pn._is_valid_folder(tmp_logbook) is True

    @pytest.mark.parametrize('folder_name', invalid_folders)
    def test_is_valid_folder_fail(self, tmp_path_factory, folder_name):
        assert pn._is_valid_folder(
            tmp_path_factory.mktemp(folder_name)) is False

    def test_is_valid_folder_no_changes(self, cloned_repo):
        pn._is_valid_folder(pathlib.Path(cloned_repo.working_dir))
        self.assert_repo_unchanged(cloned_repo)

    def test_is_valid_folder_no_output(self, tmp_path, capsys):
        pn._is_valid_folder(tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_is_valid_folder_page(self, tmp_page):
        with pytest.raises(OSError):
            pn._is_valid_folder(tmp_page)

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_is_valid_folder_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn._is_valid_folder(path)

    def test_is_valid_folder_missing_parameter(self):
        with pytest.raises(TypeError):
            pn._is_valid_folder()

    def test_is_valid_folder_extra_parameter(self, tmp_path):
        with pytest.raises(TypeError):
            pn._is_valid_folder(tmp_path, 'extra parameter')

    def test_is_valid_logbook_folder(self, tmp_path):
        assert pn._is_valid_logbook_folder(tmp_path) is False

    def test_is_valid_logbook_folder_notebook(self, tmp_notebook):
        assert pn._is_valid_logbook_folder(tmp_notebook) is False

    def test_is_valid_logbook_folder_logbook(self, tmp_logbook):
        assert pn._is_valid_logbook_folder(tmp_logbook) is True

    @pytest.mark.parametrize('folder_name', invalid_logbook)
    def test_is_valid_logbook_folder_fail(self, tmp_path_factory, folder_name):
        assert pn._is_valid_logbook_folder(
            tmp_path_factory.mktemp(folder_name)) is False

    def test_is_valid_logbook_folder_no_changes(self, cloned_repo):
        pn._is_valid_logbook_folder(pathlib.Path(cloned_repo.working_dir)
                                    .joinpath(self.cloned_logbook))
        self.assert_repo_unchanged(cloned_repo)

    def test_is_valid_logbook_folder_no_output(self, tmp_path, capsys):
        pn._is_valid_logbook_folder(tmp_path)
        captured = capsys.readouterr()
        assert len(captured.out) == 0

    def test_is_valid_logbook_folder_page(self, tmp_logbook_page):
        with pytest.raises(OSError):
            pn._is_valid_folder(tmp_logbook_page)

    @pytest.mark.parametrize('path, error_type', invalid_paths)
    def test_is_valid_logbook_folder_invalid_input(self, path, error_type):
        with pytest.raises(error_type):
            pn._is_valid_logbook_folder(path)

    def test_is_valid_logbook_folder_missing_parameter(self):
        with pytest.raises(TypeError):
            pn._is_valid_logbook_folder()

    def test_is_valid_logbook_folder_extra_parameter(self, tmp_path):
        with pytest.raises(TypeError):
            pn._is_valid_logbook_folder(tmp_path, 'extra parameter')

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

    @pytest.mark.parametrize('test_line', invalid_lines)
    def test_is_blank_line_invalid_input(self, test_line):
        with pytest.raises(AttributeError):
            pn._is_blank_line(test_line)

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

    @pytest.mark.parametrize('test_line', invalid_lines)
    def test_is_navigation_line_invalid_input(self, test_line):
        with pytest.raises(TypeError):
            pn._is_navigation_line(test_line)

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

    @pytest.mark.parametrize('test_line', invalid_lines)
    def test_is_title_line_invalid_input(self, test_line):
        with pytest.raises(AttributeError):
            pn._is_title_line(test_line)
