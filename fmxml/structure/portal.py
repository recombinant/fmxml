#
# coding: utf-8
#
# fmxml.structure.portal
#


class Portal:
    __slots__ = ('_fms', '_layout', '_table_name', '_field_definition_lookup')

    def __init__(self, layout, table_name):
        self._fms = layout.fms
        self._layout = layout
        self._table_name = table_name
        self._field_definition_lookup = {}

    @property
    def fms(self):
        return self._fms

    @property
    def layout(self):
        return self._layout

    @property
    def table_name(self):
        return self._table_name

    def add_field_definition_(self, field_name, field_definition):
        self._field_definition_lookup[field_name] = field_definition

    @property
    def field_names(self):
        names = list(self._field_definition_lookup)
        names.sort()
        return names
