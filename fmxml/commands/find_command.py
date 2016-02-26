# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import namedtuple, OrderedDict

from .base_command import BaseCommand
from .mixins import RecordIdMixin, ScriptMixin, PreFindScriptMixin, PreSortScriptMixin
from ..fms import FMS_FIND_AND, FMS_FIND_OR
from ..fms import \
    FMS_FIND_OP_EQ, FMS_FIND_OP_NEQ, \
    FMS_FIND_OP_GT, FMS_FIND_OP_GTE, \
    FMS_FIND_OP_LT, FMS_FIND_OP_LTE, \
    FMS_FIND_OP_CN, \
    FMS_FIND_OP_BW, FMS_FIND_OP_EW
from ..fms import FMS_SORT_DESCEND, FMS_SORT_ASCEND

FindCriteria = namedtuple('FindCriteria', 'field_name test_value op')
SortOrder = namedtuple('SortOrder', 'precedence order')


class FindCommand(RecordIdMixin,
                  ScriptMixin,
                  PreFindScriptMixin,
                  PreSortScriptMixin,
                  BaseCommand):
    """
    –find or –findall (Find records) query commands

    Automatically selects *-find* or *-findall* as appropriate.
    """
    __slots__ = ['__logical_operator',
                 '__skip', '__max',
                 '__lay_response',
                 '__sort_fields', '__find_criteria', ]

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)

        self.__max = \
            self.__logical_operator = \
            self.__lay_response = None
        self.__skip = 0
        self.__find_criteria = []  # list of FindCriteria
        self.__sort_fields = OrderedDict()

    def get_query(self):
        command_params = super().get_command_params()

        if self.__logical_operator is not None:
            command_params['-lop'] = self.__logical_operator
        if self.__skip:
            command_params['-skip'] = self.__skip
        if self.__max is not None:
            command_params['-max'] = self.__max
        if self.__lay_response is not None:
            command_params['-lay.response'] = self.__lay_response

        for field_name, test_value, op in self.__find_criteria:
            command_params[field_name] = test_value
            if op is not None:
                assert op in {
                    FMS_FIND_OP_GT, FMS_FIND_OP_GTE,
                    FMS_FIND_OP_LT, FMS_FIND_OP_LTE,
                    FMS_FIND_OP_EQ, FMS_FIND_OP_NEQ,
                    FMS_FIND_OP_BW, FMS_FIND_OP_EW,
                    FMS_FIND_OP_CN,
                }
                param = '{}.op'.format(field_name)
                command_params[param] = op

        sort_precedence = {}
        for field_name in self.__sort_fields:
            precedence = self.__sort_fields[field_name].precedence
            order = self.__sort_fields[field_name].order
            sort_precedence[precedence] = (field_name, order)
        for precedence in sorted(list(sort_precedence)):
            field_name, order = sort_precedence[precedence]
            command_params['-sortfield.{}'.format(precedence)] = field_name
            if order is not None:
                command_params['-sortorder.{}'.format(precedence)] = order

        if self.record_id is None and not self.__find_criteria:
            command_params['-findall'] = None
        else:
            command_params['-find'] = None

        return self.urlencode_query(command_params)

    @property
    def skip(self):
        return self.__skip

    def set_skip(self, skip=0):
        """–skip (Skip records) query parameter

        Args:
            skip (int): Specifies how many records to skip in the found set. Defaults to zero.
        """
        assert isinstance(skip, int) and skip >= 0
        self.__skip = skip

    @property
    def max(self):
        return self.__max

    def set_max(self, max_=None):
        """–max (Maximum records) query parameter

        Args:
            max_ (int, str, optional): Maximum number of records to return. Defaults to all.
        """
        assert max_ is None or max_ == 'all' or (isinstance(max_, int) and max_ >= 0)
        self.__max = max_

    @property
    def logical_operator(self):
        return self.__logical_operator

    def set_logical_operator(self, logical_operator):
        """–lop (Logical operator) query parameter

        Args:
            logical_operator: Either FMS_FIND_AND, FMS_FIND_OR or None
        """
        assert logical_operator in {FMS_FIND_AND, FMS_FIND_OR, None}
        if logical_operator in {FMS_FIND_AND, FMS_FIND_OR, None}:
            self.__logical_operator = logical_operator

    def set_lay_response(self, lay_response=None):
        """–lay.response (Switch layout for response) query parameter

        Args:
            lay_response (str, optional): Layout to switch to for XML response.
        """
        assert lay_response is None or isinstance(lay_response, str)
        self.__lay_response = lay_response

    def add_sort_rule(self, field_name, precedence, order=None):
        """–sortfield (Sort field) query parameter

        -sortfield.precedence-number=fully-qualified-field-name

        Args:
          field_name (str, None): Fully qualified field name to sort on. None if
          precedence (int, None): Integer from 1 to 9 inclusive.
          order (str, optional): Direction of sort. If not supplied FileMaker
            will silently default to ascending order.
        """
        assert field_name is None or isinstance(field_name, str)
        assert isinstance(precedence, int) and 0 < precedence <= 9
        assert order in {FMS_SORT_ASCEND, FMS_SORT_DESCEND, None}

        # Remove anything with the same precedence.
        # Maximum of 9 items, so brute force is Ok.
        for tmp_field_name in list(self.__sort_fields.keys()):
            if self.__sort_fields[tmp_field_name].precedence == precedence:
                del self.__sort_fields[tmp_field_name]

        self.__sort_fields[field_name] = SortOrder(precedence, order)
        self.__sort_fields.move_to_end(field_name)  # LIFO

    def del_sort_rule(self, field_name):
        """
        Remove a sortfield

        Args:
            field_name (str): Name of field to be removed.
        """
        if field_name in self.__sort_fields:
            del self.__sort_fields[field_name]

    def clear_sort_rules(self):
        """
        Remove any rules set by :py:member:`add_sort_rule`
        """
        self.__sort_fields.clear()

    def add_find_criterion(self, field_name, test_value, op=None):
        """
        fieldname.op (Comparison operator) query parameter

        table-name::field-name=value&table-name::field-name.op=op-symbol

        Args:
            field_name (str): Name of the field.
            test_value: Value to test against.
            op (str, optional):
        """

        self.__find_criteria.append(FindCriteria(field_name, test_value, op))

    def clear_find_criteria(self):
        self.__find_criteria.clear()
