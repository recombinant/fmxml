#
# coding: utf-8
#
# Stubs for fmxml.commands.mixins.foundset_mixin
#
from typing import Union

from .. import command_container as command_container_module
from ... import fms as fms_module

MaxType = Union[int, str, None]


class FoundSetMixin:
    _max: MaxType
    _skip: int

    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str) \
            -> None:
        ...

    def get_command_params(self) \
            -> command_container_module.CommandContainer:
        ...

    @property
    def skip(self) -> int:
        ...

    def set_skip(self, skip: int = 0) -> None:
        ...

    @property
    def max(self) -> MaxType:
        ...

    def set_max(self, max_: MaxType = None) -> None:
        ...
