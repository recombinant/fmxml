# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import namedtuple, OrderedDict

from .base_command import BaseCommand
from .mixins import RecordIdMixin, FoundSetMixin, SortRulesMixin,\
    ScriptsMixin, PreFindScriptsMixin,\
    PreSortScriptsMixin, RelatedsSetsMixin
from ..fms import FMS_FIND_AND, FMS_FIND_OR
from ..fms import \
    FMS_FIND_OP_EQ, FMS_FIND_OP_NEQ, \
    FMS_FIND_OP_GT, FMS_FIND_OP_GTE, \
    FMS_FIND_OP_LT, FMS_FIND_OP_LTE, \
    FMS_FIND_OP_CN, \
    FMS_FIND_OP_BW, FMS_FIND_OP_EW
from ..fms import FMS_SORT_DESCEND, FMS_SORT_ASCEND

FindCriteria = namedtuple('FindCriteria', 'field_name test_value op')


class FindCommand(SortRulesMixin,
                  RecordIdMixin,
                  FoundSetMixin,
                  ScriptsMixin,
                  PreFindScriptsMixin,
                  PreSortScriptsMixin,
                  RelatedsSetsMixin,
                  BaseCommand):
    """
    –find or –findall (Find records) query commands

    Automatically selects *-find* or *-findall* as appropriate.
    """
    __slots__ = ('__logical_operator',
                 '__lay_response',
                 '__find_criteria',)

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)

        self.__logical_operator = \
            self.__lay_response = None
        self.__find_criteria = []  # list of FindCriteria

    def get_query(self):
        command_params = super().get_command_params()

        if self.__logical_operator is not None:
            command_params['-lop'] = self.__logical_operator
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

        if self.record_id is None and not self.__find_criteria:
            command_params['-findall'] = None
        else:
            command_params['-find'] = None

        return command_params.as_query()

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
