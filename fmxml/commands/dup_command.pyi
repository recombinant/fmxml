#
# coding: utf-8
#
# Stubs for fmxml.commands.dup_command
#
from typing import Optional

from . import base_command as base_command_module
from .mixins import record_id_mixin as record_id_mixin_module
from .. import fms as fms_module


class DupCommand(record_id_mixin_module.RecordIdMixin,
                 base_command_module.BaseCommand):
    def __init__(self,
                 fms: fms_module.FileMakerServer,
                 layout_name: str,
                 record_id: Optional[int] = ...) \
            -> None:
        ...

    def get_query(self) -> str:
        ...
