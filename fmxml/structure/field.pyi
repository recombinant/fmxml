#
# coding: utf-8
#
# Stubs for fmxml.structure.field
#
import datetime
from decimal import Decimal
from typing import Any, Union

from . import field_definition as field_definition_module
from . import layout as layout_module

Value = Union[str, int, Decimal, datetime.datetime, None]


class Field:
    _layout: layout_module.Layout = ...
    _name: str = ...
    _field_definition: field_definition_module.FieldDefinition = ...
    # TODO: maybe _value could be something
    _value: Any = ...

    def __init__(self,
                 layout: layout_module.Layout,
                 name: str,
                 value: Value) \
            -> None:
        ...

    @property
    def name(self) -> str: ...

    @property
    def value(self) -> Value: ...

    def set_value(self, value: Value) -> None: ...

    @property
    def unmunged_value(self) -> Value: ...

    def validate(self) -> bool: ...

    def is_updated(self) -> bool: ...
