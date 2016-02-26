# -*- mode: python tab-width: 4 coding: utf-8 -*-
from .base_command import BaseCommand
from .mixins import RecordIdMixin, ScriptMixin


class DeleteCommand(RecordIdMixin, ScriptMixin, BaseCommand):
    """
    –delete (Delete record) query command
    """
    __slots__ = []

    def __init__(self, fms, layout_name, record_id):
        super().__init__(fms, layout_name)

        assert isinstance(record_id, int)
        self.set_record_id(record_id, _oneshot=True)

    def get_query(self):
        assert self.record_id is not None

        command_params = super().get_command_params()

        command_params['-delete'] = None
        return self.urlencode_query(command_params)
