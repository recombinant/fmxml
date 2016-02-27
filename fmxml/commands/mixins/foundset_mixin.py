# -*- mode: python tab-width: 4 coding: utf-8 -*-
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
