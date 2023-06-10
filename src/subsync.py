#!/usr/bin/env python3

import glob
import os
import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from datetime import timedelta as td


@dataclass
class BaseStruct:
    args: Namespace = None
    srt_path: str = None
    alt_srt: str = None


def main() -> None:
    struct = BaseStruct()

    parse_args(struct)
    get_srt(struct)
    change_timelines(struct)
    create_alt_srt(struct)


def parse_args(struct: BaseStruct) -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "offset",
        help="amount of seconds to shift (+-0.000)",
        type=float,
    )
    parser.add_argument(
        "-p",
        "--path",
        help="absolute or relative path to the file",
    )
    struct.args = parser.parse_args()


def get_srt(struct: BaseStruct) -> None:
    if struct.args.path:
        struct.srt_path = struct.args.path if struct.args.path.endswith(".srt") else f"{struct.args.path}.srt"
        return

    srts: set[str] = set(glob.glob("*.srt")) - set(glob.glob("*old-[0-9][0-9].srt"))

    match len(srts):
        case 0:
            sys.exit("No srt file found")
        case 1:
            pass
        case _:
            sys.exit(f"More than 1 srt file found: {len(srts)} {tuple(srts)}")

    struct.srt_path = srts.pop()


def change_timelines(struct: BaseStruct) -> None:
    with open(struct.srt_path, "r", encoding="ISO-8859-1") as rf:
        origin_srt: str = rf.read().strip()

    blocks: list[str] = origin_srt.split("\n\n")
    timelines: list[str] = [line.splitlines()[1] for line in blocks if len(line.splitlines()) >= 3]

    raw_times: list[tuple[str, str]] = [
        (
            timeline.split()[0],
            timeline.split()[2],
        )
        for timeline in timelines
    ]

    parsed_times: list[tuple[td, td]] = [
        (
            td(
                hours=float(init.split(":")[0]),
                minutes=float(init.split(":")[1]),
                seconds=float(init.split(":")[2].split(",")[0]),
                milliseconds=float(init.split(":")[2].split(",")[1]),
            ),
            td(
                hours=float(end.split(":")[0]),
                minutes=float(end.split(":")[1]),
                seconds=float(end.split(":")[2].split(",")[0]),
                milliseconds=float(end.split(":")[2].split(",")[1]),
            ),
        )
        for init, end in raw_times
    ]

    alt_times: list[tuple[td, td]] = list()
    offset: td = td(seconds=struct.args.offset)

    for init, end in parsed_times:
        if (init + offset).total_seconds() < 0:
            continue

        alt_times.append((init + offset, end + offset))

    formatted_alt_times: list[tuple[str, str]] = [
        (
            str(init)[:-3].zfill(12).replace(".", ",") if init.microseconds else f"{str(init).zfill(8)},000",
            str(end)[:-3].zfill(12).replace(".", ",") if end.microseconds else f"{str(end).zfill(8)},000",
        )
        for init, end in alt_times
    ]

    struct.alt_srt = origin_srt

    for (init, end), (alt_init, alt_end) in zip(raw_times, formatted_alt_times):
        struct.alt_srt = struct.alt_srt.replace(init, alt_init).replace(end, alt_end)


def create_alt_srt(struct: BaseStruct) -> None:
    origin_srt_path: str = struct.srt_path.replace(".srt", "-old-00.srt")
    increment: int = 1

    while True:
        if os.path.isfile(origin_srt_path):
            origin_srt_path: str = origin_srt_path.replace(
                f"-old-{str(increment - 1).zfill(2)}.srt",
                f"-old-{str(increment).zfill(2)}.srt",
            )
            increment += 1
            continue

        os.rename(struct.srt_path, origin_srt_path)
        break

    with open(struct.srt_path, "w", encoding="ISO-8859-1") as wf:
        wf.write(struct.alt_srt)


if __name__ == "__main__":
    main()
    print("Complete!")
