#
# coding: utf-8
#
# Stubs for fmxml.structure.command_result
#
from typing import List

from . import layout as layout_module
from . import record as record_module
from .. import fms as fms_module
from ..parsers import data_grammar as data_grammar_module
from ..structure import field_container as field_container_module


class CommandResult:
    _fms: fms_module.FileMakerServer = ...
    _error_code: int = ...
    _layout: layout_module.Layout = ...
    _total_count: int = ...
    _found_count: int = ...
    _fetch_size: int = ...
    _records: List[record_module.Record] = ...

    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 parsed_data: data_grammar_module.RawFMResultSet) \
            -> None:
        ...

    @property
    def layout(self) -> layout_module.Layout: ...

    @property
    def records(self) -> List[record_module.Record]: ...

    @property
    def field_names(self) -> List[str]: ...

    @property
    def portal_names(self) -> List[str]: ...

    @property
    def total_count(self) -> int: ...

    @property
    def found_count(self) -> int: ...

    @property
    def fetch_size(self) -> int: ...

    def _create_new_record(self,
                           layout: layout_module.Layout,
                           raw_record: data_grammar_module.RawRecord) \
            -> record_module.Record:
        ...

    @staticmethod
    def _raw_record_field_factory(layout: layout_module.Layout,
                                  raw_record_fields: List[data_grammar_module.RawField]) \
            -> field_container_module.FieldContainer:
        ...
