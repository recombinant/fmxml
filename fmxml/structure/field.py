#
# coding: utf-8
#
# fmxml.structure.field
#


class Field:
    __slots__ = ('_layout', '_name', '_value', '_field_definition',)

    def __init__(self, layout, name, value=None):
        self._layout = layout
        self._name = name
        self._field_definition = layout.get_field_definition(name)
        self._value = self._field_definition.munge_value(value)

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    def set_value(self, value):
        if value != self._value:
            self._value = self._field_definition.munge_value(value)
        return value

    @property
    def unmunged_value(self):
        """
        Returns:
            A value suitable for the FileMaker field definition
            defining this field.
        """
        return self._field_definition.unmunge_value(self._value)

    def validate(self):
        return self._field_definition.validate(self._value)

    def is_updated(self):
        raise NotImplementedError  # TODO: refactor to make this work

    def clear_update_flag_(self):
        raise NotImplementedError  # TODO: refactor to make this work
