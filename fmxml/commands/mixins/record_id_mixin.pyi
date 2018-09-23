#
# coding: utf-8
#
# Stubs for fmxml.commands.mixins.record_id_mixin
#
from typing import Optional

from .. import command_container as command_container_module
from ... import fms as fms_module


class RecordIdMixin:
    _record_id: Optional[int]

    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str) \
            -> None:
        ...

    def get_command_params(self) \
            -> command_container_module.CommandContainer:
        ...

    def _get_record_id(self) -> Optional[int]:
        ...

    def _set_record_id(self, record_id: Optional[int] = None) -> None:
        ...

    record_id: Optional[int] = ...
