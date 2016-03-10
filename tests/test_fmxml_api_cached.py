# -*- mode: python tab-width: 4 coding: utf-8 -*-
"""
Rather than calling the server every time these tests are run, the responses
are cached (in files) against the url of each call the first time a call is
made. This is for the find related commands only - no data changes so the
responses are always the same.
"""
import logging
import os
import re
import urllib.parse
from pathlib import Path
from urllib.parse import SplitResult, urlsplit, urlunsplit, urlencode, parse_qsl

import pytest
from numpy import random

from fmxml import FindQuery, FindRequestDefinition
from fmxml.commands.command_container import SAFE_CHARS
from fmxml.fms import FileMakerServer, FMS_SORT_ASCEND, FMS_FIND_OP_EW, FMS_FIND_OP_BW, \
    FMS_FIND_OP_CN, FMS_FIND_OP_EQ, FMS_FIND_OP_NEQ, FMS_SORT_DESCEND, FMS_FIND_OR
from fmxml.structure import Record
from tests import secret


def _execute(self, query, xml_grammar='fmresultset'):
    """
    Monkey patch.
    Replacement function for FileMakerServer. Caches +execute() responses.
    """
    assert query
    assert isinstance(query, str)
    assert xml_grammar
    assert isinstance(xml_grammar, str)

    self.log.info(query)

    # '*', ':' and '/' are safe for a query, but not always for a filename.
    unsafe = r'\*|:|/'
    # Re-encode fully.
    sr = urlsplit(query)  # looking for characters in url path
    if re.search(unsafe, sr.path):
        command = re.search('(-[a-z]+$)', query).group(1)
        safe = re.sub(unsafe, '', SAFE_CHARS)
        query2 = urlencode(parse_qsl(query), safe=safe, quote_via=urllib.parse.quote)
        if query2:
            query2 = '&'.join([query2, command])
        else:
            query2 = command  # e.g. -dbnames
    else:
        query2 = query

    # The filename.
    xml_filename = '{}{}.xml'.format(xml_grammar, query2)
    xml_filename = Path(__file__).parent / 'data' / xml_filename
    xml_filename = str(xml_filename)
    if os.name == 'nt':
        # Need to check for overly long file names.
        if not xml_filename.startswith('\\\\?\\') and len(xml_filename) > 260:
            if not re.match(r'\A[a-z]:\\', xml_filename, re.I):
                raise AssertionError('path length too long: {!r}'.format(xml_filename))
            xml_filename = r'\\?\{}'.format(xml_filename)
    # -------------------------------------------------------------------------
    # The url.
    path = '/fmi/xml/{}.xml'.format(xml_grammar)
    hostspec = self.hostspec

    sr = urlsplit(hostspec)
    sr = SplitResult(scheme=sr.scheme, netloc=sr.netloc, path=path, query=query, fragment='')
    # Join together (correctly) for xml_url.
    xml_url = urlunsplit(sr)
    # -------------------------------------------------------------------------
    if os.path.isfile(xml_filename):
        self.log.info(os.path.split(xml_filename)[1])
        xml_bytes = open(xml_filename, 'rb').read()

    else:
        self.log.info(xml_url)

        resp = self.requests_session.get(url=xml_url)
        resp.raise_for_status()  # promulgate errors from the bowels of requests

        xml_bytes = resp.content
        # Save it for later use.
        open(xml_filename, 'wb').write(xml_bytes)
    # -------------------------------------------------------------------------

    return xml_bytes


@pytest.fixture()
def fms_cached():
    connection = secret.get_connection('fmphp_sample')
    setattr(FileMakerServer, '_execute', _execute)  # Monkey patch.
    fms_ = FileMakerServer(log_level=logging.INFO, **connection)
    return fms_


@pytest.fixture()
def layout_name():
    return 'Form View'


def test_01_dbnames(fms_cached):
    db_names = fms_cached.get_db_names()

    assert db_names
    assert isinstance(db_names, list)
    assert all([isinstance(name, str) for name in db_names])
    assert 'FMPHP_Sample' in db_names


def test_02_layout_names(fms_cached):
    layout_names = fms_cached.get_layout_names()

    assert isinstance(layout_names, list)

    assert isinstance(layout_names, list)
    assert all([isinstance(name, str) for name in layout_names])
    assert 'Form View' in layout_names


def test_03_script_names(fms_cached):
    script_names = fms_cached.get_script_names()

    assert isinstance(script_names, list)
    assert len(script_names)
    assert all([isinstance(name, str) for name in script_names])
    # Some of the script names in FMPHP_Sample
    script_name_subset = {'Show Sample Data', 'Echantillons',
                          'Mostra dati di esempio', 'Beispieldaten zeigen',
                          'Visa exempeldata', 'サンプルデータの表示'}
    assert script_name_subset.issubset(set(script_names))


def test_04_records(fms_cached, layout_name):
    # Get all the records, there should not be many.

    find_command = fms_cached.create_find_records_command(layout_name)
    command_result = find_command.execute()
    records = command_result.records
    assert len(command_result.records), command_result.fetch_size
    assert len(command_result.records), command_result.total_count

    assert isinstance(records, list)
    assert len(records)
    for record in records:
        assert isinstance(record, Record)

        assert isinstance(record.record_id, int)
        assert record.record_id > 0

        assert isinstance(record.modification_id, int)
        assert record.modification_id > 0

        assert layout_name == record.layout.name

        # Portals
        table_names = record.portal_table_names
        assert isinstance(table_names, list)
        assert not len(table_names)

        # Parent (shouldn't be one)
        assert record.parent is None

        # Record Id
        record_id = record.record_id
        record2 = fms_cached.find_record_by_id(layout_name, record_id)
        assert record.record_id == record2.record_id


def test_05_layout(fms_cached, layout_name):
    layout = fms_cached.get_layout(layout_name)
    assert layout.database_name == fms_cached.db_name
    assert layout.name == layout_name

    layout = fms_cached.get_layout(layout_name)
    assert layout.database_name == fms_cached.db_name
    assert layout.name == layout_name


def test_09_sort1(fms_cached, layout_name):
    # sort by title
    find_command = fms_cached.create_find_records_command(layout_name)
    find_command.add_sort_rule('Title', 1, FMS_SORT_ASCEND)
    command_result = find_command.execute()
    records = command_result.records
    titles = [record.get_field_value('Title') for record in records]
    assert titles == sorted(titles)

    # reverse sort by title
    find_command.add_sort_rule('Title', 1, FMS_SORT_DESCEND)
    command_result = find_command.execute()
    records = command_result.records
    titles = [record.get_field_value('Title') for record in records]
    assert titles == sorted(titles, reverse=True)

    # two sorts, quantity first then title
    find_command.add_sort_rule('Quantity in Stock', 1, FMS_SORT_DESCEND)
    find_command.add_sort_rule('Title', 2, FMS_SORT_ASCEND)
    command_result = find_command.execute()
    records1 = command_result.records
    records2 = command_result.records[:]
    random.shuffle(records2)
    records2.sort(key=lambda record: record.get_field_value('Title'))
    # TODO: convert fields base on FieldDefinition
    records2.sort(key=lambda record: int(record.get_field_value('Quantity in Stock')),
                  reverse=True)

    for idx in range(len(records1)):
        for field_name in ['Quantity in Stock', 'Title']:
            assert \
                records1[idx].get_field_value(field_name) == \
                records2[idx].get_field_value(field_name)


def test_10_findquery(fms_cached, layout_name):
    findquery_command = fms_cached.create_findquery_command(layout_name)

    # Specify search criterion for first find request
    query1 = FindQuery('Quantity in Stock', '<100')

    # Specify search criterion for second find request
    query2 = FindQuery('Quantity in Stock', '0')

    # Specify search criterion for third find request
    query3 = FindQuery('Cover Photo Credit', 'The Dallas Morning News')

    query_definition1 = FindRequestDefinition([query1, ])
    query_definition2 = FindRequestDefinition([query2, ], omit=True)
    query_definition3 = FindRequestDefinition([query3, ], omit=True)

    # Add find requests to findquery command
    findquery_command.add_request_definitions(query_definition1,
                                              query_definition2,
                                              query_definition3)

    # Set sort order
    findquery_command.add_sort_rule('Title', 1, FMS_SORT_DESCEND)

    # Execute compound find command
    command_result = findquery_command.execute()

    # Get records from found set
    records = command_result.records

    assert records


def test_11_find(fms_cached, layout_name):
    find_command = fms_cached.create_find_records_command(layout_name)
    find_command.add_find_criterion('Title', 'Pennsylvania 24/7')
    command_result = find_command.execute()
    assert command_result.fetch_size == 1
    assert len(command_result.records) == 1

    # Clear find criteria.
    find_command.clear_find_criteria()
    find_command.add_find_criterion('Title', 'Pennsylvania 24/7')
    assert command_result.fetch_size == 1
    assert len(command_result.records) == 1

    # Add another criteria (giving two).
    find_command.add_find_criterion('Title', 'New York 24/7')
    find_command.set_logical_operator(FMS_FIND_OR)
    command_result = find_command.execute()
    assert command_result.fetch_size == 2
    assert len(command_result.records) == 2

    record_id_set = {record.record_id for record in command_result.records}
    assert len(record_id_set) == 2

    # Repeat last search in one step.
    find_command = fms_cached.create_find_records_command(layout_name)
    find_command.add_find_criterion('Title', 'Pennsylvania 24/7')
    find_command.add_find_criterion('Title', 'New York 24/7')
    find_command.set_logical_operator(FMS_FIND_OR)
    command_result = find_command.execute()
    assert command_result.fetch_size == 2
    assert len(command_result.records) == 2

    assert record_id_set == {record.record_id for record in command_result.records}


def test_12_findany(fms_cached, layout_name):
    command = fms_cached.create_findany_record_command(layout_name)
    command_result = command.execute()

    assert len(command_result.records) == 1
    assert command_result.fetch_size == 1


def test_13_find_op_neq(fms_cached, layout_name):
    command = fms_cached.create_find_records_command(layout_name)
    command.add_find_criterion('Title', 'New York 24/7', op=FMS_FIND_OP_NEQ)
    command_result = command.execute()

    assert command_result.total_count == 12
    assert command_result.found_count == 11
    assert command_result.fetch_size == 11
    record_id_set = {record.record_id for record in command_result.records}
    assert len(record_id_set) == 11

    # # alternatively...
    # command = fms_cached.create_find_records_command(layout_name)
    # command.add_find_criterion('Title', 'omit,New York 24/7')
    # command_result = command.execute()
    # assert record_id_set == {record.record_id for record in command_result.records}


def test_14_find_op_eq(fms_cached, layout_name):
    command = fms_cached.create_find_records_command(layout_name)
    command.add_find_criterion('Title', 'New York 24/7', op=FMS_FIND_OP_EQ)
    command_result = command.execute()

    assert command_result.found_count == 1
    assert command_result.fetch_size == 1
    record_id_set = {record.record_id for record in command_result.records}
    assert len(record_id_set) == 1

    # alternatively...
    command = fms_cached.create_find_records_command(layout_name)
    command.add_find_criterion('Title', '=New York 24/7')
    command_result = command.execute()
    assert record_id_set == {record.record_id for record in command_result.records}


def test_15_find_op_cn(fms_cached, layout_name):
    command = fms_cached.create_find_records_command(layout_name)
    # Test contains 'as'
    command.add_find_criterion('Title', 'as', op=FMS_FIND_OP_CN)
    command_result = command.execute()

    assert command_result.found_count == 3
    assert command_result.fetch_size == 3
    record_id_set = {record.record_id for record in command_result.records}
    assert len(record_id_set) == 3

    # alternatively...
    command = fms_cached.create_find_records_command(layout_name)
    # Test contains 'as'
    command.add_find_criterion('Title', '*as*')
    command_result = command.execute()
    assert record_id_set == {record.record_id for record in command_result.records}


def test_16_find_op_cn(fms_cached, layout_name):
    command = fms_cached.create_find_records_command(layout_name)
    # Test begins with 'bw'
    command.add_find_criterion('Title', 'C', op=FMS_FIND_OP_BW)
    command_result = command.execute()

    assert command_result.found_count == 2
    assert command_result.fetch_size == 2


def test_17_find_op_ew(fms_cached, layout_name):
    command = fms_cached.create_find_records_command(layout_name)
    # Test ends with 'ew'
    command.add_find_criterion('Title', 'a 24/7', op=FMS_FIND_OP_EW)
    command_result = command.execute()

    assert command_result.found_count == 6
    assert command_result.fetch_size == 6
    expected = {'Alaska 24/7', 'America 24/7', 'Arizona 24/7',
                'California 24/7', 'Florida 24/7', 'Pennsylvania 24/7', }
    found = {record.get_field_value('Title') for record in command_result.records}
    assert expected == found
    record_id_set = {record.record_id for record in command_result.records}
    assert len(record_id_set) == 6

    command = fms_cached.create_find_records_command(layout_name)
    command.add_find_criterion('Title', '*a 24/7')
    command_result = command.execute()
    found = {record.get_field_value('Title') for record in command_result.records}
    assert expected == found
    assert record_id_set == {record.record_id for record in command_result.records}


def test_18_skip(fms_cached, layout_name):
    command = fms_cached.create_find_records_command(layout_name)
    command.add_sort_rule('Title', 1, FMS_SORT_ASCEND)
    command.set_skip(skip=5)
    command_result = command.execute()

    assert command_result.found_count == 12
    assert command_result.fetch_size == 7
    assert len(command_result.records) == 7

    expected = {'Florida 24/7', 'Hawaii 24/7', 'Idaho 24/7',
                'New York 24/7', 'Pennsylvania 24/7', 'Texas 24/7',
                'Washington 24/7', }
    found = {record.get_field_value('Title') for record in command_result.records}
    assert expected == found


def test_19_max(fms_cached, layout_name):
    command = fms_cached.create_find_records_command(layout_name)
    command.add_sort_rule('Title', 1, FMS_SORT_ASCEND)
    command.set_max(max_=3)
    command_result = command.execute()

    assert command_result.total_count == 12
    assert command_result.found_count == 12
    assert command_result.fetch_size == 3
    assert len(command_result.records) == 3

    expected = {'Alaska 24/7', 'America 24/7', 'Arizona 24/7', }
    found = {record.get_field_value('Title') for record in command_result.records}
    assert expected == found


def test_20_skip_max(fms_cached, layout_name):
    command = fms_cached.create_find_records_command(layout_name)
    command.add_sort_rule('Title', 1, FMS_SORT_ASCEND)
    command.set_skip(skip=5)
    command.set_max(max_=4)
    command_result = command.execute()

    assert command_result.total_count == 12
    assert command_result.found_count == 12
    assert command_result.fetch_size == 4
    assert len(command_result.records) == 4

    expected = {'Florida 24/7', 'Hawaii 24/7',
                'Idaho 24/7', 'New York 24/7', }
    found = {record.get_field_value('Title') for record in command_result.records}
    assert expected == found


def test_21_findall(fms_cached, layout_name):
    findall_command = fms_cached.create_find_records_command(layout_name)
    command_result = findall_command.execute()

    assert len(command_result.records) == 12
    assert command_result.total_count == 12
    assert command_result.fetch_size == 12
    assert command_result.found_count == 12
