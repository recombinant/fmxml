#
# coding: utf-8
#
# fmxml.commands.mixins.record_id_mixin
#
from .. import base_command as base_command_module


class RecordIdMixin(base_command_module.BaseCommand0):
    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self._record_id = None

    def get_command_params(self):
        command_params = super().get_command_params()

        if self._record_id is not None:
            command_params['-recid'] = str(self._record_id)

        return command_params

    def _get_record_id(self):
        return self._record_id

    def _set_record_id(self, record_id=None):
        """
        –recid (Record ID) query parameter

        Args:
            record_id (int, optional): A record id. Defaults to None which means all records.
        """
        assert (record_id is None
                or (isinstance(record_id, int) and record_id > 0))
        self._record_id = record_id

    record_id = property(fget=_get_record_id, fset=_set_record_id)
