#
# coding: utf-8
#
# Stubs for fmxml.commands.mixins.script_mixin
#
from typing import Optional, List

from .. import command_container as command_container_module
from ... import fms as fms_module


class ScriptDetail:
    _pre: str = ...
    _script_name: Optional[str] = ...
    _script_params: Optional[List[str]] = ...

    def __init__(self, pre: str) -> None:
        ...

    def add_command_params(self,
                           command_params: command_container_module.CommandContainer) \
            -> command_container_module.CommandContainer:
        ...

    def add_script(self,
                   script_name: str,
                   *script_params: str) \
            -> None:
        ...


class ScriptMixin:
    _script_detail: ScriptDetail = ...

    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str) \
            -> None:
        ...

    def get_command_params(self) \
            -> command_container_module.CommandContainer:
        ...

    def set_script(self,
                   script_name: str,
                   *script_params: str) \
            -> None:
        ...


class PreFindScriptMixin:
    _prefind_script_detail: ScriptDetail = ...

    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str) \
            -> None:
        ...

    def get_command_params(self) \
            -> command_container_module.CommandContainer:
        ...

    def set_prefind_script(self,
                           script_name: str,
                           *script_params: str) \
            -> None:
        ...


class PreSortScriptMixin:
    _pre_sort_script_detail: ScriptDetail = ...

    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str) \
            -> None:
        ...

    def get_command_params(self) \
            -> command_container_module.CommandContainer:
        ...

    def set_presort_script(self,
                           script_name: str,
                           *script_params: str) \
            -> None:
        ...
