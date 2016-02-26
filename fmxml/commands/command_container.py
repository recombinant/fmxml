# -*- mode: python tab-width: 4 coding: utf-8 -*-
from _operator import attrgetter
from collections import namedtuple, Counter

Command = namedtuple('Command', 'cmd arg')
Command.__new__.__defaults__ = (None,)


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
    >>> for cmd, arg in cc:
    ...     print(cmd, arg)
    -db FMPHP_Sample
    -lay Form View
    -view None
    >>> cc.has_cmd('-view')
    True
    >>> del cc['-view']
    >>> cc.has_cmd('-view')
    False
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
    >>> cc._remove(re.compile(r'-sort.*'))
    >>> len(cc)
    3
    """

    def __init__(self, *commands):
        self.__data = []
        for command in commands:
            self.__data.append(Command(command.cmd, command.arg))

    def __setitem__(self, cmd, arg):
        self.__data.append(Command(cmd, arg))

    def __iter__(self):
        yield from self.__data

    def __len__(self):
        return len(self.__data)

    def _remove(self, regex_obj):
        """
        :param regex_obj: regular expression object to test against.
            Removes any commands that match.
        :return:
        """
        deletable = []
        for idx, (cmd, arg) in enumerate(self.__data):
            if regex_obj.match(cmd):
                deletable.append(idx)

        deletable.reverse()
        for idx in deletable:
            del self.__data[idx]

    # TODO: development code
    def __delitem__(self, key):
        # Check that there is only one.
        counter = Counter(map(attrgetter('cmd'), self.__data))
        assert counter[key] == 1

        for idx, (cmd, arg) in enumerate(self.__data):
            if cmd == key:
                del self.__data[idx]
                return

    # TODO: development code
    def empty(self):
        return not bool(self.__data)

    # TODO: development code
    def has_cmd(self, cmd):
        assert isinstance(cmd, str)
        return any(command.cmd == cmd for command in self.__data)
