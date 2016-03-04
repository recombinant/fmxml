# -*- mode: python tab-width: 4 coding: utf-8 -*-
import logging
from collections import OrderedDict
from io import BytesIO
from urllib.parse import urlsplit

import pytest
from PIL import Image
from numpy import random

from fmxml.commands import NewCommand
from fmxml.fms import FileMakerServer
from fmxml.structure import Record

log = logging.getLogger('test_api')

try:
    from secret import get_connection
except ImportError:
    def get_connection(name):
        return {
            'fmphp_sample': {
                'hostspec': 'http://localhost',
                'username': 'user',
                'password': 'password',
                'db': 'FMPHP_Sample',
            },
            'connection2': {
                'hostspec': 'http://localhost:80',
                'username': 'user',
                'password': 'password'
            },
            'connection3': {
                'hostspec': 'https://localhost',
                'username': 'user',
                'password': 'password'
            },
            'connection4': {
                'hostspec': 'https://localhost:443',
                'username': 'user',
                'password': 'password'
            },
        }[name]


@pytest.fixture(scope='module')
def fms():
    connection = get_connection('fmphp_sample')
    fms_ = FileMakerServer(log_level=logging.WARN, **connection)
    return fms_


@pytest.fixture()
def layout_name():
    return 'Form View'


def test_01_db_names(fms):
    """
    Check that get_database_names() works and that
    the "FMPHP_Sample" is present.
    """
    connection = get_connection('fmphp_sample')
    fms = FileMakerServer(**connection)
    db_names = fms.get_db_names()

    assert isinstance(db_names, list)
    assert all([isinstance(name, str) for name in db_names])
    assert 'FMPHP_Sample' in db_names


def test_04_records(fms, layout_name):
    # get all the records, there should not be many

    find_command = fms.create_find_records_command(layout_name)
    command_result = find_command.execute()  # -findall
    records = command_result.records

    shuffled_records = records[:]
    random.shuffle(shuffled_records)

    while shuffled_records:
        record = shuffled_records.pop()

        field_value = record.get_field_value('Cover Image')
        if field_value:
            # Check that the image has a valid URL
            url = fms.get_container_data_url(field_value)
            parts = urlsplit(url)

            # Should have everything but fragment - parts[4]
            # scheme netloc path query
            for i in range(4):
                assert parts[i] != ''

            # Get the image bytes
            container_bytes = fms.get_container_data(field_value)
            assert isinstance(container_bytes, bytes)
            assert len(container_bytes)

            # Check that it is an image
            im = Image.open(BytesIO(container_bytes))
            im.load()
            assert im.format == 'JPEG'
            break


def test_05_dup_delete1(fms, layout_name):
    # Using DeleteCommand.
    dup_command = fms.create_dup_record_command(layout_name, 5)
    command_results = dup_command.execute()
    record = command_results.records[0]

    assert command_results.total_count > 12

    record5 = fms.find_record_by_id(layout_name, 5)

    assert record.record_id != record5.record_id

    record = fms.create_findany_record_command(layout_name)
    assert command_results.total_count > 12
    command_results = record.execute()

    del_command = fms.create_delete_record_command(layout_name)

    find_result = fms.create_find_records_command(layout_name).execute()
    records = find_result.records
    total_count = find_result.total_count
    assert total_count > 12

    layout = fms.get_layout(layout_name)
    for record in records:
        field_names = [
            'Title', 'Status', 'Author', 'Publisher', 'Cover Photo Credit',
            'Description', 'Quantity in Stock', 'Number of Pages',
            'Cover Image']

        assert command_results.field_names == [
            'Title', 'Status', 'Author', 'Publisher', 'Cover Photo Credit',
            'Description', 'Quantity in Stock', 'Number of Pages', 'Cover Image']
        for field_name in field_names:
            field_definition = layout.get_field_definition(field_name)
            valuelist = field_definition.get_valuelist()
            if valuelist is None:
                continue
            value = record.get_field_value(field_name)
            assert any(item.display == value for item in valuelist)

        if record.record_id > 12:
            del_command.set_record_id(record.record_id)
            del_result = del_command.execute()
            total_count -= 1
            assert total_count == del_result.total_count

    record = fms.create_findany_record_command(layout_name)
    find_result = record.execute()
    assert find_result.total_count == 12


def test_06_dup_delete2(fms, layout_name):
    # Using the Record.delete() method.
    dup_command = fms.create_dup_record_command(layout_name, 7)
    command_results = dup_command.execute()
    record = command_results.records[0]

    assert command_results.total_count > 12

    record5 = fms.find_record_by_id(layout_name, 7)

    assert record.record_id != record5.record_id

    record = fms.create_findany_record_command(layout_name)
    command_results = record.execute()
    assert command_results.total_count > 12
    assert command_results.field_names == [
        'Title', 'Status', 'Author', 'Publisher', 'Cover Photo Credit',
        'Description', 'Quantity in Stock', 'Number of Pages', 'Cover Image']

    find_result = fms.create_find_records_command(layout_name).execute()
    records = find_result.records
    total_count = find_result.total_count
    assert total_count > 12

    for record in records:
        assert command_results.field_names == [
            'Title', 'Status', 'Author', 'Publisher', 'Cover Photo Credit',
            'Description', 'Quantity in Stock', 'Number of Pages', 'Cover Image']
        if record.record_id > 12:
            record.delete()

    record = fms.create_findany_record_command(layout_name)
    find_result = record.execute()
    assert find_result.total_count == 12


def test_07_dup_new_fqfn(fms, layout_name):
    # new Record directly accessing NewCommand.
    new_command = NewCommand(fms, layout_name)
    # The repetition is here for pedagogical purposes.
    value_table = OrderedDict([('Title(0)', 'Another Book'),
                               ('Status(0)', 'Popular'),
                               ('Author(0)', 'John Doe'),
                               ('Publisher(0)', 'Jane Doe Publishing Inc.'),
                               ('Cover Photo Credit(0)', 'Fred Bloggs'),
                               ('Description(0)', 'A boring book'),
                               ('Quantity in Stock(0)', 3000),
                               ('Number of Pages(0)', 20)])
    for k, v in value_table.items():
        new_command.add_new_fqfn(k, v)
    command_result = new_command.execute()
    assert len(command_result.records) == 1
    assert command_result.total_count == 13

    # TODO: valuelist for Status

    record1 = command_result.records[0]
    assert isinstance(record1, Record)
    for fqfn in value_table:
        field_name = fqfn[:-3]
        assert value_table[fqfn] == record1.get_field_value(field_name)

    record2 = fms.find_record_by_id(layout_name, record1.record_id)
    assert isinstance(record2, Record)
    for fqfn in value_table:
        field_name = fqfn[:-3]
        assert value_table[fqfn] == record2.get_field_value(field_name)

    assert record1.record_id == record2.record_id
    assert record1.modification_id == record2.modification_id

    record2.delete()

    record = fms.create_findany_record_command(layout_name)
    find_result = record.execute()
    assert find_result.total_count == 12


def test_08_edit_fqfn(fms, layout_name):
    record1 = fms.find_record_by_id(layout_name, 7)
    record2 = fms.create_dup_record_command(layout_name, 7).execute().records[0]
    assert isinstance(record1, Record)
    assert isinstance(record2, Record)

    title = 'Fahrenheit 451'
    assert record2.get_field_value('Title') != title

    edit_command = fms.create_edit_record_command(layout_name, record2.record_id)
    edit_command.add_edit_fqfn('Title', title)
    record3 = edit_command.execute().records[0]
    assert isinstance(record3, Record)

    assert record3.get_field_value('Title') == title
    assert record3.record_id == record2.record_id
    assert record3.modification_id > record2.modification_id

    record4 = fms.find_record_by_id(layout_name, record2.record_id)
    assert record4
    assert record4.record_id == record2.record_id
    assert record4.get_field_value('Title') == title
