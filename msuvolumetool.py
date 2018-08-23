#!/usr/local/bin/python

"""
Edits the volume of .pcm MSU-1 files.
"""

import os
import shutil
from math import floor
from struct import pack, unpack
from argparse import ArgumentParser
from functools import partial
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
                existing volume is assumed to be 100%%; for example, to cut the
                volume in half, use 50, and to double the volume use 200. If
                this argument is not provided, you will be asked to give a
                percentage.""",
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


def validate_args(msu_files):
    """
    Return False if the arguments aren't valid.
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


def validate_is_msu(msu_filename):
    """
    Simple validator that a given file does indeed have MSU headers.
    """
    with open(msu_filename, 'rb') as msu_file:
        msu_file.seek(0)
        first_four = msu_file.read(4).decode('utf-8')
        return first_four == 'MSU1'


def copy_edit_volume(msu_filename, target, percentage):
    """
    Modifies samples in an MSU file against the given percentage.
    """
    with open(msu_filename, 'rb') as msu:
        # Move over the first 8 bytes - header and loop.
        target.write(msu.read(8))
        # Determine the modifier
        modifier = percentage / 100.0
        for sample in iter(partial(msu.read, 2), ''):
            # Possibly slow, but what IS the idiom for iterating over bytes in
            # Python anyway? Revisit?
            if len(sample) != 2:
                return
            sample_int = unpack('<h', sample)
            # Rather than casting directly to an integer, floor() it first to
            # get consistent output. Not that I suspect this is something a
            # human could pick up on.
            packed_sample = pack('<h', int(floor(sample_int[0] * modifier)))
            target.write(packed_sample)


def main():
    """
    Main; perform the batch volume control.
    """
    # Get and validate arguments.
    args = get_arguments()
    msu_files = get_msu_files(args['target'])
    if not validate_args(msu_files):
        return 1
    if not args['percentage']:
        args['percentage'] = get_percentage()

    code = 0
    for msu_filename in msu_files:
        # @TODO: Validate space in the temp folder.
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
        main()
    except KeyboardInterrupt:
        print("Exiting ...")
