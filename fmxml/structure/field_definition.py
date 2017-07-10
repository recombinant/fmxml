#
# coding: utf-8
#
# fmxml.structure.field_definition
#
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
    __slots__ = (
        '_layout', '_field_name', '_portal', '_auto_entered', '_global',
        '_not_empty', '_numeric_only', '_four_digit_year', '_time_of_day',
        '_max_repetitions', '_valuelist_name',
        '_max_characters', '_type', '_result',
    )

    def __init__(self, layout, raw_field_definition, portal=None):
        # raw_field_definition is a namedtuple
        self._layout = layout
        self._portal = portal
        self._valuelist_name = None

        for name in iter(raw_field_definition.__slots__):
            value = getattr(raw_field_definition, name)
            value_bool = value == 'yes'

            if name == 'name':
                self._field_name = value
            elif name == 'auto_enter':
                self._auto_entered = value_bool
            elif name == 'global':
                self._global = value_bool
            elif name == 'max_repeat':
                self._max_repetitions = int(value)
            elif name == 'four_digit_year':
                self._four_digit_year = value_bool
            elif name == 'not_empty':
                self._not_empty = value_bool
            elif name == 'numeric_only':
                self._numeric_only = value_bool
            elif name == 'time_of_day':
                self._time_of_day = value_bool
            elif name == 'result':
                assert value in KNOWN_RESULTS, value
                self._result = value
            elif name == 'type':
                assert value in KNOWN_TYPES, value
                self._type = value
            elif name == 'max_characters':
                self._max_characters = int(value) if value else 0
            else:
                raise AssertionError((name, value))

    @property
    def field_name(self):
        """
        Returns:
          Name of the field that this definition refers to.
        """
        return self._field_name

    @property
    def layout(self):
        """
        Returns:
          :py:class:`.Layout`: :py:class:`.Layout` instance that contains this field.
        """
        return self._layout

    def munge_value(self, value):
        """
        Create a suitable internal representation of the value. If it value
        does not match expected format the value is left unchanged.

        Args:
            value: Inbound variable from FileMaker.

        Returns:
            Munged variation of the variable.
        """
        if self._type != 'normal':
            assert self._type in KNOWN_TYPES
            return value

        if value is None and not self._not_empty:
            return value

        if value == '' and not self._not_empty:
            return value

        assert self._result in KNOWN_RESULTS

        if self._result in {RESULT_CONTAINER, RESULT_UNKNOWN, }:  # ----------
            return value
        elif self._result == RESULT_TEXT:  # ---------------------------------
            if isinstance(value, str):
                return value
        elif self._result == RESULT_NUMBER:  # -------------------------------
            if isinstance(value, (int, float, Decimal)):
                return value
            elif isinstance(value, str):
                if re.match(r'\A[+-]?[1-9][0-9]*\Z', value):
                    return int(value)
                try:
                    return Decimal(value)
                except decimal.InvalidOperation:
                    pass
            self.layout.fms.log.warning('Unexpected NUMBER value for field: {}, {!r}'
                                        .format(self._field_name, value))
            return value
        elif self._result == RESULT_DATE:  # ---------------------------------
            assert not self._time_of_day
            # assert self._four_digit_year
            assert self._layout.date_format == 'MM/dd/yyyy'

            if isinstance(value, (datetime.date, datetime.datetime)):
                return value
            elif isinstance(value, str):
                try:
                    return datetime.datetime.strptime(value, '%m/%d/%Y').date()
                except ValueError:
                    pass
            self.layout.fms.log.warning('Unexpected DATE value for field: {}, {!r}'
                                        .format(self._field_name, value))
            return value
        elif self._result == RESULT_TIME:  # ---------------------------------
            assert self._layout.time_format == 'HH:mm:ss'
            if isinstance(value, (datetime.time, datetime.datetime)):
                return value
            elif isinstance(value, str):
                try:
                    return datetime.datetime.strptime(value, '%H:%M:%S').time()
                except ValueError:
                    pass
            self.layout.fms.log.warning('Unexpected TIME value for field: {}, {!r}'
                                        .format(self._field_name, value))
            return value
        elif self._result == RESULT_TIMESTAMP:  # ----------------------------
            assert self._layout.timestamp_format == 'MM/dd/yyyy HH:mm:ss'
            if isinstance(value, datetime.datetime):
                return value
            elif isinstance(value, str):
                try:
                    return datetime.datetime.strptime(value, '%m/%d/%Y %H:%M:%S')
                except ValueError:
                    pass
            self.layout.fms.log.warning('Unexpected TIMESTAMP value for field: {}, {!r}'
                                        .format(self._field_name, value))
            return value

    def set_valuelist_name_(self, valuelist_name):
        assert valuelist_name
        assert isinstance(valuelist_name, str)
        assert self._valuelist_name is None or self._valuelist_name == valuelist_name
        self._valuelist_name = valuelist_name

    def get_valuelist(self):
        if self._valuelist_name is None:
            return None
        else:
            return self._layout.get_valuelist(self._valuelist_name)
