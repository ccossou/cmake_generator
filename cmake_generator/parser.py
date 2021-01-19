import logging
import glob
import os
import re

from . import constants
from . import generator

LOG = logging.getLogger(__name__)


def find_files(path):
    """
    Find all pycmake files recursively in a given path

    :param str path:
    :return: list of files
    :rtype: list(str)
    """

    filename = constants.pycmake_filename

    return glob.glob(os.path.join(path, f"**/{filename}"), recursive=True)


def parse_file(file):
    """
    Parse a given pycmake file

    :param file: relative or absolute path to the file
    :return:
    """
    obj = open(file, "r")

    install = False
    custom_install = None

    targets = []
    for line in obj:
        if not line.strip():
            continue

        # Prepare and concatenate multiple lines if the command is not single line
        full_line = line
        if "(" in full_line:
            while ")" not in full_line:
                line = obj.readline()
                full_line += line

        command, args = parse_command(full_line)

        if command == "project":
            project_name, version_number, language = args
        elif command == "install":
            install = True
            if args:
                custom_install = args[0]
        elif command == "library":
            target_name = args[0]

            # Exclude target name from the arg passed to the function
            priv_source, pub_source, priv_header, pub_header = parse_target_args(args[1:])

            t = generator.Library(target_name)
            t.add_sources(public=pub_source, private=priv_source)
            t.add_headers(public=pub_header, private=priv_header)
            targets.append(t)
        elif command == "executable":
            target_name = args[0]

    obj.close()

    # Create actual CMakeList.txt file
    project = generator.Project(project_name, version_number, language, custom_install=custom_install, install=install)
    project.add_targets(*targets)
    project.set_cwd(os.path.dirname(file))

    return project


def parse_command(text):
    """
    parse a command and its argument in a text that can be on multiple lines

    :param str text:
    :return: command, args
    :rtype: str, list(str)
    """

    text = text.strip()

    command_pattern = re.compile(r"([^\(]+)\(([^\)]+)\)")

    match = re.search(command_pattern, text)
    command_name = match.group(1)
    args = match.group(2).split()  # will strip tabs, extra spaces and newline character

    return command_name, args


def parse_target_args(args):
    """
    Given a list of arguments for a target (library or executable), will return them sorted in sub-list

    Note that the list of argument need to be filtered and only contain dependencies, and private/public sources.

    so for a library it's args[1:], and for an executable, the main source need to also be excluded

    :param list(str) args:
    :return: priv_source, pub_source, priv_header, pub_header
    :rtype: list(str), list(str), list(str), list(str)
    """

    private_sources = []
    public_sources = []
    private_dep = []
    public_dep = []

    for word in args:
        if word.upper() == "PRIVATE":
            active_list = private_sources
        elif word.upper() == "PUBLIC":
            active_list = public_sources
        elif word.upper() == "PRIVATE_DEPENDENCIES":
            active_list = private_dep
        elif word.upper() == "PUBLIC_DEPENDENCIES":
            active_list = public_dep
        else:
            active_list.append(word)

    priv_header = []
    priv_source = []
    for item in private_sources:
        if any(ext in item for ext in constants.header_ext):
            priv_header.append(item)
        else:
            priv_source.append(item)

    pub_header = []
    pub_source = []
    for item in public_sources:
        if any(ext in item for ext in constants.header_ext):
            pub_header.append(item)
        else:
            pub_source.append(item)

    return priv_source, pub_source, priv_header, pub_header
