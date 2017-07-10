#
# coding: utf-8
#
# Stubs for fmxml.commands.command_container
#
from decimal import Decimal
from typing import Optional, Iterator, List, Pattern, Union

SAFE_CHARS: str = ...

Arg = Union[int, str, Decimal, None]


# TODO: 20170630 should use NamedTuple for Command - hints is borked.
# class Command(NamedTuple):
#     cmd: str
#     arg: str = None
class Command:
    cmd: str
    arg: Arg

    def __init__(self, cmd: str, arg: Arg = ...) -> None:
        ...


class CommandContainer:
    _data: List[Command]

    def __init__(self, *commands: Command) -> None:
        ...

    def __setitem__(self, cmd: str, arg: Optional[str]) -> None: ...

    def __iter__(self) -> Iterator[Command]: ...

    def __len__(self) -> int: ...

    # TODO: replace object with the real thing
    def remove_(self, regex_obj: Pattern[str]) -> None: ...

    # TODO: development code
    def __delitem__(self, key: str) -> None: ...

    # TODO: development code
    def empty(self) -> bool: ...

    # TODO: development code
    def has_cmd(self, cmd: str) -> bool: ...

    def as_query(self) -> str: ...
