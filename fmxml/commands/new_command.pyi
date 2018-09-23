#
# coding: utf-8
#
# Stubs for fmxml.commands.new_command
#
from typing import NamedTuple, List, Any

from .base_command import BaseCommand
from .. import fms as fms_module


class NewField(NamedTuple):
    fqfn: str
    value: Any


class NewCommand(BaseCommand):
    _fqfn_list: List[NewField]

    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str) \
            -> None:
        ...

    def get_query(self) -> str:
        ...

    def add_new_fqfn(self,
                     fqfn: str,
                     value: Any) \
            -> None:
        ...

    def set_field_value(self,
                        field_name: str,
                        value: Any,
                        repetition_number: int = 0) \
            -> None:
        ...
