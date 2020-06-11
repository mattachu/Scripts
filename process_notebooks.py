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
                with open(page_file, 'r') as f:
                    self.content = f.readlines()
            else:
                raise OSError(f'Cannot find file: {page_file}')

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
        self.path = None
        if notebook_path is not None:
            if notebook_path.is_dir():
                self.path = notebook_path
            else:
                raise OSError(f'Cannot find path: {notebook_path}')

class Logbook(Notebook):
    """Special notebook object for logbooks, containing logbook pages."""
    pass


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
