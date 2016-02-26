# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import namedtuple

from .base_command import BaseCommand
from .mixins import RecordIdMixin

EditList = namedtuple('EditList', 'fqfn value')


class EditCommand(RecordIdMixin, BaseCommand):
    """Handles the *-edit* command"""
    __slots__ = ['__mod_id', '__edit_list']

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self.__mod_id = None
        self.__edit_list = []

    def get_query(self):
        assert self.record_id is not None
        command_params = super().get_command_params()

        if self.__mod_id is not None:
            command_params['-modid'] = str(self.__mod_id)

        for edit in self.__edit_list:
            command_params[edit.fqfn] = edit.value

        command_params['-edit'] = None
        return self.urlencode_query(command_params)

    @property
    def mod_id(self):
        return self.__mod_id

    def set_mod_id(self, mod_id=None):
        """
        –modid (Modification ID) query parameter

        Args:
            mod_id (int, optional): A modification id. Defaults to None which means -modid omitted.
        """
        assert mod_id is None or isinstance(mod_id, int)
        self.__mod_id = mod_id

    def add_edit(self, fqfn, value):
        self.__edit_list.append(EditList(fqfn, value))
