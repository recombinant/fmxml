# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import namedtuple

from .base_command import BaseCommand

NewField = namedtuple('NewField', 'fqfn value')


class NewCommand(BaseCommand):
    """
    –new (New record) query command
    """
    __slots__ = ['__fqfn_list', ]

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self.__fqfn_list = []

    def get_query(self):
        command_params = super().get_command_params()

        for field in self.__fqfn_list:
            command_params[field.fqfn] = field.value

        command_params['-new'] = None
        return self.urlencode_query(command_params)

    def add_new_fqfn(self, fqfn, value):
        """
        Fully Qualified Field Name

        *table-name::field-name(repetition-number).record-id*

        Args:
            fqfn: Fully qualified field name.
            value: Value of the field.
        """
        self.__fqfn_list.append(NewField(fqfn, value))
