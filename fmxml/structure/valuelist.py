# -*- mode: python tab-width: 4 coding: utf-8 -*-
import collections
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
    __slots__ = ('__name', '__type', '__valuelist')

    def __init__(self, name, raw_values):
        self.__name = name

        # this is good estimate at the type of value list
        if all(raw_value.display == raw_value.text for raw_value in raw_values):
            self.__type = ValuelistDisplayEnum.VALUELIST_FIRST
        elif all(raw_value.display.startswith('{} '.format(raw_value.text))
                 for raw_value in raw_values):
            self.__type = ValuelistDisplayEnum.VALUELIST_BOTH
        else:
            self.__type = ValuelistDisplayEnum.VALUELIST_SECOND

        self.__valuelist = [
            ValueTuple(display=raw_value.display, text=raw_value.text)
            for raw_value in raw_values
            ]

    @property
    def name(self):
        return self.__name

    def __getitem__(self, item):
        return self.__valuelist[item]

    def __len__(self):
        return len(self.__valuelist)

    def __iter__(self):
        return iter(self.__valuelist)

    def __repr__(self):
        return 'Valuelist(name={}, valuelist_display={}, valuelist={})' \
            .format(repr(self.__name),
                    self.__display,
                    repr(self.__valuelist))

    # The following do not make any sense in the context of a value list.
    def __contains__(self, item):
        raise NotImplementedError

    def __reversed__(self):
        raise NotImplementedError

    def count(self, value):
        raise NotImplementedError
