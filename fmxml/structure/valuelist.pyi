#
# coding: utf-8
#
# Stubs for fmxml.structure.valuelist
#
import collections.abc
from enum import Enum
from typing import NamedTuple

from ..parsers import info_grammar as info_grammar_module


class ValueTuple(NamedTuple):
    display: str
    text: str


class ValuelistDisplayEnum(Enum):
    VALUELIST_FIRST = ...
    VALUELIST_BOTH = ...
    VALUELIST_SECOND = ...


class Valuelist(collections.abc.Sequence):
    _name: str = ...
    _type: str = ...
    _valuelist: str = ...

    def __init__(self,
                 name: str,
                 raw_values: info_grammar_module.RawValuelist) \
            -> None:
        ...

    @property
    def name(self) -> str:
        ...
