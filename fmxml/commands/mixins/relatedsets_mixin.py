# -*- mode: python tab-width: 4 coding: utf-8 -*-
class RelatedsSetsMixin:
    """
    -relatedsets.filter (Filter portal records) query parameter

    -relatedsets.max (Limit portal records) query parameter
    """

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self.__relatedsets_filter = None
        self.__relatedsets_max = None

    def set_relatedsets_filter(self, filter=None):
        from ...fms import \
            FMS_RELATEDSETS_FILTER_LAYOUT, \
            FMS_RELATEDSETS_FILTER_NONE

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
