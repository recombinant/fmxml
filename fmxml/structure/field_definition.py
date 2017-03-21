# -*- mode: python tab-width: 4 coding: utf-8 -*-
import datetime
import decimal
import re

from decimal import Decimal

RESULT_TEXT = 'text'
RESULT_NUMBER = 'number'
RESULT_DATE = 'date'
RESULT_TIME = 'time'
RESULT_TIMESTAMP = 'timestamp'
RESULT_CONTAINER = 'container'
RESULT_UNKNOWN = 'unknown'

KNOWN_TYPES = {'normal', 'calculation', 'summary', 'unknown', }
KNOWN_RESULTS = {RESULT_TEXT,
                 RESULT_NUMBER,
                 RESULT_DATE,
                 RESULT_TIME,
                 RESULT_TIMESTAMP,
                 RESULT_CONTAINER,
                 RESULT_UNKNOWN, }


class FieldDefinition:
    pass
    __slots__ = (
        '__layout', '__field_name', '__portal', '__auto_entered', '__global',
        '__not_empty', '__numeric_only', '__four_digit_year', '__time_of_day',
        '__max_repetitions', '__valuelist_name',
        '__max_characters', '__type', '__result',
    )

    def __init__(self, layout, raw_field_definition, portal=None):
        # raw_field_definition is a namedtuple
        self.__layout = layout
        self.__portal = portal
        self.__valuelist_name = None

        for name in raw_field_definition.__slots__:
            value = getattr(raw_field_definition, name)
            value_bool = value == 'yes'

            if name == 'name':
                self.__field_name = value
            elif name == 'auto_enter':
                self.__auto_entered = value_bool
            elif name == 'global':
                self.__global = value_bool
            elif name == 'max_repeat':
                self.__max_repetitions = int(value)
            elif name == 'four_digit_year':
                self.__four_digit_year = value_bool
            elif name == 'not_empty':
                self.__not_empty = value_bool
            elif name == 'numeric_only':
                self.__numeric_only = value_bool
            elif name == 'time_of_day':
                self.__time_of_day = value_bool
            elif name == 'result':
                assert value in KNOWN_RESULTS, value
                self.__result = value
            elif name == 'type':
                assert value in KNOWN_TYPES, value
                self.__type = value
            elif name == 'max_characters':
                self.__max_characters = int(value) if value else 0
            else:
                raise AssertionError((name, value))

    @property
    def field_name(self):
        """
        Returns:
          str: Name of the field that this definition refers to.
        """
        return self.__field_name

    @property
    def layout(self):
        """
        Returns:
          :py:class:`.Layout`: :py:class:`.Layout` instance that contains this field.
        """
        return self.__layout

    def munge_value(self, value):
        """
        Create a suitable internal representation of the value. If it value
        does not match expected format the value is left unchanged.

        Args:
            value: Inbound variable from FileMaker.

        Returns:
            Munged variation of the variable.
        """
        if self.__type != 'normal':
            assert self.__type in KNOWN_TYPES
            return value

        if value is None and not self.__not_empty:
            return value

        if value == '' and not self.__not_empty:
            return value

        assert self.__result in KNOWN_RESULTS

        if self.__result in {RESULT_CONTAINER, RESULT_UNKNOWN, }:  # ----------
            return value
        elif self.__result == RESULT_TEXT:  # ---------------------------------
            if isinstance(value, str):
                return value
        elif self.__result == RESULT_NUMBER:  # -------------------------------
            if isinstance(value, (int, float, Decimal)):
                return value
            elif isinstance(value, str):
                if re.match(r'\A[+-]?[1-9][0-9]*\Z', value):
                    return int(value)
                try:
                    return Decimal(value)
                except decimal.InvalidOperation:
                    pass
            self.layout.fms.log.warn('Unexpected NUMBER value for field: {}, {!r}'
                                     .format(self.__field_name, value))
            return value
        elif self.__result == RESULT_DATE:  # ---------------------------------
            assert not self.__time_of_day
            # assert self.__four_digit_year
            assert self.__layout.date_format == 'MM/dd/yyyy'

            if isinstance(value, (datetime.date, datetime.datetime)):
                return value
            elif isinstance(value, str):
                try:
                    return datetime.datetime.strptime(value, '%m/%d/%Y').date()
                except ValueError:
                    pass
            self.layout.fms.log.warn('Unexpected DATE value for field: {}, {!r}'
                                     .format(self.__field_name, value))
            return value
        elif self.__result == RESULT_TIME:  # ---------------------------------
            assert self.__layout.time_format == 'HH:mm:ss'
            if isinstance(value, (datetime.time, datetime.datetime)):
                return value
            elif isinstance(value, str):
                try:
                    return datetime.datetime.strptime(value, '%H:%M:%S').time()
                except ValueError:
                    pass
            self.layout.fms.log.warn('Unexpected TIME value for field: {}, {!r}'
                                     .format(self.__field_name, value))
            return value
        elif self.__result == RESULT_TIMESTAMP:  # ----------------------------
            assert self.__layout.timestamp_format == 'MM/dd/yyyy HH:mm:ss'
            if isinstance(value, datetime.datetime):
                return value
            elif isinstance(value, str):
                try:
                    return datetime.datetime.strptime(value, '%m/%d/%Y %H:%M:%S')
                except ValueError:
                    pass
            self.layout.fms.log.warn('Unexpected TIMESTAMP value for field: {}, {!r}'
                                     .format(self.__field_name, value))
            return value

    def set_valuelist_name_(self, valuelist_name):
        assert valuelist_name
        assert isinstance(valuelist_name, str)
        assert self.__valuelist_name is None or self.__valuelist_name == valuelist_name
        self.__valuelist_name = valuelist_name

    def get_valuelist(self):
        if self.__valuelist_name is None:
            return None
        else:
            return self.__layout.get_valuelist(self.__valuelist_name)
