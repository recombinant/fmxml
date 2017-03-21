# -*- mode: python tab-width: 4 coding: utf-8 -*-
from .command_container import CommandContainer, Command
from ..parsers import DataGrammarParser
from ..structure import CommandResult


class BaseCommand:
    """
    Base for command classes.

    This class must be on the right of any mixins so that it is at the end of
    the mro."""
    __slots__ = ('__fms', '__layout_name',)

    def __init__(self, fms, layout_name):
        assert fms
        assert layout_name
        assert isinstance(layout_name, str)
        self.__fms = fms
        self.__layout_name = layout_name

    def get_command_params(self):
        db = self.__fms.db_name
        assert db
        command_params = CommandContainer(
            Command('-db', db),
            Command('-lay', self.__layout_name),
        )
        return command_params

    def execute(self):
        query = self.get_query()
        xml_bytes = self.__fms.execute_(query)
        assert xml_bytes

        parsed_data = DataGrammarParser().parse(xml_bytes)
        # populate result
        return CommandResult(self.__fms, parsed_data)
