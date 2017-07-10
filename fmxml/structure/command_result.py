#
# coding: utf-8
#
# fmxml.structure.command_result
#
from collections import Counter

from . import layout as layout_module
from . import record as record_module


class CommandResult:
    __slots__ = ('_fms', '_error_code', '_layout', '_found_count',
                 '_fetch_size', '_records', '_total_count',)

    def __init__(self, fms, parsed_data):
        self._fms = fms

        self._error_code = int(parsed_data.error.code)
        # Either no error or record does not exist.
        assert self._error_code in [0, 401], self._error_code

        self._layout = layout_module.Layout(self._fms, parsed_data)

        datasource = parsed_data.datasource
        self._total_count = int(datasource.total_count)

        resultset = parsed_data.resultset
        self._found_count = int(resultset.count)
        self._fetch_size = int(resultset.fetch_size)

        record_list = []
        for raw_record in resultset.records:
            new_record = self._create_new_record(self._layout, raw_record)

            # portal
            if raw_record.relatedsets:
                for table_name, portal_raw_records in raw_record.relatedsets.items():
                    for portal_raw_record in portal_raw_records:
                        new_portal_record = self._create_new_record(
                            self._layout,
                            portal_raw_record)
                        new_record.add_portal_record_(table_name, new_portal_record)

            record_list.append(new_record)

        self._records = record_list

    @property
    def layout(self):
        return self._layout

    @property
    def records(self):
        return self._records

    @property
    def field_names(self):
        return self._layout.field_names

    @property
    def portal_names(self):
        return self._layout.portal_names

    @property
    def total_count(self):
        return self._total_count

    @property
    def found_count(self):
        return self._found_count

    @property
    def fetch_size(self):
        return self._fetch_size

    def _create_new_record(self, layout_or_portal, raw_record):
        """
        Helper function, eliminates duplicate code. This is used for both
        layout and portal.
        """
        field_container = self._raw_record_field_factory(layout_or_portal, raw_record.fields)
        record: record_module.Record = record_module.Record(layout_or_portal, field_container)
        record.record_id = int(raw_record.record_id)
        record.modification_id = int(raw_record.modification_id)
        return record

    @staticmethod
    def _raw_record_field_factory(layout, raw_record_fields):
        """
        For internal use only. Used when parsing the fmresultset grammar.

        Args:
            layout: Layout that these records belong to.
            raw_record_fields: A list of raw record fields from :py:class:`.DataGrammarParser`

        Returns:
          :py:class:`.FieldContainer`: A :py:class:`.FieldContainer` instance
            containing a representation of `raw_records`
        """
        from .field_container import FieldContainer
        # get the raw records and turn them into a list of tuples
        # [((name, (data, ...)), (name, (data, ...)), ...]
        fields = []
        for raw_field in raw_record_fields:
            field_name = raw_field.name
            record_data = []
            for data in raw_field.data:
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
