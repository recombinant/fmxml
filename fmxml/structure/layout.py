# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import OrderedDict
from typing import Dict, List

from . import field_definition as fd_module
from . import portal as portal_module
from .. import commands as commands_module
from .. import parsers as parsers_module
from .. import structure as structure_module
from .. import fms as fms_module


class Layout:
    __slots__ = ('__fms',
                 '__name',
                 '__database_name',
                 '__date_format',
                 '__time_format',
                 '__timestamp_format',
                 '__field_definition_lookup',
                 '__valuelists',
                 '__portals',)

    def __init__(self, fms: 'fms_module.FileMakerServer', parsed_data):

        self.__fms = fms  # type: fms_module.FileMakerServer
        self.__field_definition_lookup = OrderedDict()  # type: Dict[str, fd_module.FieldDefinition]
        self.__valuelists = {}  # type: Dict[str, structure_module.Valuelist]
        self.__portals = {}  # type: Dict[str, portal_module.Portal]

        datasource = parsed_data.datasource
        self.__name: str = datasource.layout
        self.__database_name: str = datasource.database
        self.__date_format: str = datasource.date_format
        self.__time_format: str = datasource.time_format
        self.__timestamp_format: str = datasource.timestamp_format

        field_definitions = parsed_data.field_definitions
        for field_definition in field_definitions:
            field_definition = fd_module.FieldDefinition(self, field_definition)
            # field definitions can be duplicated (they should be the same)
            self.__field_definition_lookup[field_definition.field_name] = field_definition

        # TODO: move to Portal.
        portal_definitions_lookup = parsed_data.relatedset_definitions
        for table_name, field_definitions in portal_definitions_lookup.items():
            portal = portal_module.Portal(self, table_name)

            for field_definition in field_definitions:
                field_definition = fd_module.FieldDefinition(self, field_definition, portal)

                # Add it to the layout there should be :: in it, so there won't be an collision
                # Used by FMLayer.get_definition()
                self.__field_definition_lookup[field_definition.field_name] = field_definition

                # Add it to the portal anyway, used in FieldContainer
                portal.add_field_definition_(field_definition.field_name, field_definition)

            self._add_portal(portal.table_name, portal)

        self.__load_fmpxmllayout()

    @property
    def fms(self):
        return self.__fms

    @property
    def name(self) -> str:
        return self.__name

    @property
    def database_name(self) -> str:
        return self.__database_name

    def has_field_definition(self, field_name: str) -> bool:
        return field_name in self.__field_definition_lookup

    def get_field_definition(self, field_name: str) -> 'fd_module.FieldDefinition':
        """
        Args:
            field_name (str): Name of field.

        Returns:
            `FieldDefinition`: Field definition relating to this field.
        """
        return self.__field_definition_lookup[field_name]

    @property
    def field_names(self) -> List[str]:
        return list(self.__field_definition_lookup)

    def get_valuelist(self, valuelist_name: str) -> 'structure_module.Valuelist':
        return self.__valuelists[valuelist_name]

    def __load_fmpxmllayout(self):
        """
        Load the value lists (if any). This only happens when the layout
        is loaded. Each layout is only loaded once (by name).
        """
        # The manual states that 'record_id' can be used as a
        # parameter, though there's no need here...
        record_id = None

        if record_id:
            # The manual (page 55) says you can do this...
            command_params = [
                commands_module.Command('-db', self.__fms.db_name),
                commands_module.Command('-lay', self.__name),
                commands_module.Command('-recid', record_id),
                commands_module.Command('-view'), ]
        else:
            # But as the layer is being read, only this is required...
            command_params = [
                commands_module.Command('-db', self.__fms.db_name),
                commands_module.Command('-lay', self.__name),
                commands_module.Command('-view'), ]

        # ------------------------------------------------- read in the grammar
        query = commands_module.CommandContainer(*command_params).as_query()
        xml_bytes = self.__fms.execute_(query, xml_grammar='FMPXMLLAYOUT')
        assert xml_bytes

        parser = parsers_module.InfoGrammarParser()
        fmpxmllayout = parser.parse(xml_bytes)
        # ---------------------------------------- add the value lists (if any)
        for raw_field in fmpxmllayout.layout.raw_fields:
            # style_type = raw_field.style.type_
            valuelist_name = raw_field.style.valuelist_name
            if valuelist_name:
                field_name = raw_field.name
                field_definition = self.get_field_definition(field_name)
                field_definition.set_valuelist_name_(valuelist_name)

        for raw_valuelist in fmpxmllayout.raw_valuelists:
            name = raw_valuelist.name
            raw_values = raw_valuelist.raw_values

            self.__valuelists[name] = structure_module.Valuelist(name, raw_values)

    @property
    def date_format(self) -> str:
        return self.__date_format

    @property
    def time_format(self) -> str:
        return self.__time_format

    @property
    def timestamp_format(self) -> str:
        return self.__timestamp_format

    def _add_portal(self, table_name: str, portal):
        self.__portals[table_name] = portal

    @property
    def portal_names(self) -> List[str]:
        return list(self.__portals)
