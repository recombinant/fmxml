#
# coding: utf-8
#
# fmxml.parsers.data_grammar2
#
from collections import namedtuple
from contextlib import closing
from typing import List, NamedTuple
from xml.etree.ElementTree import XMLPullParser

from .grammar_base import ElemInitialiser
from .grammar_base import GrammarParserBase
from .grammar_base import RawProduct
from .grammar_base import elem_to_namedtuple

RawDatabase = namedtuple('RawDatabase', ['name', 'records', 'dateformat', 'timeformat', 'layout', ])
RawResultset = namedtuple('RawResultset', ['found', 'rows', ])
RawRow = namedtuple('RawRow', ['modid', 'recordid', 'cols', ])
RawCol = namedtuple('RawCol', ['data', ])

RawFMPXMLResult = NamedTuple('RawFMPXMLResult',
                             [('errorcode', str),
                              ('product', str),
                              ('database', RawDatabase),
                              ('fields', List[str]),
                              ('resultset', RawResultset), ])


class RawFieldDefinition(ElemInitialiser):
    # 'type' won't work as a field in namedtuple
    __slots__ = ('emptyok', 'maxrepeat', 'name', 'type',)


class DataGrammar2Parser(GrammarParserBase):
    """
    This class does nothing more than parse xml bytes obtained from
    the FileMaker® Server's Custom Web Publishing `FMPXMLRESULT` grammar.

    Everything is returned through the :py:meth:`parse` method.

    The DTD can be found at, say:
        https://localhost/fmi/xml/FMPXMLRESULT.dtd
    """
    __slots__ = ()

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
            return self._parser_read_events(parser)

    @staticmethod
    def _parser_read_events(parser):
        fmpxmlresult = None
        ns = ''  # For removal of element tag namespace.
        nsl = 0  # Length of ns

        for event, elem in parser.read_events():
            if event == 'start-ns':
                # elem == (prefix, namespaceURI)
                ns = f'{{{elem[1]}}}'
                nsl = len(ns)
                continue

            # elif event == 'end-ns':
            #     # elem == (prefix, namespaceURI)
            #     ns = ''
            #     nsl = 0
            #     continue

            # eliminate namespace from tag if present
            if ns and elem.tag.startswith(ns):
                elem.tag = elem.tag[nsl:]

            assert elem.tag in {'FMPXMLRESULT', 'ERRORCODE', 'PRODUCT', 'DATABASE', 'METADATA',
                                'FIELD', 'RESULTSET', 'ROW', 'COL', 'DATA', }

            if elem.tag == 'FMPXMLRESULT':
                if event == 'start':
                    fmpxmlresult = RawFMPXMLResult(errorcode=None,
                                                   product=None,
                                                   database=None,
                                                   fields=[],
                                                   resultset=None, )
                elif event == 'end':
                    return fmpxmlresult

            elif elem.tag == 'ERRORCODE':
                if event == 'start':
                    fmpxmlresult = fmpxmlresult._replace(errorcode=elem.text)

            elif elem.tag == 'PRODUCT':
                if event == 'start':
                    product = elem_to_namedtuple(elem, RawProduct)
                    fmpxmlresult = fmpxmlresult._replace(product=product)
                    del product

            elif elem.tag == 'DATABASE':
                if event == 'start':
                    database = elem_to_namedtuple(elem, RawDatabase)
                    fmpxmlresult = fmpxmlresult._replace(database=database)

            elif elem.tag == 'METADATA':
                if event == 'start':
                    assert isinstance(fmpxmlresult.fields, list)
                    assert not fmpxmlresult.fields

            elif elem.tag == 'FIELD':
                if event == 'start':
                    fmpxmlresult.fields.append(RawFieldDefinition(elem))

            elif elem.tag == 'RESULTSET':
                if event == 'start':
                    assert fmpxmlresult.resultset is None
                    found = elem.get('FOUND')
                    resultset = RawResultset(found=found, rows=[])
                    fmpxmlresult = fmpxmlresult._replace(resultset=resultset)
                    del found, resultset

            elif elem.tag == 'ROW':
                if event == 'start':
                    modid = elem.get('MODID')
                    recordid = elem.get('RECORDID')
                    row = RawRow(modid=modid, recordid=recordid, cols=[])
                    fmpxmlresult.resultset.rows.append(row)
                    del modid, recordid, row

            elif elem.tag == 'COL':
                if event == 'start':
                    col = RawCol(data=[])
                    fmpxmlresult.resultset.rows[-1].cols.append(col)
                    del col

            elif elem.tag == 'DATA':
                fmpxmlresult.resultset.rows[-1].cols[-1].data.append(elem.text)

            else:  # pragma: no cover
                raise AssertionError(event, elem.tag)
