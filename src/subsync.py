#!/usr/bin/env python3

import glob
import os
import sys
from argparse import ArgumentParser, Namespace
from datetime import timedelta as td


def main() -> None:
    args: Namespace = parse_args()
    subsfile: str = get_file(args)
    change_timelines(args, subsfile)


def parse_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("offset", help="amount of seconds to shift (+-0.000)", type=float)
    parser.add_argument("-p", "--path", help="absolute or relative path to the file")
    return parser.parse_args()


def get_file(args: Namespace) -> str:
    if args.path:
        return args.path if args.path.endswith(".srt") else f"{args.path}.srt"

    srts: set[str] = set(glob.glob("*.srt")) - set(glob.glob("*old-[0-9].srt"))

    if len(srts) == 0:
        print("No .srt file found", file=sys.stderr)
        sys.exit(1)

    elif len(srts) > 1:
        print(f"More than 1 .srt file found: {len(srts)}", file=sys.stderr)
        sys.exit(2)

    return srts.pop()


def change_timelines(args: Namespace, subsfile: str) -> None:
    with open(subsfile, "r", encoding="ISO-8859-1") as rf:
        original_subsfile: str = rf.read().strip()

    blocks: list[str] = original_subsfile.split("\n\n")
    timelines: list[str] = [line.splitlines()[1] for line in blocks if len(line.splitlines()) >= 3]

    raw_inits_and_ends: list[tuple[str, str]] = [
        (
            timeline.split()[0],
            timeline.split()[2],
        )
        for timeline in timelines
    ]

    parsed_inits_and_ends: list[tuple[td, td]] = [
        (
            td(
                hours=float(raw_init.split(":")[0]),
                minutes=float(raw_init.split(":")[1]),
                seconds=float(raw_init.split(":")[2].split(",")[0]),
                milliseconds=float(raw_init.split(":")[2].split(",")[1]),
            ),
            td(
                hours=float(raw_end.split(":")[0]),
                minutes=float(raw_end.split(":")[1]),
                seconds=float(raw_end.split(":")[2].split(",")[0]),
                milliseconds=float(raw_end.split(":")[2].split(",")[1]),
            ),
        )
        for raw_init, raw_end in raw_inits_and_ends
    ]

    altered_inits_and_ends: list[tuple[td, td]] = list()
    offset: td = td(seconds=args.offset)

    for init, end in parsed_inits_and_ends:
        if (init + offset).total_seconds() < 0:
            continue

        altered_inits_and_ends.append((init + offset, end + offset))

    formatted_altered_inits_and_ends: list[tuple[str, str]] = [
        (
            str(init)[:-3].zfill(12).replace(".", ",") if init.microseconds else f"{str(init).zfill(8)},000",
            str(end)[:-3].zfill(12).replace(".", ",") if end.microseconds else f"{str(end).zfill(8)},000",
        )
        for init, end in altered_inits_and_ends
    ]

    altered_subsfile: str = original_subsfile

    for (raw_init, raw_end), (altered_init, altered_end) in zip(raw_inits_and_ends, formatted_altered_inits_and_ends):
        altered_subsfile: str = altered_subsfile.replace(raw_init, altered_init).replace(raw_end, altered_end)

    old_subsfile: str = subsfile.replace(".srt", "-old-0.srt")
    increment: int = 1

    while True:
        if os.path.isfile(old_subsfile):
            old_subsfile: str = old_subsfile.replace(f"-old-{increment - 1}.srt", f"-old-{increment}.srt")
            increment += 1
            continue

        os.rename(subsfile, old_subsfile)
        break

    with open(subsfile, "w", encoding="ISO-8859-1") as wf:
        wf.write(altered_subsfile)


if __name__ == "__main__":
    main()
    print("Complete!")
