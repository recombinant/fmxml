# -*- mode: python tab-width: 4 coding: utf-8 -*-
import datetime
from collections import namedtuple

from decimal import Decimal

from .base_command import BaseCommand

NewField = namedtuple('NewField', 'fqfn value')


class NewCommand(BaseCommand):
    """
    –new (New record) query command
    """
    __slots__ = ('__fqfn_list',)

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self.__fqfn_list = []

    def get_query(self):
        command_params = super().get_command_params()

        for field in self.__fqfn_list:
            command_params[field.fqfn] = field.value

        command_params['-new'] = None
        return command_params.as_query()

    def add_new_fqfn(self, fqfn, value):
        """
        Fully Qualified Field Name

        *table-name::field-name(repetition-number).record-id*

        Args:
            fqfn: Fully qualified field name.
            value: Value of the field.
        """
        self.__fqfn_list.append(NewField(fqfn, value))

    def set_field_value(self, field_name, value, repetition=0):
        assert isinstance(field_name, str)
        assert isinstance(value, (int, str, Decimal, datetime.date)), type(value)
        assert isinstance(repetition, int)

        if isinstance(value, datetime.date):
            value = value.strftime('%m/%d/%Y')

        fqfn = '{}({})'.format(field_name, repetition)
        self.add_new_fqfn(fqfn, value)
