#
# coding: utf-8
#
# Stubs for fmxml.commands.findany_command
#
from . import base_command as base_command_module
from .mixins import relatedsets_mixin as relatedsets_mixin_module


class FindAnyCommand(relatedsets_mixin_module.RelatedsSetsMixin,
                     base_command_module.BaseCommand):
    def get_query(self) -> str:
        ...
