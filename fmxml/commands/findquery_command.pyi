#
# coding: utf-8
#
# Stubs for fmxml.commands.findquery_command
#
from typing import NamedTuple, List

from . import base_command as base_command_module
from .mixins import foundset_mixin as foundset_mixin_module
from .mixins import script_mixin as script_mixin_module
from .mixins import sort_rules_mixin as sort_rules_mixin_module
from .. import fms as fms_module


class FindQuery(NamedTuple):
    field_name: str
    test_value: str


class FindRequestDefinition:
    queries: List[FindQuery] = ...
    omit: bool = ...

    def __init__(self,
                 queries: List[FindQuery],
                 omit: bool = ...) \
            -> None:
        ...


class FindQueryCommand(foundset_mixin_module.FoundSetMixin,
                       sort_rules_mixin_module.SortRulesMixin,
                       script_mixin_module.ScriptMixin,
                       script_mixin_module.PreFindScriptMixin,
                       script_mixin_module.PreSortScriptMixin,
                       base_command_module.BaseCommand):
    _request_definitions: List[FindRequestDefinition] = ...

    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str) \
            -> None:
        ...

    def get_query(self) -> str:
        ...

    def add_request_definitions(self,
                                request_definition1: FindRequestDefinition,
                                request_definition2: FindRequestDefinition,
                                *args: FindRequestDefinition) \
            -> None:
        ...
