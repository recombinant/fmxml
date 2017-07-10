#
# coding: utf-8
#
# Stubs for fmxml.commands.find_command
#
from collections import namedtuple
from typing import Optional, List, Any

from .base_command import BaseCommand
from .mixins import (RecordIdMixin, FoundSetMixin, SortRulesMixin,
                     ScriptMixin, PreFindScriptMixin,
                     PreSortScriptMixin, RelatedsSetsMixin)
from .. import fms as fms_module

FindCriteria = namedtuple('FindCriteria', 'field_name test_value op')


class FindCommand(SortRulesMixin,
                  RecordIdMixin,
                  FoundSetMixin,
                  ScriptMixin,
                  PreFindScriptMixin,
                  PreSortScriptMixin,
                  RelatedsSetsMixin,
                  BaseCommand):
    _logical_operator: Optional[str] = ...
    _lay_response: Optional[str] = ...
    _find_criteria: List[FindCriteria] = ...

    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str) \
            -> None:
        ...

    def get_query(self) -> str:
        ...

    @property
    def logical_operator(self) -> Optional[str]:
        ...

    def set_logical_operator(self, logical_operator: Optional[str]) \
            -> None:
        ...

    def set_lay_response(self, lay_response: Optional[str] = ...) \
            -> None:
        ...

    def add_find_criterion(self,
                           field_name: str,
                           test_value: Any,
                           op: Optional[str] = ...) \
            -> None:
        ...

    def clear_find_criteria(self) \
            -> None:
        ...
