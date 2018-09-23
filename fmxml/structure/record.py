#
# coding: utf-8
#
# fmxml.structure.record
#
from collections import defaultdict
from copy import copy

from . import field_container as field_container_module
from . import layout as layout_module


class Record:
    __slots__ = ('_fms',
                 '_layout',
                 '_record_id',
                 '_modification_id',
                 '_field_container',
                 '_portal_records',
                 '_parent_record',
                 '_portal_name',)

    def __init__(self,
                 layout,
                 field_container=None):
        assert layout
        assert isinstance(layout, layout_module.Layout)

        self._layout = layout
        self._fms = layout.fms
        self._record_id = None
        self._modification_id = None
        self._portal_records = defaultdict(list)
        self._parent_record = None
        self._portal_name = None

        if field_container is None:
            self._field_container = field_container_module.FieldContainer(layout)
        else:
            self._field_container = copy(field_container)

    @property
    def layout(self):
        return self._layout

    @property
    def field_names(self):
        return self._layout.field_names

    # -------------

    def _get_modification_id(self):
        return self._modification_id

    def _set_modification_id(self, modification_id):
        assert isinstance(modification_id, int)
        self._modification_id = modification_id

    modification_id = property(fget=_get_modification_id, fset=_set_modification_id)

    # -------------

    def _get_record_id(self):
        return self._record_id

    def _set_record_id(self, record_id):
        self._record_id = record_id

    record_id = property(fget=_get_record_id, fset=_set_record_id)

    # -------------

    @property
    def portal_table_names(self):
        return list(self._portal_records)

    def add_portal_record_(self, table_name, portal_record):
        self._portal_records[table_name].append(portal_record)
        portal_record._portal_name = table_name
        portal_record._parent_record = self

    @property
    def parent(self):
        return self._parent_record

    def get_field_value(self, field_name, repetition_number=0):
        return self._field_container.get_field_value(field_name, repetition_number)

    def get_field_values(self, field_name):
        return self._field_container.get_field_values(field_name)

    def delete(self):
        assert self._record_id

        if self._parent_record:
            # Page 45 Deleting portal records.
            # TODO: test
            command_object = self._fms.create_edit_command(
                self._parent_record.layout.name,
                self._parent_record.record_id)
            command_object.set_delete_portal(f'{self._layout.name}.{self._record_id}')
            return command_object.execute()
        else:
            command_object = self._fms.create_delete_record_command(
                self._layout.name,
                self._record_id)
            return command_object.execute()

    def duplicate(self):
        assert self._record_id

        command_object = self._fms.create_dup_record_command(
            self._layout.name,
            self._record_id)
        command_result = command_object.execute()

        assert command_result.records

        record = command_result.records[0]

        assert isinstance(record, Record)
        return record
