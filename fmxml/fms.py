# -*- mode: python tab-width: 4 coding: utf-8 -*-
import logging

# Logical operators for FindCommand
FMS_FIND_AND = 'and'
FMS_FIND_OR = 'or'

# Sort direction for FindCommand
FMS_SORT_ASCEND = 'ascend'
FMS_SORT_DESCEND = 'descend'

# Find op constants
#
FMS_FIND_OP_EQ = 'eq'  # =word
FMS_FIND_OP_NEQ = 'neq'  # omit, word
FMS_FIND_OP_GT = 'gt'  # > word
FMS_FIND_OP_GTE = 'gte'  # >= word
FMS_FIND_OP_LT = 'lt'  # < word
FMS_FIND_OP_LTE = 'lte'  # <= word
FMS_FIND_OP_CN = 'cn'  # *word*
FMS_FIND_OP_BW = 'bw'  # word*
FMS_FIND_OP_EW = 'ew'  # *word


class FileMakerServer:
    __slots__ = ['__log', '__prop_lookup', ]

    def __init__(self, log_level=logging.WARNING):
        logging.basicConfig(level=log_level)
        self.__log = logging.getLogger('FileMakerServer')
        # self.log.info('FileMakerServer.__init__()')
        self.__prop_lookup = {}

    def set_property(self, prop_name, value):
        """
        Args:
            prop_name (str): Name of the property to set.
            value: Value of the property to set.
        """
        self.__prop_lookup[prop_name] = value

    def get_property(self, prop_name):
        """
        Args:
            prop_name (str): Name of the property to get.

        Returns:
            Value of property `prop_name` or `None` if it does
            not exist.
        """
        return self.__prop_lookup.get(prop_name, None)
