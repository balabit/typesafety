#!/usr/bin/python3
#
# Copyright (c) 2013-2018 Balabit
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import collections
import argparse
import os.path
import datetime
import re
import sys


def load_pattern_file(fn):
    res = []
    with open(fn) as f:
        for line in f:
            line = line.split('#', 1)[0].strip()

            if not line:
                continue

            res.append(re.compile(line))

    return res


def match_patterns(text, patterns):
    return any(pattern.search(text) is not None for pattern in patterns)


THIS_YEAR = datetime.datetime.now().year
BASE_PATH = os.path.dirname(__file__)
EXCLUDE_DIRS = load_pattern_file(os.path.join(BASE_PATH, 'copyright_dirs.exclude'))
EXCLUDE_FILES = load_pattern_file(os.path.join(BASE_PATH, 'copyright_files.exclude'))
with open(os.path.join(BASE_PATH, 'copyright.txt')) as f:
    COPYRIGHT_TEXT = f.read()
FILTER_EXTENSION = {'.py', '.sh'}
BEGIN_PATTERN = re.compile(r"^Copyright \(c\) 2013-(20[0-9]{2}) Balabit$")

UPDATE_COPYRIGHT_HEADER = '''
Copyright (c) 2013-{year} Balabit
{copyright}\
'''.format(year=THIS_YEAR, copyright=COPYRIGHT_TEXT)


class CommentError(Exception):
    def __init__(self, filename, message):
        super().__init__(message)

        self.filename = filename
        self.message = message


def locate_files(base_path):
    for name in os.listdir(base_path):
        fullpath = os.path.join(base_path, name)

        if os.path.isfile(fullpath):
            ext = os.path.splitext(name)[1]
            if ext not in FILTER_EXTENSION:
                continue

            if match_patterns(fullpath, EXCLUDE_FILES):
                continue

            if os.lstat(fullpath).st_size == 0:
                continue

            yield fullpath

        elif os.path.isdir(fullpath):
            if match_patterns(fullpath, EXCLUDE_DIRS):
                continue

            for res in locate_files(fullpath):
                yield res


HeaderComment = collections.namedtuple('HeaderComment', ['begin_line', 'end_line', 'body', 'has_hashbang'])


def get_header_comment(filename):
    begin_line = None
    end_line = 0
    has_hashbang = False
    comment = []

    with open(filename) as f:
        for index, line in enumerate(f):
            line = line.strip()

            if not line or line[0] != '#':
                end_line = index
                break

            if line[:2].startswith('#!'):
                has_hashbang = True
                continue

            if begin_line is None:
                begin_line = index

            if line == '#':
                comment.append('')
                continue

            if line[:2] != '# ':
                raise CommentError(filename, "Invalid comment line format")

            comment.append(line[2:])

    if begin_line is None:
        begin_line = end_line

    return HeaderComment(
        begin_line=begin_line,
        end_line=end_line,
        body=comment,
        has_hashbang=has_hashbang
    )


def check_file_header(filename):
    comment = get_header_comment(filename)

    if not comment.body:
        raise CommentError(filename, 'Missing copyright header')

    if comment.body[0] != '' or comment.body[-1] != '':
        raise CommentError(filename, 'Copyright header format invalid')

    match = BEGIN_PATTERN.match(comment.body[1])
    if match is None:
        raise CommentError(filename, 'Copyright header format invalid')

    if int(match.group(1)) != THIS_YEAR:
        raise CommentError(filename, 'Copyright year in headers invalid')

    if '\n'.join(comment.body[2:]) != COPYRIGHT_TEXT:
        raise CommentError(filename, 'Copyright text not the expected one')


def update_file_header(filename):
    try:
        check_file_header(filename)
        return

    except CommentError:
        pass

    with open(filename) as f:
        data = f.read().split('\n')

    header = get_header_comment(filename)
    new_header_block = ['# {}'.format(line).rstrip() for line in UPDATE_COPYRIGHT_HEADER.split('\n')]
    if not header.body:
        # New comment line, add a newline after the block
        new_header_block.append('')

    data[header.begin_line:header.end_line] = new_header_block

    with open(filename, 'w') as f:
        f.write('\n'.join(data))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copyright header manager script')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--update', action='store_true',
                       help='Update existing headers and add missing ones.')
    group.add_argument('--check', action='store_true',
                       help='Check existence and correctness of the header copyright information.')
    parser.add_argument('path', help='Path to check the files in.')

    options = parser.parse_args()

    rc = 0
    if options.check:
        header_printed = False
        for filename in locate_files(options.path):
            try:
                check_file_header(filename)

            except CommentError as exc:
                if not header_printed:
                    header_printed = True
                    print('Errors:', file=sys.stderr)

                print('  {}: {}'.format(exc.filename, exc.message), file=sys.stderr)
                rc = 1

        if rc != 0:
            print(file=sys.stderr)
            print('You should run the following command:', file=sys.stderr)
            print(file=sys.stderr)
            print('  $ {} --update {}'.format(sys.argv[0], options.path), file=sys.stderr)
            print(file=sys.stderr)

    elif options.update:
        for filename in locate_files(options.path):
            update_file_header(filename)

    else:
        assert False, "Not reachable code"

    exit(rc)
