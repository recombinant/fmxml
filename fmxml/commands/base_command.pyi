#
# coding: utf-8
#
# Stubs for fmxml.commands.base_command
#
import abc

from .. import fms as fms_module
from ..commands import command_container as command_container_module
from ..structure import command_result as command_result_module


class BaseCommand0(abc.ABC):
    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str) \
            -> None:
        ...

    def get_command_params(self) -> command_container_module.CommandContainer:
        ...


class BaseCommand1(abc.ABC):
    def get_query(self) -> str:
        ...


class BaseCommand(BaseCommand1):
    _fms: fms_module.FileMakerServer
    _layout_name: str

    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str) \
            -> None:
        ...

    def get_command_params(self) -> command_container_module.CommandContainer:
        ...

    def execute(self) -> command_result_module.CommandResult:
        ...
