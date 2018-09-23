#
# coding: utf-8
#
# fmxml.commands.base_command
#
import abc

from .command_container import CommandContainer, Command
from ..parsers import DataGrammarParser
from ..structure import CommandResult


class BaseCommand0(abc.ABC):
    def __init__(self, fms, layout_name):
        """
        Pass in the FileMakerServer instance and the name of the Layer.
        """
        pass

    def get_command_params(self):
        """
        CommandContainer
        """
        pass


class BaseCommand1(abc.ABC):
    def get_query(self):
        return 'abc'


class BaseCommand(BaseCommand1, BaseCommand0):
    """
    Base for command classes.

    This class must be on the right of any mixins so that it is at the end of
    the mro."""
    __slots__ = ('_fms', '_layout_name',)

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)
        assert fms
        assert layout_name
        assert isinstance(layout_name, str)
        self._fms = fms
        self._layout_name = layout_name

    def get_command_params(self):
        db = self._fms.db_name
        assert db
        command_params = CommandContainer(
            Command('-db', db),
            Command('-lay', self._layout_name),
        )
        return command_params

    def execute(self):
        query = self.get_query()
        xml_bytes = self._fms.execute_query(query)
        assert xml_bytes

        parsed_data = DataGrammarParser().parse(xml_bytes)
        # populate result
        return CommandResult(self._fms, parsed_data)
