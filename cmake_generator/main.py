import logging

from . import parser

LOG = logging.getLogger(__name__)


def pycmake(path):
    """
    Run PYCmake recursively in the path given. will try to locate all PyCMake files and create cmake files from them

    :param str path:
    :return:
    """

    files = parser.find_files(path)

    for file in files:
        project = parser.parse_file(file)
        project.write()
