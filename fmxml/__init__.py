#
# coding: utf-8
#
# fmxml.__init__
#
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'

from .fms import FileMakerServer
from . import commands
from . import parsers
from . import structure
