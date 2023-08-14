#!/usr/bin/env python3

import glob
import os
import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class BaseStruct:
    args: Namespace | None = None
    srt_path: str = ""
    alt_srt: str = ""


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
    assert struct.args is not None

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
    assert struct.args is not None

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

    parsed_times: list[tuple[timedelta, timedelta]] = [
        (
            parse_times(r_init),
            parse_times(r_end),
        )
        for r_init, r_end in raw_times
    ]

    alt_times: list[tuple[timedelta, timedelta]] = list()
    offset: timedelta = timedelta(seconds=struct.args.offset)

    for p_init, p_end in parsed_times:
        if (p_init + offset).total_seconds() < 0:
            continue

        alt_times.append((p_init + offset, p_end + offset))

    formatted_alt_times: list[tuple[str, str]] = [
        (
            str(a_init)[:-3].zfill(12).replace(".", ",") if a_init.microseconds else f"{str(a_init).zfill(8)},000",
            str(a_end)[:-3].zfill(12).replace(".", ",") if a_end.microseconds else f"{str(a_end).zfill(8)},000",
        )
        for a_init, a_end in alt_times
    ]

    struct.alt_srt = origin_srt

    for (r_init, r_end), (fa_init, fa_end) in zip(raw_times, formatted_alt_times):
        struct.alt_srt = struct.alt_srt.replace(r_init, fa_init).replace(r_end, fa_end)


def parse_times(raw: str) -> timedelta:
    return timedelta(
        hours=float(raw.split(":")[0]),
        minutes=float(raw.split(":")[1]),
        seconds=float(raw.split(":")[2].split(",")[0]),
        milliseconds=float(raw.split(":")[2].split(",")[1]),
    )


def create_alt_srt(struct: BaseStruct) -> None:
    increment: int = 0

    while True:
        old_path: str = struct.srt_path.replace(".srt", f"-old-{str(increment).zfill(2)}.srt")

        if os.path.isfile(old_path):
            increment += 1
            continue

        os.rename(struct.srt_path, old_path)
        break

    with open(struct.srt_path, "w", encoding="ISO-8859-1") as wf:
        wf.write(struct.alt_srt)


if __name__ == "__main__":
    main()
    print("Complete!")
