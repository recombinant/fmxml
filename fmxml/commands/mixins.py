# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import OrderedDict, namedtuple

from ..fms import FMS_SORT_ASCEND, FMS_SORT_DESCEND


class RecordIdMixin:
    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self.__record_id = None

    def get_command_params(self):
        command_params = super().get_command_params()

        if self.__record_id is not None:
            command_params['-recid'] = str(self.__record_id)

        return command_params

    @property
    def record_id(self):
        return self.__record_id

    def set_record_id(self, record_id=None, _oneshot=False):
        """
        –recid (Record ID) query parameter

        Args:
            record_id (int, optional): A record id. Defaults to None which means all records.
            _oneshot (bool): Internal use only.
        """
        assert record_id is None \
               or (isinstance(record_id, int) and record_id > 0)
        self.__record_id = record_id

        if _oneshot:
            # Don't want to call set_record_id() again.
            self.set_record_id = self.__not_implemented

    def __not_implemented(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError


class ScriptDetails:
    """
    Shared mixins cannot inherit from a shared base class if they share
    variables. Hence the use of this class to be instantiated as a member
    variable in the similar mixins.
    """
    __slots__ = ['__pre', '__script_name', '__script_params']

    def __init__(self, pre):
        assert isinstance(pre, str)
        self.__pre = pre
        self.__script_name = None
        self.__script_params = None

    def get_command_params(self, command_params):
        if self.__script_name is not None:
            command_params['-script{}'.format(self.__pre)] = self.__script_name
            if self.__script_params:
                command_params['-script{}.param'.format(self.__pre)] = '|'.join(
                    self.__script_params)

        return command_params

    def add_script(self, script_name, *script_params):
        assert script_name
        assert isinstance(script_name, str)
        assert all([isinstance(param, str) for param in script_params])

        self.__script_name = script_name
        self.__script_params = list(script_params)


class ScriptMixin:
    """
    –script (Script) query parameter

    –script.param (Pass parameter to Script) query parameter
    """

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self.__script_details = ScriptDetails('')

    def get_command_params(self):
        return self.__script_details.get_command_params(super().get_command_params())

    def set_script(self, script_name, *script_params):
        self.__script_details.add_script(script_name, *script_params)


class PreFindScriptMixin:
    """
    –script.param (Pass parameter to Script) query parameter

    –script.prefind (Script before Find) query parameter
    """

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self.__script_details = ScriptDetails('.prefind')

    def get_command_params(self):
        return self.__script_details.get_command_params(super().get_command_params())

    def set_prefind_script(self, script_name, *script_params):
        self.__script_details.add_script(script_name, *script_params)


class PreSortScriptMixin:
    """
    –script.presort (Script before Sort) query parameter

    –script.presort.param (Pass parameter to Script before Sort) query parameter
    """

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self.__script_details = ScriptDetails('.presort')

    def get_command_params(self):
        return self.__script_details.get_command_params(super().get_command_params())

    def set_presort_script(self, script_name, *script_params):
        self.__script_details.add_script(script_name, *script_params)


class FoundSetMixin:
    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self.__max = None
        self.__skip = 0

    def get_command_params(self):
        command_params = super().get_command_params()

        if self.__skip:
            command_params['-skip'] = self.__skip
        if self.__max is not None:
            command_params['-max'] = self.__max

        return command_params

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


class RelatedsSetMixin:
    """
    -relatedsets.filter (Filter portal records) query parameter

    -relatedsets.max (Limit portal records) query parameter
    """

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self.__relatedsets_filter = None
        self.__relatedsets_max = None

    def set_relatedsets_filter(self, filter=None):
        from ..fms import \
            FMS_RELATEDSETS_FILTER_LAYOUT, FMS_RELATEDSETS_FILTER_NONE

        assert filter is None or \
               filter in {FMS_RELATEDSETS_FILTER_LAYOUT,
                          FMS_RELATEDSETS_FILTER_NONE}
        self.__relatedsets_filter = filter

    def set_relatedsets_max(self, max_=None):
        assert max is None or max_ == 'all' or (isinstance(max_, int) and max_ >= 0)
        self.__relatedsets_max = max_

    def get_command_params(self):
        command_params = super().get_command_params()

        if self.__relatedsets_filter is not None:
            command_params['-relatedsets.filter'] = self.__relatedsets_filter
            if self.__relatedsets_max is not None:
                command_params['-relatedsets.max'] = self.__relatedsets_max

        return command_params


SortOrder = namedtuple('SortOrder', 'precedence order')


class SortRuleMixin:
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
