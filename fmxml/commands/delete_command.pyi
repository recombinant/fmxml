#
# coding: utf-8
#
# Stubs for fmxml.commands.delete_command
#
from . import base_command as base_command_module
from .mixins import record_id_mixin as record_id_mixin_module
from .mixins import script_mixin as script_mixin_module
from .. import fms as fms_module


class DeleteCommand(record_id_mixin_module.RecordIdMixin,
                    script_mixin_module.ScriptMixin,
                    base_command_module.BaseCommand):
    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str,
                 record_id: int) \
            -> None:
        ...

    def get_query(self) -> str:
        ...
