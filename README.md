# sub-sync

An application written in Python that enables a fixed setting of subtitle time offsets to a selected `srt`
file through the CLI by overwriting its time intervals.

## Usage

The script can be executed via the CLI with or without a `-p` or `--path` keyword argument. If omitting the use, the
script will look for a `srt` file in the current working directory and exit if none or more than one match is found.

Help can be output through the use of the `-h` or `--help` option:

```
[user@host ~]$ subsync.py -h
usage: subsync.py [-h] [-p PATH] offset

positional arguments:
  offset                amount of seconds to shift (+-0.000)

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  absolute or relative path to the file
```

A negative offset value **hastens**, while a positive offset value **delays** the subtitles.

## Bad forms

`srt` files usually follow the principle of:

1. enumeration,
2. time interval, and
3. sub content

This script assumes that to be the form of the passed file and may error out if the form is different. Even though it
rarely happens, the culprit for such mismatches is usually the bad-form advertising of a sub group at the top of
the `srt` file. Either manually delete that block or change it to fit the format.
