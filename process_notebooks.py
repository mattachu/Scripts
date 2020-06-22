"""Process a set of notebooks to include internal links and contents pages.

Usage:
  process_notebooks.py [<folder>]
  process_notebooks.py --help
"""

from docopt import docopt
import pathlib
import re

# Settings
PAGE_SUFFIX = '.md'
HOME_DESCRIPTOR = 'Home'
HOMEPAGE_FILENAME = 'Home'
CONTENTS_DESCRIPTOR = 'Contents'
CONTENTS_FILENAME = 'Contents'
README_DESCRIPTOR = 'Readme'
README_FILENAME = 'Readme'
LOGBOOK_FOLDER_NAME = 'Logbook'
UNKNOWN_DESCRIPTOR = 'Unknown'

class Page():
    """Standard page in a notebook."""
    _descriptor = 'page'
    def __init__(self, page_file=None, parent=None):
        self.content = None
        self.path = None
        self.parent = None
        if page_file is not None:
            if self._is_valid_page(page_file):
                self.path = page_file
                self.load_content()
            else:
                raise ValueError(f'Not a valid {self._descriptor}: {page_file}')
        if parent is not None:
            if self._is_valid_parent(parent):
                self.parent = parent
            else:
                raise ValueError(f'Received invalid parent object.')

    def load_content(self):
        """Load the content of the page from file."""
        if self.path is None:
            self.content = None
        else:
            if self._is_valid_page(self.path):
                with open(self.path, 'r') as f:
                    self.content = f.readlines()
            else:
                raise ValueError(f'Not a valid page: {self.path}')

    def get_title(self):
        """Find the title of a page."""
        if self.content is not None:
            for line in self.content:
                if _is_blank_line(line) or _is_navigation_line(line):
                    continue
                if _is_title_line(line):
                    return line[2:].strip()
                else:
                    break
        if self.path is not None:
            return self._convert_filename_to_title()
        else:
            return UNKNOWN_DESCRIPTOR

    def get_root(self):
        """Find the top-level notebook."""
        return _get_root(self)

    def _is_valid_page(self, page_file):
        return _is_valid_page(page_file)

    def _is_valid_parent(self, parent):
        return isinstance(parent, Notebook)

    def _convert_filename_to_title(self):
        if self.path is None:
            return None
        else:
            return self.path.stem.replace('_', ' ').replace('-', ' ').strip()

class HomePage(Page):
    """A special page showing the overall contents at the root level."""
    _descriptor = 'home page'
    def get_title(self):
        return HOME_DESCRIPTOR
    def _is_valid_page(self, page_file):
        if not _is_valid_page(page_file):
            return False
        else:
            return page_file.stem == HOMEPAGE_FILENAME

class ContentsPage(Page):
    """A special automatically-generated page showing the notebook contents."""
    _descriptor = 'contents page'
    def get_title(self):
        return CONTENTS_DESCRIPTOR
    def _is_valid_page(self, page_file):
        if not _is_valid_page(page_file):
            return False
        else:
            return page_file.stem == CONTENTS_FILENAME

class ReadmePage(Page):
    """A special descriptive page showing the notebook contents."""
    _descriptor = 'readme page'
    def get_title(self):
        title = super().get_title()
        if title == UNKNOWN_DESCRIPTOR:
            return README_DESCRIPTOR
        else:
            return title
    def _is_valid_page(self, page_file):
        if not _is_valid_page(page_file):
            return False
        else:
            return page_file.stem == README_FILENAME

class LogbookPage(Page):
    """Logbook page in a notebook, with date attributes."""
    _descriptor = 'logbook page'
    def _is_valid_page(self, page_file):
        return _is_valid_logbook_page(page_file)
    def _convert_filename_to_title(self):
        if self.path is None:
            return None
        else:
            return self.path.stem.replace('_', '-').strip()

class Notebook():
    """Standard notebook object containing pages."""
    _descriptor = 'notebook'
    def __init__(self, notebook_path=None, parent=None):
        self.contents = []
        self.path = None
        self.parent = None
        if notebook_path is not None:
            if self._is_valid_folder(notebook_path):
                self.path = notebook_path
                self.load_contents()
            else:
                raise ValueError(f'Not a valid {self._descriptor}: '
                                 f'{notebook_path}')
        if parent is not None:
            if self._is_valid_parent(parent):
                self.parent = parent
            else:
                raise ValueError(f'Received invalid parent object.')

    def load_contents(self):
        """Load the contents of the notebook from its directory."""
        self.contents = []
        if self.path is not None:
            for item in self.path.iterdir():
                if item.is_file():
                    if self._is_valid_home_page(item):
                        self.add_home_page(item)
                    elif self._is_valid_contents_page(item):
                        self.add_contents_page(item)
                    elif self._is_valid_readme_page(item):
                        self.add_readme_page(item)
                    elif self._is_valid_page(item):
                        self.add_page(item)
                elif item.is_dir():
                    if _is_valid_logbook_folder(item):
                        self.add_logbook(item)
                    elif _is_valid_folder(item):
                        self.add_notebook(item)

    def add_page(self, page_path=None):
        """Add a page to a notebook."""
        self.contents.append(Page(page_path, parent=self))

    def add_home_page(self, page_path=None):
        """Add a home page to a notebook."""
        if self.get_root() == self:
            self.contents.append(HomePage(page_path, parent=self))
        else:
            raise ValueError('Can only add home page at the root level.')

    def add_contents_page(self, page_path=None):
        """Add a contents page to a notebook."""
        self.contents.append(ContentsPage(page_path, parent=self))

    def add_readme_page(self, page_path=None):
        """Add a readme page to a notebook."""
        self.contents.append(ReadmePage(page_path, parent=self))

    def add_notebook(self, notebook_path=None):
        """Add a nested notebook inside a notebook."""
        self.contents.append(Notebook(notebook_path, parent=self))

    def add_logbook(self, logbook_path=None):
        """Add a nested logbook inside a notebook."""
        self.contents.append(Logbook(logbook_path, parent=self))

    def get_title(self):
        """Give the title of the folder."""
        title = None
        if self._has_readme_page():
            title = self._get_title_from_readme()
            if title is not None:
                return title
        if self.path is not None:
            title = self._get_title_from_path()
            if title is not None:
                return title
        return UNKNOWN_DESCRIPTOR

    def get_root(self):
        """Find the top-level folder."""
        return _get_root(self)

    def get_pages(self):
        """Return a list of contents that are (standard) pages."""
        return [item for item in self.contents if type(item) == Page]

    def get_home_page(self):
        """Returns the home page if it exists, assuming there is only one."""
        if not self.get_root() == self:
            return None
        for item in self.contents:
            if isinstance(item, HomePage):
                return item
        return None

    def get_contents_page(self):
        """Returns the contents page if it exists, assuming there is only one."""
        for item in self.contents:
            if isinstance(item, ContentsPage):
                return item
        return None

    def get_readme_page(self):
        """Returns the readme page if it exists, assuming there is only one."""
        for item in self.contents:
            if isinstance(item, ReadmePage):
                return item
        return None

    def get_notebooks(self):
        """Return a list of contents that are notebooks."""
        return [item for item in self.contents if type(item) == Notebook]

    def get_logbooks(self):
        """Return a list of contents that are logbooks."""
        return [item for item in self.contents if type(item) == Logbook]

    def _has_contents_page(self):
        return any([isinstance(item, ContentsPage) for item in self.contents])

    def _has_readme_page(self):
        return any([isinstance(item, ReadmePage) for item in self.contents])

    def _get_title_from_readme(self):
        if not self._has_readme_page():
            return None
        readme_title = self.get_readme_page().get_title()
        if readme_title in [UNKNOWN_DESCRIPTOR, README_FILENAME]:
            return None
        else:
            return readme_title

    def _get_title_from_path(self):
        if not self.path:
            return None
        return self.path.stem.replace('_', ' ').replace('-', ' ').strip()

    def _is_valid_page(self, page_path):
        return _is_valid_page(page_path)

    def _is_valid_home_page(self, page_path):
        if not self.get_root() == self:
            return False
        else:
            return _is_valid_home_page(page_path)

    def _is_valid_contents_page(self, page_path):
        return _is_valid_contents_page(page_path)

    def _is_valid_readme_page(self, page_path):
        return _is_valid_readme_page(page_path)

    def _is_valid_folder(self, folder_path):
        return _is_valid_folder(folder_path)

    def _is_valid_parent(self, parent):
        return isinstance(parent, Notebook) and not isinstance(parent, Logbook)

class Logbook(Notebook):
    """Special notebook object for logbooks, containing logbook pages."""
    _descriptor = 'logbook'

    def add_page(self, page_path=None):
        """Add a page to a logbook."""
        self.contents.append(LogbookPage(page_path, parent=self))

    def add_notebook(self, notebook_path=None):
        """Don't allow nested notebooks inside a logbook."""
        pass

    def add_logbook(self, logbook_path=None):
        """Don't allow nested logbooks inside a logbook."""
        pass

    def get_notebooks(self):
        """Don't allow nested notebooks inside a logbook."""
        return []

    def get_logbooks(self):
        """Don't allow nested logbooks inside a logbook."""
        return []

    def get_pages(self):
        """Return a list of contents that are logbook pages."""
        return [item for item in self.contents if isinstance(item, LogbookPage)]

    def _is_valid_page(self, page_path):
        return _is_valid_logbook_page(page_path)

    def _is_valid_folder(self, folder_path):
        return _is_valid_logbook_folder(folder_path)


# Utility functions
def _is_valid_page(page_file):
    if not page_file.is_file():
        raise OSError(f'Cannot find file: {page_file}')
    return page_file.suffix == PAGE_SUFFIX

def _is_valid_home_page(page_file):
    if _is_valid_page(page_file):
        return page_file.stem == HOMEPAGE_FILENAME
    return False

def _is_valid_contents_page(page_file):
    if _is_valid_page(page_file):
        return page_file.stem == CONTENTS_FILENAME
    return False

def _is_valid_readme_page(page_file):
    if _is_valid_page(page_file):
        return page_file.stem == README_FILENAME
    return False

def _is_valid_logbook_page(page_file):
    if not _is_valid_page(page_file):
        return False
    if re.search(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', page_file.stem) is not None:
        return True
    if re.search(r'^[0-9]{4}-[0-9]{2}$', page_file.stem) is not None:
        return True
    return False

def _is_valid_folder(folder_path):
    if not folder_path.is_dir():
        raise OSError(f'Cannot find folder: {folder_path}')
    return not folder_path.stem.startswith('.')

def _is_valid_logbook_folder(folder_path):
    if not _is_valid_folder(folder_path):
        return False
    return folder_path.stem == LOGBOOK_FOLDER_NAME

def _is_blank_line(line):
    return line.strip() == ''

def _is_navigation_line(line):
    if re.search(r'\[[^]]*\]\([^\)]*\)', line) is not None:
        return True
    return False

def _is_title_line(line):
    return line.startswith('# ')

def _get_root(item):
    while item.parent is not None:
        item = item.parent
    return item


# Processing procedures
def process_all(arguments):
    """Work through all subfolders and process all notebooks and logbooks."""
    pass


# What to do when run as a script
if __name__ == '__main__':
    arguments = docopt(__doc__)
    process_all(arguments)
