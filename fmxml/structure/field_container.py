#
# coding: utf-8
#
# fmxml.structure.field_container
#
from collections import Counter
from typing import Dict

from . import layout as layout_module
from . import portal as portal_module
from .field import Field


def single_field_factory(layout, field_values):
    """
    Takes::
        {field_name1: value1, field_name2: value2}
    or::
        [(field_name, value), (field_name, value), ...]

    *Lists and tuples are interchangeable here.*

    and converts to a :py:class:`.FieldContainer` instance.

    Parameters:
      layout: Layout that these fields belong to.
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
      layout: Layout that these fields belong to.
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
        """

        Args:
            layout: Can be a Layout or a Portal
            field_value_dict:
        """
        assert isinstance(layout, (layout_module.Layout, portal_module.Portal)), layout

        # for datasource date-format etc.
        self._fms = layout.fms
        self._layout = layout
        self._fields = {}
        # Calling set_field_value() will find the field properties and
        # convert them appropriately where possible.
        if field_value_dict is not None:
            for field_name in field_value_dict:
                for repetition_number in field_value_dict[field_name]:
                    value = field_value_dict[field_name][repetition_number]
                    self.set_field_value(field_name, value, repetition_number)

    def __missing__(self, key):
        value = self[key] = {}  # TODO: test & fix
        raise NotImplementedError
        # return value

    def __copy__(self):
        return self._partial_copy(*self._fields)

    def __deepcopy__(self, memo):
        # fms.__logger messes with deepcopy
        raise NotImplementedError

    @property
    def names(self):
        names = list(self._fields)
        names.sort()
        return names

    def set_field_value(self, field_name, value, repetition_number):
        assert isinstance(repetition_number, int), repetition_number
        if field_name not in self._fields:
            self._fields[field_name] = {}
        # TODO: convert here is necessary
        if repetition_number not in self._fields[field_name]:
            self._fields[field_name][repetition_number] = Field(self._layout, field_name, value)
        else:
            self._fields[field_name][repetition_number].set_value(value)

    def get_field_value(self, field_name, repetition_number=0):
        return self._fields[field_name][repetition_number].value

    def _get_field_repetition_numbers(self, field_name):
        fields = self._fields[field_name]  # type: Dict[int, Field]
        repetition_numbers = list(fields)
        repetition_numbers.sort()
        return fields, repetition_numbers

    def get_field_values(self, field_name):
        fields, repetition_numbers = self._get_field_repetition_numbers(field_name)
        return [fields[num].value for num in repetition_numbers]

    def iter_fields(self):
        for field_name in self._fields:
            fields, repetition_numbers = self._get_field_repetition_numbers(field_name)
            for num in repetition_numbers:
                field = fields[num]
                yield field.name, field.value, num

    def iter_updated_fields(self):
        for field_name in self._fields:
            fields, repetition_numbers = self._get_field_repetition_numbers(field_name)
            for num in repetition_numbers:
                field = fields[num]
                if field.is_updated():
                    yield field.name, field.value, num

    def iter_updated_fields_unmunged(self):
        for field_name in self._fields:
            fields, repetition_numbers = self._get_field_repetition_numbers(field_name)
            for num in repetition_numbers:
                field = fields[num]
                if field.is_updated():
                    yield field.name, field.unmunged_value, num

    def _partial_copy(self, *field_names):
        # extract field name(s) as a new FieldContainer, for testing.
        # {field_name: {num: value, ...}, ...}
        # If all field_names are provided then a complete copy is created.
        return FieldContainer(
            self._layout,
            {field_name: {num: self._fields[field_name][num].value
                          for num in sorted(list(self._fields[field_name]))
                          }
             for field_name in field_names
             })

    @property
    def _debug_fields(self):
        # This allows access to the internals of FieldContainer which may change.
        return self._fields

    def clear_update_flags_(self):
        for field_name in self._fields:
            for repetition_number in self._fields[field_name]:
                self._fields[field_name][repetition_number].clear_update_flag_()

    def validate(self, field_name=None):
        if field_name:
            if field_name in self._fields:
                return all(self._fields[field_name][repetition_number].validate()
                           for repetition_number in self._fields[field_name])
            else:
                return False  # Invalid field name, return False
        else:
            return all(self._fields[field_name][repetition_number].validate()
                       for field_name in self._fields
                       for repetition_number in self._fields[field_name])

    pass
    # def munge(self, field_name=None):
    #     if field_name:
    #         if field_name in self._fields:
    #             for repetition_number in self._fields[field_name]:
    #                 self._fields[field_name][repetition_number]._munge()
    #     else:
    #         for field_name in self._fields:
    #             for repetition_number in self._fields[field_name]:
    #                 self._fields[field_name][repetition_number]._munge()
