#
# coding: utf-8
#
# fmxml.commands.mixins.relatedsets_mixin
#
from .. import base_command as base_command_module


class RelatedsSetsMixin(base_command_module.BaseCommand0):
    """
    -relatedsets.filter (Filter portal records) query parameter

    -relatedsets.max (Limit portal records) query parameter
    """

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self._relatedsets_filter = None
        self._relatedsets_max = None

    def set_relatedsets_filter(self, filter_=None):
        from ...fms import (FMS_RELATEDSETS_FILTER_LAYOUT,
                            FMS_RELATEDSETS_FILTER_NONE)

        assert (filter_ is None or
                filter_ in {FMS_RELATEDSETS_FILTER_LAYOUT,
                            FMS_RELATEDSETS_FILTER_NONE})
        self._relatedsets_filter = filter_

    def set_relatedsets_max(self, max_=None):
        assert max is None or max_ == 'all' or (isinstance(max_, int) and max_ >= 0)
        self._relatedsets_max = max_

    def get_command_params(self):
        command_params = super().get_command_params()

        if self._relatedsets_filter is not None:
            command_params['-relatedsets.filter'] = self._relatedsets_filter
            if self._relatedsets_max is not None:
                command_params['-relatedsets.max'] = self._relatedsets_max

        return command_params
