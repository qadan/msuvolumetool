# MSU Volume Tool

Tool for modifying the volume of one or more .pcm MSU-1 files.

_NOTE_: This tool is intended for spot-check usage on downloaded MSU packs that
don't sound right in any specific MSU-1 playback implementation. The transform
is currently lossy and structure may be lost with repeated use. For packs in
development, it's still recommended to modify the actual .wav source using a
tool that supports waveform normalization and dynamic range compression.

## Requirements

* Python 3.2 or higher

Compiled executables are available in the releases.

## Usage

The executable can be plopped into a folder full of .pcm files and run to batch
modify the volume of all files in the folder. You will be asked for the
percentage modifier to use.

The modifier is compared to the existing value of each sample of the .pcm and is
used as a percentage by which to modify the sample, so:

* Using a modifier of 50 halves each sample
* Using a modifier of 200 doubles each sample

Et cetera. This shouldn't necessarily be used as a metric to determine the
overall feel of the change in volume, just as the strict rule of how much each
sample is modified by. You may need to run the tool a couple times to get things
where you like it, or run against the `-1.pcm` file and see where that puts you.

Alternatively, you can run the tool from the command line and target individual
files.

**N.B.** Don't go hog-wild with your multiplier. Values for each sample tend to
cap out at around +/- 1500 before getting super loud, and the maximum value for
a sample in either direction is 32767. Rather than checking on every single
sample for every single file whether or not it's within a valid range, I'm
opting to go the fast route and warn you here; it'll just crash if you go out of
range.

Here's the output of `msuvolumetool -h`:

```
usage: msuvolumetool.py [-h] [-p PERCENTAGE] [-t TARGET]

Batch edits .pcm MSU-1 formatted files. Returns an exit code of 0 if all
editing was successful, or 1 if any issues arose during processing.

optional arguments:
  -h, --help            show this help message and exit
  -p PERCENTAGE, --percentage PERCENTAGE
                        The percentage offset by which to change the volume.
                        The existing volume of each sample in the source is
                        assumed to be 100%; for example, to cut each sample in
                        half, use 50, and to double each sample, use 200. If
                        this argument is not provided, you will be asked to
                        give a percentage.
  -t TARGET, --target TARGET
                        The path to a .pcm file, or a folder full of .pcm
                        files to edit. The files will be validated and any
                        valid .pcm files will be edited. Not recursive. Will
                        default to /Users/DTM-2/gits/msuvolumetool. You may
                        also specify the path to a single file to edit.
```

## TODO

* Make it so you can drag and drop things onto the executable
* Make it so the tool doesn't have to overwrite your existing files.

## Troubleshooting

Contact me if you're having troubles, or just open an issue here.

* Discord - `fantallis#3161`
* Twitter - [@itsqadan](https://twitter.com/itsqadan)

## License

[GPL v3](https://www.gnu.org/licenses/gpl.txt)
