# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import namedtuple


def elem_to_namedtuple(elem, tuple_class=None):
    """
    Converts an etree elem leaf instance's items into a dictionary
    suitable for use initialising a namedtuple by replacing '-' with '_'
    and rejigging reserved words. So::

        fetch-size

    becomes::

        fetch_size

    This dictionary is then used to create an instance of `tuple_class`
    which is returned.

    Parameters:
      elem (:py:class:`xml.etree.ElementTree.Element`): Object instance to
        be converted.
      tuple_class: A namedtuple class, an instance of which is to be created
        and returned.

    Returns:
        Instance of `tuple_class`.
    """
    intermediate_dict = {k.lower().replace('-', '_'): v for k, v in elem.items()}
    return tuple_class(**intermediate_dict)


class ElemInitialiser:
    """
    Similar to :py:func:`elem_to_namedtuple`, but initialises the
    class members rather than a namedtuple.
    """

    def __init__(self, elem):
        for k, v in elem.items():
            k = k.replace('-', '_')
            setattr(self, k, v)


RawProduct = namedtuple('RawProduct', 'build name version')


class GrammarParserBase:
    def parse(self, xml_bytes):  # pragma: no cover
        raise NotImplementedError
