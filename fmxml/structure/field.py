# -*- mode: python tab-width: 4 coding: utf-8 -*-
class Field:
    __slots__ = ('__layout', '__name', '__value', '__field_definition',)

    def __init__(self, layout, name, value=None):
        self.__layout = layout
        self.__name = name
        self.__field_definition = layout.get_field_definition(name)
        self.__value = self.__field_definition._munge_value(value)

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    def set_value(self, value):
        if value != self.__value:
            self.__value = self.__field_definition._munge_value(value)
        return value

    @property
    def unmunged_value(self):
        """
        Returns:
            A value suitable for the FileMaker field definition
            defining this field.
        """
        return self.__field_definition._unmunge_value(self.__value)

    def validate(self):
        return self.__field_definition.validate(self.__value)
