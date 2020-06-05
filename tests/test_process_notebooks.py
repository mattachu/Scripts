# Tests process_notebooks.py

import pytest
import shutil
import pathlib

#import process_notebooks

class TestProcessNotebooks:

    # Setup before testing
    def setup_class(self):
        self.notebook_path = (pathlib.Path.home()
                              .joinpath('OneDrive/Documents/Notebooks'))
        self.test_page_contents = 'Hello world'
        self.test_logbook_contents = 'Hello world'


    # Fixtures
    @pytest.fixture
    def tmp_page(self, tmp_path):
        tempfile = tmp_path.joinpath('tempfile.md')
        with open(tempfile, 'w') as f:
            f.write(self.test_page_contents)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture
    def tmp_logbook_page(self, tmp_path):
        tempfile = tmp_path.joinpath('tempfile.md')
        with open(tempfile, 'w') as f:
            f.write(self.test_logbook_contents)
        yield tempfile
        if tempfile.is_file():
            tempfile.unlink()

    @pytest.fixture(scope="class")
    def notebook_copy(self, tmpdir_factory):
        source_path = self.notebook_path.as_posix()
        destination_path = tmpdir_factory.mktemp('data').join('Notebooks')
        tmp_path = shutil.copytree(source_path, destination_path)
        yield pathlib.Path(tmp_path)
        shutil.rmtree(tmp_path)


    # Dummy test
    def test_dummy1(self):
        assert True

    def test_dummy2(self, notebook_copy):
        assert True

    def test_dummy3(self, notebook_copy):
        assert True
