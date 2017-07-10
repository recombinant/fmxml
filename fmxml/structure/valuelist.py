#
# coding: utf-8
#
# fmxml.structure.valuelist
#
import collections.abc
from collections import namedtuple
from enum import Enum

ValueTuple = namedtuple('ValueTuple', 'display text')


class ValuelistDisplayEnum(Enum):
    # "Also display values from second field" is not selected
    VALUELIST_FIRST = 1

    # "Also display values from second field"
    # "Show values only from second field" are both selected
    VALUELIST_BOTH = 2

    # "Also display values from second field" is selected
    # "Show values only from second" field is not selected
    VALUELIST_SECOND = 3


class Valuelist(collections.abc.Sequence):
    __slots__ = ('_name', '_type', '_valuelist')

    def __init__(self, name, raw_values):
        self._name = name

        # this is good estimate at the type of value list
        if all(raw_value.display == raw_value.text for raw_value in raw_values):
            self._type = ValuelistDisplayEnum.VALUELIST_FIRST
        elif all(raw_value.display.startswith(f'{raw_value.text} ')
                 for raw_value in raw_values):
            self._type = ValuelistDisplayEnum.VALUELIST_BOTH
        else:
            self._type = ValuelistDisplayEnum.VALUELIST_SECOND

        self._valuelist = [
            ValueTuple(display=raw_value.display, text=raw_value.text)
            for raw_value in raw_values
        ]

    @property
    def name(self):
        return self._name

    def __getitem__(self, item):
        return self._valuelist[item]

    def __len__(self):
        return len(self._valuelist)

    def __iter__(self):
        return iter(self._valuelist)

    def __repr__(self):
        return f'Valuelist(name={self._name!r}, valuelist={self._valuelist!r})'

    # The following do not make any sense in the context of a value list.
    def __contains__(self, item):
        raise NotImplementedError

    def __reversed__(self):
        raise NotImplementedError

    def count(self, value):
        raise NotImplementedError
