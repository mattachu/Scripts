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
            if page_file.is_file():
                self.path = page_file
                self.load_content()
            else:
                raise OSError(f'Cannot find file: {page_file}')

    def load_content(self):
        """Load the content of the page from file."""
        if self.path is None:
            self.content = None
        else:
            with open(self.path, 'r') as f:
                self.content = f.readlines()

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

    def _convert_filename_to_title(self):
        if self.path is None:
            return None
        else:
            return self.path.stem.replace('_', ' ').replace('-', ' ').strip()

class LogbookPage(Page):
    """Logbook page in a notebook, with date attributes."""
    def _convert_filename_to_title(self):
        if self.path is None:
            return None
        else:
            return self.path.stem.replace('_', '-').strip()

class Notebook():
    """Standard notebook object containing pages."""
    def __init__(self, notebook_path=None):
        self.contents = None
        self.path = None
        if notebook_path is not None:
            if notebook_path.is_dir():
                self.path = notebook_path
                self.load_contents()
            else:
                raise OSError(f'Cannot find path: {notebook_path}')

    def load_contents(self):
        """Load the contents of the notebook from its directory."""
        if self.path is None:
            self.contents = None
        else:
            self.contents = []
            for item in self.path.iterdir():
                if item.is_file():
                    self.add_page(item)
                elif item.is_dir():
                    self.add_folder(item)

    def add_page(self, page_path=None):
        """Add a page to a notebook."""
        if self.contents is None:
            self.contents = []
        self.contents.append(Page(page_path))

    def add_folder(self, folder_path):
        """Add a subfolder to a notebook, either as a notebook or logbook."""
        if folder_path.stem == 'Logbook':
            self.add_logbook(folder_path)
        else:
            self.add_notebook(folder_path)

    def add_notebook(self, notebook_path=None):
        """Add a nested notebook inside a notebook."""
        if self.contents is None:
            self.contents = []
        self.contents.append(Notebook(notebook_path))

    def add_logbook(self, logbook_path=None):
        """Add a nested logbook inside a notebook."""
        if self.contents is None:
            self.contents = []
        self.contents.append(Logbook(logbook_path))

class Logbook(Notebook):
    """Special notebook object for logbooks, containing logbook pages."""

    def add_page(self, page_path=None):
        """Add a page to a logbook."""
        if self.contents is None:
            self.contents = []
        self.contents.append(LogbookPage(page_path))


# Utility functions
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
