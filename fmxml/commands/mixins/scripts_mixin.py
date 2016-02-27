# -*- mode: python tab-width: 4 coding: utf-8 -*-
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


class ScriptsMixin:
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


class PreFindScriptsMixin:
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


class PreSortScriptsMixin:
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
