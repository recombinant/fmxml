# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import namedtuple

from .base_command import BaseCommand
from .mixins import RecordIdMixin

EditField = namedtuple('EditField', 'fqfn value')


class EditCommand(RecordIdMixin, BaseCommand):
    """
    -edit (Edit record) query command
    """
    __slots__ = ('__mod_id', '__fqfn_list', '__delete_related',)

    def __init__(self, fms, layout_name, record_id):
        super().__init__(fms, layout_name)

        # TODO: test if fqfn with record-id is Ok (record_id parameter not required?)
        assert isinstance(record_id, int)
        self.set_record_id(record_id, _oneshot=True)

        self.__mod_id = \
            self.__delete_related = None
        self.__fqfn_list = []

    def get_query(self):
        assert self.record_id is not None
        # need record_id for -delete.related
        assert self.__delete_related is None or self.record_id is not None

        command_params = super().get_command_params()

        if self.__mod_id is not None:
            command_params['-modid'] = str(self.__mod_id)

        if self.__delete_related is not None:
            command_params['-delete.related'] = self.__delete_related

        for field in self.__fqfn_list:
            command_params[field.fqfn] = field.value

        command_params['-edit'] = None
        return command_params.as_query()

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

    def set_delete_related(self, delete_related=None):
        """–delete.related (Portal records delete) query parameter

        Args:
            delete_related (str, optional): Portal record to delete
        """
        assert delete_related is None or isinstance(delete_related, str)
        self.__delete_related = delete_related

    def add_edit_fqfn(self, fqfn, value):
        """
        Fully Qualified Field Name

        *table-name::field-name(repetition-number).record-id*

        - *record-id* is only required for portal records.
        - *table-name* is only required if the field is not in the underlying
          table of the layout specified in the query string.
        - *repetition-number* is required for repeating fields.

        Just the *field-name* should be adequate for on-layout non-repeating
        fields.

        Args:
            fqfn: Fully qualified field name.
            value: Value of the field.
        """
        self.__fqfn_list.append(EditField(fqfn, value))
