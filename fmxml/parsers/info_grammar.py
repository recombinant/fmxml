#
# coding: utf-8
#
# fmxml.parsers.info_grammar
#
from collections import namedtuple
from contextlib import closing
from xml.etree.ElementTree import XMLPullParser

from .grammar_base import GrammarParserBase
from .grammar_base import RawProduct
from .grammar_base import elem_to_namedtuple

RawFMPXMLLayout = namedtuple('RawFMPXMLLayout', 'errorcode product layout raw_valuelists')
RawLayout = namedtuple('RawLayout', 'database name raw_fields')
RawField = namedtuple('RawField', 'name style')
RawStyle = namedtuple('RawStyle', 'type_ valuelist_name')
RawValuelist = namedtuple('RawValuelist', 'name raw_values')
RawValue = namedtuple('RawValue', 'display text')


class InfoGrammarParser(GrammarParserBase):
    __slots__ = ()

    def parse(self, xml_bytes):
        assert xml_bytes
        assert isinstance(xml_bytes, bytes)

        parser = XMLPullParser(['start', 'end', 'start-ns', 'end-ns'])  # ignore 'comment' & 'pi'
        with closing(parser) as parser:
            parser.feed(xml_bytes)
            return self._parser_read_events(parser)

    @staticmethod
    def _parser_read_events(parser):
        # the DTD can be found at, say:
        # http://localhost/fmi/xml/FMPXMLLAYOUT.dtd
        fmpxmllayout = None

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

            assert elem.tag in {'FMPXMLLAYOUT', 'PRODUCT', 'ERRORCODE',
                                'LAYOUT', 'FIELD', 'STYLE',
                                'VALUELISTS', 'VALUELIST', 'VALUE'}

            if elem.tag == 'FMPXMLLAYOUT':
                if event == 'start':
                    fmpxmllayout = RawFMPXMLLayout(errorcode=None,
                                                   product=None,
                                                   layout=[],
                                                   raw_valuelists=[])
                elif event == 'end':
                    return fmpxmllayout

            elif elem.tag == 'ERRORCODE':
                if event == 'start':
                    fmpxmllayout = fmpxmllayout._replace(errorcode=elem.text)

            elif elem.tag == 'PRODUCT':
                if event == 'start':
                    product = elem_to_namedtuple(elem, RawProduct)
                    fmpxmllayout = fmpxmllayout._replace(product=product)
                    del product

            elif elem.tag == 'LAYOUT':
                if event == 'start':
                    database = elem.get('DATABASE')
                    name = elem.get('NAME')
                    layout = RawLayout(database=database, name=name, raw_fields=[])
                    fmpxmllayout = fmpxmllayout._replace(layout=layout)
                    del database, name, layout

            elif elem.tag == 'FIELD':
                if event == 'start':
                    name = elem.get('NAME')
                    style = None
                    raw_field = RawField(name=name, style=style)
                    fmpxmllayout.layout.raw_fields.append(raw_field)
                    del name, style, raw_field

            elif elem.tag == 'STYLE':
                if event == 'start':
                    # TYPE will be one of these:
                    # POPUPLIST|POPUPMENU|CHECKBOX|RADIOBUTTONS|SCROLLTEXT|SELECTIONLIST|EDITTEXT|CALENDAR
                    type_ = elem.get('TYPE')
                    valuelist_name = elem.get('VALUELIST')
                    style = RawStyle(type_=type_, valuelist_name=valuelist_name)
                    assert fmpxmllayout.layout.raw_fields[-1].style is None
                    raw_field = fmpxmllayout.layout.raw_fields[-1]
                    raw_field = raw_field._replace(style=style)
                    fmpxmllayout.layout.raw_fields[-1] = raw_field
                    del type_, valuelist_name, style, raw_field

            elif elem.tag == 'VALUELISTS':
                if event == 'start':
                    assert isinstance(fmpxmllayout.raw_valuelists, list)
                    assert not fmpxmllayout.raw_valuelists

            elif elem.tag == 'VALUELIST':
                if event == 'start':
                    name = elem.get('NAME')
                    raw_valuelist = RawValuelist(name=name, raw_values=[])
                    fmpxmllayout.raw_valuelists.append(raw_valuelist)
                    del name, raw_valuelist

            elif elem.tag == 'VALUE':
                if event == 'start':
                    # append the value to the last valuelist's values list
                    display = elem.get('DISPLAY')
                    text = elem.text
                    raw_value = RawValue(display=display, text=text)
                    fmpxmllayout.raw_valuelists[-1].raw_values.append(raw_value)
                    del display, text, raw_value

            else:  # pragma: no cover
                raise AssertionError(event, elem.tag)
