# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import defaultdict, namedtuple
from contextlib import closing
from xml.etree.ElementTree import XMLPullParser

from .grammar_base import ElemInitialiser
from .grammar_base import GrammarParserBase
from .grammar_base import RawProduct
from .grammar_base import elem_to_namedtuple


class RawFMResultSet(ElemInitialiser):
    __slots__ = ['version', 'xmlns', 'error', 'product', 'datasource', 'resultset',
                 'field_definitions', 'relatedset_definitions']

    def __init__(self, elem):
        super().__init__(elem)
        self.error = \
            self.product = \
            self.datasource = \
            self.resultset = None  # These are in metadata
        self.field_definitions = []
        self.relatedset_definitions = defaultdict(list)


RawError = namedtuple('RawError', 'code')
RawDataSource = namedtuple(
    'RawDataSource',
    'database date_format layout table time_format timestamp_format total_count')


class RawFieldDefinition(ElemInitialiser):
    __slots__ = ['auto_enter', 'four_digit_year', 'global', 'max_repeat', 'name', 'not_empty',
                 'numeric_only', 'max_characters', 'result', 'time_of_day', 'type']

    def __init__(self, elem):
        super().__init__(elem)
        # max-characters is #IMPLIED in the DTD
        if not hasattr(self, 'max_characters'):
            self.max_characters = None


class RawResultSet(ElemInitialiser):
    __slots__ = ['count', 'fetch_size', 'records']

    def __init__(self, elem):
        super().__init__(elem)
        self.records = []


class RawRecord(ElemInitialiser):
    __slots__ = ['record_id', 'mod_id', 'fields', 'relatedsets']

    def __init__(self, elem):
        super().__init__(elem)
        self.fields = []
        self.relatedsets = {}


class RawField(ElemInitialiser):
    __slots__ = ['name', 'data']

    def __init__(self, elem):
        super().__init__(elem)
        self.data = []


class DataGrammarParser(GrammarParserBase):
    """
    This class does nothing more than parse xml bytes obtained from
    the FileMaker® Server's Custom Web Publishing `fmresultset` grammar.

    Everything is returned through the :py:meth:`parse` method.

    The DTD can be found at, say:
        https://localhost/fmi/xml/fmresultset.dtd
    """
    __slots__ = []

    def parse(self, xml_bytes):
        """
        Given *xml_bytes* return the data as a tree of Python objects.

        Args:
            xml_bytes (bytes): Byte string of XML data.

        Returns:
            results
        """
        assert xml_bytes
        assert isinstance(xml_bytes, bytes)

        parser = XMLPullParser(['start', 'end', 'start-ns', 'end-ns'])  # ignore 'comment' & 'pi'

        with closing(parser) as parser:
            parser.feed(xml_bytes)
            return self.__parser_read_events(parser)

    def __parser_read_events(self, parser):
        table_name = parent_raw_record = current_raw_record = None

        ns = ''  # For removal of element tag namespace.
        nsl = 0  # Length of ns

        for event, elem in parser.read_events():

            if event == 'start-ns':
                # elem == (prefix, namespaceURI)
                ns = '{{{}}}'.format(elem[1])
                nsl = len(ns)
                continue

            # elif event == 'end-ns':
            #     ns = ''
            #     nsl = 0
            #     continue

            # eliminate namespace from tag if present
            if ns and elem.tag.startswith(ns):
                elem.tag = elem.tag[nsl:]

            assert elem.tag in {'fmresultset', 'error', 'product', 'datasource',
                                'metadata', 'relatedset-definition', 'field-definition',
                                'resultset', 'relatedset', 'record', 'field', 'data', }

            if elem.tag == 'fmresultset':
                if event == 'start':
                    fmresultset = RawFMResultSet(elem)
                elif event == 'end':
                    return fmresultset

            elif elem.tag == 'error':
                if event == 'start':
                    raw_error = elem_to_namedtuple(elem, RawError)
                    fmresultset.error = raw_error

            elif elem.tag == 'product':
                if event == 'start':
                    raw_product = elem_to_namedtuple(elem, RawProduct)
                    fmresultset.product = raw_product

            elif elem.tag == 'datasource':
                if event == 'start':
                    raw_datasource = elem_to_namedtuple(elem, RawDataSource)
                    fmresultset.datasource = raw_datasource

            elif elem.tag == 'metadata':
                if event == 'start':
                    # The metadata tag is superfluous.
                    # It can be removed and its children can be moved
                    # to its parent.
                    pass

            elif elem.tag == 'relatedset-definition':
                if event == 'start':
                    table_name = elem.get('table')
                    assert table_name not in fmresultset.relatedset_definitions
                    fmresultset.relatedset_definitions[table_name] = []
                elif event == 'end':
                    table_name = None

            elif elem.tag == 'field-definition':
                if event == 'start':
                    raw_field_definition = RawFieldDefinition(elem)
                    if table_name is None:
                        fmresultset.field_definitions.append(raw_field_definition)
                    else:
                        fmresultset.relatedset_definitions[table_name].append(raw_field_definition)

            elif elem.tag == 'resultset':
                if event == 'start':
                    raw_resultset = RawResultSet(elem)
                    fmresultset.resultset = raw_resultset

            elif elem.tag == 'relatedset':
                if event == 'start':
                    table_name = elem.get('table')
                    parent_raw_record = current_raw_record  # push
                    current_raw_record = None  # ------------ push
                    assert table_name not in parent_raw_record.relatedsets
                    parent_raw_record.relatedsets[table_name] = []
                elif event == 'end':
                    table_name = None
                    current_raw_record = parent_raw_record  # pop
                    parent_raw_record = None  # ------------- pop

            elif elem.tag == 'record':
                if event == 'start':
                    current_raw_record = RawRecord(elem)

                elif event == 'end':
                    if table_name is None:
                        fmresultset.resultset.records.append(current_raw_record)
                    else:
                        parent_raw_record.relatedsets[table_name].append(current_raw_record)
                    current_raw_record = None

            elif elem.tag == 'field':
                if event == 'start':
                    # There may be more than one repetition of a field in a layout.
                    current_raw_record.fields.append(RawField(elem))

            elif elem.tag == 'data':
                if event == 'end':  # get the text
                    current_raw_record.fields[-1].data.append(elem.text)

            else:  # pragma: no cover
                raise AssertionError(event, elem.tag)
