#
# coding: utf-8
#
# fmxml.commands.command_container
#
import urllib.parse
from collections import Counter
from operator import attrgetter

SAFE_CHARS = '*!():;,/ '


# TODO: 20170630 should use NamedTuple for Command - hints is borked.
# Command = namedtuple('Command', 'cmd arg')
# Command.__new__.__defaults__ = (None,)
# # or
# class Command(NamedTuple):
#     cmd: str
#     arg: str = None
class Command:
    def __init__(self, cmd, arg=None):
        self.cmd = cmd
        self.arg = arg

    def __repr__(self):
        return f'Command(cmd={self.cmd!r}, arg={self.arg!r})'


class CommandContainer:
    """
    Class to hold FileMaker® query commands and parameters::
    >>> cc = CommandContainer()
    >>> cc.empty()
    True
    >>> cc['-db'] = 'FMPHP_Sample'
    >>> cc['-lay'] = 'Form View'
    >>> cc['-view'] = None
    >>> cc.empty()
    False
    >>> for command in cc:
    ...     print(command.cmd, command.arg)
    -db FMPHP_Sample
    -lay Form View
    -view None
    >>> cc.has_cmd('-view')
    True
    >>> del cc['-view']
    >>> cc.has_cmd('-view')
    False

    # Test Command class
    >>> Command('-db', 'employees')
    Command(cmd='-db', arg='employees')
    >>> Command('-findall')
    Command(cmd='-findall', arg=None)
    >>> import pytest
    >>> with pytest.raises(TypeError):
    ...     Command()

    >>> command_params = [
    ...    Command('-db', 'employees'),
    ...    Command('-lay', 'performance'),
    ...    Command('-sortfield.1', 'dept'),
    ...    Command('-sortfield.2', 'rating'),
    ...    Command('-findall'),
    ... ]
    >>> cc = CommandContainer(*command_params)
    >>> len(cc)
    5
    >>> import re
    >>> cc.remove_(re.compile(r'-sort.*'))
    >>> len(cc)
    3
    """

    def __init__(self, *commands):
        self._data = []
        for command in commands:
            self._data.append(Command(command.cmd, command.arg))

    def __setitem__(self, cmd, arg):
        self._data.append(Command(cmd, arg))

    def __iter__(self):
        yield from self._data

    def __len__(self):
        return len(self._data)

    def remove_(self, cre):
        """
        :param cre: compiled regular expression object to test against.
            Removes any commands that match.
        :return:
        """
        deletable = []
        for idx, command in enumerate(self._data):
            if cre.match(command.cmd):
                deletable.append(idx)

        deletable.reverse()
        for idx in deletable:
            del self._data[idx]

    # TODO: development code
    def __delitem__(self, key):
        # Check that there is only one.
        counter = Counter(map(attrgetter('cmd'), self._data))
        assert counter[key] == 1

        for idx, command in enumerate(self._data):
            if command.cmd == key:
                del self._data[idx]
                return

    # TODO: development code
    def empty(self):
        return not bool(self._data)

    # TODO: development code
    def has_cmd(self, cmd):
        assert isinstance(cmd, str)
        return any(command.cmd == cmd for command in self._data)

    def as_query(self):
        """
        Returns:
            String suitable for the parameter section of a FileMaker url query.
        """
        start_list, end_list = [], []
        # URL encode the query, but don't put =arg on the trailing "command"
        for command in self._data:
            # TODO: not necessary when using NamedTuple for Command
            cmd = command.cmd
            arg = command.arg

            if arg is not None:
                start_list.append((cmd, arg))  # cmd=arg
            else:
                end_list.append(cmd)  # cmd

        if start_list:
            # Command parameters - not HTML so safe= can be extended.
            start_string = urllib.parse.urlencode(start_list,
                                                  safe=SAFE_CHARS,
                                                  encoding='utf-8',
                                                  quote_via=urllib.parse.quote)
        else:
            start_string = ''

        if end_list:
            # command verb, there should only be one
            assert len(end_list) == 1
            # ASCII - therefore no encoding needed
            end_string = end_list[-1]
        else:
            raise AssertionError('Invalid command parameter sequence')  # pragma: no cover

        if start_string:
            return '&'.join([start_string, end_string])
        else:
            return end_string
