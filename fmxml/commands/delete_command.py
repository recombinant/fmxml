# -*- mode: python tab-width: 4 coding: utf-8 -*-
from .base_command import BaseCommand
from .mixins import RecordIdMixin, ScriptsMixin


class DeleteCommand(RecordIdMixin, ScriptsMixin, BaseCommand):
    """
    –delete (Delete record) query command
    """
    __slots__ = ()

    def __init__(self, fms, layout_name, record_id):
        super().__init__(fms, layout_name)
        self.set_record_id(record_id)

    def get_query(self):
        assert self.record_id is not None

        command_params = super().get_command_params()
        command_params['-delete'] = None
        return command_params.as_query()
