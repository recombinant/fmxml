# -*- mode: python tab-width: 4 coding: utf-8 -*-


class RecordIdMixin:
    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self.__record_id = None

    def get_command_params(self):
        command_params = super().get_command_params()

        if self.__record_id is not None:
            command_params['-recid'] = str(self.__record_id)

        return command_params

    @property
    def record_id(self):
        return self.__record_id

    def set_record_id(self, record_id=None):
        """
        –recid (Record ID) query parameter

        Args:
            record_id (int, optional): A record id. Defaults to None which means all records.
        """
        assert record_id is None \
               or (isinstance(record_id, int) and record_id > 0)
        self.__record_id = record_id
