#
# coding: utf-8
#
# Stubs for fmxml.structure.portal
#
from typing import Dict, List

from . import field_definition as field_definition_module
from . import layout as layout_module
from .. import fms as fms_module


class Portal:
    _fms: fms_module.FileMakerServer = ...
    _layout: layout_module.Layout = ...
    _table_name: str = ...
    _field_definition_lookup: Dict[str, field_definition_module.FieldDefinition] = ...

    def __init__(self,
                 layout: layout_module.Layout,
                 table_name: str) \
            -> None:
        ...

    @property
    def fms(self) -> fms_module.FileMakerServer:
        ...

    @property
    def layout(self) -> layout_module.Layout:
        ...

    @property
    def table_name(self) -> str:
        ...

    def add_field_definition_(self,
                              field_name: str,
                              field_definition: field_definition_module.FieldDefinition) \
            -> None:
        ...

    @property
    def field_names(self) -> List[str]:
        ...
