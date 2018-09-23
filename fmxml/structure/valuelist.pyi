#
# coding: utf-8
#
# Stubs for fmxml.structure.valuelist
#
import collections.abc
from enum import Enum
from typing import NamedTuple, List

from ..parsers import info_grammar as info_grammar_module


class ValueTuple(NamedTuple):
    display: str
    text: str


class ValuelistDisplayEnum(Enum):
    VALUELIST_FIRST: int = ...
    VALUELIST_BOTH: int = ...
    VALUELIST_SECOND: int = ...


class Valuelist(collections.abc.Sequence):
    _name: str
    _type: str
    _valuelist: str

    def __init__(self,
                 name: str,
                 raw_values: List[info_grammar_module.RawValue]) \
            -> None:
        ...

    @property
    def name(self) -> str:
        ...
