#
# coding: utf-8
#
# Stubs for fmxml.parsers.data_grammar2
#
from typing import NamedTuple, List, Optional
from xml.etree.ElementTree import XMLPullParser

from .grammar_base import ElemInitialiser
from .grammar_base import GrammarParserBase


class RawCol(NamedTuple):
    data: str


class RawRow(NamedTuple):
    modid: str
    recordid: str
    cols: str


class RawResultset(NamedTuple):
    found: str
    rows: List[RawRow]


class RawDatabase(NamedTuple):
    name: str
    records: str
    dateformat: str
    timeformat: str
    layout: str


class RawFMPXMLResult(NamedTuple):
    errorcode: str
    product: Optional[str]
    database: Optional[RawDatabase]
    fields: List[str]
    resultset: RawResultset


class RawFieldDefinition(ElemInitialiser):
    ...


class DataGrammar2Parser(GrammarParserBase):
    def parse(self, xml_bytes: bytes) -> RawFMPXMLResult:
        ...

    @staticmethod
    def _parser_read_events(parser: XMLPullParser) -> RawFMPXMLResult:
        ...
