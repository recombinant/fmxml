# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import namedtuple

from .base_command import BaseCommand

NewField = namedtuple('NewField', 'fqfn value')


class NewCommand(BaseCommand):
    """
    –new (New record) query command
    """
    __slots__ = ['__field_list', ]

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self.__field_list = []

    def get_query(self):
        command_params = super().get_command_params()

        for field in self.__field_list:
            command_params[field.fqfn] = field.value

        command_params['-new'] = None
        return self.urlencode_query(command_params)

    def add_new_field(self, fqfn, value):
        self.__field_list.append(NewField(fqfn, value))
