# Tests process_notebooks.py

import pytest
import pathlib
import git
import shutil
from contextlib import nullcontext as does_not_raise

import process_notebooks as pn


# Test generation
test_objects = [
    'page',
    'logbook page',
    'logbook month',
    'contents',
    'home',
    'readme',
    'notebook',
    'logbook']

test_lines = {
    'blank': '',
    'text': ('Page content, including some `code` '
             'or [different](link1) [types][link2] of [links][].'),
    'title': '# Page title',
    'subtitle': '## [Subtopic](link)',
    'bullet': '* Bullet line content including a [link][].',
    'navigation': '[Home](link1) > [Folder](link2) > [Notebook](link3)',
    'link': '[link]: https://link.com/link'}

test_lines_strip_all_links = {
    'blank': '',
    'text': 'Page content, including some `code` or different types of links.',
    'title': '# Page title',
    'subtitle': '## Subtopic',
    'bullet': '* Bullet line content including a link.',
    'navigation': 'Home > Folder > Notebook',
    'link': ''}

test_lines_strip_reference_links = {
    'blank': '',
    'text': ('Page content, including some `code` '
             'or [different](link1) types of links.'),
    'title': '# Page title',
    'subtitle': '## [Subtopic](link)',
    'bullet': '* Bullet line content including a link.',
    'navigation': '[Home](link1) > [Folder](link2) > [Notebook](link3)',
    'link': ''}

test_lines_strip_absolute_links = {
    'blank': '',
    'text': ('Page content, including some `code` '
             'or different [types][link2] of [links][].'),
    'title': '# Page title',
    'subtitle': '## Subtopic',
    'bullet': '* Bullet line content including a [link][].',
    'navigation': 'Home > Folder > Notebook',
    'link': '[link]: https://link.com/link'}

test_lines_title = {
    'blank': 'ValueError',
    'text': ('# Page content, including some `code` '
             'or [different](link1) [types][link2] of [links][].'),
    'title': '# Page title',
    'subtitle': '# [Subtopic](link)',
    'bullet': '# Bullet line content including a [link][].',
    'navigation': '# [Home](link1) > [Folder](link2) > [Notebook](link3)',
    'link': '# [link]: https://link.com/link'}

test_contents = {
    'empty': [],
    'blank': [''],
    'standard': ['[< Home](../Contents)',
                 '',
                 '# Page title',
                 '',
                 'Page summary, including some `code` or [links][].',
                 '',
                 'Page content.',
                 '',
                 '## Section',
                 '',
                 'Section summary.',
                 '',
                 'Section content.'
                 '',
                 '### Subsection',
                 '',
                 'Subsection summary that is longer than other summaries and',
                 'so runs onto more than one line.',
                 'It may also include more than one sentence.',
                 '',
                 'Subsection content.',
                 '',
                 '### Empty subsection',
                 '',
                 '### Third subsection',
                 '',
                 'Third subsection summary:',
                 '* Third subsection content bullet.',
                 '* Third subsection content bullet.',
                 '',
                 '## Another section',
                 '',
                 'Summary for another section:',
                 '',
                 '> Quoted content.',
                 '',
                 '## Section without summary',
                 '',
                 '* Section content bullet.',
                 '* Section content bullet.',
                 '',
                 '### Subsection',
                 '',
                 'Subsection summary.',
                 ''],
    'plain': ['Page content.'],
    'no-title': ['[< Home](../Contents)',
                 '',
                 'Page summary, including some `code` or [links][].',
                 '',
                 'Page content.',
                 '',
                 '# Section',
                 '',
                 'Section summary.',
                 '',
                 'Section content.'
                 '',
                 '## Subsection',
                 '',
                 'Subsection summary that is longer than other summaries and',
                 'so runs onto more than one line.',
                 'It may also include more than one sentence.',
                 '',
                 'Subsection content.',
                 '',
                 '## Empty subsection',
                 '',
                 '## Third subsection',
                 '',
                 'Third subsection summary:',
                 '* Third subsection content bullet.',
                 '* Third subsection content bullet.',
                 '',
                 '# Another section',
                 '',
                 'Summary for another section:',
                 '',
                 '> Quoted content.',
                 '',
                 '# Section without summary',
                 '',
                 '* Section content bullet.',
                 '* Section content bullet.',
                 '',
                 '## Subsection',
                 '',
                 'Subsection summary.',
                 ''],
    'no-summary': ['[< Home](../Contents)',
                   '',
                   '# Section',
                   '',
                   'Section summary.',
                   '',
                   'Section content.'
                   '',
                   '## Subsection',
                   '',
                   'Subsection summary that is longer than other summaries and',
                   'so runs onto more than one line.',
                   'It may also include more than one sentence.',
                   '',
                   'Subsection content.',
                   '',
                   '## Empty subsection',
                   '',
                   '## Third subsection',
                   '',
                   'Third subsection summary:',
                   '* Third subsection content bullet.',
                   '* Third subsection content bullet.',
                   '',
                   '# Another section',
                   '',
                   'Summary for another section:',
                   '',
                   '> Quoted content.',
                   '',
                   '# Section without summary',
                   '',
                   '* Section content bullet.',
                   '* Section content bullet.',
                   '',
                   '## Subsection',
                   '',
                   'Subsection summary.',
                   '']}

contents_title = {
    'empty': None,
    'blank': None,
    'standard': 'Page title',
    'plain': None,
    'no-title': None,
    'no-summary': None}

logbook_title = contents_title

contents_summary = {
    'empty': None,
    'blank': None,
    'standard': 'Page summary, including some `code` or links.',
    'plain': 'Page content.',
    'no-title': 'Page summary, including some `code` or links.',
    'no-summary': None}

logbook_summary = {
    'empty': None,
    'blank': None,
    'standard': None,
    'plain': 'Page content.',
    'no-title': 'Page summary, including some `code` or links.',
    'no-summary': None}

contents_sections = {
    'empty': [],
    'blank': [],
    'standard': [['# Section',
                  '',
                  'Section summary.',
                  '',
                  'Section content.'
                  '',
                  '## Subsection',
                  '',
                  'Subsection summary that is longer than other summaries and',
                  'so runs onto more than one line.',
                  'It may also include more than one sentence.',
                  '',
                  'Subsection content.',
                  '',
                  '## Empty subsection',
                  '',
                  '## Third subsection',
                  '',
                  'Third subsection summary:',
                  '* Third subsection content bullet.',
                  '* Third subsection content bullet.',
                  ''],
                 ['# Another section',
                  '',
                  'Summary for another section:',
                  '',
                  '> Quoted content.',
                  ''],
                 ['# Section without summary',
                  '',
                  '* Section content bullet.',
                  '* Section content bullet.',
                  '',
                  '## Subsection',
                  '',
                  'Subsection summary.',
                  '']],
    'plain': [],
    'no-title': [['# Section',
                  '',
                  'Section summary.',
                  '',
                  'Section content.'
                  '',
                  '## Subsection',
                  '',
                  'Subsection summary that is longer than other summaries and',
                  'so runs onto more than one line.',
                  'It may also include more than one sentence.',
                  '',
                  'Subsection content.',
                  '',
                  '## Empty subsection',
                  '',
                  '## Third subsection',
                  '',
                  'Third subsection summary:',
                  '* Third subsection content bullet.',
                  '* Third subsection content bullet.',
                  ''],
                 ['# Another section',
                  '',
                  'Summary for another section:',
                  '',
                  '> Quoted content.',
                  ''],
                 ['# Section without summary',
                  '',
                  '* Section content bullet.',
                  '* Section content bullet.',
                  '',
                  '## Subsection',
                  '',
                  'Subsection summary.',
                  '']],
    'no-summary': [['# Section',
                    '',
                    'Section summary.',
                    '',
                    'Section content.'
                    '',
                    '## Subsection',
                    '',
                    'Subsection summary that is longer than other summaries and',
                    'so runs onto more than one line.',
                    'It may also include more than one sentence.',
                    '',
                    'Subsection content.',
                    '',
                    '## Empty subsection',
                    '',
                    '## Third subsection',
                    '',
                    'Third subsection summary:',
                    '* Third subsection content bullet.',
                    '* Third subsection content bullet.',
                    ''],
                   ['# Another section',
                    '',
                    'Summary for another section:',
                    '',
                    '> Quoted content.',
                    ''],
                   ['# Section without summary',
                    '',
                    '* Section content bullet.',
                    '* Section content bullet.',
                    '',
                    '## Subsection',
                    '',
                    'Subsection summary.',
                    '']]}

logbook_sections = {
    'empty': [],
    'blank': [],
    'standard': [['# Page title',
                  '',
                  'Page summary, including some `code` or [links][].',
                  '',
                  'Page content.',
                  '',
                  '## Section',
                  '',
                  'Section summary.',
                  '',
                  'Section content.'
                  '',
                  '### Subsection',
                  '',
                  'Subsection summary that is longer than other summaries and',
                  'so runs onto more than one line.',
                  'It may also include more than one sentence.',
                  '',
                  'Subsection content.',
                  '',
                  '### Empty subsection',
                  '',
                  '### Third subsection',
                  '',
                  'Third subsection summary:',
                  '* Third subsection content bullet.',
                  '* Third subsection content bullet.',
                  '',
                  '## Another section',
                  '',
                  'Summary for another section:',
                  '',
                  '> Quoted content.',
                  '',
                  '## Section without summary',
                  '',
                  '* Section content bullet.',
                  '* Section content bullet.',
                  '',
                  '### Subsection',
                  '',
                  'Subsection summary.',
                  '']],
    'plain': [],
    'no-title': [['# Section',
                  '',
                  'Section summary.',
                  '',
                  'Section content.'
                  '',
                  '## Subsection',
                  '',
                  'Subsection summary that is longer than other summaries and',
                  'so runs onto more than one line.',
                  'It may also include more than one sentence.',
                  '',
                  'Subsection content.',
                  '',
                  '## Empty subsection',
                  '',
                  '## Third subsection',
                  '',
                  'Third subsection summary:',
                  '* Third subsection content bullet.',
                  '* Third subsection content bullet.',
                  ''],
                 ['# Another section',
                  '',
                  'Summary for another section:',
                  '',
                  '> Quoted content.',
                  ''],
                 ['# Section without summary',
                  '',
                  '* Section content bullet.',
                  '* Section content bullet.',
                  '',
                  '## Subsection',
                  '',
                  'Subsection summary.',
                  '']],
    'no-summary': [['# Section',
                    '',
                    'Section summary.',
                    '',
                    'Section content.'
                    '',
                    '## Subsection',
                    '',
                    'Subsection summary that is longer than other summaries and',
                    'so runs onto more than one line.',
                    'It may also include more than one sentence.',
                    '',
                    'Subsection content.',
                    '',
                    '## Empty subsection',
                    '',
                    '## Third subsection',
                    '',
                    'Third subsection summary:',
                    '* Third subsection content bullet.',
                    '* Third subsection content bullet.',
                    ''],
                   ['# Another section',
                    '',
                    'Summary for another section:',
                    '',
                    '> Quoted content.',
                    ''],
                   ['# Section without summary',
                    '',
                    '* Section content bullet.',
                    '* Section content bullet.',
                    '',
                    '## Subsection',
                    '',
                    'Subsection summary.',
                    '']]}

contents_outline = {
    'empty': None,
    'blank': None,
    'standard': ['Page summary, including some `code` or links.',
                 '',
                 '* Section: Section summary.',
                 '    - Subsection: Subsection summary that is longer than other summaries and so runs onto more than one line. It may also include more than one sentence.',
                 '    - Empty subsection',
                 '    - Third subsection: Third subsection summary.',
                 '* Another section: Summary for another section.',
                 '* Section without summary',
                 '    - Subsection: Subsection summary.'],
    'plain': ['Page content.'],
    'no-title': ['Page summary, including some `code` or links.',
                 '',
                 '* Section: Section summary.',
                 '    - Subsection: Subsection summary that is longer than other summaries and so runs onto more than one line. It may also include more than one sentence.',
                 '    - Empty subsection',
                 '    - Third subsection: Third subsection summary.',
                 '* Another section: Summary for another section.',
                 '* Section without summary',
                 '    - Subsection: Subsection summary.'],
    'no-summary': ['* Section: Section summary.',
                   '    - Subsection: Subsection summary that is longer than other summaries and so runs onto more than one line. It may also include more than one sentence.',
                   '    - Empty subsection',
                   '    - Third subsection: Third subsection summary.',
                   '* Another section: Summary for another section.',
                   '* Section without summary',
                   '    - Subsection: Subsection summary.']}

logbook_outline = {
    'empty': None,
    'blank': None,
    'standard': ['* Page title: Page summary, including some `code` or links.',
                 '    - Section: Section summary.',
                 '        + Subsection: Subsection summary that is longer than other summaries and so runs onto more than one line. It may also include more than one sentence.',
                 '        + Empty subsection',
                 '        + Third subsection: Third subsection summary.',
                 '    - Another section: Summary for another section.',
                 '    - Section without summary',
                 '        + Subsection: Subsection summary.'],
    'plain': ['Page content.'],
    'no-title': ['Page summary, including some `code` or links.',
                 '',
                 '* Section: Section summary.',
                 '    - Subsection: Subsection summary that is longer than other summaries and so runs onto more than one line. It may also include more than one sentence.',
                 '    - Empty subsection',
                 '    - Third subsection: Third subsection summary.',
                 '* Another section: Summary for another section.',
                 '* Section without summary',
                 '    - Subsection: Subsection summary.'],
    'no-summary': ['* Section: Section summary.',
                   '    - Subsection: Subsection summary that is longer than other summaries and so runs onto more than one line. It may also include more than one sentence.',
                   '    - Empty subsection',
                   '    - Third subsection: Third subsection summary.',
                   '* Another section: Summary for another section.',
                   '* Section without summary',
                   '    - Subsection: Subsection summary.']}

first_blank_line = {
    'empty': 'None',
    'blank': '0',
    'standard': '1',
    'plain': 'None',
    'no-title': '1',
    'no-summary': '1'}

first_text_line = {
    'empty': 'None',
    'blank': 'None',
    'standard': '4',
    'plain': '0',
    'no-title': '2',
    'no-summary': '4'}

first_subtitle = {
    'empty': 'None',
    'blank': 'None',
    'standard': '8',
    'plain': 'None',
    'no-title': '6',
    'no-summary': '2'}

first_title = {
    'empty': 'None',
    'blank': 'None',
    'standard': '2',
    'plain': 'None',
    'no-title': '6',
    'no-summary': '2'}

def build_test_def(
        object_type='page', method_type='create', test_object=None,
        error_type=None, path=None, filename=None, title=None, parent=None):
    """Return a dictionary of test parameters for passing between functions."""
    return {'object_type': object_type,
            'method_type': method_type,
            'test_object': test_object,
            'error_type': error_type,
            'path': path,
            'filename': filename,
            'title': title,
            'parent': parent}

def modify_test_def(
        test_def, object_type=None, method_type=None, test_object=None,
        error_type=None, path=None, filename=None, title=None, parent=None):
    """Return a modified test definition for parametric testing."""
    new_test_def = test_def.copy()
    for key in new_test_def.keys():
        if eval(key) is not None:
            new_test_def[key] = eval(key)
    return new_test_def

def build_all_tests(object_type, method_type='create'):
    """Build all tests for all scenarios on the current method."""
    test_list = get_tests(object_type, method_type)
    return build_tests(test_list)

def build_tests(test_list):
    """Convert list of test scenarios to list of `pytest.param` objects."""
    new_test_list = []
    for test_scenario in test_list:
        new_test_list.append(build_test(*test_scenario))
    return new_test_list

def build_test(test_type, test_def, expected):
    """Create a Pytest parameter set for a parametric test."""
    test_params = build_test_params(test_type, test_def, expected)
    test_id = build_test_string(test_type, test_def, expected)
    return pytest.param(test_params, id=test_id)

def build_test_params(test_type, test_def, expected):
    """Set the parameter values to give to the test function."""
    params = {}
    params['test_type'] = test_type
    params['expected'] = expected
    if test_def['error_type'] is not None:
        params['error condition'] = f"pytest.raises({test_def['error_type']})"
    else:
        params['error condition'] = 'does_not_raise()'
    params['path'] = test_def['path'] or 'None'
    params['filename'] = test_def['filename'] or 'None'
    params['title'] = test_def['title'] or 'None'
    params['parent'] = get_generator(test_def['parent']) or 'None'
    method = get_method_parameters(test_def['method_type'])
    if method['do'] ==  'load':
        params['existing'] = 'None'
    elif method['do'] ==  'overwrite':
        params['existing'] = get_existing_generator(test_def['object_type'])
    elif method['do'] in ['valid', 'strip', 'make']:
        params['object'] = get_generator(test_def['test_object'])
    elif method['do'] in ['find', 'has']:
        if test_def['test_object'] is not None:
            params['object'] = test_contents[test_def['test_object']]
        else:
            params['object'] = None
    elif method['do'] == 'match':
        params['object'] = test_def['test_object']
    return params

def build_test_string(test_type, test_def, expected):
    """Create a test description string for a parametric test"""
    method = get_method_parameters(test_def['method_type'])
    if method['do'] == 'overwrite':
        test_id = f"{test_def['method_type']}, {test_type}"
    elif (method['do'] in ['valid', 'find', 'strip', 'has', 'make', 'read']
            and test_def['test_object'] is not None):
        test_id = f"{test_def['test_object']}, {test_type}"
    else:
        test_id = test_type
    test_string = []
    if 'clash' in test_type:
        return test_id
    elif test_type == 'invalid path':
        return f"{test_id}: {test_def['path']}"
    elif test_type == 'invalid file':
        filename = test_def['path'].replace("tmp_file_factory('","")[:-2]
        return f'{test_id}: {filename}'
    elif test_type == 'invalid folder':
        filename = test_def['path'].replace("tmp_folder_factory('","")[:-2]
        return f'{test_id}: {filename}'
    if test_def['path'] is not None:
        test_string.append('path')
    if test_def['title'] is not None:
        if test_def['title'] == get_matching(test_def['object_type'], 'title'):
            test_string.append('title')
        else:
            test_string.append(f"{test_def['title']}")
    if test_def['filename'] is not None:
        if test_def['filename'] == get_matching(
                test_def['object_type'], 'filename'):
            test_string.append('filename')
        else:
            test_string.append(f"{test_def['filename']}")
    if test_def['parent'] is not None:
        test_string.append(f"parent {test_def['parent']}")
    if len(test_string) > 0:
        if 'invalid' in test_type:
            test_id = f'{test_id}: ' + ', '.join(test_string)
        else:
            test_id = ', '.join(test_string) + f': {test_id}'
    return test_id

def get_tests(object_type, method_type):
    """Return a list of tests for all parameters of the current method."""
    test_def = build_test_def(object_type, method_type)
    parameter_list = get_parameter_list(method_type)
    method = get_method_parameters(method_type)
    tmp_path = get_temp_path(object_type)
    test_list = []
    if method['do'] in ['create', 'add', 'load', 'overwrite', 'rebuild']:
        test_list = test_list + get_object_tests(test_def)
        if 'path' in parameter_list:
            path_def = modify_test_def(test_def, path=tmp_path)
            test_list = test_list + get_object_tests(path_def)
        if method['do'] != 'rebuild':
            test_list = test_list + get_invalid_input_tests(test_def)
        if method['do'] == 'load':
            test_list = test_list + get_tests(object_type, 'overwrite')
    if method['do'] in ['valid', 'strip', 'make', 'read']:
        if 'path' in parameter_list:
            for test_object in test_objects:
                if object_type == 'function':
                    expected_object = get_test_object(method_type)
                    tmp_path = get_temp_path(test_object)
                object_def = modify_test_def(test_def,
                    test_object=test_object, path=tmp_path)
                test_list = test_list + get_validation_tests(object_def)
                test_list = test_list + get_io_tests(object_def)
                if object_type != 'function' or test_object == expected_object:
                    test_list = test_list + get_invalid_input_tests(object_def)
        if 'line' in parameter_list:
            for line_object in test_lines:
                if method['do'] == 'valid':
                    expected_object = get_test_object(method_type)
                else:
                    expected_object = 'text'
                object_def = modify_test_def(test_def, test_object=line_object)
                test_list = test_list + get_validation_tests(object_def)
                test_list = test_list + get_io_tests(object_def)
                if line_object == expected_object:
                    test_list = test_list + get_invalid_input_tests(object_def)
    if method['do'] in ['get', 'match', 'has', 'multiple']:
        if method['do'] == 'match':
            test_def = modify_test_def(test_def, test_object=tmp_path)
        creation_def = modify_test_def(test_def, method_type='create')
        path_def = modify_test_def(test_def, path=tmp_path)
        for combination in get_test_combinations(creation_def):
            new_test_def = modify_test_def(combination, method_type=method_type)
            new_path_def = modify_test_def(new_test_def, path=tmp_path)
            if method['do'] == 'has' and 'content' in parameter_list:
                for content in test_contents:
                    object_def = modify_test_def(new_test_def, test_object=content)
                    object_path_def = modify_test_def(new_path_def, test_object=content)
                    test_list = test_list + get_method_tests(object_def)
                    test_list = test_list + get_method_tests(object_path_def)
            elif method['do'] == 'multiple':
                test_list = test_list + get_validation_tests(new_test_def)
                test_list = test_list + get_validation_tests(new_path_def)
            else:
                test_list = test_list + get_method_tests(new_test_def)
                test_list = test_list + get_method_tests(new_path_def)
        test_list = test_list + get_io_tests(test_def)
        test_list = test_list + get_io_tests(path_def)
    if method['do'] == 'find':
        if 'content' in parameter_list:
            for content in test_contents:
                object_def = modify_test_def(test_def, test_object=content)
                test_list = test_list + get_validation_tests(object_def)
    if test_list == []:
        raise ValueError(f'Invalid test method type: {method_type}')
    return test_list

def get_test(test_type, test_def, expected):
    """Return a test scenario for the given test."""
    if 'Error' in expected[test_type]:
        new_test_def = modify_test_def(test_def, error_type=expected[test_type])
        return (test_type, new_test_def, 'None')
    else:
        return (test_type, test_def, expected[test_type])

def get_object_tests(test_def):
    """Return a list of all tests for a particular object."""
    test_list = []
    for combination in get_test_combinations(test_def):
        test_list = test_list + get_property_tests(combination)
    test_list = test_list + get_io_tests(test_def)
    return test_list

def get_property_tests(test_def):
    """Return a list of tests of page/notebook object properties."""
    expected = expectations(test_def)
    method = get_method_parameters(test_def['method_type'])
    if method['do'] == 'rebuild':
        test_list = [get_test('contents', test_def, expected)]
    else:
        test_list = []
        test_list.append(get_test('return type', test_def, expected))
        test_list.append(get_test('path', test_def, expected))
        test_list.append(get_test('contents', test_def, expected))
        test_list.append(get_test('title', test_def, expected))
        test_list.append(get_test('filename', test_def, expected))
        test_list.append(get_test('link', test_def, expected))
        test_list.append(get_test('parent', test_def, expected))
    return test_list

def get_validation_tests(test_def):
    """Return a list of tests that validate an object passed to a method."""
    test_list = []
    if test_def['method_type'].startswith('read'):
        test_list.append(get_test('contents', test_def, expectations(test_def)))
    else:
        test_list.append(get_test('result', test_def, expectations(test_def)))
    if ' line' in test_def['method_type']:
        new_test_line = test_def['test_object'] + ' + newline'
        new_test_def = modify_test_def(test_def, test_object=new_test_line)
        test_list.append(get_test('result', new_test_def, expectations(test_def)))
    return test_list

def get_method_tests(test_def):
    """Return a list of tests that check a result from an object method."""
    test_list = []
    expected = expectations(test_def)
    method = get_method_parameters(test_def['method_type'])
    if method['get'] in ['title', 'summary', 'outline', 'content', 'navigation',
                         'next', 'previous', 'up', 'month']:
        test_list.append(get_test('result', test_def, expected))
    elif method['get'] in ['pages', 'notebooks', 'logbooks']:
        test_list.append(get_test('return type', test_def, expected))
        test_list.append(get_test('contents', test_def, expected))
    else:
        raise ValueError(f"Invalid method call: {test_def['method_type']}")
    return test_list

def get_io_tests(test_def):
    """Return a list of tests of input/output that apply to all functions."""
    test_list = []
    if error_expected(test_def):
        return []
    test_list.append(('quiet', test_def, 'capsys.readouterr().out'))
    if test_def['path'] is not None:
        cloned_path = get_cloned_path(test_def)
        new_test_def = modify_test_def(test_def, path=cloned_path)
        test_list.append(('no changes', new_test_def, 'cloned_repo'))
    return test_list

def get_invalid_input_tests(test_def):
    """Return a list tests with invalid inputs for the different parameters."""
    test_list = []
    if error_expected(test_def):
        return []
    parameter_list = get_parameter_list(test_def['method_type'])
    method = get_method_parameters(test_def['method_type'])
    if 'path' in parameter_list:
        if test_def['object_type'] == 'function':
            tmp_path = get_temp_path(get_test_object(test_def['method_type']))
        else:
            tmp_path = get_temp_path(test_def['object_type'])
        path_def = modify_test_def(test_def, path=tmp_path)
        if 'title' in parameter_list:
            new_test_def = modify_test_def(path_def,
                                           error_type='ValueError',
                                           title="'Non-matching title'")
            test_list.append(('title clash', new_test_def, None))
        if 'filename' in parameter_list:
            new_test_def = modify_test_def(path_def,
                                           error_type='ValueError',
                                           filename="'unmatched_filename'")
            test_list.append(('filename clash', new_test_def, None))
        for test_path, error_type in invalid_paths:
            if method['do'] == 'read' and error_type == 'OSError':
                error_type = 'ValueError'
            new_test_def = modify_test_def(path_def,
                                           path=test_path,
                                           error_type=error_type)
            test_list.append(('invalid path', new_test_def, None))
        test_list = test_list + get_invalid_file_tests(path_def)
    if 'title' in parameter_list:
        for test_string in invalid_strings:
            new_test_def = modify_test_def(test_def,
                                           title=test_string,
                                           error_type='ValueError')
            test_list.append(('invalid title', new_test_def, None))
    if 'filename' in parameter_list:
        error_type = get_filename_error_type(test_def['object_type'])
        for test_string in invalid_strings:
            new_test_def = modify_test_def(test_def,
                                           filename=test_string,
                                           error_type=error_type)
            test_list.append(('invalid filename', new_test_def, None))
    if 'parent' in parameter_list:
        error_type = get_parent_error_type(test_def['method_type'])
        for test_parent in invalid_parents:
            new_test_def = modify_test_def(test_def,
                                           parent=test_parent,
                                           error_type=error_type)
            test_list.append(('invalid parent', new_test_def, None))
    if 'line' in parameter_list:
        for test_line in invalid_strings + ['None']:
            if method['do'] == 'strip':
                error_type = 'TypeError'
            elif method['do'] == 'make':
                error_type = 'ValueError'
            else:
                error_type = get_line_error_type(
                    get_test_object(test_def['method_type']))
                new_test_def = modify_test_def(test_def,
                                            test_object=test_line,
                                            error_type=error_type)
                test_list.append(('invalid line', new_test_def, None))
    return test_list

def get_invalid_file_tests(test_def):
    """Return a list of tests with invalid temporary file or folder objects."""
    method = get_method_parameters(test_def['method_type'])
    if method['do'] == 'valid':
        object_type = test_def['test_object']
        error_type = None
        expected = 'False'
    else:
        object_type = test_def['object_type']
        error_type = 'ValueError'
        expected = None
    if object_type in ['notebook', 'nested']:
        test_items = invalid_notebook
        generator = 'tmp_folder_factory'
        test_type = 'invalid folder'
    elif method['do'] == 'read':
        test_items = []
    elif object_type == 'logbook':
        test_items = invalid_logbook
        generator = 'tmp_folder_factory'
        test_type = 'invalid folder'
    else:
        test_items = invalid_filenames(object_type)
        generator = 'tmp_file_factory'
        test_type = 'invalid file'
    test_list = []
    for item in test_items:
        new_test_def = modify_test_def(
            test_def, path=f"{generator}('{item}')", error_type=error_type)
        test_list.append((test_type, new_test_def, expected))
    return test_list

def get_test_combinations(test_def):
    """Return a list of test definitions for different parameter combinations."""
    test_list = []
    parameter_list = get_parameter_list(test_def['method_type'])
    test_list.append(test_def)
    if 'title' in parameter_list:
        matching_title = get_matching(test_def['object_type'], 'title')
        test_list.append(modify_test_def(test_def, title=matching_title))
    if 'filename' in parameter_list:
        matching_filename = get_matching(test_def['object_type'], 'filename')
        test_list.append(modify_test_def(test_def, filename=matching_filename))
    if 'parent' in parameter_list:
        for test_parent in ['notebook', 'logbook']:
            test_list.append(modify_test_def(test_def, parent=test_parent))
    if 'title' in parameter_list and 'filename' in parameter_list:
        test_list.append(modify_test_def(test_def,
                                         title=matching_title,
                                         filename=matching_filename))
    if ('title' in parameter_list
            and 'filename' in parameter_list
            and 'parent' in parameter_list):
        for test_parent in ['notebook', 'logbook']:
            test_list.append(modify_test_def(test_def,
                                             title=matching_title,
                                             filename=matching_filename,
                                             parent=test_parent))
    if test_def['method_type'] == 'add':
        return [test for test in test_list if test['parent'] is not None]
    else:
        return test_list

def get_parameter_list(method_type):
    """Return list of the parameters to be tested for different methods."""
    method = get_method_parameters(method_type)
    if method['do'] in ['create', 'rebuild']:
        return ['path', 'title', 'filename', 'parent']
    elif method['do'] in ['add', 'multiple']:
        return ['path', 'parent']
    elif method['do'] in ['load', 'overwrite']:
        return ['path']
    elif method['do'] in ['valid', 'strip', 'make', 'match', 'read']:
        return [method['get']]
    elif method['do'] == 'get':
        return []
    elif method['do'] == 'find':
        return ['content']
    elif method['do'] == 'has':
        return ['path', 'title', 'filename', 'parent', 'content']
    else:
        raise ValueError(f'Invalid method type: {method_type}')

def get_temp_path(object_type):
    """Return name of temporary object fixture."""
    if object_type == 'page':
        return 'tmp_page'
    elif object_type == 'logbook page':
        return 'tmp_logbook_page'
    elif object_type == 'contents':
        return 'tmp_contents_page'
    elif object_type == 'logbook contents':
        return 'tmp_logbook_contents_page'
    elif object_type == 'logbook month':
        return 'tmp_logbook_month_page'
    elif object_type == 'home':
        return 'tmp_home_page'
    elif object_type == 'readme':
        return 'tmp_readme_page'
    elif object_type == 'logbook readme':
        return 'tmp_logbook_readme_page'
    elif object_type == 'notebook':
        return 'tmp_notebook'
    elif object_type == 'logbook':
        return 'tmp_logbook'
    elif object_type == 'nested':
        return 'tmp_nested'
    elif object_type == 'function':
        return None
    else:
        raise ValueError(f'Invalid test object: {object_type}')

def get_test_object(method_type):
    """Return type of object being checked for function methods."""
    return ' '.join(method_type.split()[2:])

def get_cloned_path(test_def):
    """Return path to a particular test object in the cloned repo."""
    if test_def['object_type'] == 'function':
        test_object_type = get_test_object(test_def['method_type'])
    else:
        test_object_type = test_def['object_type']
    if test_object_type == 'page':
        path = 'self.cloned_page'
    elif test_object_type == 'logbook page':
        path = 'self.cloned_logbook_page'
    elif test_object_type == 'contents':
        path = 'self.cloned_contents_page'
    elif test_object_type == 'logbook contents':
        path = 'self.cloned_logbook_contents_page'
    elif test_object_type == 'logbook month':
        path = 'self.cloned_logbook_month_page'
    elif test_object_type == 'home':
        path = 'self.cloned_home_page'
    elif test_object_type == 'readme':
        path = 'self.cloned_readme_page'
    elif test_object_type == 'logbook readme':
        path = 'self.cloned_logbook_readme_page'
    elif test_object_type in ['notebook', 'nested']:
        path = 'self.cloned_nested_notebook'
    elif test_object_type == 'logbook':
        path = 'self.cloned_logbook'
    else:
        raise ValueError(f'Invalid test object: {test_object_type}')
    return f'pathlib.Path(cloned_repo.working_dir).joinpath({path})'

def get_matching(object_type, parameter):
    """Return matching values for test parameters."""
    if object_type == 'page':
        if parameter == 'title':
            return 'self.test_page_title'
        elif parameter == 'filename':
            return 'tmp_page.stem.strip()'
        else:
            raise ValueError(f'Invalid matching parameter: {parameter}')
    elif object_type == 'logbook page':
        if parameter == 'title':
            return 'self.test_logbook_page_title'
        elif parameter == 'filename':
            return 'tmp_logbook_page.stem.strip()'
        else:
            raise ValueError(f'Invalid matching parameter: {parameter}')
    elif object_type in ['contents', 'logbook contents']:
        if parameter == 'title':
            return 'self.contents_descriptor'
        elif parameter == 'filename':
            return 'self.contents_filename'
        else:
            raise ValueError(f'Invalid matching parameter: {parameter}')
    elif object_type == 'home':
        if parameter == 'title':
            return 'self.homepage_descriptor'
        elif parameter == 'filename':
            return 'self.homepage_filename'
        else:
            raise ValueError(f'Invalid matching parameter: {parameter}')
    elif object_type == 'readme':
        if parameter == 'title':
            return 'self.test_notebook_title'
        elif parameter == 'filename':
            return 'self.readme_filename'
        else:
            raise ValueError(f'Invalid matching parameter: {parameter}')
    elif object_type == 'logbook readme':
        if parameter == 'title':
            return 'self.readme_descriptor'
        elif parameter == 'filename':
            return 'self.readme_filename'
        else:
            raise ValueError(f'Invalid matching parameter: {parameter}')
    elif object_type == 'logbook month':
        if parameter == 'title':
            return 'self.test_logbook_month_title'
        elif parameter == 'filename':
            return 'tmp_logbook_month_page.stem.strip()'
        else:
            raise ValueError(f'Invalid matching parameter: {parameter}')
    elif object_type in ['notebook', 'nested']:
        if parameter == 'title':
            return 'self.test_notebook_title'
        elif parameter == 'filename':
            return 'self.temp_notebook'
        else:
            raise ValueError(f'Invalid matching parameter: {parameter}')
    elif object_type == 'logbook':
        if parameter == 'title':
            return 'self.logbook_folder_name'
        elif parameter == 'filename':
            return 'self.temp_logbook'
        else:
            raise ValueError(f'Invalid matching parameter: {parameter}')
    else:
        raise ValueError(f'Invalid test object: {object_type}')

def get_generator(object_type):
    """Return code to generate a particular object."""
    if object_type == 'page':
        return 'pn.Page()'
    elif object_type == 'logbook page':
        return 'pn.LogbookPage()'
    elif object_type == 'logbook month':
        return 'pn.LogbookMonth()'
    elif object_type == 'contents':
        return 'pn.ContentsPage()'
    elif object_type == 'home':
        return 'pn.HomePage()'
    elif object_type == 'readme':
        return 'pn.ReadmePage()'
    elif object_type == 'notebook':
        return 'pn.Notebook()'
    elif object_type == 'logbook':
        return 'pn.Logbook()'
    elif object_type is None:
        return None
    elif object_type in test_lines:
        return f"test_lines['{object_type}']"
    elif 'newline' in object_type:
        return f"test_lines['{object_type.split()[0]}'\n]"
    else:
        return object_type

def get_filename_error_type(object_type):
    """Different objects can cause different error types."""
    if object_type in ['logbook page', 'logbook month']:
        return 'TypeError'
    else:
        return 'ValueError'

def get_parent_error_type(method_type):
    """Different methods can cause different error types."""
    if method_type == 'add':
        return 'AttributeError'
    else:
        return 'ValueError'

def get_line_error_type(line_type):
    """Different methods can cause different error types."""
    if line_type in ['navigation', 'link']:
        return 'TypeError'
    elif line_type == 'text':
        return 'ValueError'
    else:
        return 'AttributeError'

def get_title_from_filename(filename, object_type):
    """Work out what the generated filename should be."""
    if object_type in ['logbook page', 'logbook month']:
        return filename
    else:
        return f"{filename}.replace('_', ' ').replace('-', ' ').strip()"

def get_existing_object(object_type):
    """Return existing object name, filename and contents for overwrite tests."""
    if object_type == 'page':
        object_name = 'existing_page'
        filename = 'existing_page.md'
        contents = 'self.test_logbook_page'
    elif object_type == 'logbook page':
        object_name = 'existing_page'
        filename = '2001-01-01.md'
        contents = 'self.test_logbook_page'
    elif object_type == 'logbook month':
        object_name = 'existing_page'
        filename = '2001-01.md'
        contents = 'self.test_logbook_page'
    elif object_type in ['contents', 'logbook contents']:
        object_name = 'existing_page'
        filename = 'Contents.md'
        contents = 'self.test_logbook_page'
    elif object_type == 'home':
        object_name = 'existing_page'
        filename = 'Home.md'
        contents = 'self.test_logbook_page'
    elif object_type in ['readme', 'logbook readme']:
        object_name = 'existing_page'
        filename = 'Readme.md'
        contents = 'self.test_logbook_page'
    elif object_type == 'notebook':
        object_name = 'existing_notebook'
        filename = 'existing_notebook'
        contents = 'tmp_notebook'
    elif object_type == 'logbook':
        object_name = 'existing_logbook'
        filename = 'Logbook'
        contents = 'tmp_logbook'
    elif object_type == 'nested':
        object_name = 'existing_notebook'
        filename = 'existing_notebook'
        contents = 'tmp_nested'
    else:
        raise ValueError(f'Invalid existing object type: {object_type}')
    return object_name, filename, contents

def get_existing_generator(object_type):
    """Return code to generate existing objects for overwrite tests."""
    _, filename, contents = get_existing_object(object_type)
    if object_type in ['notebook', 'logbook', 'nested']:
        return (f"shutil.copytree({contents}, tmp_folder_factory('{filename}'),"
                                 "dirs_exist_ok=True)")
    else:
        return f"shutil.copyfile({contents}, tmp_file_factory('{filename}'))"

def get_method_parameters(method_string):
    """For method tests, return a dictionary of parameters."""
    params = {}
    components = method_string.split()
    params['do'] = components[0]
    if len(components) > 1:
        params['get'] = components[1]
    else:
        params['get'] = None
    if len(components) > 2:
        params['link'] = components[2]
    else:
        params['link'] = None
    if len(components) > 3:
        params['generator'] = components[3]
    else:
        params['generator'] = None
    return params

def is_valid_nesting(test_def):
    """Does the object fit inside its parent?"""
    if (test_def['object_type'] in ['notebook', 'logbook', 'nested']
        and test_def['parent'] == 'logbook'):
        # Logbooks can't contain nested notebooks
        return False
    elif (test_def['object_type'] == 'page'
        and test_def['parent'] == 'logbook'):
        # Logbooks can't contain standard pages
        if (test_def['path'] is None
                and test_def['method_type'] in ['add', 'multiple']):
            # This combination creates a default page, so is ok
            return True
        else:
            # Other combinations are not ok
            return False
    elif (test_def['object_type'] in ['logbook page', 'logbook month']
        and test_def['parent'] == 'notebook'):
        # Standard notebook can't contain logbook pages
        if test_def['method_type'] in ['add', 'multiple']:
            # This combination creates a default page, so is ok
            return True
        else:
            # Other combinations are not ok
            return False
    elif (test_def['object_type'] == 'nested'
        and test_def['path'] is not None):
        # Nested notebook fixture has a homepage at the root
        return False
    else:
        return True

def error_expected(test_def):
    """Is the current test expected to produce an error?"""
    if test_def['error_type'] is not None:
        return True
    expected = expectations(test_def)
    if 'result' in expected and 'Error' in expected['result']:
        return True
    elif 'return type' in expected and 'Error' in expected['return type']:
        return True
    return False

# Define expectations for parametric tests
def expectations(test_def):
    """Return dictionary of expected values for the current tests."""
    expected = {}
    method = get_method_parameters(test_def['method_type'])
    # Expected object properties
    expected['path'] = 'None'
    expected['title'] = None
    expected['filename'] = None
    expected['link'] = None
    title_from_contents = None
    title_from_path = None
    if test_def['object_type'] == 'page':
        expected['return type'] = 'pn.Page'
        title_from_contents = 'self.test_page_title'
        summary = 'self.test_page_summary'
        outline = 'self.test_page_outline'
        navigation = 'self.test_page_navigation'
    elif test_def['object_type'] == 'logbook page':
        expected['return type'] = 'pn.LogbookPage'
        title_from_path = 'self.test_logbook_page_title'
        summary = 'self.test_logbook_page_summary'
        outline = 'self.test_logbook_page_outline'
        navigation = 'self.test_logbook_page_navigation'
    elif test_def['object_type'] in ['contents', 'logbook contents']:
        expected['return type'] = 'pn.ContentsPage'
        expected['title'] = 'self.contents_descriptor'
        expected['filename'] = 'self.contents_filename'
        expected['link'] = 'self.contents_filename'
        if test_def['object_type'] == 'logbook contents':
            summary = 'self.test_logbook_contents_page_summary'
            outline = 'self.test_logbook_contents_page_outline'
        else:
            summary = 'self.test_contents_page_summary'
            outline = 'self.test_contents_page_outline'
        navigation = 'None'
    elif test_def['object_type'] == 'home':
        expected['return type'] = 'pn.HomePage'
        expected['title'] = 'self.homepage_descriptor'
        expected['filename'] = 'self.homepage_filename'
        expected['link'] = 'self.homepage_filename'
        summary = 'self.test_home_page_summary'
        outline = 'self.test_home_page_outline'
        navigation = 'None'
    elif test_def['object_type'] == 'readme':
        expected['return type'] = 'pn.ReadmePage'
        expected['title'] = 'self.readme_descriptor'
        title_from_contents = 'self.test_notebook_title'
        expected['filename'] = 'self.readme_filename'
        expected['link'] = 'self.readme_filename'
        summary = 'self.test_readme_page_summary'
        outline = 'self.test_readme_page_outline'
        navigation = 'None'
    elif test_def['object_type'] == 'logbook readme':
        expected['return type'] = 'pn.ReadmePage'
        expected['title'] = 'self.readme_descriptor'
        expected['filename'] = 'self.readme_filename'
        expected['link'] = 'self.readme_filename'
        summary = 'self.test_logbook_readme_page_summary'
        outline = 'self.test_logbook_readme_page_outline'
        navigation = 'None'
    elif test_def['object_type'] == 'logbook month':
        expected['return type'] = 'pn.LogbookMonth'
        title_from_contents = 'self.test_logbook_month_title'
        summary = 'None'
        outline = 'None'
        navigation = 'self.test_logbook_month_page_navigation'
    elif test_def['object_type'] in ['notebook', 'nested']:
        expected['return type'] = 'pn.Notebook'
        title_from_contents = 'self.test_notebook_title'
        summary = 'self.test_readme_page_summary'
        outline = 'NotImplementedError'
        navigation = 'self.test_notebook_navigation'
        if test_def['parent'] is None:
            expected['link'] = 'self.homepage_descriptor'
        else:
            expected['link'] = 'self.contents_descriptor'
    elif test_def['object_type'] == 'logbook':
        expected['return type'] = 'pn.Logbook'
        title_from_contents = 'self.logbook_folder_name'
        summary = 'self.test_logbook_readme_page_summary'
        outline = 'NotImplementedError'
        navigation = 'self.test_logbook_navigation'
        if test_def['parent'] is None:
            expected['link'] = 'self.homepage_descriptor'
        else:
            expected['link'] = 'self.contents_descriptor'
    elif test_def['object_type'] == 'function':
        pass
    else:
        raise ValueError(f"Invalid test object type: {test_def['object_type']}")
    if test_def['filename'] is not None:
        expected['filename'] = test_def['filename']
        if test_def['object_type'] not in ['notebook',
                                           'logbook',
                                           'nested']:
            expected['link'] = test_def['filename']
        expected['title'] = get_title_from_filename(
            test_def['filename'], test_def['object_type'])
    if test_def['title'] is not None:
        expected['title'] = test_def['title']
    if test_def['method_type'] == 'overwrite':
        existing_object, *_ = get_existing_object(test_def['object_type'])
        expected['path'] = existing_object
        expected['filename'] = f'{existing_object}.stem'
        if test_def['object_type'] in ['notebook', 'logbook', 'nested']:
            expected['title'] = title_from_contents
            expected['link'] = 'self.homepage_descriptor'
        else:
            expected['title'] = get_title_from_filename(
                expected['filename'], test_def['object_type'])
            expected['link'] = expected['filename']
    if test_def['path'] is not None:
        if test_def['method_type'] in ['create', 'add']:
            expected['path'] = test_def['path']
            expected['title'] = title_from_path or expected['title']
            expected['filename'] = str(test_def['path'])+'.stem'
            if test_def['object_type'] not in ['notebook',
                                               'logbook',
                                               'nested']:
                expected['link'] = str(test_def['path'])+'.stem'
        expected['contents'] = test_def['path']
        expected['title'] = title_from_contents or expected['title']
    else:
        if test_def['method_type'] == 'overwrite':
            expected['contents'] = existing_object
        else:
            expected['path'] = 'None'
            expected['contents'] = '[]'
    expected['title'] = expected['title'] or 'self.unknown_descriptor'
    expected['filename'] = expected['filename'] or 'self.unknown_descriptor'
    expected['link'] = expected['link'] or 'self.unknown_descriptor'
    if test_def['parent'] is not None:
        if is_valid_nesting(test_def):
            expected['parent'] = 'test_parent'
            # Handle nesting that is valid but non-standard
            if (test_def['object_type'] in ['logbook page', 'logbook month']
                    and test_def['parent'] == 'notebook'):
                expected['return type'] = 'pn.Page'
                if test_def['path'] is not None:
                    expected['title'] = expected['title'] + ".replace('-', ' ')"
            elif (test_def['object_type'] == 'logbook month'
                    and test_def['path'] is None):
                expected['return type'] = 'pn.LogbookPage'
        else:
            expected['return type'] = 'ValueError'
            expected['path'] = 'ValueError'
            expected['contents'] = 'ValueError'
            expected['title'] = 'ValueError'
            expected['filename'] = 'ValueError'
            expected['link'] = 'ValueError'
            expected['parent'] = 'ValueError'
            expected['result'] = 'ValueError'
    else:
        expected['parent'] = 'None'
    # Expected method results
    if method['do'] == 'multiple':
        if 'Error' not in expected['return type']:
            if test_def['object_type'] in ['page', 'logbook page',
                                           'logbook month']:
                expected['result'] = 'test_page'
            else:
                expected['result'] = 'ValueError'
    elif method['do'] == 'valid':
        if test_def['object_type'] == 'function':
            expected_object_type = get_test_object(test_def['method_type'])
            given_object_type = test_def['test_object']
        else:
            expected_object_type = test_def['test_object']
            given_object_type = test_def['object_type']
        if (   (    expected_object_type in ['notebook', 'logbook', 'nested']
                and given_object_type not in ['notebook', 'logbook', 'nested'])
            or (    expected_object_type not in ['notebook', 'logbook', 'nested']
                and given_object_type in ['notebook', 'logbook', 'nested'])):
            expected['result'] = 'OSError'
        elif expected_object_type == 'page':
            expected['result'] = 'True'
        elif expected_object_type == given_object_type:
            expected['result'] = 'True'
        elif (   (    expected_object_type == 'contents'
                  and given_object_type == 'logbook contents')
              or (    expected_object_type == 'readme'
                  and given_object_type == 'logbook readme')
              or (    expected_object_type == 'notebook'
                  and given_object_type == 'nested')):
            expected['result'] = 'True'
        else:
            expected['result'] = 'False'
    elif method['do'] == 'get':
        if method['generator'] is not None:
            creation_def = modify_test_def(test_def, method_type='create')
            creation_expectations = expectations(creation_def)
            expected_generator = creation_expectations[method['generator']]
            if 'Error' in expected_generator:
                expected['result'] = expected_generator
            else:
                new_def = build_test_def(test_def['object_type'], 'create')
                new_def = eval(f"modify_test_def(new_def, "
                               f"{method['generator']}=expected_generator)")
                expected['result'] = expectations(new_def)[method['get']]
        else:
            if 'Error' not in expected['return type']:
                if method['get'] in ['summary', 'outline']:
                    expected_result = eval(method['get'])
                    if (test_def['path'] is not None
                            or 'Error' in expected_result):
                        expected['result'] = expected_result
                    else:
                        expected['result'] = 'None'
                elif method['get'] == 'navigation':
                    if navigation != 'None' and test_def['parent'] is not None:
                        if test_def['path'] is None and test_def['title'] is None:
                            if test_def['filename'] is not None:
                                navigation = f"{test_def['filename']}.replace('_', ' ')"
                            else:
                                if test_def['object_type'] in ['logbook page',
                                                               'logbook month']:
                                    navigation = 'None'
                                else:
                                    navigation = 'self.unknown_descriptor'
                        if (test_def['object_type'] == 'logbook month'
                                and test_def['path'] is None
                                and test_def['title'] is None):
                            expected['result'] = 'self.navigation_home_pages'
                        elif test_def['object_type'] in ['logbook page',
                                                         'logbook month']:
                            expected['result'] = navigation
                        elif test_def['object_type'] in ['notebook', 'logbook',
                                                         'nested']:
                            expected['result'] = ("self.navigation_home_notebooks + "
                                                + "self.navigation_separator + "
                                                + navigation)
                        else:
                            expected['result'] = ("self.navigation_home_pages + "
                                                + "self.navigation_separator + "
                                                + navigation)
                    else:
                        expected['result'] = 'None'
                elif method['get'] in ['pages', 'notebooks', 'logbooks']:
                    expected['return type'] = 'list'
                    if (method['get'] in ['notebooks', 'logbooks']
                            and test_def['object_type'] != 'nested'):
                        expected['contents'] = '[]'
                    if (test_def['object_type'] == 'logbook month'
                            and method['get'] == 'pages'):
                        if (test_def['parent'] is not None
                                and (test_def['path'] is not None
                                     or test_def['filename'] is not None)):
                            expected['contents'] = 'this_month_pages'
                        else:
                            expected['contents'] = '[]'
                elif method['get'] in ['next', 'previous', 'up']:
                    if (method['get'] == 'up'
                            and test_def['object_type'] == 'logbook month'):
                        expected['result'] = 'test_parent'
                    elif (test_def['parent'] is not None
                            and (test_def['path'] is not None
                                or test_def['filename'] is not None
                                or test_def['title'] is not None)):
                        expected['result'] = 'extra_page'
                    else:
                        expected['result'] = 'None'
                elif method['get'] == 'month':
                    if (test_def['path'] is not None
                            or test_def['filename'] is not None):
                        expected['result'] = 'self.temp_logbook_month'
                    else:
                        expected['result'] = 'None'
    elif method['do'] == 'find':
        if method['get'] == 'blank':
            expected['result'] = first_blank_line[test_def['test_object']]
        elif method['get'] == 'text':
            expected['result'] = first_text_line[test_def['test_object']]
        elif method['get'] == 'subtitle':
            expected['result'] = first_subtitle[test_def['test_object']]
        elif method['get'] == 'first_title':
            expected['result'] = first_title[test_def['test_object']]
        elif method['get'] == 'title':
            if test_def['object_type'] == 'logbook page':
                expected['result'] = f"logbook_title['{test_def['test_object']}']"
            else:
                expected['result'] = f"contents_title['{test_def['test_object']}']"
        elif method['get'] == 'summary':
            expected['result'] = f"contents_summary['{test_def['test_object']}']"
        elif method['get'] == 'sections':
            if test_def['object_type'] == 'logbook page':
                expected['result'] = f"logbook_sections['{test_def['test_object']}']"
            else:
                expected['result'] = f"contents_sections['{test_def['test_object']}']"
        elif method['get'] == 'outline':
            if test_def['object_type'] == 'logbook page':
                expected['result'] = f"logbook_outline['{test_def['test_object']}']"
            else:
                expected['result'] = f"contents_outline['{test_def['test_object']}']"
        else:
            raise ValueError(f"Unexpected object to find: {method['get']}")
    elif method['do'] == 'strip':
        test_type = get_test_object(test_def['method_type'])
        line_type = test_def['test_object']
        if test_type in ['reference', 'default']:
            expected['result'] = f"test_lines_strip_reference_links['{line_type}']"
        elif test_type == 'absolute':
            expected['result'] = f"test_lines_strip_absolute_links['{line_type}']"
        elif test_type == 'all':
            expected['result'] = f"test_lines_strip_all_links['{line_type}']"
    elif method['do'] == 'match':
        if not 'result' in expected:
            if test_def['test_object'] == test_def['path']:
                expected['result'] = 'True'
            else:
                expected['result'] = 'False'
    elif method['do'] == 'has':
        if method['get'] == 'summary':
            if not 'Error' in expected['return type']:
                if test_def['test_object'] is None:
                    expected['result'] = 'False'
                elif test_def['object_type'] == 'logbook page':
                    expected['result'] = ("logbook_summary['"
                                        + test_def['test_object']
                                        + "'] is not None")
                else:
                    expected['result'] = ("contents_summary['"
                                        + test_def['test_object']
                                        + "'] is not None")
    elif method['do'] == 'read':
        if test_def['test_object'] is None:
            expected['contents'] = 'None'
        elif test_def['test_object'] in ['notebook', 'logbook']:
            expected['result'] = 'ValueError'
            expected['contents'] = 'ValueError'
        else:
            expected['contents'] = get_temp_path(test_def['test_object'])
    elif method['do'] == 'make':
        if 'Error' in test_lines_title[test_def['test_object']]:
            expected['result'] = test_lines_title[test_def['test_object']]
        else:
            expected['result'] = f"test_lines_title['{test_def['test_object']}']"
    elif method['do'] == 'rebuild':
        if 'Error' not in expected['contents']:
            if (test_def['parent'] is not None
                    and is_valid_nesting(test_def)
                    and (test_def['path'] is not None
                        or test_def['filename'] is not None)):
                expected['contents'] = get_temp_path(test_def['object_type'])
            else:
                expected['contents'] = '[]'
    return expected


# Invalid objects for parametrised testing
invalid_paths = [
        ("'string'", 'AttributeError'),
        ("3.142", 'AttributeError'),
        ("[1, 2, 3]", 'AttributeError'),
        ("pathlib.Path('/not/a/path')", 'OSError')]

invalid_folders = ['.vscode', '.config']

invalid_notebook = invalid_folders + ['Logbook', 'Attachments']

invalid_logbook = invalid_folders + [
    'Notebooks', 'PKU-2019', 'Software', 'Attachments']

invalid_parents = [
    "'string'",
    "3.142",
    "[1, 2, 3]",
    "pathlib.Path('/not/a/path')",
    "pathlib.Path.home()",
    "pn.Page()"]

invalid_strings = [
    "3.142",
    "[1, 2, 3]",
    "pathlib.Path('/not/a/path')",
    "pathlib.Path.home()",
    "pn.Page()",
    "pn.Notebook()"]

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
        if object_type not in ['logbook page', 'logbook month']:
            filename_list.append('2020-01-01.md')
            filename_list.append('2020-01.md')
        if object_type != 'home':
            filename_list.append('Home.md')
        if object_type not in ['contents', 'logbook contents']:
            filename_list.append('Contents.md')
        if object_type not in ['readme', 'logbook readme']:
            filename_list.append('Readme.md')
        return filename_list


# Main test class
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
        self.temp_notebook = 'temp_notebook'
        self.temp_page = 'temp_file'
        self.temp_pages = ['page1.md', 'page2.md', 'page3.md']
        self.temp_logbook = 'Logbook'
        self.temp_logbook_page = '2020-01-01'
        self.temp_logbook_month = '2020-01'
        self.temp_logbook_pages = ['2020-01-01.md',
                                   '2020-01-02.md',
                                   '2020-01-03.md']
        self.extra_logbook_month = '2019-12'
        self.test_message = 'Hello world'
        self.test_page_title = 'Page title'
        self.test_logbook_page_title = self.temp_logbook_page
        self.test_logbook_month_title = 'January 2020'
        self.test_notebook_title = 'Notebook title'
        self.test_page_summary = 'Page summary, including some `code` or links.'
        self.test_logbook_page_summary = 'Page *summary*, including some `code` or links.'
        self.test_contents_page_summary = 'Description of notebook scope and contents.'
        self.test_home_page_summary = 'This page explains the overall contents.'
        self.test_readme_page_summary = 'Description of notebook scope and contents.'
        self.test_logbook_contents_page_summary = None
        self.test_logbook_readme_page_summary = 'Logbook for this notebook scope.'
        self.test_page_outline = [self.test_page_summary,
                                  '',
                                  '* Subsection title: Subsection summary.']
        self.test_logbook_page_outline = [self.test_logbook_page_summary,
                                          '',
                                          '* Section: Summary for contents in a separate logbook.',
                                          '* Another section: Summary for contents in a different logbook.',
                                          '* Other work and communications: Subsection summary.']
        self.test_contents_page_outline = [self.test_contents_page_summary,
                                           '',
                                           '* Folders',
                                           '    - Admin: Various administrative notes and records.',
                                           '    - Project: Notebook for a particular project.',
                                           '    - Logbook: Logbook for this notebook scope.',
                                           '* Pages',
                                           '    - Preparatory research: Research into the project.',
                                           '    - Software links: Some information about software related to this notebook scope.']
        self.test_home_page_outline = [self.test_home_page_summary]
        self.test_readme_page_outline = [self.test_readme_page_summary]
        self.test_logbook_contents_page_outline = [self.test_logbook_contents_page_summary]
        self.test_logbook_readme_page_outline = [self.test_logbook_readme_page_summary]
        self.page_suffix = '.md'
        self.homepage_descriptor = 'Home'
        self.homepage_filename = 'Home'
        self.contents_descriptor = 'Contents'
        self.contents_filename = 'Contents'
        self.readme_filename = 'Readme'
        self.readme_descriptor = 'Readme'
        self.logbook_folder_name = 'Logbook'
        self.unknown_descriptor = 'Unknown'
        self.test_page_navigation = self.test_page_title
        self.test_logbook_page_navigation = '[< 2019-01-01](2019-01-01) | [January 2020](2020-01) | [2021-01-01 >](2021-01-01)'
        self.test_logbook_month_page_navigation = '[< 2019-01](2019-01) | [Home](Home) | [2021-01 >](2021-01)'
        self.test_notebook_navigation = self.test_notebook_title
        self.test_logbook_navigation = self.temp_logbook
        self.navigation_home_pages = f'[{self.homepage_descriptor}]({self.homepage_filename})'
        self.navigation_home_notebooks = f'[{self.homepage_descriptor}](../{self.homepage_filename})'
        self.navigation_separator = ' > '
        self.blank_line = ''


    # Fixtures
    @pytest.fixture
    def tmp_file_factory(self, tmp_path):
        created_files = []
        factory_path = tmp_path.joinpath('factory')
        factory_path.mkdir()
        def _new_temp_file(filename):
            tempfile = factory_path.joinpath(filename)
            with open(tempfile, 'w') as f:
                f.write(self.test_message)
            created_files.append(tempfile)
            return tempfile
        yield _new_temp_file
        for file in created_files:
            if file.is_file():
                file.unlink()

    @pytest.fixture
    def tmp_folder_factory(self, tmp_path):
        created_folders = []
        factory_path = tmp_path.joinpath('folders')
        factory_path.mkdir()
        def _new_temp_folder(folder_name):
            temp_folder = factory_path.joinpath(folder_name)
            temp_folder.mkdir()
            created_folders.append(temp_folder)
            return temp_folder
        yield _new_temp_folder
        for folder in created_folders:
            if folder.is_dir():
                shutil.rmtree(folder)

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
    def tmp_notebook_without_readme(self, tmp_path):
        """Create a temporary notebook folder and add some pages."""
        notebook_folder = tmp_path.joinpath(self.temp_notebook)
        self.create_and_fill_folder(notebook_folder, add_readme=False)
        yield notebook_folder
        shutil.rmtree(notebook_folder)

    @pytest.fixture
    def tmp_logbook_without_readme(self, tmp_path):
        """Create a temporary logbook folder and add some pages."""
        logbook_folder = tmp_path.joinpath(self.temp_logbook)
        self.create_and_fill_folder(
            logbook_folder, is_logbook=True, add_readme=False)
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
        cloned_repo = source_repo.clone(destination_path, branch='master')
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

    def assert_page_contents_match(self, test_contents, generator_page):
        """Assert that page contents match the generator page file."""
        with open(generator_page, 'r')  as f:
            file_contents = [line.strip() for line in f.readlines()]
        assert test_contents == file_contents

    def assert_notebook_contents_match(self, notebook_contents, tmp_notebook):
        """Assert that notebook contents match the generator folder."""
        for filename in self.temp_pages:
            this_path = tmp_notebook.joinpath(filename)
            assert this_path in [item.path for item in notebook_contents
                                 if isinstance(item, pn.Page)]
        for item in notebook_contents:
            if not isinstance(item, pn.Page):
                continue
            if isinstance(item, pn.HomePage):
                self.assert_page_contents_match(item.contents, self.test_home_page)
            elif isinstance(item, pn.ContentsPage):
                self.assert_page_contents_match(item.contents, self.test_contents_page)
            elif isinstance(item, pn.ReadmePage):
                self.assert_page_contents_match(item.contents, self.test_readme_page)
            else:
                self.assert_page_contents_match(item.contents, self.test_page)

    def assert_logbook_contents_match(self, logbook_contents, tmp_logbook):
        """Assert that logbook contents match the generator folder."""
        for filename in self.temp_logbook_pages:
            this_path = tmp_logbook.joinpath(filename)
            assert this_path in [item.path for item in logbook_contents
                                 if isinstance(item, pn.Page)]
        for item in logbook_contents:
            if not isinstance(item, pn.Page):
                continue
            if isinstance(item, pn.ContentsPage):
                self.assert_page_contents_match(
                        item.contents, self.test_logbook_contents_page)
            elif isinstance(item, pn.ReadmePage):
                self.assert_page_contents_match(
                        item.contents, self.test_logbook_readme_page)
            else:
                assert isinstance(item, pn.LogbookPage)
                self.assert_page_contents_match(
                        item.contents, self.test_logbook_page)

    def assert_contents_match(self, test_object, expected):
        """Select correct assertion based on object type."""
        if isinstance(test_object, pn.Page):
            self.assert_page_contents_match(test_object.contents, expected)
        elif isinstance(test_object, pn.Logbook):
            self.assert_logbook_contents_match(test_object.contents, expected)
        elif isinstance(test_object, pn.Notebook):
            self.assert_notebook_contents_match(test_object.contents, expected)
        elif isinstance(test_object, list):
            if len(test_object) == 0:
                assert test_object == expected
            elif isinstance(test_object[0], pn.Notebook):
                expected = expected.joinpath(test_object[0].filename)
                test_object = test_object[0].contents
                if expected.name == self.temp_logbook:
                    self.assert_logbook_contents_match(test_object, expected)
                else:
                    self.assert_notebook_contents_match(test_object, expected)
            else:
                if isinstance(expected, list):
                    assert test_object == expected
                elif isinstance(expected, pathlib.Path):
                    if expected.name == self.temp_logbook:
                        self.assert_logbook_contents_match(test_object, expected)
                    elif expected.is_file():
                        self.assert_page_contents_match(test_object, expected)
                    else:
                        self.assert_notebook_contents_match(test_object, expected)
                else:
                    raise ValueError(f'Invalid expected object: {expected}')
        else:
            raise ValueError(f'Invalid test object for matching: {test_object}')


    # Parametric assertions
    def assert_parametric(self, test_object, test_type, expected):
        if test_type == 'result':
            assert test_object == expected
        elif 'invalid' in test_type:
            assert test_object == False
        elif test_type == 'return type':
            assert isinstance(test_object, expected)
        elif test_type == 'path':
            if expected is None:
                assert test_object.path is None
            else:
                assert isinstance(test_object.path, pathlib.Path)
                assert test_object.path == expected
        elif test_type == 'contents':
            if test_object is None:
                contents = None
            elif isinstance(test_object, list):
                contents = test_object
            else:
                contents = test_object.contents
            if expected is None:
                assert contents is None
            elif expected == []:
                assert isinstance(contents, list)
                assert contents == []
            else:
                assert isinstance(contents, list)
                self.assert_contents_match(test_object, expected)
        elif test_type == 'parent':
            if expected is None:
                assert test_object.parent is None
            else:
                assert isinstance(test_object.parent, pn.TreeItem)
                assert test_object.parent == expected
        elif test_type == 'title':
            if expected is None:
                assert test_object.title is None
            else:
                assert isinstance(test_object.title, str)
                assert test_object._is_valid_title(test_object.title)
                assert test_object.title == expected
        elif test_type == 'filename':
            if expected is None:
                assert test_object.filename is None
            else:
                assert isinstance(test_object.filename, str)
                assert test_object._is_valid_filename(test_object.filename)
                assert test_object.filename == expected
        elif test_type == 'link':
            if expected is None:
                assert test_object.link is None
            else:
                assert isinstance(test_object.link, str)
                assert test_object._is_valid_link(test_object.link)
                assert test_object.link == expected
        elif test_type == 'quiet':
            assert len(expected) == 0
        elif test_type == 'no changes':
            self.assert_repo_unchanged(expected)
        else:
            raise ValueError(f'Invalid test type: {test_type}')


    # --------------------------------------------------------------------------
    # Tests start
    # --------------------------------------------------------------------------

    # Constants
    @pytest.mark.parametrize('constant, value', [
        ('pn.PAGE_SUFFIX', 'self.page_suffix'),
        ('pn.HOME_DESCRIPTOR', 'self.homepage_descriptor'),
        ('pn.HOMEPAGE_FILENAME', 'self.homepage_filename'),
        ('pn.CONTENTS_DESCRIPTOR', 'self.contents_descriptor'),
        ('pn.CONTENTS_FILENAME', 'self.contents_filename'),
        ('pn.README_DESCRIPTOR', 'self.readme_descriptor'),
        ('pn.README_FILENAME', 'self.readme_filename'),
        ('pn.LOGBOOK_FOLDER_NAME', 'self.logbook_folder_name'),
        ('pn.UNKNOWN_DESCRIPTOR', 'self.unknown_descriptor'),
        ('pn.BLANK_LINE', 'self.blank_line')])
    def test_constant_value(self, constant, value):
        assert eval(constant) == eval(value)


    # Creating page objects
    @pytest.mark.parametrize('test_params', build_all_tests('page'))
    def test_create_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('logbook page'))
    def test_create_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookPage(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('contents'))
    def test_create_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_contents_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ContentsPage(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('logbook contents'))
    def test_create_logbook_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_contents_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ContentsPage(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('logbook month'))
    def test_create_logbook_month_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_month_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookMonth(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('home'))
    def test_create_home_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_home_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.HomePage(path=eval(test_params['path']),
                                    filename=test_filename,
                                    title=test_title,
                                    parent=test_parent)
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('readme'))
    def test_create_readme_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_readme_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ReadmePage(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('logbook readme'))
    def test_create_logbook_readme_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_readme_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ReadmePage(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))


    # Loading data to page objects
    @pytest.mark.parametrize('test_params', build_all_tests('page', 'load'))
    def test_load_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page):
        with eval(test_params['error condition']):
            existing_page = eval(test_params['existing'])
            test_page = pn.Page(path=existing_page)
            test_page.load_contents(eval(test_params['path']))
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'load'))
    def test_load_contents_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_page):
        with eval(test_params['error condition']):
            existing_page = eval(test_params['existing'])
            test_page = pn.LogbookPage(path=existing_page)
            test_page.load_contents(eval(test_params['path']))
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('contents', 'load'))
    def test_load_contents_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_contents_page):
        with eval(test_params['error condition']):
            existing_page = eval(test_params['existing'])
            test_page = pn.ContentsPage(path=existing_page)
            test_page.load_contents(eval(test_params['path']))
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook contents', 'load'))
    def test_load_contents_logbook_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_contents_page):
        with eval(test_params['error condition']):
            existing_page = eval(test_params['existing'])
            test_page = pn.ContentsPage(path=existing_page)
            test_page.load_contents(eval(test_params['path']))
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'load'))
    def test_load_contents_logbook_month_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_month_page):
        with eval(test_params['error condition']):
            existing_page = eval(test_params['existing'])
            test_page = pn.LogbookMonth(path=existing_page)
            test_page.load_contents(eval(test_params['path']))
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('home', 'load'))
    def test_load_contents_home_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_home_page):
        with eval(test_params['error condition']):
            existing_page = eval(test_params['existing'])
            test_page = pn.HomePage(path=existing_page)
            test_page.load_contents(eval(test_params['path']))
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('readme', 'load'))
    def test_load_contents_readme_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_readme_page):
        with eval(test_params['error condition']):
            existing_page = eval(test_params['existing'])
            test_page = pn.ReadmePage(path=existing_page)
            test_page.load_contents(eval(test_params['path']))
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook readme', 'load'))
    def test_load_contents_logbook_readme_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_readme_page):
        with eval(test_params['error condition']):
            existing_page = eval(test_params['existing'])
            test_page = pn.ReadmePage(path=existing_page)
            test_page.load_contents(eval(test_params['path']))
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))


    # Getting information from page objects
    @pytest.mark.parametrize('test_params', build_all_tests('page', 'valid path'))
    def test_is_valid_path_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page):
        with eval(test_params['error condition']):
            test_page = eval(test_params['object'])
            result = test_page._is_valid_path(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'valid path'))
    def test_is_valid_path_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_page):
        with eval(test_params['error condition']):
            test_page = eval(test_params['object'])
            result = test_page._is_valid_path(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('contents', 'valid path'))
    def test_is_valid_path_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_contents_page):
        with eval(test_params['error condition']):
            test_page = eval(test_params['object'])
            result = test_page._is_valid_path(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook contents', 'valid path'))
    def test_is_valid_path_logbook_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_contents_page):
        with eval(test_params['error condition']):
            test_page = eval(test_params['object'])
            result = test_page._is_valid_path(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'valid path'))
    def test_is_valid_path_logbook_month_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_month_page):
        with eval(test_params['error condition']):
            test_page = eval(test_params['object'])
            result = test_page._is_valid_path(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('home', 'valid path'))
    def test_is_valid_path_home_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_home_page):
        with eval(test_params['error condition']):
            test_page = eval(test_params['object'])
            result = test_page._is_valid_path(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('readme', 'valid path'))
    def test_is_valid_path_readme_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_readme_page):
        with eval(test_params['error condition']):
            test_page = eval(test_params['object'])
            result = test_page._is_valid_path(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('page', 'get title from filename'))
    def test_get_title_from_filename_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._get_title_from_filename()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page',
                                             'get title from filename'))
    def test_get_title_from_filename_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookPage(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            result = test_page._get_title_from_filename()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('contents',
                                             'get title from filename'))
    def test_get_title_from_filename_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_contents_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ContentsPage(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_page._get_title_from_filename()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('home', 'get title from filename'))
    def test_get_title_from_filename_home_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_home_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.HomePage(path=eval(test_params['path']),
                                    filename=test_filename,
                                    title=test_title,
                                    parent=test_parent)
            result = test_page._get_title_from_filename()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('readme',
                                             'get title from filename'))
    def test_get_title_from_filename_readme_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_readme_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ReadmePage(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            result = test_page._get_title_from_filename()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('page', 'get summary'))
    def test_get_summary_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params, tmp_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page.get_summary()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'get summary'))
    def test_get_summary_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookPage(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            result = test_page.get_summary()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('contents', 'get summary'))
    def test_get_summary_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_contents_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ContentsPage(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_page.get_summary()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('home', 'get summary'))
    def test_get_summary_home_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_home_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.HomePage(path=eval(test_params['path']),
                                    filename=test_filename,
                                    title=test_title,
                                    parent=test_parent)
            result = test_page.get_summary()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('page', 'get outline'))
    def test_get_outline_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params, tmp_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page.get_outline()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'get outline'))
    def test_get_outline_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookPage(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            result = test_page.get_outline()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('contents', 'get outline'))
    def test_get_outline_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_contents_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ContentsPage(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_page.get_outline()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('home', 'get outline'))
    def test_get_outline_home_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_home_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.HomePage(path=eval(test_params['path']),
                                    filename=test_filename,
                                    title=test_title,
                                    parent=test_parent)
            result = test_page.get_outline()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'get previous'))
    def test_get_previous_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookPage(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            if (test_parent is not None
                    and test_page.filename == self.temp_logbook_page):
                this_date = self.temp_logbook_page
                earlier_date = str(int(this_date[:4]) - 1) + '-01-01'
                extra_page = pn.LogbookPage(filename=earlier_date,
                                            title=earlier_date,
                                            parent=test_parent)
            result = test_page.get_previous()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'get next'))
    def test_get_next_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookPage(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            if (test_parent is not None
                    and test_page.filename == self.temp_logbook_page):
                this_date = self.temp_logbook_page
                later_date = str(int(this_date[:4]) + 1) + '-01-01'
                extra_page = pn.LogbookPage(filename=later_date,
                                            title=later_date,
                                            parent=test_parent)
            result = test_page.get_next()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'get up'))
    def test_get_up_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookPage(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            if (test_parent is not None
                    and test_page.filename == self.temp_logbook_page):
                this_date = self.temp_logbook_page
                month_date = this_date[:7]
                extra_page = pn.LogbookMonth(filename=month_date,
                                             title=month_date,
                                             parent=test_parent)
            result = test_page.get_up()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'get month'))
    def test_get_month_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookPage(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            result = test_page.get_month()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'get previous'))
    def test_get_previous_logbook_month(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_month_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookMonth(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            if (test_parent is not None
                    and test_page.filename == self.temp_logbook_month):
                this_date = self.temp_logbook_month
                earlier_date = str(int(this_date[:4]) - 1) + '-01'
                extra_page = pn.LogbookMonth(filename=earlier_date,
                                             title=earlier_date,
                                             parent=test_parent)
            result = test_page.get_previous()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'get next'))
    def test_get_next_logbook_month(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_month_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookMonth(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            if (test_parent is not None
                    and test_page.filename == self.temp_logbook_month):
                this_date = self.temp_logbook_month
                later_date = str(int(this_date[:4]) + 1) + '-01'
                extra_page = pn.LogbookMonth(filename=later_date,
                                             title=later_date,
                                             parent=test_parent)
            result = test_page.get_next()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'get up'))
    def test_get_up_logbook_month(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_month_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookMonth(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_page.get_up()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'get month'))
    def test_get_month_logbook_month(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_month_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookMonth(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_page.get_month()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'get pages'))
    def test_get_pages_logbook_month(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_month_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookMonth(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            if (test_parent is not None
                    and test_page.filename == self.temp_logbook_month):
                this_month = self.temp_logbook_month
                other_month = str(int(this_month[0:4]) + 1) + '-01'
                dates = []
                for day in range(1, 31):
                    dates.append(this_month + '-' + str(day).zfill(2))
                    dates.append(other_month + '-' + str(day).zfill(2))
                this_month_pages = []
                for date in dates:
                    new_page = pn.LogbookPage(filename=date,
                                              title=date,
                                              parent=test_parent)
                    if date[0:7] == this_month:
                        this_month_pages.append(new_page)
                this_month_pages.sort()
            result = test_page.get_pages()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('page', 'get navigation'))
    def test_get_navigation_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params, tmp_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page.get_navigation()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'get navigation'))
    def test_get_navigation_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookPage(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            if (test_parent is not None
                    and test_page.filename == self.temp_logbook_page):
                this_date = self.temp_logbook_page
                month_date = self.temp_logbook_month
                early_date = str(int(this_date[:4]) - 1) + '-01-01'
                later_date = str(int(this_date[:4]) + 1) + '-01-01'
                month_page = pn.LogbookMonth(filename=month_date,
                                             title=self.test_logbook_month_title,
                                             parent=test_parent)
                early_page = pn.LogbookPage(filename=early_date,
                                            title=early_date,
                                            parent=test_parent)
                later_page = pn.LogbookPage(filename=later_date,
                                            title=later_date,
                                            parent=test_parent)
            result = test_page.get_navigation()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('contents', 'get navigation'))
    def test_get_navigation_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_contents_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ContentsPage(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_page.get_navigation()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook contents', 'get navigation'))
    def test_get_navigation_logbook_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_contents_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ContentsPage(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_page.get_navigation()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'get navigation'))
    def test_get_navigation_logbook_month_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_month_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookMonth(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            if test_parent is not None:
                home_page = pn.HomePage(parent=test_parent)
                if test_page.filename == self.temp_logbook_month:
                    this_date = self.temp_logbook_month
                    early_date = str(int(this_date[:4]) - 1) + '-01'
                    later_date = str(int(this_date[:4]) + 1) + '-01'
                    early_page = pn.LogbookMonth(filename=early_date,
                                                title=early_date,
                                                parent=test_parent)
                    later_page = pn.LogbookMonth(filename=later_date,
                                                title=later_date,
                                                parent=test_parent)
            result = test_page.get_navigation()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('home', 'get navigation'))
    def test_get_navigation_home_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_home_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.HomePage(path=eval(test_params['path']),
                                    filename=test_filename,
                                    title=test_title,
                                    parent=test_parent)
            result = test_page.get_navigation()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('readme', 'get navigation'))
    def test_get_navigation_readme_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_readme_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ReadmePage(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            result = test_page.get_navigation()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook readme', 'get navigation'))
    def test_get_navigation_logbook_readme_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_readme_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ReadmePage(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            result = test_page.get_navigation()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))


    # Handling page contents
    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'valid line blank'))
    def test_is_blank_line(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._is_blank_line(eval(test_params['object']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'valid line navigation'))
    def test_is_navigation_line(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._is_navigation_line(eval(test_params['object']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'valid line title'))
    def test_is_title_line(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._is_title_line(eval(test_params['object']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'valid line subtitle'))
    def test_is_subtitle_line(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._is_subtitle_line(eval(test_params['object']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'valid line bullet'))
    def test_is_bullet_line(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._is_bullet_line(eval(test_params['object']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'valid line link'))
    def test_is_link_line(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._is_link_line(eval(test_params['object']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'valid line text'))
    def test_is_text_line(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._is_text_line(eval(test_params['object']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'find blank'))
    def test_find_first_blank_line(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._find_first_blank_line(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'find text'))
    def test_find_first_text_line(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._find_first_text_line(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'find first_title'))
    def test_find_first_title_line(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._find_first_title_line(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'find subtitle'))
    def test_find_first_subtitle(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._find_first_subtitle(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'strip line reference'))
    def test_strip_reference_links(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._strip_reference_links(eval(test_params['object']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'strip line absolute'))
    def test_strip_absolute_links(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._strip_absolute_links(eval(test_params['object']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'strip line all'))
    def test_strip_links_all(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._strip_links(eval(test_params['object']), 'all')
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'strip line reference'))
    def test_strip_links_reference(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._strip_links(eval(test_params['object']), 'reference')
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'strip line absolute'))
    def test_strip_links_absolute(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._strip_links(eval(test_params['object']), 'absolute')
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'strip line default'))
    def test_strip_links_default(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._strip_links(eval(test_params['object']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('page', 'find title'))
    def test_get_title_from_contents_page(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_title(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'find title'))
    def test_get_title_from_contents_logbook_page(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookPage(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_title(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'find title'))
    def test_get_title_from_contents_logbook_month(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookMonth(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_title(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('contents', 'find title'))
    def test_get_title_from_contents_contents_page(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ContentsPage(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_title(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('readme', 'find title'))
    def test_get_title_from_contents_readme(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ReadmePage(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_title(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('page', 'find summary'))
    def test_get_summary_from_contents_page(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_summary(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'find summary'))
    def test_get_summary_from_contents_logbook_page(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookPage(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_summary(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'find summary'))
    def test_get_summary_from_contents_logbook_month(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookMonth(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_summary(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('contents', 'find summary'))
    def test_get_summary_from_contents_contents_page(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ContentsPage(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_summary(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('readme', 'find summary'))
    def test_get_summary_from_contents_readme(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ReadmePage(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_summary(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('page', 'find sections'))
    def test_get_sections_from_contents_page(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_sections(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'find sections'))
    def test_get_sections_from_contents_logbook_page(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookPage(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_sections(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'find sections'))
    def test_get_sections_from_contents_logbook_month(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookMonth(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_sections(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('contents', 'find sections'))
    def test_get_sections_from_contents_contents_page(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ContentsPage(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_sections(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('readme', 'find sections'))
    def test_get_sections_from_contents_readme(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ReadmePage(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page._get_sections(test_params['object'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('page', 'find outline'))
    def test_get_outline_from_contents_page(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page.get_outline()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'find outline'))
    def test_get_outline_from_contents_logbook_page(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookPage(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page.get_outline()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'find outline'))
    def test_get_outline_from_contents_logbook_month(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookMonth(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page.get_outline()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('contents', 'find outline'))
    def test_get_outline_from_contents_contents_page(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ContentsPage(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page.get_outline()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('readme', 'find outline'))
    def test_get_outline_from_contents_readme(self, capsys, test_params):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ReadmePage(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            test_page.contents = test_params['object']
            result = test_page.get_outline()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('page', 'match content with page'))
    def test_contents_match(self, capsys, test_params, tmp_page, cloned_repo):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            result = test_page._contents_match(eval(test_params['object']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('page', 'match content with page'))
    def test_contents_match_modified(self, capsys, test_params,
                                     tmp_page, cloned_repo):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            test_page.contents = [self.test_message]
            result = test_page._contents_match(eval(test_params['object']))
            if eval(test_params['expected']) is True:
                expected = False
            else:
                expected = eval(test_params['expected'])
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   expected)

    @pytest.mark.parametrize('test_params', build_all_tests('page', 'has summary'))
    def test_has_summary_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.Page(path=eval(test_params['path']),
                                filename=test_filename,
                                title=test_title,
                                parent=test_parent)
            if test_params['object'] is not None:
                test_page.contents = test_params['object']
            result = test_page._has_summary()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'has summary'))
    def test_has_summary_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookPage(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            if test_params['object'] is not None:
                test_page.contents = test_params['object']
            result = test_page._has_summary()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'has summary'))
    def test_has_summary_logbook_month(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_month_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookMonth(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            if test_params['object'] is not None:
                test_page.contents = test_params['object']
            result = test_page._has_summary()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('home', 'has summary'))
    def test_has_summary_home_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_home_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.HomePage(path=eval(test_params['path']),
                                    filename=test_filename,
                                    title=test_title,
                                    parent=test_parent)
            if test_params['object'] is not None:
                test_page.contents = test_params['object']
            result = test_page._has_summary()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('contents', 'has summary'))
    def test_has_summary_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_contents_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ContentsPage(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            if test_params['object'] is not None:
                test_page.contents = test_params['object']
            result = test_page._has_summary()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('readme', 'has summary'))
    def test_has_summary_readme(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_readme_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ReadmePage(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            if test_params['object'] is not None:
                test_page.contents = test_params['object']
            result = test_page._has_summary()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook readme', 'has summary'))
    def test_has_summary_logbook_readme(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_readme_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.ReadmePage(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            if test_params['object'] is not None:
                test_page.contents = test_params['object']
            result = test_page._has_summary()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))


    # Creating notebook objects
    @pytest.mark.parametrize('test_params', build_all_tests('notebook'))
    def test_create_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_notebook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Notebook(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            self.assert_parametric(test_notebook,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('logbook'))
    def test_create_logbook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_logbook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_logbook = pn.Logbook(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            self.assert_parametric(test_logbook,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('nested'))
    def test_create_notebook_nested(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_nested):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Notebook(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            self.assert_parametric(test_notebook,
                                   test_params['test_type'],
                                   eval(test_params['expected']))


    # Loading data to notebook objects
    @pytest.mark.parametrize('test_params', build_all_tests('page', 'add'))
    def test_add_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params, tmp_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Notebook()
            test_parent.add_page(eval(test_params['path']))
            test_page = test_parent.contents[-1]
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'add'))
    def test_add_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Logbook()
            test_parent.add_page(eval(test_params['path']))
            test_page = test_parent.contents[-1]
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('contents', 'add'))
    def test_add_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_contents_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Notebook()
            test_parent.add_contents_page(eval(test_params['path']))
            test_page = test_parent.contents[-1]
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook contents', 'add'))
    def test_add_logbook_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_contents_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Logbook()
            test_parent.add_contents_page(eval(test_params['path']))
            test_page = test_parent.contents[-1]
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'add'))
    def test_add_logbook_month_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_month_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Logbook()
            test_parent.add_page(eval(test_params['path']))
            test_page = test_parent.contents[-1]
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('home', 'add'))
    def test_add_home_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_home_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Notebook()
            test_parent.add_home_page(eval(test_params['path']))
            test_page = test_parent.contents[-1]
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('readme', 'add'))
    def test_add_readme_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_readme_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Notebook()
            test_parent.add_readme_page(eval(test_params['path']))
            test_page = test_parent.contents[-1]
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook readme', 'add'))
    def test_add_logbook_readme_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_readme_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Logbook()
            test_parent.add_readme_page(eval(test_params['path']))
            test_page = test_parent.contents[-1]
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('notebook', 'add'))
    def test_add_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_notebook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Notebook()
            test_parent.add_notebook(eval(test_params['path']))
            test_page = test_parent.contents[-1]
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('logbook', 'add'))
    def test_add_logbook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_logbook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Notebook()
            test_parent.add_logbook(eval(test_params['path']))
            test_page = test_parent.contents[-1]
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('page', 'multiple'))
    def test_add_multiple_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params, tmp_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Notebook()
            test_parent.add_page(eval(test_params['path']))
            result = test_parent.add_page(eval(test_params['path']))
            if len(test_parent.contents) > 0:
                test_page = test_parent.contents[-1]
            else:
                test_page = None
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook page', 'multiple'))
    def test_add_multiple_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Logbook()
            test_parent.add_page(eval(test_params['path']))
            result = test_parent.add_page(eval(test_params['path']))
            if len(test_parent.contents) > 0:
                test_page = test_parent.contents[-1]
            else:
                test_page = None
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('contents', 'multiple'))
    def test_add_multiple_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_contents_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Notebook()
            test_parent.add_contents_page(eval(test_params['path']))
            result = test_parent.add_contents_page(eval(test_params['path']))
            if len(test_parent.contents) > 0:
                test_page = test_parent.contents[-1]
            else:
                test_page = None
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook contents', 'multiple'))
    def test_add_multiple_logbook_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_contents_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Logbook()
            test_parent.add_contents_page(eval(test_params['path']))
            result = test_parent.add_contents_page(eval(test_params['path']))
            if len(test_parent.contents) > 0:
                test_page = test_parent.contents[-1]
            else:
                test_page = None
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'multiple'))
    def test_add_multiple_logbook_month_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_month_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Logbook()
            test_parent.add_page(eval(test_params['path']))
            result = test_parent.add_page(eval(test_params['path']))
            if len(test_parent.contents) > 0:
                test_page = test_parent.contents[-1]
            else:
                test_page = None
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('home', 'multiple'))
    def test_add_multiple_home_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_home_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Notebook()
            test_parent.add_home_page(eval(test_params['path']))
            result = test_parent.add_home_page(eval(test_params['path']))
            if len(test_parent.contents) > 0:
                test_page = test_parent.contents[-1]
            else:
                test_page = None
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('readme', 'multiple'))
    def test_add_multiple_readme_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_readme_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Notebook()
            test_parent.add_readme_page(eval(test_params['path']))
            result = test_parent.add_readme_page(eval(test_params['path']))
            if len(test_parent.contents) > 0:
                test_page = test_parent.contents[-1]
            else:
                test_page = None
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook readme', 'multiple'))
    def test_add_multiple_logbook_readme_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_readme_page):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent']) or pn.Logbook()
            test_parent.add_readme_page(eval(test_params['path']))
            result = test_parent.add_readme_page(eval(test_params['path']))
            if len(test_parent.contents) > 0:
                test_page = test_parent.contents[-1]
            else:
                test_page = None
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('notebook', 'load'))
    def test_load_contents_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_notebook, tmp_path):
        with eval(test_params['error condition']):
            existing_notebook = eval(test_params['existing'])
            test_notebook = pn.Notebook(path=existing_notebook)
            test_notebook.load_contents(eval(test_params['path']))
            self.assert_parametric(test_notebook,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params', build_all_tests('logbook', 'load'))
    def test_load_contents_logbook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_logbook, tmp_path):
        with eval(test_params['error condition']):
            existing_logbook = eval(test_params['existing'])
            test_logbook = pn.Logbook(path=existing_logbook)
            test_logbook.load_contents(eval(test_params['path']))
            self.assert_parametric(test_logbook,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('nested', 'load'))
    def test_load_contents_nested_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_nested, tmp_path):
        with eval(test_params['error condition']):
            existing_notebook = eval(test_params['existing'])
            test_notebook = pn.Notebook(path=existing_notebook)
            test_notebook.load_contents(eval(test_params['path']))
            self.assert_parametric(test_notebook,
                                   test_params['test_type'],
                                   eval(test_params['expected']))


    # Getting information from notebook objects
    @pytest.mark.parametrize('test_params',
                             build_all_tests('notebook', 'valid path'))
    def test_is_valid_path_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_notebook):
        with eval(test_params['error condition']):
            test_notebook = eval(test_params['object'])
            result = test_notebook._is_valid_path(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook', 'valid path'))
    def test_is_valid_path_logbook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_logbook):
        with eval(test_params['error condition']):
            test_notebook = eval(test_params['object'])
            result = test_notebook._is_valid_path(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('nested', 'valid path'))
    def test_is_valid_path_nested_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_nested):
        with eval(test_params['error condition']):
            test_notebook = eval(test_params['object'])
            result = test_notebook._is_valid_path(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('notebook', 'get pages'))
    def test_get_pages_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_notebook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Notebook(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_notebook.get_pages()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook', 'get pages'))
    def test_get_pages_logbook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_logbook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_logbook = pn.Logbook(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            result = test_logbook.get_pages()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('nested', 'get pages'))
    def test_get_pages_nested_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_nested):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Notebook(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_notebook.get_pages()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('notebook', 'get notebooks'))
    def test_get_notebooks_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_notebook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Notebook(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_notebook.get_notebooks()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook', 'get notebooks'))
    def test_get_notebooks_logbook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_logbook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_logbook = pn.Logbook(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            result = test_logbook.get_notebooks()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('nested', 'get notebooks'))
    def test_get_notebooks_nested_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_nested):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Notebook(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_notebook.get_notebooks()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('notebook', 'get logbooks'))
    def test_get_logbooks_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_notebook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Notebook(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_notebook.get_logbooks()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook', 'get logbooks'))
    def test_get_logbooks_logbook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_logbook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_logbook = pn.Logbook(path=eval(test_params['path']),
                                      filename=test_filename,
                                      title=test_title,
                                      parent=test_parent)
            result = test_logbook.get_logbooks()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('nested', 'get logbooks'))
    def test_get_logbooks_nested_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_nested):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Notebook(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_notebook.get_logbooks()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('notebook', 'get summary'))
    def test_get_summary_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_notebook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Notebook(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_notebook.get_summary()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook', 'get summary'))
    def test_get_summary_logbook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_logbook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Logbook(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            result = test_notebook.get_summary()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('nested', 'get summary'))
    def test_get_summary_nested_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_nested):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Notebook(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_notebook.get_summary()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('notebook', 'get outline'))
    def test_get_outline_notebook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_notebook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Notebook(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_notebook.get_outline()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook', 'get outline'))
    def test_get_outline_logbook(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_logbook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Logbook(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            result = test_notebook.get_outline()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('nested', 'get outline'))
    def test_get_outline_nested(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_nested):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Notebook(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_notebook.get_outline()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('notebook', 'get navigation'))
    def test_get_navigation_notebook(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_notebook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Notebook(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_notebook.get_navigation()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook', 'get navigation'))
    def test_get_navigation_logbook(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Logbook(path=eval(test_params['path']),
                                       filename=test_filename,
                                       title=test_title,
                                       parent=test_parent)
            result = test_notebook.get_navigation()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('nested', 'get navigation'))
    def test_get_navigation_nested(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_nested):
        with eval(test_params['error condition']):
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_notebook = pn.Notebook(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            result = test_notebook.get_navigation()
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))


    # Utility functions
    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'valid path page'))
    def test_is_valid_page_file(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page, tmp_logbook_page, tmp_contents_page, tmp_home_page,
            tmp_readme_page, tmp_logbook_month_page, tmp_notebook, tmp_logbook):
        with eval(test_params['error condition']):
            result = pn._is_valid_page_file(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
        build_all_tests('function', 'valid path logbook page'))
    def test_is_valid_logbook_page_file(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page, tmp_logbook_page, tmp_contents_page, tmp_home_page,
            tmp_readme_page, tmp_logbook_month_page, tmp_notebook, tmp_logbook):
        with eval(test_params['error condition']):
            result = pn._is_valid_logbook_page_file(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
        build_all_tests('function', 'valid path logbook month'))
    def test_is_valid_logbook_month_file(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page, tmp_logbook_page, tmp_contents_page, tmp_home_page,
            tmp_readme_page, tmp_logbook_month_page, tmp_notebook, tmp_logbook):
        with eval(test_params['error condition']):
            result = pn._is_valid_logbook_month_file(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
        build_all_tests('function', 'valid path contents'))
    def test_is_valid_contents_page_file(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page, tmp_logbook_page, tmp_contents_page, tmp_home_page,
            tmp_readme_page, tmp_logbook_month_page, tmp_notebook, tmp_logbook):
        with eval(test_params['error condition']):
            result = pn._is_valid_contents_page_file(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
        build_all_tests('function', 'valid path home'))
    def test_is_valid_home_page_file(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page, tmp_logbook_page, tmp_contents_page, tmp_home_page,
            tmp_readme_page, tmp_logbook_month_page, tmp_notebook, tmp_logbook):
        with eval(test_params['error condition']):
            result = pn._is_valid_home_page_file(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
        build_all_tests('function', 'valid path readme'))
    def test_is_valid_readme_page_file(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page, tmp_logbook_page, tmp_contents_page, tmp_home_page,
            tmp_readme_page, tmp_logbook_month_page, tmp_notebook, tmp_logbook):
        with eval(test_params['error condition']):
            result = pn._is_valid_readme_page_file(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
        build_all_tests('function', 'valid path notebook'))
    def test_is_valid_notebook_folder(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_page, tmp_logbook_page, tmp_contents_page, tmp_home_page,
            tmp_readme_page, tmp_logbook_month_page, tmp_notebook, tmp_logbook):
        with eval(test_params['error condition']):
            result = pn._is_valid_notebook_folder(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
        build_all_tests('function', 'valid path logbook'))
    def test_is_valid_logbook_folder(
            self, capsys, tmp_folder_factory, cloned_repo, test_params,
            tmp_page, tmp_logbook_page, tmp_contents_page, tmp_home_page,
            tmp_readme_page, tmp_logbook_month_page, tmp_notebook, tmp_logbook):
        with eval(test_params['error condition']):
            result = pn._is_valid_logbook_folder(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
        build_all_tests('function', 'read path page'))
    def test_load_file_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page, tmp_logbook_page, tmp_contents_page, tmp_home_page,
            tmp_readme_page, tmp_logbook_month_page, tmp_notebook, tmp_logbook):
        with eval(test_params['error condition']):
            result = pn._load_file(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
        build_all_tests('function', 'read path logbook page'))
    def test_load_file_logbook_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page, tmp_logbook_page, tmp_contents_page, tmp_home_page,
            tmp_readme_page, tmp_logbook_month_page, tmp_notebook, tmp_logbook):
        with eval(test_params['error condition']):
            result = pn._load_file(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
        build_all_tests('function', 'read path home'))
    def test_load_file_home_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page, tmp_logbook_page, tmp_contents_page, tmp_home_page,
            tmp_readme_page, tmp_logbook_month_page, tmp_notebook, tmp_logbook):
        with eval(test_params['error condition']):
            result = pn._load_file(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
        build_all_tests('function', 'read path contents'))
    def test_load_file_contents_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page, tmp_logbook_page, tmp_contents_page, tmp_home_page,
            tmp_readme_page, tmp_logbook_month_page, tmp_notebook, tmp_logbook):
        with eval(test_params['error condition']):
            result = pn._load_file(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
        build_all_tests('function', 'read path readme'))
    def test_load_file_readme_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page, tmp_logbook_page, tmp_contents_page, tmp_home_page,
            tmp_readme_page, tmp_logbook_month_page, tmp_notebook, tmp_logbook):
        with eval(test_params['error condition']):
            result = pn._load_file(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
        build_all_tests('function', 'read path logbook month'))
    def test_load_file_logbook_month_page(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_page, tmp_logbook_page, tmp_contents_page, tmp_home_page,
            tmp_readme_page, tmp_logbook_month_page, tmp_notebook, tmp_logbook):
        with eval(test_params['error condition']):
            result = pn._load_file(eval(test_params['path']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'make line title'))
    def test_make_title(self, capsys, test_params):
        with eval(test_params['error condition']):
            result = pn._title(eval(test_params['object']))
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))

    @pytest.mark.parametrize('test_params',
                             build_all_tests('function', 'make line title'))
    @pytest.mark.parametrize('level', [1, 2, 3])
    def test_make_title_multilevel(self, capsys, test_params, level):
        with eval(test_params['error condition']):
            result = pn._title(eval(test_params['object']), title_level=level)
            # Add a title level on each iteration after the first
            if (test_params['test_type'] == 'result'
                    and test_params['expected'] is not None
                    and level > 1):
                test_params['expected'] = "'#' + " + test_params['expected']
            self.assert_parametric(result,
                                   test_params['test_type'],
                                   eval(test_params['expected']))


    # Building summaries
    @pytest.mark.parametrize('test_params',
                             build_all_tests('logbook month', 'rebuild'))
    def test_rebuild_logbook_month(
            self, capsys, tmp_file_factory, cloned_repo, test_params,
            tmp_logbook_month_page, tmp_logbook):
        with eval(test_params['error condition']):
            # Create page
            test_parent = eval(test_params['parent'])
            test_title = eval(test_params['title'])
            test_filename = eval(test_params['filename'])
            test_page = pn.LogbookMonth(path=eval(test_params['path']),
                                        filename=test_filename,
                                        title=test_title,
                                        parent=test_parent)
            # Clear initial contents
            test_page.contents = []
            # Create other pages to generate summary
            if (test_parent is not None
                    and test_page.filename == self.temp_logbook_month):
                for page in self.temp_logbook_pages:
                    this_path = tmp_logbook.joinpath(page)
                    date = page.replace('.md', '')
                    pn.LogbookPage(path=this_path,
                                   filename=date,
                                   title=date,
                                   parent=test_parent)
                pn.LogbookMonth(filename=self.extra_logbook_month,
                                parent=test_parent)
                pn.ContentsPage(parent=test_parent)
            # Rebuild summary from pages
            test_page.rebuild()
            # Test result
            self.assert_parametric(test_page,
                                   test_params['test_type'],
                                   eval(test_params['expected']))
