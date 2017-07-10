#
# coding: utf-8
#
# fmxml.commands.mixins.script_mixin
#
from .. import base_command as base_command_module


class ScriptDetail:
    """
    Shared mixins cannot inherit from a shared base class if they share
    variables. Hence the use of this class to be instantiated as a member
    variable in the similar mixins.
    """
    __slots__ = ('_pre', '_script_name', '_script_params',)

    def __init__(self, pre):
        assert isinstance(pre, str)
        self._pre = pre
        self._script_name = None
        self._script_params = None

    def get_command_params(self, command_params):
        if self._script_name is not None:
            command_params[f'-script{self._pre}'] = self._script_name
            if self._script_params:
                command_params[f'-script{self._pre}.param'] = '|'.join(
                    self._script_params)

        return command_params

    def add_script(self, script_name, *script_params):
        assert script_name
        assert isinstance(script_name, str)
        assert all([isinstance(param, str) for param in script_params])

        self._script_name = script_name
        self._script_params = list(script_params)


class ScriptMixin(base_command_module.BaseCommand0):
    """
    –script (Script) query parameter

    –script.param (Pass parameter to Script) query parameter
    """

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self._script_detail = ScriptDetail('')

    def get_command_params(self):
        return self._script_detail.get_command_params(super().get_command_params())

    def set_script(self, script_name, *script_params):
        self._script_detail.add_script(script_name, *script_params)


class PreFindScriptMixin(base_command_module.BaseCommand0):
    """
    –script.param (Pass parameter to Script) query parameter

    –script.prefind (Script before Find) query parameter
    """

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self._prefind_script_detail = ScriptDetail('.prefind')

    def get_command_params(self):
        return self._prefind_script_detail.get_command_params(super().get_command_params())

    def set_prefind_script(self, script_name, *script_params):
        self._prefind_script_detail.add_script(script_name, *script_params)


class PreSortScriptMixin(base_command_module.BaseCommand0):
    """
    –script.presort (Script before Sort) query parameter

    –script.presort.param (Pass parameter to Script before Sort) query parameter
    """

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        self._pre_sort_script_detail = ScriptDetail('.presort')

    def get_command_params(self):
        return self._pre_sort_script_detail.get_command_params(super().get_command_params())

    def set_presort_script(self, script_name, *script_params):
        self._pre_sort_script_detail.add_script(script_name, *script_params)
