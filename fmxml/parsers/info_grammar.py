# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import namedtuple
from contextlib import closing
from xml.etree.ElementTree import XMLPullParser

from .grammar_base import GrammarParserBase
from .grammar_base import RawProduct
from .grammar_base import elem_to_namedtuple

RawFMPXMLLayout = namedtuple('RawFMPXMLLayout', 'errorcode product layout valuelists')
RawLayout = namedtuple('RawLayout', 'database name fields')
RawField = namedtuple('RawField', 'name style')
RawStyle = namedtuple('RawStyle', 'type_ valuelist')
RawValuelist = namedtuple('RawValuelist', 'name values')
RawValue = namedtuple('RawValue', 'display text')


class InfoGrammarParser(GrammarParserBase):
    __slots__ = []

    def parse(self, xml_bytes):
        assert xml_bytes
        assert isinstance(xml_bytes, bytes)

        parser = XMLPullParser(['start', 'end', 'start-ns', 'end-ns'])  # ignore 'comment' & 'pi'
        with closing(parser) as parser:
            parser.feed(xml_bytes)
            return self.__parser_read_events(parser)

    def __parser_read_events(self, parser):
        # the DTD can be found at, say:
        # http://localhost/fmi/xml/FMPXMLLAYOUT.dtd
        fmpxmllayout = None

        ns = ''  # For removal of element tag namespace.
        nsl = 0  # Length of ns

        for event, elem in parser.read_events():
            if event == 'start-ns':
                # elem == (prefix, namespaceURI)
                ns = '{{{}}}'.format(elem[1])
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
                                                   valuelists=[])
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
                    layout = RawLayout(database=database, name=name, fields=[])
                    fmpxmllayout = fmpxmllayout._replace(layout=layout)
                    del database, name, layout

            elif elem.tag == 'FIELD':
                if event == 'start':
                    name = elem.get('NAME')
                    style = None
                    field = RawField(name=name, style=style)
                    fmpxmllayout.layout.fields.append(field)
                    del name, style, field

            elif elem.tag == 'STYLE':
                if event == 'start':
                    # TYPE will be one of these:
                    # POPUPLIST|POPUPMENU|CHECKBOX|RADIOBUTTONS|SCROLLTEXT|SELECTIONLIST|EDITTEXT|CALENDAR
                    type_ = elem.get('TYPE')
                    valuelist = elem.get('VALUELIST')
                    style = RawStyle(type_=type_, valuelist=valuelist)
                    assert fmpxmllayout.layout.fields[-1].style is None
                    field = fmpxmllayout.layout.fields[-1]
                    field = field._replace(style=style)
                    fmpxmllayout.layout.fields[-1] = field
                    del type_, valuelist, style

            elif elem.tag == 'VALUELISTS':
                if event == 'start':
                    assert isinstance(fmpxmllayout.valuelists, list)
                    assert not fmpxmllayout.valuelists

            elif elem.tag == 'VALUELIST':
                if event == 'start':
                    name = elem.get('NAME')
                    valuelist = RawValuelist(name=name, values=[])
                    fmpxmllayout.valuelists.append(valuelist)
                    del name, valuelist

            elif elem.tag == 'VALUE':
                if event == 'start':
                    # append the value to the last valuelist's values list
                    display = elem.get('DISPLAY')
                    text = elem.text
                    value = RawValue(display=display, text=text)
                    fmpxmllayout.valuelists[-1].values.append(value)
                    del display, text, value

            else:  # pragma: no cover
                raise AssertionError(event, elem.tag)
