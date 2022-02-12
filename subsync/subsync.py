#!/usr/bin/env python3

"""A script for setting offsets to subtitle files.

An offset is passed in as a positional argument and is expressed in seconds:
- negative: hasten (-0.500)
- positive: delay (+0.800 or 0.800)

On default, a .srt file located in the current directory is taken in.
A condition for that to happen is that exactly 1 .srt file exists in it.

To specify the exact file, a path keyword argument can be used:
--path: passes an absolute or relative path to the file.

Upon running, the old subtitle file "foo" will be renamed to "foo-old" and the newly output file
with the offsets in place will now be named "foo". The old file is not automatically deleted.
"""

import glob
import os
import sys
from argparse import ArgumentParser, Namespace
from datetime import timedelta as td
from typing import List, Tuple, Set


def main() -> None:
    """Core delegation of tasks to other functions and their stockpile."""

    args: Namespace = parse_args()
    subfile: str = get_file(args)
    change_timelines(args, subfile)
    print('Complete!')


def parse_args() -> Namespace:
    """Parses positional and optional arguments.

    :return: an object holding the parsed args
    """
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument('offset', help='amount of seconds to shift (+-0.000)', type=float)
    parser.add_argument('-p', '--path', help='absolute or relative path to the file')
    args: Namespace = parser.parse_args()

    return args


def get_file(args: Namespace) -> str:
    """Fetches the file through a specified method.

    If no method is specified, defaults to the .srt in the current directory.
    Should multiple .srt files exist in the current directory, --path must be given.

    :param args: an object holding the parsed args
    :return: path to the sub file
    """
    if args.path:
        return args.path if args.path.endswith('.srt') else f'{args.path}.srt'

    srts: Set[str] = set(glob.glob('*.srt')) - set(glob.glob('*old-[0-9].srt'))

    if len(srts) == 0:
        sys.exit(
            f'No .srt file found\n'
            f'Position yourself inside a directory with the file or specify it via the --path flag'
        )

    elif len(srts) != 1:
        sys.exit(
            f'More than 1 .srt file found: {len(srts)}\n'
            f'Consider using the --path flag to specify precisely one'
        )

    return srts.pop()


def change_timelines(args: Namespace, subfile: str) -> None:
    """Alters the timelines while keeping the original file.

    Fetches the timelines from the original sub file, parses them, renames the old file and
    drops the new timelines with the offset applied to a new sub file with the old one's name.

    :param args: an object holding the parsed args
    :param subfile: path to the sub file
    """
    with open(subfile, 'r', encoding='ISO-8859-1') as rf:
        original_subfile: str = rf.read()

    blocks: List[str] = original_subfile.split('\n\n')
    timelines: List[str] = [line.splitlines()[1] for line in blocks if len(line.splitlines()) >= 3]

    raw_inits_and_ends: List[Tuple[str, str]] = [
        (timeline.split()[0], timeline.split()[2]) for timeline in timelines
    ]

    parsed_inits_and_ends: List[Tuple[td, td]] = [
        (
            td(
                hours=float(raw_init.split(':')[0]),
                minutes=float(raw_init.split(':')[1]),
                seconds=float(raw_init.split(':')[2].split(',')[0]),
                milliseconds=float(raw_init.split(':')[2].split(',')[1])
            ),
            td(
                hours=float(raw_end.split(':')[0]),
                minutes=float(raw_end.split(':')[1]),
                seconds=float(raw_end.split(':')[2].split(',')[0]),
                milliseconds=float(raw_end.split(':')[2].split(',')[1])
            )
        ) for raw_init, raw_end in raw_inits_and_ends
    ]

    altered_inits_and_ends: List[Tuple[td, td]] = list()
    offset: td = td(seconds=args.offset)

    for init, end in parsed_inits_and_ends:
        if (init + offset).total_seconds() < 0:
            continue

        altered_inits_and_ends.append((init + offset, end + offset))

    formatted_altered_inits_and_ends: List[Tuple[str, str]] = [
        (
            str(init)[:-3].zfill(12).replace('.', ',') if init.microseconds else f'{str(init).zfill(8)},000',
            str(end)[:-3].zfill(12).replace('.', ',') if end.microseconds else f'{str(end).zfill(8)},000'
        ) for init, end in altered_inits_and_ends
    ]

    altered_subfile: str = original_subfile

    for (raw_init, raw_end), (altered_init, altered_end) in zip(raw_inits_and_ends, formatted_altered_inits_and_ends):
        altered_subfile: str = altered_subfile.replace(raw_init, altered_init).replace(raw_end, altered_end)

    old_subfile: str = subfile.replace('.srt', '-old-0.srt')
    increment: int = 1

    while True:
        if os.path.isfile(old_subfile):
            old_subfile: str = old_subfile.replace(f'-old-{increment - 1}.srt', f'-old-{increment}.srt')
            increment += 1
            continue

        os.rename(subfile, old_subfile)
        break

    with open(subfile, 'w', encoding='ISO-8859-1') as wf:
        wf.write(altered_subfile)


if __name__ == '__main__':
    main()
