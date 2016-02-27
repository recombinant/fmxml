# -*- mode: python tab-width: 4 coding: utf-8 -*-
import urllib.parse

from .command_container import CommandContainer, Command


class BaseCommand:
    """
    Base for command classes.

    This class must be on the right any mixins so that it is at the end of the
    mro."""
    __slots__ = ['__fms', '__layout_name', ]

    def __init__(self, fms, layout_name):
        assert fms
        assert layout_name
        assert isinstance(layout_name, str)
        self.__fms = fms
        self.__layout_name = layout_name

    def get_command_params(self):
        db = self.__fms.get_property('db')
        assert db
        command_params = CommandContainer(
            Command('-db', db),
            Command('-lay', self.__layout_name),
        )
        return command_params

    def urlencode_query(self, command_params):
        start, end = [], []
        # URL encode the query, but don't put =arg on the trailing "command"
        for cmd, arg in command_params:
            assert isinstance(cmd, str)
            assert isinstance(arg, (str, int, type(None)))
            if arg is not None:
                start.append((cmd, arg))  # cmd=arg
            else:
                end.append(cmd)  # cmd

        if start:
            # command parameters
            # not HTML so safe can be extended for debugging if necessary
            # safe = '(),;!<>'
            start = urllib.parse.urlencode(start, safe='!():;,/ ', encoding='utf-8',
                                           quote_via=urllib.parse.quote)

        if end:
            # command verb, there should only be one
            assert len(end) == 1
            # ASCII - therefore no encoding needed
            end = end[-1]

        if start and end:
            return '&'.join([start, end])

        raise AssertionError('Invalid command parameter sequence')  # pragma: no cover
