# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import namedtuple, OrderedDict

SortOrder = namedtuple('SortOrder', 'precedence order')


class SortRulesMixin:
    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self.__sort_fields = OrderedDict()

    def get_command_params(self):
        command_params = super().get_command_params()

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

        return command_params

    def add_sort_rule(self, field_name, precedence, order=None):
        """–sortfield (Sort field) query parameter

        -sortfield.precedence-number=fully-qualified-field-name

        Args:
          field_name (str, None): Fully qualified field name to sort on. None if
          precedence (int, None): Integer from 1 to 9 inclusive.
          order (str, optional): Direction of sort. If not supplied FileMaker
            will silently default to ascending order.
        """
        from ...fms import FMS_SORT_ASCEND, FMS_SORT_DESCEND
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
