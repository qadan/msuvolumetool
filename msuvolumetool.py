#!/usr/local/bin/python

"""
Edits the volume of .pcm MSU-1 files.
"""

import os
import shutil
from psutil import disk_usage
from struct import pack, unpack
from sys import exit
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile


def get_arguments():
    """
    Gets the argument list for this command.
    """
    cwd = os.getcwd()
    parser = ArgumentParser(
        description="""Batch edits .pcm MSU-1 formatted files. Returns an exit
                       code of 0 if all editing was successful, or 1 if any
                       issues arose during processing.""")
    parser.add_argument(
        '-p',
        '--percentage',
        help="""The percentage offset by which to change the volume. The
                existing volume of each sample in the source is assumed to be
                100%%; for example, to cut each sample in half, use 50, and to
                double each sample, use 200. If this argument is not provided,
                you will be asked to give a percentage.""",
        type=int,
        default=False)
    parser.add_argument(
        '-t',
        '--target',
        help="""The path to a .pcm file, or a folder full of .pcm files to
                edit. The files will be validated and any valid .pcm files will
                be edited. Not recursive. Will default to %s. You may also
                specify the path to a single file to edit.""" % cwd,
        default=cwd)
    return vars(parser.parse_args())


def validate_files(msu_files):
    """
    Return False if the files aren't valid.

    This basically means if no files were found, in which case msu_files will
    be empty.
    """
    if not msu_files:
        print("""No MSU files in the given target, or the target does not have
                 a .pcm extension.""")
        return False
    return True


def get_percentage():
    """
    Gets the percentage modifier if none is provided.
    """
    while True:
        choice = input("Enter the volume percentage to set the file(s) to: ")
        try:
            percentage = int(choice)
            if percentage < 1:
                print("Please enter a number larger than 0.")
                continue
            if percentage == 100:
                print("This won't change the volume; enter a different number.")
            return percentage
        except ValueError:
            print("Please enter a positive number.")


def get_msu_files(target):
    """
    Simple filter for .msu files.

    The target can be a directory containing .msu files, or an .msu file.
    Returns the list of any appropriate files found.
    """
    files = []
    if os.path.isdir(target):
        for filename in os.listdir(target):
            if filename.endswith('.pcm'):
                files.append(os.path.join(target, filename))
    if target.endswith('.pcm'):
        files.append(target)
    return files


def validate_space(msu_filename):
    """
    Validates that enough space exists to create a copy of msu_filename.

    The copy will be precisely the same size.

    There's an inherent race condition here, but we're trying our best ok?
    """
    diskinfo = disk_usage(msu_filename)
    fileinfo = os.stat(msu_filename)
    return fileinfo.st_size <= diskinfo.free


def validate_is_msu(msu_filename):
    """
    Simple validator that a given file does indeed have MSU headers.
    """
    with open(msu_filename, 'rb') as msu_file:
        msu_file.seek(0)
        first_four = msu_file.read(4).decode('utf-8')
        return first_four == 'MSU1'


def yield_sample_chunks(msu_filename):
    """
    Yields chunks from the sample portion of the MSU file.
    """
    with open(msu_filename, 'rb') as msu:
        msu.seek(8)
        while True:
            chunk = msu.read(2)
            if chunk:
                unpacked_chunk = unpack('<h', chunk)
                yield unpacked_chunk[0]
            else:
                break


def copy_edit_volume(msu_filename, target, percentage):
    """
    Modifies samples in an MSU file against the given percentage.
    """
    # Move over the first 8 bytes - header and loop.
    with open(msu_filename, 'rb') as msu:
        target.write(msu.read(8))

    # Determine the modifier
    modifier = percentage / 100.0
    for sample in yield_sample_chunks(msu_filename):
        target.write(pack('<h', int(round(sample * modifier))))


def main():
    """
    Main; perform the batch volume control.
    """
    # Get and validate arguments.
    args = get_arguments()
    msu_files = get_msu_files(args['target'])
    if not validate_files(msu_files):
        return 1
    if not args['percentage']:
        args['percentage'] = get_percentage()

    code = 0
    verb = "Increased" if args['percentage'] > 100 else "Decreased"
    for msu_filename in msu_files:
        # Validate space in the temp folder.
        if not validate_space(msu_filename):
            print("Not enough space to create temp file for %s; skipping ..." %
                 msu_filename)
            continue
        # Ensure the file actually has an MSU header.
        if not validate_is_msu(msu_filename):
            print(
                "Failed to validate %s as MSU; skipping ..." %
                msu_filename)
            code = 1
            continue

        # Copy to a temp location we can work with.
        with NamedTemporaryFile(delete=False) as tf:
            # Edit the copy, then overwrite the original.
            copy_path = tf.name
            copy_edit_volume(msu_filename, tf, args['percentage'])
        shutil.move(copy_path, msu_filename)
        print("Set volume of %s to %s%%" %
              (msu_filename, str(args['percentage'])))

    # Will be 1 if issues were encountered.
    return code


# Code runner.
if __name__ == '__main__':
    try:
        code = main()
        if code > 0:
            # This is a bit of a hack-y workaround for the use case outside of
            # the command line, just to ensure people do see any errors.
            input("Press Enter to continue ...")
        exit(code)
    except KeyboardInterrupt:
        print("Exiting ...")
    except SyntaxError:
        pass
