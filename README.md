# sub-sync

![python_version](https://img.shields.io/badge/python-v3.9%2B-b0c9ff)
![dependencies](https://img.shields.io/badge/dependencies-none-e0b0ff)

An application written in Python that enables a fixed setting of subtitle time offsets to a selected **srt**
file via the CLI by overwriting its time intervals.

It differs from utilizing subtitle shifts inside any media player by permenently applying timeline changes, not just
during the active session. Sync audio and subtitles once, watch multiple times.

## Usage

The script can be executed via the CLI with or without a `-p` or `--path` keyword argument.

If omitting the use, the code will look for a **srt** file in the current working directory and exit if none or more
than one match is found. An exception to this case are **srt** files that abide by a regex match: `*old-[0-9].srt`. This
is done in order to allow rapid readjustments when attempting to set an audio-subtitle sync via trial and
error—see [output](#output).

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

A negative offset value ***hastens***, while a positive offset value ***delays*** the subtitles.

## Output

The output is a new **srt** file with newly set timelines, with the old file being kept and renamed
to `-old-{increment}.srt`, where `{increment}` is a serial increment of old **srt** files in the same directory,
starting with 0.

## Bad forms

**srt** files usually follow the principle of:

1. enumeration,
2. time interval, and
3. sub content

This code assumes that to be the form of the passed file and may error out if the form is different. Even though it
rarely happens, the culprit for such mismatches is usually the bad-form advertising of a subtitle group at the top of
the **srt** file. Either manually delete that block or change it to fit the format.
