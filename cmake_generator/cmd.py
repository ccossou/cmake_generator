import logging
import argparse
import os

from . import main

LOG = logging.getLogger(__name__)


def pycmake_from_cmdline(args):


    # Create argument parser to track and handle command line arguments.
    parser = argparse.ArgumentParser(description="Generate CMake files from PyCMake files")
    parser.add_argument('path', type=str, nargs='?', default=None, help='path')
    parser.add_argument('--version', action='store_true',
                        help='Display the MIRISim version number')
    known, _ = parser.parse_known_args(args)

    if known.version:
        from . import version
        print("PyCMake {}".format(version.__version__))
        return

    # Verify that the required filenames were provided and the files exist.
    try:
        # Verify input arguments were provided.
        if known.path is None:
            path = os.getcwd()
        else:
            path = known.path

    except Exception as e:
        print("\nError parsing configuration:")
        print(str(e))
        parser.print_help()
        return

    # run PyCMake
    try:
        main.pycmake(path)
    except Exception as e:
        print("\nError running PyCMake:")
        print(str(e))
        raise
