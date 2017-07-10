#
# coding: utf-8
#
# Stubs for fmxml.structure.field_container
#
import datetime
from decimal import Decimal
from typing import List, Tuple, Dict, Iterator, Union, Optional, Any

from . import layout as layout_module
from . import portal as portal_module
from .field import Field

Value = Union[str, int, Decimal, datetime.datetime, None]

# Passed to FieldContainer constructor
# { field_name: { repetition_number: field_value } }
FieldValueDict = Dict[str, Dict[int, Value]]

# Internal to FieldContainer
# { field_name: { repetition_number: Field } }
FieldLookup = Dict[str, Dict[int, Field]]

LayerPortal = Union[layout_module.Layout, portal_module.Portal]

FieldValues1 = Dict[str, Value]
FieldValues2 = List[Tuple[str, Value]]
FieldValues = Union[FieldValues1, FieldValues2]


class FieldContainer:
    from ..fms import FileMakerServer

    _fms: FileMakerServer
    _layout: LayerPortal
    _fields: FieldLookup

    def __init__(self,
                 layout: LayerPortal,
                 field_value_dict: Optional[FieldValueDict] = ...) \
            -> None:
        ...

    # def __missing__(self, key: str) -> Dict[]:

    def __copy__(self) -> 'FieldContainer':
        ...

    @property
    def names(self) -> List[str]:
        ...

    def set_field_value(self,
                        field_name: str,
                        value: Value,
                        repetition_number: int) \
            -> None:
        ...

    def get_field_value(self, field_name: str, repetition_number: int = ...) -> Value:
        ...

    def _get_field_repetition_numbers(self, field_name: str) -> Tuple[Dict[int, Field], List[int]]:
        ...

    def get_field_values(self, field_name: str) -> List[Value]:
        ...

    def iter_fields(self) -> Iterator[Tuple[str, Value, int]]:
        ...

    def iter_updated_fields(self) -> Iterator[Tuple[str, Value, int]]:
        ...

    def iter_updated_fields_unmunged(self) -> Iterator[Tuple[str, Value, int]]:
        ...

    def _partial_copy(self, *field_names: str) -> FieldContainer:
        ...

    @property
    def _debug_fields(self) -> FieldLookup:
        ...

    def validate(self, field_name: Optional[str]) -> bool:
        ...


# TODO: Annotate properly
def _raw_record_field_factory(layout: LayerPortal, raw_records: Any) -> FieldContainer:
    ...


#
# Takes
#   FieldValue1
#     {field_name1: value1, field_name2: value2}
# or
#   FieldValue2
#     [(field_name, value), (field_name, value), ...]
#
def single_field_factory(layout: LayerPortal, field_values: FieldValues) -> FieldContainer:
    ...


def repetition_field_factory(layout: LayerPortal, field_values: FieldValues) -> FieldContainer:
    ...
