#
# coding: utf-8
#
# Stubs for fmxml.commands.edit_command
#
from typing import Optional, NamedTuple, Any, List

from . import base_command as base_command_module
from .mixins import record_id_mixin as record_id_mixin_module
from .. import fms as fms_module


class EditField(NamedTuple):
    fqfn: str
    value: Any


class EditCommand(record_id_mixin_module.RecordIdMixin,
                  base_command_module.BaseCommand):
    _delete_related: str
    _modification_id: Optional[int]
    _fqfn_list: List[str]

    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str,
                 record_id: Optional[int] = None,
                 modification_id: Optional[int] = None) \
            -> None:
        ...

    def get_query(self) -> str:
        ...

    def _get_modification_id(self) -> int:
        ...

    def _set_modification_id(self,
                             modification_id: Optional[int] = None) \
            -> None:
        ...

    # TODO:
    modification_id: Optional[int] = ...

    def set_delete_related(self, delete_related: Optional[str] = None) -> None:
        ...

    def add_edit_fqfn(self, fqfn: str, value: Any) -> None:
        ...
