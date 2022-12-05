# sub-sync

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Enables a fixed setting of subtitle time offsets to a selected `srt` file via the CLI by overwriting its time intervals.

It differs from utilizing subtitle shifts inside an arbitrary media player, due to permenently applying timeline
changes, not just during an active session. In other words, sync audio and subtitle tracks once, use them appropriately
multiple times.

## Usage

A negative offset value ***hastens***, while a positive offset value ***delays*** the subtitles. The script can be
executed via the CLI with or without a `-p` or `--path` parameter.

If omitting the use, the code will look for a `srt` file in the current working directory and exit if none or more
than one match is found. An exception to this case are `srt` files that abide by a glob match: `*old-[0-9].srt`. This
is done in order to allow rapid readjustments when attempting to set an audio-subtitle sync via trial and
error—see [output](#output).

Help can be output through the use of the `-h` or `--help` option:

```commandline
$ subsync.py --help
usage: subsync.py [-h] [-p PATH] offset

positional arguments:
  offset                amount of seconds to shift (+-0.000)

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  absolute or relative path to the file
```

## Output

The output is a new `srt` file with newly set timelines, with the old file being kept and renamed
to `-old-{increment}.srt`, where `{increment}` is a serial increment of old `srt` files in the same directory, starting
with 0.

## Bad forms

`srt` files usually follow the ordered principle of:

1. enumeration
2. time interval
3. sub content

This code assumes that to be the form of the passed file and may error out if the form is different. Even though it
rarely happens, the culprit for such mismatches is usually a type of bad-form advertising of a subtitle group at the top
of the file. Either manually delete that segment or change it to fit the format.
