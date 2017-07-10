#
# coding: utf-8
#
# Stubs for fmxml.parsers.grammar_base
#
from typing import NamedTuple, TypeVar, Type, Union
from xml.etree.ElementTree import Element

from . import data_grammar as data_grammar_module
from . import data_grammar2 as data_grammar_module2
from . import info_grammar as info_grammar_module

T = TypeVar('T')


def elem_to_namedtuple(elem: Element, tuple_class: Type[T]) -> T:
    ...


class ElemInitialiser:
    def __init__(self, elem: Element) -> None:
        ...


class RawProduct(NamedTuple):
    build: str
    name: str
    version: str


class GrammarParserBase:
    def parse(self, xml_bytes: bytes) \
            -> Union[info_grammar_module.RawFMPXMLLayout,
                     data_grammar_module.RawFMResultSet,
                     data_grammar_module2.RawFMPXMLResult,
            ]:
        ...
