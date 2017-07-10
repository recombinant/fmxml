#
# coding: utf-8
#
# fmxml.commands.delete_command
#
from .base_command import BaseCommand
from .mixins import RecordIdMixin, ScriptMixin


class DeleteCommand(RecordIdMixin, ScriptMixin, BaseCommand):
    """
    –delete (Delete record) query command
    """

    def __init__(self, fms, layout_name, record_id):
        super().__init__(fms, layout_name)
        self.record_id = record_id  # property in RecordIdMixin

    def get_query(self):
        assert self.record_id is not None

        command_params = super().get_command_params()
        command_params['-delete'] = None
        return command_params.as_query()
