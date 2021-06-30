#!/usr/bin/env python3

"""
A script for setting offsets to subtitle files

An offset is passed in as a positional argument and is expressed in seconds
- negative: hasten (-0.500)
- positive: delay (+0.800 or 0.800)

On default, a .srt file located in the current directory is taken in
A condition for that to happen is that exactly 1 .srt file exists in it

To specify the exact file, a path keyword argument can be used:
--path: passes an absolute or relative path to the file

Upon running, the old subtitle file "foo" will be renamed to "foo-old" and the newly output file
with the offsets in place will now be named "foo". The old file is not automatically deleted
"""

import sys
import os
import glob
from argparse import ArgumentParser, Namespace
from datetime import timedelta as td
from typing import List


def main() -> None:
    """
    Core delegation of tasks to other functions and their stockpile
    """
    args: Namespace = parse_args()
    subfile: str = get_file(args)
    change_timelines(args, subfile)
    print('Complete!')


def parse_args() -> Namespace:
    """
    Parses one positional and one optional argument:
    offset: positional, sets the amount in seconds to either hasten (neg) or delay (pos) the subs
    --path: optional, finds the file through its absolute or relative path

    :return: an object holding the parsed args
    """
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument('offset', help='amount of seconds to shift (+-0.000)', type=float, metavar='offset')
    parser.add_argument('-p', '--path', help='absolute or relative path to the file', metavar='')
    args: Namespace = parser.parse_args()

    return args


def get_file(args: Namespace) -> str:
    """
    Fetches the file through a specified method
    If no method is specified, defaults to the .srt in the current directory
    Should multiple .srt files exist in the current directory, --path must be given

    :param args: an object holding the parsed args
    :return: path to the sub file
    """
    if args.path:
        return args.path if args.path.endswith('.srt') else f'{args.path}.srt'

    srts: List[str] = glob.glob('*.srt')

    if len(srts) != 1:
        sys.exit(
            f'More than 1 .srt file found: {len(srts)}\n'
            f'Consider using the --path flag to specify precisely one'
        )

    return srts[0]


def change_timelines(args: Namespace, subfile: str) -> None:
    """
    Fetches the timelines from the original sub file, parses them, renames the old file and
    drops the new timelines with the offset applied to a new sub file with the old one's name

    :param args: an object holding the parsed args
    :param subfile: path to the sub file
    """
    with open(subfile, 'r', encoding='ISO-8859-1') as rf:
        raw: str = rf.read()

    blocks: List[str] = raw.split('\n\n')
    timelines: List[str] = [line.splitlines()[1] for line in blocks if len(line.splitlines()) >= 3]

    raw_inits: List[str] = [timeline.split()[0] for timeline in timelines]
    raw_ends: List[str] = [timeline.split()[2] for timeline in timelines]

    inits: List[td] = [td(
        hours=float(r.split(':')[0]),
        minutes=float(r.split(':')[1]),
        seconds=float(r.split(':')[2].split(',')[0]),
        milliseconds=float(r.split(':')[2].split(',')[1])
    ) for r in raw_inits]

    ends: List[td] = [td(
        hours=float(r.split(':')[0]),
        minutes=float(r.split(':')[1]),
        seconds=float(r.split(':')[2].split(',')[0]),
        milliseconds=float(r.split(':')[2].split(',')[1])
    ) for r in raw_ends]

    offset: td = td(seconds=args.offset)

    for idx, (init_time, end_time) in enumerate(zip(inits, ends)):
        if (init_time + offset).total_seconds() < 0:
            continue

        inits[idx]: td = init_time + offset
        ends[idx]: td = end_time + offset

    re_inits: List[str] = [
        str(f)[:-3].zfill(12).replace('.', ',') if f.microseconds else f'{str(f).zfill(8)},000' for f in inits
    ]

    re_ends: List[str] = [
        str(f)[:-3].zfill(12).replace('.', ',') if f.microseconds else f'{str(f).zfill(8)},000' for f in ends
    ]

    formatted: str = raw

    for raw_i, re_i in zip(raw_inits, re_inits):
        formatted: str = formatted.replace(raw_i, re_i)

    for raw_e, re_e in zip(raw_ends, re_ends):
        formatted: str = formatted.replace(raw_e, re_e)

    os.rename(subfile, subfile.replace('.srt', '-old.srt'))

    with open(subfile, 'w') as wf:
        wf.write(formatted)


if __name__ == '__main__':
    main()
