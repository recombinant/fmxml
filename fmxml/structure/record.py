# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import defaultdict
from copy import copy
from typing import List, Any, Optional

from . import field_container as fc_module
from . import layout as layout_module


class Record:
    __slots__ = ('__fms',
                 '__layout',
                 '__record_id',
                 '__modification_id',
                 '__field_container',
                 '__portal_records',
                 '__parent_record',
                 '__portal_name',)

    def __init__(self,
                 layout: 'layout_module.Layout',
                 field_container: 'fc_module.FieldContainer' = None):
        assert layout
        assert isinstance(layout, layout_module.Layout)

        self.__layout = layout  # type: layout_module.Layout
        self.__fms = layout.fms
        self.__record_id = None
        self.__modification_id = None
        self.__portal_records = defaultdict(list)
        self.__parent_record = None
        self.__portal_name: str = None

        if field_container is None:
            self.__field_container = fc_module.FieldContainer(layout)  # type: fc_module.FieldContainer
        else:
            self.__field_container: fc_module.FieldContainer = copy(field_container)  # type: fc_module.FieldContainer

    @property
    def layout(self) -> layout_module.Layout:
        return self.__layout

    @property
    def record_id(self):
        return self.__record_id

    @property
    def modification_id(self):
        return self.__modification_id

    @property
    def field_names(self):
        return self.__layout.field_names

    def set_record_id_(self, record_id):
        assert isinstance(record_id, int)
        self.__record_id = record_id

    def set_modification_id(self, modification_id):
        assert isinstance(modification_id, int)
        self.__modification_id = modification_id

    @property
    def portal_table_names(self):
        return list(self.__portal_records)

    def add_portal_record_(self, table_name, portal_record):
        self.__portal_records[table_name].append(portal_record)
        portal_record.__portal_name = table_name
        portal_record.__parent_record = self

    @property
    def parent(self) -> Optional['Record']:
        return self.__parent_record

    def get_field_value(self, field_name: str, repetition_number: int = 0) -> Any:
        return self.__field_container.get_field_value(field_name, repetition_number)

    def get_field_values(self, field_name: str) -> List[Any]:
        return self.__field_container.get_field_values(field_name)

    def delete(self):
        assert self.__record_id

        if self.__parent_record:
            # Page 45 Deleting portal records.
            # TODO: test
            command_object = self.__fms.create_edit_command(
                self.__parent_record.layout.name,
                self.__parent_record.record_id)
            command_object.set_delete_portal(self.__layout.name + '.' + self.__record_id)
            return command_object.execute()
        else:
            command_object = self.__fms.create_delete_record_command(
                self.__layout.name,
                self.__record_id)
            return command_object.execute()

    def duplicate(self):
        assert self.__record_id

        command_object = self.__fms.create_dup_record_command(
            self.__layout.name,
            self.__record_id)
        command_result = command_object.execute()

        assert command_result.records

        record = command_result.records[0]

        assert isinstance(record, Record)
        return record
