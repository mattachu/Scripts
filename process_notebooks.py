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
FOLDERS_DESCRIPTOR = 'Folders'
PAGES_DESCRIPTOR = 'Pages'

# Constants
BLANK_LINE = ''


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
            self.parent.contents.append(self)
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
                self.contents = []
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
        if other == self.get_root():
            title = HOME_DESCRIPTOR
        else:
            title = other.title
        return f'[{title}]({self.get_relative_path(other)})'

    def get_navigation(self):
        """Return a line containing breadcrumb links to current item."""
        if self.get_root() == self:
            return None
        breadcrumbs = [self.get_relative_link(parent)
                       for parent in list(reversed(self.get_parents()))]
        breadcrumbs.append(self.title)
        return ' > '.join(breadcrumbs)

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
        if self._has_summary():
            return self._get_summary(self.contents)

    def get_outline(self):
        summary = self.get_summary()
        if summary is not None:
            outline = [summary, BLANK_LINE]
        else:
            outline = []
        sections = self._get_sections(self.contents)
        for section in sections:
            outline = outline + self._get_bullets(section)
        if outline == []:
            return None
        while outline[-1] == '':
            outline = outline[:-1]
        return outline

    def _is_valid_parent(self, parent):
        if type(self) in [Page, ContentsPage]:
            return (isinstance(parent, Notebook)
                    and not isinstance(parent, Logbook))
        else:
            return isinstance(parent, Notebook)

    def _is_valid_path(self, file_path):
        return _is_valid_page_file(file_path)

    def _load_contents_from_path(self, file_path):
        """Load the content of the page from file."""
        self.contents = _load_file(file_path)

    def _get_title_from_contents(self):
        return self._get_title(self.contents)

    def _get_title(self, contents):
        if contents is not None:
            if sum([self._is_title_line(line) for line in contents]) == 1:
                for line in contents:
                    if self._is_navigation_line(line):
                        continue
                    elif self._is_blank_line(line):
                        continue
                    elif self._is_title_line(line):
                        return self._strip_links(line[2:].strip(), 'all')
                    else:
                        return None

    def _get_summary(self, contents):
        start_line = self._find_first_text_line(contents)
        if start_line is None:
            return None
        subsection = self._find_first_subtitle(contents)
        if subsection is None or start_line < subsection:
            lines = self._find_first_blank_line(contents[start_line:]) or 1
            summary = ' '.join(contents[start_line:start_line+lines]).strip()
            summary = self._strip_links(summary, 'reference')
            if summary.find(r': * ') > 0:
                summary = summary[:summary.find(r': * ')] + '.'
            if summary[-1] == ':':
                summary = summary[:-1] + '.'
            return summary

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
                summary = summary.replace('\n', '')
                text = f'{text}: {summary}'
            bullets = [text]
            for subsection in self._get_sections(section):
                bullets = bullets + self._get_bullets(subsection, next_bullet)
            return bullets

    def _has_summary(self):
        return self._get_summary(self.contents) is not None

    def _contents_match(self, file_path):
        """Compare the current content of the page with file contents."""
        return self.contents == _load_file(file_path)

    def _is_blank_line(self, line):
        return line.strip() == ''

    def _is_navigation_line(self, line):
        link = r'\[[^]]*\]\([^\)]*\)'
        text = r'[A-Za-z0-9 ]*'
        separator = r'[\|>]'
        pattern = f'^{link}(( {separator} {link})* {separator} ({link}|{text}))?$'
        if re.search(pattern, line) is not None:
            return True
        return False

    def _is_title_line(self, line):
        return line.startswith('# ')

    def _is_subtitle_line(self, line, starting_level=1):
        if starting_level == 0:
            return line.startswith('#')
        else:
            return line.startswith('##')

    def _is_bullet_line(self, line):
        return line.startswith('* ')

    def _is_link_line(self, line):
        reference = r'\[[^]]*\]\: [^\s]*'
        descriptive = r'.*\: \[[^]]*\](\([^\)]*\)|\[[^\]]*\])'
        if re.search(f'^({reference}|{descriptive})$', line) is not None:
            return True
        return False

    def _is_text_line(self, line):
        if not isinstance(line, str):
            raise ValueError(f'Not a valid content line: {line}')
        elif self._is_blank_line(line):
            return False
        elif self._is_title_line(line):
            return False
        elif self._is_subtitle_line(line):
            return False
        elif self._is_link_line(line):
            return False
        elif self._is_navigation_line(line):
            return False
        elif self._is_bullet_line(line):
            return False
        else:
            return True

    def _find_first_blank_line(self, content):
        return next((idx for idx, line in enumerate(content)
                    if self._is_blank_line(line)), None)

    def _find_first_text_line(self, content):
        return next((idx for idx, line in enumerate(content)
                    if self._is_text_line(line)), None)

    def _find_first_title_line(self, content):
        return next((idx for idx, line in enumerate(content)
                    if self._is_title_line(line)), None)

    def _find_first_subtitle(self, content):
        if self._get_title(content) is not None:
            starting_level = 1
        else:
            starting_level = 0
        return next((idx for idx, line in enumerate(content)
                    if self._is_subtitle_line(line, starting_level)), None)

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

    def get_navigation(self):
        """Don't return any navigation as already at home page."""
        return None

    def _is_valid_parent(self, parent):
        """Home pages must be contained at the root level."""
        return isinstance(parent, Notebook) and parent.get_root() == parent

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

    def rebuild(self):
        """Rebuild contents by summarising relevant pages."""
        self.contents = []
        if self.parent is not None:
            nav = self.get_navigation()
            if nav is not None:
                self.contents.append(nav)
                self.contents.append(BLANK_LINE)
            title = self.parent.title
            if title is not None and title != UNKNOWN_DESCRIPTOR:
                self.contents.append(_title(title, title_level=1))
                self.contents.append(BLANK_LINE)
            summary = self.parent.get_summary()
            if summary is not None:
                self.contents.append(summary)
                self.contents.append(BLANK_LINE)
                self.contents.append(BLANK_LINE)
            folders = sorted(self.parent.get_notebooks(),
                             key=lambda item: item.title + item.link)
            folders = folders + self.parent.get_logbooks()
            if len(folders) > 0:
                self.contents.append(_title(FOLDERS_DESCRIPTOR, title_level=2))
                self.contents.append(BLANK_LINE)
            for folder in folders:
                self.contents.append(_title(self.get_relative_link(folder),
                                            title_level=3))
                self.contents.append(BLANK_LINE)
                summary = folder.get_summary()
                if summary is not None:
                    self.contents.append(summary)
                    self.contents.append(BLANK_LINE)
            pages = sorted(self.parent.get_pages(),
                           key=lambda item: item.title + item.link)
            if len(pages) > 0:
                self.contents.append(_title(PAGES_DESCRIPTOR, title_level=2))
                self.contents.append(BLANK_LINE)
            for page in pages:
                self.contents.append(_title(self.get_relative_link(page),
                                            title_level=3))
                self.contents.append(BLANK_LINE)
                summary = page.get_summary()
                if summary is not None:
                    self.contents.append(summary)
                    self.contents.append(BLANK_LINE)
            while len(self.contents) > 0 and self.contents[-1] == BLANK_LINE:
                self.contents = self.contents[:-1]
        return self.contents

    def get_navigation(self):
        """Return navigation link for the notebook rather than its contents page."""
        if self.parent is not None:
            return self.parent.get_navigation()

    def _is_valid_path(self, page_file):
        return _is_valid_contents_page_file(page_file)

    def _get_title_from_contents(self):
        """Return `None` because contents pages have a fixed title."""
        return None


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

    def get_navigation(self):
        """Don't return any navigation as readme pages should remain clean."""
        return None

    def _is_valid_path(self, page_file):
        return _is_valid_readme_page_file(page_file)


class LogbookPage(Page):
    """Logbook page in a notebook, with date attributes."""
    _descriptor = 'logbook page'

    def __lt__(self, other):
        return (self.filename < other.filename)

    def __gt__(self, other):
        return(self.filename > other.filename)

    def get_month(self):
        if len(self.filename) >= 7:
            if (self.filename[:4].isnumeric()
                    and self.filename[4:5] == '-'
                    and self.filename[5:7].isnumeric()):
                return self.filename[:7]

    def get_navigation(self):
        """Return links to surrounding pages."""
        left = self.get_previous()
        right = self.get_next()
        up = self.get_up()
        links = []
        if left is not None:
            links.append(f'[< {left.filename}]({self.get_relative_path(left)})')
        if up is not None:
            if isinstance(up, Logbook):
                if up.get_home_page() is not None:
                    title = up.get_home_page().title
                elif up.get_contents_page() is not None:
                    title = up.get_contents_page().title
                else:
                    title = up.title
            else:
                title = up.title
            links.append(f'[{title}]({self.get_relative_path(up)})')
        if right is not None:
            links.append(f'[{right.filename} >]({self.get_relative_path(right)})')
        if len(links) > 0:
            return ' | '.join(links)

    def get_up(self):
        if self.parent is not None:
            return next((item for item in self.parent.get_pages('months')
                         if item.get_month() == self.get_month()), None)

    def get_previous(self):
        if self.parent is not None:
            past = [item for item in self._get_siblings()
                    if item < self]
            if len(past) > 0:
                past.sort()
                return past[-1]

    def get_next(self):
        if self.parent is not None:
            future = [item for item in self._get_siblings()
                      if item > self]
            if len(future) > 0:
                future.sort()
                return future[0]

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

    def _get_title_from_contents(self):
        """Logbook page titles are set from the date, not the contents."""
        if type(self) == LogbookPage:
            return None
        return super()._get_title_from_contents()

    def _get_sections(self, contents):
        """Logbook pages without summaries need to split from the first title."""
        if type(self) == LogbookPage and contents == self.contents:
            if not self._has_summary():
                contents = ['Dummy summary', ''] + self.contents
        return super()._get_sections(contents)

    def _get_siblings(self):
        return self.parent.get_pages('days')

    def _has_summary(self):
        """Logbook pages cannot have summaries after a title line."""
        if type(self) == LogbookPage:
            title_line = self._find_first_title_line(self.contents)
            start_line = self._find_first_text_line(self.contents)
            if (title_line is not None
                    and start_line is not None
                    and title_line < start_line):
                return False
        return super()._has_summary()


class LogbookMonth(LogbookPage):
    """Special page in a notebook that summarises the month's entries."""
    _descriptor = 'logbook month page'

    def rebuild(self):
        """Rebuild contents by summarising relevant pages."""
        self.contents = []
        pages = self.get_pages()
        if len(pages) == 0:
            return None
        self.contents.append(self.get_navigation())
        self.contents.append(BLANK_LINE)
        self.contents.append(_title(self.title))
        self.contents.append(BLANK_LINE)
        for page in pages:
            self.contents.append(_title(self.get_relative_link(page),
                                        title_level=2))
            self.contents.append(BLANK_LINE)
            self.contents = self.contents + page.get_outline()
            self.contents.append(BLANK_LINE)
            self.contents.append(BLANK_LINE)
        while self.contents[-1] == BLANK_LINE:
            self.contents = self.contents[:-1]
        return self.contents

    def get_up(self):
        if self.parent is not None:
            return self.parent

    def get_pages(self):
        if self.parent is not None:
            page_list = [item for item in self.parent.get_pages('days')
                         if item.get_month() == self.get_month()]
            page_list.sort()
            return page_list
        return []

    def _is_valid_path(self, page_file):
        return _is_valid_logbook_month_file(page_file)

    def _is_valid_filename(self, filename):
        return _is_valid_logbook_month_filename(filename)

    def _get_siblings(self):
        return self.parent.get_pages('months')


class LogbookContents(ContentsPage):
    """Logbook contents are built by date rather than file names."""
    _descriptor = 'logbook contents page'

    def rebuild(self):
        """Rebuild contents by summarising relevant pages."""
        self.contents = []
        if self.parent is not None:
            nav = self.get_navigation()
            if nav is not None:
                self.contents.append(nav)
                self.contents.append(BLANK_LINE)
            months = sorted(self.parent.get_pages(types='months'),
                            key=lambda item: self.filename)
            for month in months:
                self.contents.append(_title(self.get_relative_link(month)))
                self.contents.append(BLANK_LINE)
                month.rebuild()
                this_content = month.contents
                while (len(this_content) > 0
                        and (self._is_navigation_line(this_content[0])
                            or self._is_title_line(this_content[0])
                            or self._is_blank_line(this_content[0]))):
                    this_content = this_content[1:]
                self.contents += this_content
                self.contents.append(BLANK_LINE)
                self.contents.append(BLANK_LINE)
            while len(self.contents) > 0 and self.contents[-1] == BLANK_LINE:
                self.contents = self.contents[:-1]
        return self.contents

    def _is_valid_parent(self, parent):
        return isinstance(parent, Logbook)


class Notebook(TreeItem):
    """Standard notebook object containing pages."""
    _descriptor = 'notebook'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.get_root() == self:
            self.link = HOMEPAGE_FILENAME
        else:
            self.link = CONTENTS_FILENAME

    def add_page(self, page_path=None):
        """Add a page to a notebook."""
        return Page(page_path, parent=self)

    def add_home_page(self, page_path=None):
        """Add a home page to a notebook."""
        if self.get_root() != self:
            raise ValueError('Can only add home page at the root level.')
        if self.get_home_page() is not None:
            raise ValueError('Cannot add more than one home page.')
        return HomePage(path=page_path, parent=self)

    def add_contents_page(self, page_path=None):
        """Add a contents page to a notebook."""
        if self.get_contents_page() is not None:
            raise ValueError('Cannot add more than one contents page.')
        return ContentsPage(path=page_path, parent=self)

    def add_readme_page(self, page_path=None):
        """Add a readme page to a notebook."""
        if self.get_readme_page() is not None:
            raise ValueError('Cannot add more than one readme page.')
        return ReadmePage(path=page_path, parent=self)

    def add_notebook(self, notebook_path=None):
        """Add a nested notebook inside a notebook."""
        return Notebook(path=notebook_path, parent=self)

    def add_logbook(self, logbook_path=None):
        """Add a nested logbook inside a notebook."""
        return Logbook(path=logbook_path, parent=self)

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

    def _get_title_from_contents(self):
        if self._has_readme_page():
            readme_title = self.get_readme_page().title
            if self._is_valid_title(readme_title):
                if readme_title not in [UNKNOWN_DESCRIPTOR, README_FILENAME]:
                    return readme_title

    def _has_contents_page(self):
        return any([isinstance(item, ContentsPage) for item in self.contents])

    def _has_readme_page(self):
        return any([isinstance(item, ReadmePage) for item in self.contents])


class Logbook(Notebook):
    """Special notebook object for logbooks, containing logbook pages."""
    _descriptor = 'logbook'

    def add_page(self, page_path=None):
        """Add a page to a logbook."""
        if self._is_valid_month_file(page_path):
            return LogbookMonth(page_path, parent=self)
        else:
            return LogbookPage(page_path, parent=self)

    def add_contents_page(self, page_path=None):
        """Add a contents page to a notebook."""
        if self.get_contents_page() is not None:
            raise ValueError('Cannot add more than one contents page.')
        return LogbookContents(path=page_path, parent=self)

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

    def get_pages(self, types='all'):
        """Return a list of contents that are logbook pages."""
        if types == 'all':
            return [item for item in self.contents
                    if isinstance(item, LogbookPage)]
        elif types == 'days':
            return [item for item in self.contents
                    if type(item) == LogbookPage]
        elif types == 'months':
            return [item for item in self.contents
                    if isinstance(item, LogbookMonth)]
        else:
            raise ValueError(f'Invalid logbook page type: {types}')

    def _is_valid_path(self, folder_path):
        return _is_valid_logbook_folder(folder_path)

    def _is_valid_page_file(self, page_path):
        return (_is_valid_logbook_page_file(page_path)
                or _is_valid_logbook_month_file(page_path))

    def _is_valid_month_file(self, page_path):
        return _is_valid_logbook_month_file(page_path)

    def _get_title_from_contents(self):
        return super()._get_title_from_contents() or LOGBOOK_FOLDER_NAME


# Utility functions
def _is_valid_page_file(page_file):
    if page_file is None:
        return None
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
    return False

def _is_valid_logbook_month_file(page_file):
    if _is_valid_page_file(page_file):
        return _is_valid_logbook_month_filename(page_file.stem)
    return False

def _is_valid_logbook_month_filename(filename):
    if filename == UNKNOWN_DESCRIPTOR:
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

def _load_file(filename):
    if not filename.is_file():
        raise ValueError(f'Invalid file to load as text: {filename}')
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]

def _title(text, title_level=1):
    if not isinstance(text, str):
        raise ValueError(f'Text for title is not a string: {text}')
    elif text == '':
        raise ValueError('Text for title is empty.')
    if not isinstance(title_level, int):
        raise ValueError(f'Level for title is not an integer: {title_level}')
    elif title_level < 1:
        raise ValueError(f'Level for title is less than one: {title_level}')
    while text.startswith('#') or text.startswith('* ') or text.startswith(' '):
        text = text[1:]
    return '#' * title_level + ' ' + text


# Processing procedures
def process_all(arguments):
    """Create notebook object and process all contents."""
    pass


# What to do when run as a script
if __name__ == '__main__':
    arguments = docopt(__doc__)
    process_all(arguments)
