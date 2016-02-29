# -*- mode: python tab-width: 4 coding: utf-8 -*-
import logging
from io import BytesIO
from urllib.parse import urlsplit

import pytest
from PIL import Image
from numpy import random

from fmxml.fms import FileMakerServer

log = logging.getLogger('test_api')

try:
    from secret import get_connection
except ImportError:
    def get_connection(name):
        return {
            'connection1': {
                'hostspec': 'http://localhost',
                'username': 'user',
                'password': 'password'
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
    connection = get_connection('connection1')
    fms_ = FileMakerServer(log_level=logging.WARN, **connection)
    fms_.set_property('db', 'FMPHP_Sample')
    return fms_


def test_01_db_names(fms):
    """
    Check that get_database_names() works and that
    the "FMPHP_Sample" is present.
    """
    connection = get_connection('connection1')
    fms = FileMakerServer(**connection)
    db_names = fms.get_db_names()

    assert isinstance(db_names, list)
    assert all([isinstance(name, str) for name in db_names])
    assert 'FMPHP_Sample' in db_names


def test_04_records(fms):
    # get all the records, there should not be many
    layout_name = 'Form View'

    find_command = fms.find_records_command(layout_name)
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
