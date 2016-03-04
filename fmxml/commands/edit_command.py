# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import namedtuple

from .base_command import BaseCommand
from .mixins import RecordIdMixin

EditField = namedtuple('EditField', 'fqfn value')


# TODO: delete.related portal records
class EditCommand(RecordIdMixin, BaseCommand):
    """
    -edit (Edit record) query command
    """
    __slots__ = ('__modification_id', '__fqfn_list', '__delete_related',)

    def __init__(self, fms, layout_name, record_id=None, modification_id=None):
        assert modification_id is None or isinstance(modification_id, int)

        super().__init__(fms, layout_name)

        self.__delete_related = None
        self.__fqfn_list = []

        # TODO: test if fqfn with record-id is Ok (record_id parameter not required?)
        self.set_record_id(record_id)
        self.set_modification_id(modification_id)

    def get_query(self):
        assert self.record_id is not None
        # need record_id for -delete.related
        assert self.__delete_related is None or self.record_id is not None

        command_params = super().get_command_params()

        if self.__modification_id is not None:
            command_params['-modid'] = str(self.__modification_id)

        if self.__delete_related is not None:
            command_params['-delete.related'] = self.__delete_related

        for field in self.__fqfn_list:
            command_params[field.fqfn] = field.value

        command_params['-edit'] = None
        return command_params.as_query()

    @property
    def modification_id(self):
        return self.__modification_id

    def set_modification_id(self, modification_id=None):
        """
        –modid (Modification ID) query parameter

        Args:
            modification_id (int, optional): A modification id. Defaults to None which means -modid omitted.
        """
        assert modification_id is None or \
               (isinstance(modification_id, int) and modification_id > 0)
        self.__modification_id = modification_id

    def set_delete_related(self, delete_related=None):
        """
        –delete.related (Portal records delete) query parameter

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
            fqfn (str): Fully qualified field name.
            value: Value of the field.
        """
        self.__fqfn_list.append(EditField(fqfn, value))
