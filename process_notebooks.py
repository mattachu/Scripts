"""Process a set of notebooks to include internal links and contents pages.

Usage:
  process_notebooks.py [<folder>]
  process_notebooks.py --help
"""

from docopt import docopt
import pathlib
import re

class Page():
    """Standard page in a notebook."""
    def __init__(self, page_file=None):
        self.content = None
        self.path = None
        if page_file is not None:
            if self._is_valid_page(page_file):
                self.path = page_file
                self.load_content()
            else:
                raise ValueError(f'Not a valid page: {page_file}')

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
        if self.content is None:
            return None
        else:
            for line in self.content:
                if _is_blank_line(line) or _is_navigation_line(line):
                    continue
                if _is_title_line(line):
                    return line[2:].strip()
                else:
                    return self._convert_filename_to_title()

    def _is_valid_page(self, page_file):
        return _is_valid_page(page_file)

    def _convert_filename_to_title(self):
        if self.path is None:
            return None
        else:
            return self.path.stem.replace('_', ' ').replace('-', ' ').strip()

class LogbookPage(Page):
    """Logbook page in a notebook, with date attributes."""

    def _is_valid_page(self, page_file):
        return _is_valid_logbook_page(page_file)

    def _convert_filename_to_title(self):
        if self.path is None:
            return None
        else:
            return self.path.stem.replace('_', '-').strip()

class Notebook():
    """Standard notebook object containing pages."""
    def __init__(self, notebook_path=None):
        self.contents = []
        self.path = None
        if notebook_path is not None:
            if self._is_valid_folder(notebook_path):
                self.path = notebook_path
                self.load_contents()
            else:
                raise ValueError(f'Not a valid notebook: {notebook_path}')

    def load_contents(self):
        """Load the contents of the notebook from its directory."""
        self.contents = []
        if self.path is not None:
            for item in self.path.iterdir():
                if item.is_file():
                    if self._is_valid_page(item):
                        self.add_page(item)
                elif item.is_dir():
                    if _is_valid_logbook_folder(item):
                        self.add_logbook(item)
                    elif _is_valid_folder(item):
                        self.add_notebook(item)

    def add_page(self, page_path=None):
        """Add a page to a notebook."""
        self.contents.append(Page(page_path))

    def add_notebook(self, notebook_path=None):
        """Add a nested notebook inside a notebook."""
        self.contents.append(Notebook(notebook_path))

    def add_logbook(self, logbook_path=None):
        """Add a nested logbook inside a notebook."""
        self.contents.append(Logbook(logbook_path))

    def get_nested_notebooks(self, include_logbooks=False):
        """Return a list of contents that are notebooks."""
        notebook_list = [item for item in self.contents
                         if isinstance(item, Notebook)]
        if include_logbooks is True:
            return notebook_list
        else:
            return [item for item in notebook_list
                    if not isinstance(item, Logbook)]

    def get_nested_logbooks(self):
        """Return a list of contents that are logbooks."""
        return [item for item in self.contents if isinstance(item, Logbook)]

    def get_pages(self):
        """Return a list of contents that are pages."""
        return [item for item in self.contents if isinstance(item, Page)]

    def _is_valid_page(self, page_path):
        return _is_valid_page(page_path)

    def _is_valid_folder(self, folder_path):
        return _is_valid_folder(folder_path)

class Logbook(Notebook):
    """Special notebook object for logbooks, containing logbook pages."""

    def add_page(self, page_path=None):
        """Add a page to a logbook."""
        self.contents.append(LogbookPage(page_path))

    def add_notebook(self, notebook_path=None):
        """Don't allow nested notebooks inside a logbook."""
        pass

    def add_logbook(self, logbook_path=None):
        """Don't allow nested logbooks inside a logbook."""
        pass

    def get_nested_notebooks(self, include_logbooks=False):
        """Don't allow nested notebooks inside a logbook."""
        return []

    def get_nested_logbooks(self):
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
    elif page_file.suffix == '.md':
        return True
    else:
        return False

def _is_valid_logbook_page(page_file):
    if not _is_valid_page(page_file):
        return False
    elif page_file.stem == 'Contents':
        return True
    elif re.search(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', page_file.stem):
        return True
    elif re.search(r'^[0-9]{4}-[0-9]{2}$', page_file.stem):
        return True
    else:
        return False

def _is_valid_folder(folder_path):
    if not folder_path.is_dir():
        raise OSError(f'Cannot find folder: {folder_path}')
    elif folder_path.stem.startswith('.'):
        return False
    else:
        return True

def _is_valid_logbook_folder(folder_path):
    if not _is_valid_folder(folder_path):
        return False
    if folder_path.stem == 'Logbook':
        return True
    else:
        return False

def _is_blank_line(line):
    return line.strip() == ''

def _is_navigation_line(line):
    if re.search(r'\[[^]]*\]\([^\)]*\)', line):
        return True
    else:
        return False

def _is_title_line(line):
    return line.startswith('# ')


# Processing procedures
def process_all(arguments):
    """Work through all subfolders and process all notebooks and logbooks."""
    pass


# What to do when run as a script
if __name__ == '__main__':
    arguments = docopt(__doc__)
    process_all(arguments)
