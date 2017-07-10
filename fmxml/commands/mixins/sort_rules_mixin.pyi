#
# coding: utf-8
#
# Stubs for fmxml.commands.mixins.sort_rules_mixin
#
from typing import Optional, Dict, NamedTuple

from .. import command_container as command_container_module
from ... import fms as fms_module


class SortOrder(NamedTuple):
    precedence: int
    order: str


class SortRulesMixin:
    _sort_fields: Dict[str, SortOrder] = ...

    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str) \
            -> None:
        ...

    def get_command_params(self) \
            -> command_container_module.CommandContainer:
        ...

    def add_sort_rule(self,
                      field_name: Optional[str],
                      precedence: Optional[int],
                      order: Optional[str] = ...) \
            -> None:
        ...

    def del_sort_rule(self, field_name: str) -> None:
        ...

    def clear_sort_rules(self) -> None:
        ...
