#!/usr/bin/env python3
# -*- mode: python tab-width: 4 coding: utf-8 -*-
import logging
import os
import re
from pathlib import Path

from fmxml.parsers import DataGrammarParser
from fmxml.parsers import DataGrammar2Parser
from fmxml.parsers import InfoGrammarParser

__author__ = "recombinant"
__copyright__ = "recombinant"
__license__ = "BSD"

logging.basicConfig(level=logging.DEBUG)


def test_data_grammar_db():
    path = Path(__file__).parent / 'data' / 'fmresultset-dbnames.xml'
    fmresultset = _get_data_grammar_from_file(path)

    assert fmresultset.datasource.database == 'DBNAMES'
    # assert fmresultset.datasource.total_count == '1'
    assert len(fmresultset.field_definitions) == 1
    assert fmresultset.field_definitions[0].name == 'DATABASE_NAME'
    # assert fmresultset.resultset.count == '1'
    # assert fmresultset.resultset.fetch_size == '1'
    # assert len(fmresultset.resultset.records) == 1
    assert len(fmresultset.resultset.records[0].fields) == 1
    assert fmresultset.resultset.records[0].fields[0].name == 'DATABASE_NAME'
    assert fmresultset.resultset.records[0].fields[0].data == ['FMPHP_Sample', ]


def test_data_grammar_layout():
    path = Path(__file__).parent / 'data' / 'fmresultset-db=FMPHP_Sample&-layoutnames.xml'
    fmresultset = _get_data_grammar_from_file(path)
    assert fmresultset.datasource.database == 'FMPHP_Sample'
    assert fmresultset.datasource.total_count == '6'
    assert len(fmresultset.field_definitions) == 1
    assert fmresultset.field_definitions[0].name == 'LAYOUT_NAME'
    assert fmresultset.resultset.count == '6'
    assert fmresultset.resultset.fetch_size == '6'
    assert len(fmresultset.resultset.records) == 6
    assert all(len(record.fields) == 1 for record in fmresultset.resultset.records)
    assert all(record.fields[0].name == 'LAYOUT_NAME' for record in fmresultset.resultset.records)
    assert fmresultset.resultset.records[0].fields[0].data == ['English', ]


def test_info_grammar():
    path = Path(__file__).parent / 'data' / 'FMPXMLLAYOUT-db=FMPHP_Sample&-lay=Form View&-view.xml'
    _get_info_grammar_from_file(path)


def test_coverage():
    log = logging.getLogger('test_coverage')
    # Just ramp up the coverage. No actual testing.
    root = Path(__file__).parent / 'data'
    for path in root.glob('fmresultset*.xml'):
        fmresultset = _get_data_grammar_from_file(path)
        del fmresultset

    for path in root.glob('FMPXMLRESULT*.xml'):
        xml_bytes = path.open('rb').read()
        parser = DataGrammar2Parser()
        fmpxmlresult = parser.parse(xml_bytes)
        assert fmpxmlresult
        del fmpxmlresult

    for path in root.glob('FMPXMLLAYOUT*.xml'):
        fmpxmllayout = _get_info_grammar_from_file(path)
        del fmpxmllayout


def _get_info_grammar_from_file(xml_path):
    xml_path = str(xml_path)
    if os.name == 'nt':
        # Need to check for overly long file names.
        if not xml_path.startswith('\\\\?\\') and len(xml_path) > 260:
            if not re.match(r'\A[a-z]:\\', xml_path, re.I):
                raise AssertionError('path length too long: {!r}'.format(xml_path))
            xml_path = r'\\?\{}'.format(xml_path)

    xml_bytes = open(xml_path, 'rb').read()
    parser = InfoGrammarParser()
    fmpxmllayout = parser.parse(xml_bytes)
    assert fmpxmllayout
    return fmpxmllayout


def _get_data_grammar_from_file(xml_path):
    xml_path = str(xml_path)
    if os.name == 'nt':
        # Need to check for overly long file names.
        if not xml_path.startswith('\\\\?\\') and len(xml_path) > 260:
            if not re.match(r'\A[a-z]:\\', xml_path, re.I):
                raise AssertionError('path length too long: {!r}'.format(xml_path))
            xml_path = r'\\?\{}'.format(xml_path)

    xml_bytes = open(xml_path, 'rb').read()
    parser = DataGrammarParser()
    fmresultset = parser.parse(xml_bytes)
    assert fmresultset
    return fmresultset
