# -*- mode: python tab-width: 4 coding: utf-8 -*-
class Portal:
    __slots__ = ('__fms', '__layout', '__table_name', '__field_definition_lookup')

    def __init__(self, layout, table_name):
        self.__fms = layout.fms
        self.__layout = layout
        self.__table_name = table_name
        self.__field_definition_lookup = {}

    @property
    def fms(self):
        return self.__fms

    @property
    def layout(self):
        return self.__layout

    @property
    def table_name(self):
        return self.__table_name

    def _add_field_definition(self, field_name, field_definition):
        self.__field_definition_lookup[field_name] = field_definition

    @property
    def field_names(self):
        names = list(self.__field_definition_lookup)
        names.sort()
        return names
