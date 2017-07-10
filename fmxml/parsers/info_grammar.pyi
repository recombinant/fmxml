#
# coding: utf-8
#
# Stubs for fmxml.parsers.info_grammar
#
from typing import NamedTuple, List
from xml.etree.ElementTree import XMLPullParser

from .grammar_base import GrammarParserBase


class RawStyle(NamedTuple):
    type_: str
    valuelist_name: str


class RawField(NamedTuple):
    name: str
    style: RawStyle


class RawLayout(NamedTuple):
    database: str
    name: str
    raw_fields: List[RawField]


class RawValue(NamedTuple):
    display: str
    text: str


class RawValuelist(NamedTuple):
    name: str
    raw_values: List[RawValue]


class RawFMPXMLLayout(NamedTuple):
    errorcode: int
    product: str
    layout: str
    raw_valuelists: List[RawValuelist]


class InfoGrammarParser(GrammarParserBase):
    def parse(self, xml_bytes: bytes) -> RawFMPXMLLayout:
        ...

    @staticmethod
    def _parser_read_events(parser: XMLPullParser) -> RawFMPXMLLayout:
        ...
