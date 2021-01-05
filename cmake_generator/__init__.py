import logging
logging.getLogger("cmake_generator").addHandler(logging.NullHandler())

from .version import __version__

from . import utils
from .target import *