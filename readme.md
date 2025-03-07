# sub-sync

enables a fixed setting of subtitle time offsets to a selected [subrip](https://en.wikipedia.org/wiki/SubRip) (`srt`)
file via the cli by overwriting its time intervals

it differs from utilizing subtitle shifts inside an arbitrary media player, due to permenently applying timeline
changes, not just during an active session — sync audio and subtitle tracks once, use them multiple times

## install

fetch the latest version:

```console
python3 -m pip install git+https://github.com/tainn/sub-sync.git@0.1.3
```

## usage

a negative offset value **hastens**, while a positive offset value **delays** the subtitles

the script can be executed via the cli with or without a `-p` or `--path` parameter. if omitting the use, the code will
look for a `srt` file in the current working directory and exit if none or more than one match is found. an exception to
this case are `srt` files that abide by a glob match: `*old-[0-9][0-9].srt`. this is done in order to allow rapid
readjustments ( up to 100 times ) when attempting to set an audio-subtitle sync via trial and error —
see [output](#output)

```console
$ subsync --help
usage: subsync [-h] [-p PATH] offset

positional arguments:
  offset                amount of seconds to shift (+-0.000)

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  absolute or relative path to the file
```

## output

the output is a new `srt` file with newly set timelines, with the old file being kept and renamed
to `-old-{incr}.srt`, where `{incr}` is a serial increment of old `srt` files in the same directory, starting
with 00 and ending with 99, allowing for up to 100 buffered files

## bad forms

the subrip (`srt`) files usually follow their file [format](https://en.wikipedia.org/wiki/SubRip#SubRip_file_format).
this code assumes that to be the form of the passed file and may error out if the form is different. even though it
rarely happens, the culprit for such mismatches is usually a type of bad-form advertising of a subtitle group at the top
of the file. either manually delete that segment or change it to fit the format
