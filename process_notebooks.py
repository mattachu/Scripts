"""Process a set of notebooks to include internal links and contents pages.

Usage:
  process_notebooks.py [<folder>]
  process_notebooks.py --help
"""

from docopt import docopt

# Processing procedures
def process_all(arguments):
    """Work through all subfolders and process all notebooks and logbooks."""
    pass

# What to do when run as a script
if __name__ == '__main__':
    arguments = docopt(__doc__)
    process_all(arguments)
