#
# coding: utf-8
#
# Stubs for fmxml.parsers.data_grammar
#
from typing import Optional, List, NamedTuple, Dict
from xml.etree.ElementTree import Element, XMLPullParser

from .grammar_base import ElemInitialiser
from .grammar_base import GrammarParserBase


class RawError(NamedTuple):
    code: str


class RawDataSource(NamedTuple):
    database: str
    date_format: str
    layout: str
    table: str
    time_format: str
    timestamp_format: str
    total_count: int


class RawFieldDefinition(ElemInitialiser):
    auto_enter: bool = ...
    four_digit_year: bool = ...
    # global: str = ...  # TODO:
    max_repeat: int = ...
    name: str = ...
    not_empty: bool = ...

    numeric_only: bool = ...
    max_characters: Optional[int] = ...
    result: str = ...
    time_of_day: str = ...
    type: str = ...

    def __init__(self, elem: Element) -> None:
        ...


class RawField(ElemInitialiser):
    name: str = ...
    data: List[str] = ...  # TODO:

    def __init__(self, elem: Element) -> None:
        ...


class RawRecord(ElemInitialiser):
    record_id: int = ...
    modification_id: int = ...
    fields: List[RawField] = ...
    relatedsets: str = ...  # TODO
    mod_id: int = ...  # TODO: tweak this ?

    def __init__(self, elem: Element) -> None:
        ...


class RawResultSet(ElemInitialiser):
    count: int
    fetch_size: int
    records: List[RawRecord]

    def __init__(self, elem: Element) -> None:
        ...


class DataGrammarParser(GrammarParserBase):
    def parse(self, xml_bytes: bytes) -> RawFMResultSet:
        ...

    @staticmethod
    def _parser_read_events(parser: XMLPullParser) -> RawFMResultSet:
        ...


class RawFMResultSet(ElemInitialiser):
    version: str = ...  # TODO:
    xmlns: str = ...  # TODO:
    error: str = ...  # TODO:
    product: str = ...  # TODO:
    datasource: RawDataSource = ...
    resultset: RawResultSet = ...
    field_definitions: List[RawFieldDefinition] = ...
    relatedset_definitions: Dict[str, RawFieldDefinition] = ...

    def __init__(self, elem: Element) -> None:
        ...
