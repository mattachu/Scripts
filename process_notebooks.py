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
ATTACHMENTS_FOLDER_NAME = 'Attachments'


class TreeItem():
    """Base class for all objects that can be held in a tree."""
    _descriptor = 'base class'
    def __init__(self, path=None, filename=None, title=None, parent=None):
        self.parent = None
        self.filename = None
        self.title = None
        self.link = None
        self.path = None
        self.contents = []
        if parent is not None:
            if not self._is_valid_parent(parent):
                raise ValueError(f'Received invalid parent: {parent}')
            self.parent = parent
        if filename is not None:
            if not self._is_valid_filename(filename):
                raise ValueError(f'Received invalid filename: {filename}')
            self.filename = filename
        else:
            self.filename = UNKNOWN_DESCRIPTOR
        if title is not None:
            if not self._is_valid_title(title):
                raise ValueError(f'Received invalid title: {title}')
            self.title = title
        else:
            self.title = self._get_title_from_filename() or UNKNOWN_DESCRIPTOR
        if path is not None:
            if not self._is_valid_path(path):
                raise ValueError(f'Not a valid {self._descriptor} path: {path}')
            self.path = path
            new_filename = self._get_filename_from_path() or self.filename
            if filename is not None and new_filename != filename:
                raise ValueError(f'Conflicting filename and path parameters '
                                 f'when initialising {self._descriptor}')
            self.filename = new_filename or UNKNOWN_DESCRIPTOR
            self.title = (self._get_title_from_filename()
                          or self.title
                          or UNKNOWN_DESCRIPTOR)
            self.load_contents(path)
            new_title = self._get_title_from_contents() or self.title
            if title is not None and new_title != title:
                raise ValueError(f'Conflicting title and contents '
                                 f'when initialising {self._descriptor}')
            self.title = new_title or self.title or UNKNOWN_DESCRIPTOR
        self.link = self._get_link_from_filename() or UNKNOWN_DESCRIPTOR

    def load_contents(self, path=None):
        """Load the contents of the object from a file on disk."""
        if path is None:
            path = self.path
        if path is None:
            self.contents = []
        else:
            if self._is_valid_path(path):
                self._load_contents_from_path(path)
                parsed_title = self._get_title_from_contents()
                if self._is_valid_title(parsed_title):
                    self.title = parsed_title
            else:
                raise ValueError(f'Not a valid {self._descriptor} path: {path}')

    def get_root(self):
        """Find the top-level item in the tree."""
        item = self
        while item.parent is not None:
            item = item.parent
        return item

    def get_parents(self):
        """Return a list of all parents from self back to root."""
        parents = []
        item = self
        while item.parent is not None:
            parents.append(item.parent)
            item = item.parent
        return parents

    def get_common_parent(self, other):
        """Return the first item that this item has in common with another."""
        other_path = other.get_parents()
        if not isinstance(other, Page):
            other_path = [other] + other_path
        item = self
        while item not in other_path:
            item = item.parent
        return item

    def get_relative_path(self, other):
        """Return the path of an item relative to this item."""
        common_parent = self.get_common_parent(other)
        reverse_path = ''
        if isinstance(self, Page):
            item = self.parent
        else:
            item = self
        while item is not None:
            if item == common_parent:
                break
            item = item.parent
            reverse_path = '../' + reverse_path
        forward_path = other.link
        item = other
        while item is not None:
            if item == common_parent:
                break
            if isinstance(item, Notebook):
                forward_path = item.filename + '/' + forward_path
            item = item.parent
        return reverse_path + forward_path

    def get_relative_link(self, other):
        """Return a Markdown link to the given item, relative to this item."""
        return f'[{other.title}]({self.get_relative_path(other)})'

    def get_summary(self):
        raise NotImplementedError

    def get_outline(self):
        raise NotImplementedError

    def _is_valid_parent(self, parent):
        return isinstance(parent, TreeItem)

    def _is_valid_filename(self, filename):
        return isinstance(filename, str)

    def _is_valid_title(self, title):
        return isinstance(title, str)

    def _is_valid_link(self, link):
        return isinstance(link, str)

    def _is_valid_path(self, path):
        return path.is_file() or path.is_dir()

    def _load_contents_from_path(self, path):
        raise NotImplementedError

    def _get_link_from_filename(self):
        if self.filename is not None:
            new_link = self.filename
            if self._is_valid_link(new_link):
                return new_link

    def _get_title_from_filename(self):
        if self.filename is not None:
            new_title = self.filename.replace('_', ' ').replace('-', ' ').strip()
            if self._is_valid_title(new_title):
                return new_title

    def _get_filename_from_path(self):
        if self.path is not None:
            new_filename = self.path.stem
            if self._is_valid_filename(new_filename):
                return new_filename

    def _get_title_from_contents(self):
        raise NotImplementedError


class Page(TreeItem):
    """Standard page in a notebook."""
    _descriptor = 'page'

    def get_summary(self):
        return self._get_summary(self.contents)

    def get_outline(self):
        return self._get_outline(self.contents)

    def _load_contents_from_path(self, file_path):
        """Load the content of the page from file."""
        with open(file_path, 'r') as f:
            self.contents = f.readlines()

    def _is_valid_parent(self, parent):
        if type(self) == Page:
            return (isinstance(parent, Notebook)
                    and not isinstance(parent, Logbook))
        else:
            return isinstance(parent, Notebook)

    def _is_valid_path(self, file_path):
        return _is_valid_page_file(file_path)

    def _get_title_from_contents(self):
        return self._get_title(self.contents)

    def _is_blank_line(self, line):
        return line.strip() == ''

    def _is_navigation_line(self, line):
        if re.search(r'\[[^]]*\]\([^\)]*\)', line) is not None:
            return True
        return False

    def _is_title_line(self, line):
        return line.startswith('# ')

    def _is_link_line(self, line):
        if re.search(r'\[[^]]*\]\: ', line) is not None:
            return True
        return False

    def _is_text_line(self, line):
        if not isinstance(line, str):
            raise ValueError(f'Not a valid content line: {line}')
        elif self._is_blank_line(line):
            return False
        elif self._is_title_line(line):
            return False
        elif self._is_link_line(line):
            return False
        elif self._is_navigation_line(line):
            return False
        else:
            return True

    def _find_first_blank_line(self, content):
        return next((idx for idx, line in enumerate(content)
                    if self._is_blank_line(line)), None)

    def _find_first_text_line(self, content):
        return next((idx for idx, line in enumerate(content)
                    if self._is_text_line(line)), None)

    def _strip_links(self, line, types='reference'):
        if types not in ['default', 'reference', 'absolute', 'all']:
            raise ValueError(f'Invalid link type for stripping: {types}')
        if types in ['default', 'reference', 'all']:
            line = self._strip_reference_links(line)
        if types in ['absolute', 'all']:
            line = self._strip_absolute_links(line)
        return line

    def _strip_reference_links(self, line):
        if self._is_link_line(line):
            return ''
        return re.sub(r'\[([^\]]*)\]\[[^\]]*\]', r'\1', line)

    def _strip_absolute_links(self, line):
        return re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', line)

    def _get_title(self, contents):
        if contents is not None:
            for line in contents:
                if self._is_blank_line(line) or self._is_navigation_line(line):
                    continue
                if self._is_title_line(line):
                    return line[2:].strip()
                else:
                    return None

    def _get_summary(self, contents):
        start_line = self._find_first_text_line(contents)
        if start_line is not None:
            lines = self._find_first_blank_line(contents[start_line:]) or 1
            summary = ' '.join(contents[start_line:start_line+lines]).strip()
            return self._strip_links(summary, 'reference')

    def _get_outline(self, contents):
        summary = self._get_summary(contents)
        if summary is not None:
            outline = [summary]
            sections = self._get_sections(contents)
            for section in sections:
                outline = outline + self._get_bullets(section)
            return outline

    def _get_sections(self, contents):
        if self._get_title(contents) is not None:
            section_heading = '## '
        else:
            section_heading = '# '
        section_ids = [idx for idx, line in enumerate(contents)
                    if line.startswith(section_heading)]
        sections = [contents[i:j]
                    for i, j in zip(section_ids, section_ids[1:]+[None])]
        if section_heading == '## ':
            return [[line.replace('## ', '# ') for line in section]
                    for section in sections]
        else:
            return sections

    def _get_bullets(self, section, bullet='*'):
        if bullet == '*':
            next_bullet = '    -'
        elif bullet == '    -':
            next_bullet = '        +'
        elif bullet == '        +':
            next_bullet = None
        else:
            raise ValueError(f'Invalid bullet type: {bullet}')
        title = self._get_title(section)
        summary = self._get_summary(section)
        if title is not None:
            text = f'{bullet} {title}'
            if summary is not None:
                text = f'{text}: {summary}'
            bullets = [text]
            for subsection in self._get_sections(section):
                bullets = bullets + self._get_bullets(subsection, next_bullet)
            return bullets


class HomePage(Page):
    """A special page showing the overall contents at the root level."""
    _descriptor = 'home page'
    def __init__(self, *args, **kwargs):
        if ('filename' in kwargs and kwargs['filename'] is not None
                                 and kwargs['filename'] != HOMEPAGE_FILENAME):
            raise ValueError(f'Invalid filename for {self._descriptor}: '
                             f"{kwargs['filename']}")
        if ('title' in kwargs and kwargs['title'] is not None
                              and kwargs['title'] != HOME_DESCRIPTOR):
            raise ValueError(f'Invalid title for {self._descriptor}: '
                             f"{kwargs['title']}")
        kwargs['filename'] = HOMEPAGE_FILENAME
        kwargs['title'] = HOME_DESCRIPTOR
        super().__init__(*args, **kwargs)

    def get_outline(self):
        raise TypeError('Home pages do not produce outlines.')

    def _is_valid_path(self, page_file):
        return _is_valid_home_page_file(page_file)


class ContentsPage(Page):
    """A special automatically-generated page showing the notebook contents."""
    _descriptor = 'contents page'
    def __init__(self, *args, **kwargs):
        if ('filename' in kwargs and kwargs['filename'] is not None
                                 and kwargs['filename'] != CONTENTS_FILENAME):
            raise ValueError(f'Invalid filename for {self._descriptor}: '
                             f"{kwargs['filename']}")
        if ('title' in kwargs and kwargs['title'] is not None
                              and kwargs['title'] != CONTENTS_DESCRIPTOR):
            raise ValueError(f'Invalid title for {self._descriptor}: '
                             f"{kwargs['title']}")
        kwargs['filename'] = CONTENTS_FILENAME
        kwargs['title'] = CONTENTS_DESCRIPTOR
        super().__init__(*args, **kwargs)

    def get_outline(self):
        raise TypeError('Contents pages do not produce outlines.')

    def _is_valid_path(self, page_file):
        return _is_valid_contents_page_file(page_file)


class ReadmePage(Page):
    """A special descriptive page showing the notebook contents."""
    _descriptor = 'readme page'
    def __init__(self, *args, **kwargs):
        if ('filename' in kwargs and kwargs['filename'] is not None
                                 and kwargs['filename'] != README_FILENAME):
            raise ValueError(f'Invalid filename for {self._descriptor}: '
                             f"{kwargs['filename']}")
        kwargs['filename'] = README_FILENAME
        super().__init__(*args, **kwargs)

    def _is_valid_path(self, page_file):
        return _is_valid_readme_page_file(page_file)


class LogbookPage(Page):
    """Logbook page in a notebook, with date attributes."""
    _descriptor = 'logbook page'

    def _is_valid_parent(self, parent):
        return isinstance(parent, Logbook)

    def _is_valid_path(self, page_file):
        return _is_valid_logbook_page_file(page_file)

    def _is_valid_filename(self, filename):
        return _is_valid_logbook_filename(filename)

    def _get_title_from_filename(self):
        if self.filename is not None:
            new_title = self.filename.strip()
            if self._is_valid_title(new_title):
                return new_title


class Notebook(TreeItem):
    """Standard notebook object containing pages."""
    _descriptor = 'notebook'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.get_root() == self:
            self.link = HOMEPAGE_FILENAME
        else:
            self.link = CONTENTS_FILENAME

    def _load_contents_from_path(self, folder_path):
        for item in folder_path.iterdir():
            if item.is_file():
                if self._is_valid_home_page_file(item):
                    self.add_home_page(item)
                elif self._is_valid_contents_page_file(item):
                    self.add_contents_page(item)
                elif self._is_valid_readme_page_file(item):
                    self.add_readme_page(item)
                elif self._is_valid_page_file(item):
                    self.add_page(item)
                else:
                    continue
            elif item.is_dir():
                if self._is_valid_logbook_folder(item):
                    self.add_logbook(item)
                elif self._is_valid_notebook_folder(item):
                    self.add_notebook(item)
                else:
                    continue

    def add_page(self, page_path=None):
        """Add a page to a notebook."""
        self.contents.append(Page(page_path, parent=self))

    def add_home_page(self, page_path=None):
        """Add a home page to a notebook."""
        if self.get_root() == self:
            self.contents.append(HomePage(path=page_path, parent=self))
        else:
            raise ValueError('Can only add home page at the root level.')

    def add_contents_page(self, page_path=None):
        """Add a contents page to a notebook."""
        self.contents.append(ContentsPage(path=page_path, parent=self))

    def add_readme_page(self, page_path=None):
        """Add a readme page to a notebook."""
        self.contents.append(ReadmePage(path=page_path, parent=self))

    def add_notebook(self, notebook_path=None):
        """Add a nested notebook inside a notebook."""
        self.contents.append(Notebook(path=notebook_path, parent=self))

    def add_logbook(self, logbook_path=None):
        """Add a nested logbook inside a notebook."""
        self.contents.append(Logbook(path=logbook_path, parent=self))

    def get_pages(self):
        """Return a list of contents that are (standard) pages."""
        return [item for item in self.contents if type(item) == Page]

    def get_home_page(self):
        """Returns the home page if it exists, assuming there is only one."""
        if self.get_root() == self:
            return next((item for item in self.contents
                         if isinstance(item, HomePage)), None)

    def get_contents_page(self):
        """Returns the contents page if it exists, assuming there is only one."""
        return next((item for item in self.contents
                     if isinstance(item, ContentsPage)), None)

    def get_readme_page(self):
        """Returns the readme page if it exists, assuming there is only one."""
        return next((item for item in self.contents
                     if isinstance(item, ReadmePage)), None)

    def get_notebooks(self):
        """Return a list of contents that are notebooks."""
        return [item for item in self.contents if type(item) == Notebook]

    def get_logbooks(self):
        """Return a list of contents that are logbooks."""
        return [item for item in self.contents if type(item) == Logbook]

    def get_summary(self):
        if self._has_readme_page():
            return self.get_readme_page().get_summary()

    def get_outline(self):
        raise TypeError('Notebooks do not produce outlines.')

    def _has_contents_page(self):
        return any([isinstance(item, ContentsPage) for item in self.contents])

    def _has_readme_page(self):
        return any([isinstance(item, ReadmePage) for item in self.contents])

    def _get_title_from_contents(self):
        if self._has_readme_page():
            readme_title = self.get_readme_page().title
            if self._is_valid_title(readme_title):
                if readme_title not in [UNKNOWN_DESCRIPTOR, README_FILENAME]:
                    return readme_title

    def _is_valid_path(self, file_path):
        return _is_valid_notebook_folder(file_path)

    def _is_valid_page_file(self, page_path):
        return _is_valid_page_file(page_path)

    def _is_valid_home_page_file(self, page_path):
        return _is_valid_home_page_file(page_path)

    def _is_valid_contents_page_file(self, page_path):
        return _is_valid_contents_page_file(page_path)

    def _is_valid_readme_page_file(self, page_path):
        return _is_valid_readme_page_file(page_path)

    def _is_valid_notebook_folder(self, file_path):
        return _is_valid_notebook_folder(file_path)

    def _is_valid_logbook_folder(self, file_path):
        return _is_valid_logbook_folder(file_path)

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
        raise ValueError('Cannot nest a notebook within a logbook.')

    def add_logbook(self, logbook_path=None):
        """Don't allow nested logbooks inside a logbook."""
        raise ValueError('Cannot nest a logbook within a logbook.')

    def get_notebooks(self):
        """Don't allow nested notebooks inside a logbook."""
        return []

    def get_logbooks(self):
        """Don't allow nested logbooks inside a logbook."""
        return []

    def get_pages(self):
        """Return a list of contents that are logbook pages."""
        return [item for item in self.contents if isinstance(item, LogbookPage)]

    def _get_title_from_contents(self):
        return super()._get_title_from_contents() or LOGBOOK_FOLDER_NAME

    def _is_valid_path(self, folder_path):
        return _is_valid_logbook_folder(folder_path)

    def _is_valid_page_file(self, page_path):
        return _is_valid_logbook_page_file(page_path)


# Utility functions
def _is_valid_page_file(page_file):
    if not page_file.is_file():
        raise OSError(f'Cannot find file: {page_file}')
    return page_file.suffix == PAGE_SUFFIX

def _is_valid_home_page_file(page_file):
    if _is_valid_page_file(page_file):
        return page_file.stem == HOMEPAGE_FILENAME
    return False

def _is_valid_contents_page_file(page_file):
    if _is_valid_page_file(page_file):
        return page_file.stem == CONTENTS_FILENAME
    return False

def _is_valid_readme_page_file(page_file):
    if _is_valid_page_file(page_file):
        return page_file.stem == README_FILENAME
    return False

def _is_valid_logbook_page_file(page_file):
    if _is_valid_page_file(page_file):
        return _is_valid_logbook_filename(page_file.stem)
    return False

def _is_valid_logbook_filename(filename):
    if filename == UNKNOWN_DESCRIPTOR:
        return True
    elif re.search(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', filename) is not None:
        return True
    elif re.search(r'^[0-9]{4}-[0-9]{2}$', filename) is not None:
        return True
    return False

def _is_valid_folder(folder_path):
    if not folder_path.is_dir():
        raise OSError(f'Cannot find folder: {folder_path}')
    return not folder_path.name.startswith('.')

def _is_valid_notebook_folder(folder_path):
    if _is_valid_folder(folder_path):
        return folder_path.name not in [ATTACHMENTS_FOLDER_NAME,
                                        LOGBOOK_FOLDER_NAME]
    return False

def _is_valid_logbook_folder(folder_path):
    if _is_valid_folder(folder_path):
        return folder_path.name == LOGBOOK_FOLDER_NAME
    return False


# Processing procedures
def process_all(arguments):
    """Work through all subfolders and process all notebooks and logbooks."""
    pass


# What to do when run as a script
if __name__ == '__main__':
    arguments = docopt(__doc__)
    process_all(arguments)
