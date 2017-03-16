# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import Counter


def single_field_factory(layout, field_values):
    """
    Takes::
        {field_name1: value1, field_name2: value2}
    or::
        [(field_name, value), (field_name, value), ...]

    *Lists and tuples are interchangeable here.*

    and converts to a :py:class:`.FieldContainer` instance.

    Parameters:
      layout (Layout): Layout that these fields belong to.
      field_values: Sequence of field names and multiple values.
    Returns:
      :py:class:`.FieldContainer`: A :py:class:`.FieldContainer` instance
        containing a representation of `field_values`

    See also: :py:func:`.repetition_field_factory`
    """
    if isinstance(field_values, dict):
        field_values = list(field_values.items())

    field_value_dict = dict()
    for field_name, field_value in field_values:
        # repetition number 1
        field_value_dict[field_name] = {0: field_value}

    return FieldContainer(layout, field_value_dict)


def repetition_field_factory(layout, field_values):
    """
    Much like :py:func:`.single_field_factory` but allows for repetition of fields -
    though they do not have to be repeated.


    Takes::

        {field_name: [value, value, ...], field_name: [value, ...]}

    or::

        [(field_name1, [value, value, ...]), (field_name2, [value, ...]), ...]

    *Lists and tuples are interchangeable here.*

    and converts to a :py:class:`.FieldContainer` instance.

    Parameters:
      layout (Layout): Layout that these fields belong to.
      field_values: Sequence of field names and multiple values.

    Returns:
      :py:class:`.FieldContainer`: A :py:class:`.FieldContainer` instance
        containing a representation of `field_values`
    """
    # TODO: update doc with suitable for..
    if isinstance(field_values, dict):
        field_values = list(field_values.items())

    field_value_dict = dict()
    for field_name, field_value_sequence in field_values:
        field_value_dict[field_name] = {
            repetition_number: field_value
            for repetition_number, field_value in enumerate(field_value_sequence)
            }
    return FieldContainer(layout, field_value_dict)


def _raw_record_field_factory(layout, raw_records):
    """
    For internal use only. Used when parsing the fmresultset grammar.

    Args:
        layout: Layout that these records belong to.
        raw_records: A list of raw records from :py:class:`.DataGrammarParser`

    Returns:
      :py:class:`.FieldContainer`: A :py:class:`.FieldContainer` instance
        containing a representation of `raw_records`
    """
    # get the raw records and turn them into a list of tuples
    # [((name, (data, ...)), (name, (data, ...)), ...]
    fields = []
    for record in raw_records:
        field_name = record.name
        record_data = []
        for data in record.data:
            record_data.append(data)
        fields.append((field_name, tuple(record_data)))
    # most common returns something like [('Description', 1)]
    fields = set(fields)
    assert not fields or Counter(field[0] for field in fields).most_common(1)[0][1] == 1, (
        Counter(field[0] for field in fields).most_common(1)[0][0])

    field_value_dict = dict()
    for field_name, field_value_sequence in fields:
        field_value_dict[field_name] = {
            repetition_number: field_value
            for repetition_number, field_value in enumerate(field_value_sequence)
            }
    return FieldContainer(layout, field_value_dict)


class FieldContainer:
    def __init__(self, layout, field_value_dict=None):
        from .layout import Layout
        from .portal import Portal

        assert isinstance(layout, (Layout, Portal)), layout

        self.__fm = layout.fms  # for datasource date-format etc.
        self.__layout = layout
        self.__fields = {}
        # Calling set_field_value() will find the field properties and
        # convert them appropriately where possible.
        if field_value_dict is not None:
            for field_name in field_value_dict:
                for repetition_number in field_value_dict[field_name]:
                    value = field_value_dict[field_name][repetition_number]
                    self.set_field_value(field_name, value, repetition_number)

    def __missing__(self, key):
        value = self[key] = {}  # TODO: test & fix
        return value

    def __copy__(self):
        return self._partial_copy(*self.__fields)

    def __deepcopy__(self, memo):
        # fms.__logger messes with deepcopy
        raise NotImplementedError

    @property
    def names(self):
        names = list(self.__fields)
        names.sort()
        return names

    def set_field_value(self, field_name, value, repetition_number):
        from .field import Field
        assert isinstance(repetition_number, int), repetition_number
        if field_name not in self.__fields:
            self.__fields[field_name] = {}
        # TODO: convert here is necessary
        if repetition_number not in self.__fields[field_name]:
            self.__fields[field_name][repetition_number] = Field(self.__layout, field_name, value)
        else:
            self.__fields[field_name][repetition_number].set_value(value)

    def get_field_value(self, field_name, repetition_number=0):
        return self.__fields[field_name][repetition_number].value

    def get_field_repetitions(self, field_name):
        """

        Args:
            field_name:

        Returns:
            list: All of the values for field_name
        """
        return [
            (repetition_number, self.__fields[field_name][repetition_number].value)
            for repetition_number in sorted(list(self.__fields[field_name]))
            ]

    def iter_fields(self):
        for field_name in self.__fields:
            for repetition_number in sorted(list(self.__fields[field_name])):
                field = self.__fields[field_name][repetition_number]
                yield field.name, field.value, repetition_number

    def iter_updated_fields(self):
        for field_name in self.__fields:
            for repetition_number in sorted(list(self.__fields[field_name])):
                field = self.__fields[field_name][repetition_number]
                if field.is_updated():
                    yield field.name, field.value, repetition_number

    def iter_updated_fields_unmunged(self):
        for field_name in self.__fields:
            for repetition_number in sorted(list(self.__fields[field_name])):
                field = self.__fields[field_name][repetition_number]
                if field.is_updated():
                    yield field.name, field.unmunged_value, repetition_number

    def _partial_copy(self, *field_names):
        # extract field name(s) as a new FieldContainer, for testing.
        # {field_name: {repetition_number: value, ...}, ...}
        # If all field_names are provided then a complete copy is created.
        return FieldContainer(
            self.__layout,
            {field_name:
                 {repetition_number: self.__fields[field_name][repetition_number].value
                  for repetition_number in sorted(list(self.__fields[field_name]))}
             for field_name in field_names
             })

    @property
    def _debug_fields(self):
        # This allows access to the internals of FieldContainer which may change.
        return self.__fields

    def _clear_update_flags(self):
        for field_name in self.__fields:
            for repetition_number in self.__fields[field_name]:
                self.__fields[field_name][repetition_number]._clear_update_flag()

    def validate(self, field_name=None):
        if field_name:
            if field_name in self.__fields:
                return all(self.__fields[field_name][repetition_number].validate()
                           for repetition_number in self.__fields[field_name])
            else:
                return False  # Invalid field name, return False
        else:
            return all(self.__fields[field_name][repetition_number].validate()
                       for field_name in self.__fields
                       for repetition_number in self.__fields[field_name])

    pass
    # def munge(self, field_name=None):
    #     if field_name:
    #         if field_name in self.__fields:
    #             for repetition_number in self.__fields[field_name]:
    #                 self.__fields[field_name][repetition_number]._munge()
    #     else:
    #         for field_name in self.__fields:
    #             for repetition_number in self.__fields[field_name]:
    #                 self.__fields[field_name][repetition_number]._munge()
