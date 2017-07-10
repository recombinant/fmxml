#
# coding: utf-8
#
# Stubs for fmxml.commands.mixins.relatedsets_mixin
#
from typing import Union, Optional

from .. import command_container as command_container_module
from ... import fms as fms_module

MaxType = Union[int, str, None]


class RelatedsSetsMixin:
    _relatedsets_filter: str = ...
    _relatedsets_max: MaxType = ...

    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str) \
            -> None:
        ...

    def get_command_params(self) \
            -> command_container_module.CommandContainer:
        ...

    def set_relatedsets_filter(self, filter_: Optional[str] = ...) -> None:
        ...

    def set_relatedsets_max(self, max_: MaxType = ...) -> None:
        ...
