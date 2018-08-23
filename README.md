# MSU Volume Tool

Tool for modifying the volume of one or more .pcm MSU-1 files.

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

Here's the output of `msuvolumetool -h`:

```
usage: msuvolumetool.py [-h] [-p PERCENTAGE] [-t TARGET]

Batch edits .pcm MSU-1 formatted files. Returns an exit code of 0 if all
editing was successful, or 1 if any issues arose during processing.

optional arguments:
  -h, --help            show this help message and exit
  -p PERCENTAGE, --percentage PERCENTAGE
                        The percentage offset by which to change the volume.
                        The existing volume is assumed to be 100%; for
                        example, to cut the volume in half, use 50, and to
                        double the volume use 200. If this argument is not
                        provided, you will be asked to give a percentage.
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
