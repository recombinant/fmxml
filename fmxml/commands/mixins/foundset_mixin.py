#
# coding: utf-8
#
# fmxml.commands.mixins.foundset_mixin
#
from .. import base_command as base_command_module


class FoundSetMixin(base_command_module.BaseCommand0):
    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self._max = None
        self._skip = 0

    def get_command_params(self):
        command_params = super().get_command_params()

        if self._skip:
            command_params['-skip'] = self._skip
        if self._max is not None:
            command_params['-max'] = self._max

        return command_params

    @property
    def skip(self):
        return self._skip

    def set_skip(self, skip=0):
        """–skip (Skip records) query parameter

        Args:
            skip (int): Specifies how many records to skip in the found set. Defaults to zero.
        """
        assert isinstance(skip, int) and skip >= 0
        self._skip = skip

    @property
    def max(self):
        return self._max

    def set_max(self, max_=None):
        """–max (Maximum records) query parameter

        Args:
            max_ (int, str, optional): Maximum number of records to return. Defaults to all.
        """
        assert max_ is None or max_ == 'all' or (isinstance(max_, int) and max_ >= 0)
        self._max = max_
