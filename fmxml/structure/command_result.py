# -*- mode: python tab-width: 4 coding: utf-8 -*-
from builtins import property
from collections import Counter
from typing import List

from . import layout as layout_module
from . import record as record_module


class CommandResult:
    __slots__ = ('__fms', '__error_code', '__layout', '__found_count',
                 '__fetch_size', '__records', '__total_count',)

    def __init__(self, fms, parsed_data):
        self.__fms = fms

        self.__error_code = int(parsed_data.error.code)
        # Either no error or record does not exist.
        assert self.__error_code in [0, 401], self.__error_code

        def _create_new_record(layout_, raw_record_):
            """
            Helper function, eliminates duplicate code. This is used for both
            layout and portal. The parameters' trailing underscores are
            to eliminate name collision with other variables in scope.
            """
            _field_container = _raw_record_field_factory(layout_, raw_record_.fields)
            _record = record_module.Record(layout_, _field_container)
            _record.set_record_id_(int(raw_record_.record_id))
            _record.set_modification_id(int(raw_record_.modification_id))
            return _record

        self.__layout = Layout(self.__fms, parsed_data)

        datasource = parsed_data.datasource
        self.__total_count = int(datasource.total_count)

        resultset = parsed_data.resultset
        self.__found_count = int(resultset.count)
        self.__fetch_size = int(resultset.fetch_size)

        record_list = []
        for raw_record in resultset.records:
            new_record = _create_new_record(self.__layout, raw_record)

            # portal
            if raw_record.relatedsets:
                for table_name, portal_raw_records in raw_record.relatedsets.items():
                    for portal_raw_record in portal_raw_records:
                        new_portal_record = _create_new_record(
                            self.__layout,
                            portal_raw_record)
                        new_record.add_portal_record_(table_name, new_portal_record)

            record_list.append(new_record)

        self.__records = record_list  # type: List[record_module.Record]

    @property
    def layout(self) -> 'layout_module.Layout':
        return self.__layout

    @property
    def records(self) -> List['record_module.Record']:
        return self.__records

    @property
    def field_names(self) -> List[str]:
        return self.__layout.field_names

    @property
    def portal_names(self) -> List[str]:
        return self.__layout.portal_names

    @property
    def total_count(self) -> int:
        return self.__total_count

    @property
    def found_count(self) -> int:
        return self.__found_count

    @property
    def fetch_size(self) -> int:
        return self.__fetch_size


def _raw_record_field_factory(layout, raw_records):
    """
    For internal use only. Used when parsing the fmresultset grammar.

    Args:
        layout: Layout that these records belong to.
        raw_records: A list of raw records from :py:class:`.DataGrammarParser`

    Returns:
      :py:class:`.FieldContainer`: A :py:class:`.FieldContainer` instance
        containing a representation of `raw_records`
    """
    from ..structure import FieldContainer
    # get the raw records and turn them into a list of tuples
    # [((name, (data, ...)), (name, (data, ...)), ...]
    fields = []
    for record in raw_records:
        field_name = record.name
        record_data = []
        for data in record.data:
            record_data.append(data)
        fields.append((field_name, tuple(record_data)))
    # most common returns something like [('Description', 1)]
    fields = set(fields)
    assert not fields or Counter(field[0] for field in fields).most_common(1)[0][1] == 1, (
        Counter(field[0] for field in fields).most_common(1)[0][0])

    field_value_dict = dict()
    for field_name, field_value_sequence in fields:
        field_value_dict[field_name] = {
            repetition_number: field_value
            for repetition_number, field_value in enumerate(field_value_sequence)}
    return FieldContainer(layout, field_value_dict)
