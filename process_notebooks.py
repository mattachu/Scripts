"""Process a set of notebooks to include internal links and contents pages.

Usage:
  process_notebooks.py [<folder>]
  process_notebooks.py --help
"""

from docopt import docopt
import pathlib

class Page():
    """Standard page in a notebook."""
    def __init__(self, page_file=None):
        self.content = None
        if page_file is not None:
            if page_file.is_file():
                with open(page_file, 'r') as f:
                    self.content = f.readlines()
            else:
                raise OSError(f'Cannot find file: {page_file}')

class LogbookPage(Page):
    """Logbook page in a notebook, with date attributes."""
    pass

# Processing procedures
def process_all(arguments):
    """Work through all subfolders and process all notebooks and logbooks."""
    pass

# What to do when run as a script
if __name__ == '__main__':
    arguments = docopt(__doc__)
    process_all(arguments)
