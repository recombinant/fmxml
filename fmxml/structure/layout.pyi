#
# coding: utf-8
#
# Stubs for fmxml.structure.layout
#
from typing import Dict, List

from . import field_definition as field_definition_module
from . import portal as portal_module
from . import valuelist as valuelist_module
from .. import fms as fms_module
from ..parsers import data_grammar as data_grammar_module


class Layout:
    _fms: fms_module.FileMakerServer = ...
    _name: str = ...
    _database_name: str = ...
    _date_format: str = ...
    _time_format: str = ...
    _timestamp_format: str = ...
    _field_definition_lookup: Dict[str, field_definition_module.FieldDefinition] = ...
    _valuelists: Dict[str, valuelist_module.Valuelist] = ...
    _portals: Dict[str, portal_module.Portal] = ...

    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 parsed_data: data_grammar_module.RawFMResultSet) \
            -> None:
        ...

    @property
    def fms(self) -> fms_module.FileMakerServer:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def database_name(self) -> str:
        ...

    def has_field_definition(self, field_name: str) -> bool:
        ...

    def get_field_definition(self, field_name: str) -> field_definition_module.FieldDefinition:
        ...

    @property
    def field_names(self) -> List[str]:
        return list(self._field_definition_lookup)

    def get_valuelist(self, valuelist_name: str) -> valuelist_module.Valuelist:
        ...

    def _load_fmpxmllayout(self) -> None:
        ...

    @property
    def date_format(self) -> str:
        ...

    @property
    def time_format(self) -> str:
        ...

    @property
    def timestamp_format(self) -> str:
        ...

    def _add_portal(self,
                    table_name: str,
                    portal: portal_module.Portal) \
            -> None:
        ...

    @property
    def portal_names(self) -> List[str]:
        ...
