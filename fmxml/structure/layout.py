# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import OrderedDict


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

    def __init__(self, fms, parsed_data):
        from .field_definition import FieldDefinition
        from .portal import Portal

        self.__fms = fms
        self.__field_definition_lookup = OrderedDict()  # name : FieldDefinition
        self.__valuelists = {}  # name : Valuelist
        self.__portals = {}  # name: Portal

        datasource = parsed_data.datasource
        self.__name = datasource.layout
        self.__database_name = datasource.database
        self.__date_format = datasource.date_format
        self.__time_format = datasource.time_format
        self.__timestamp_format = datasource.timestamp_format

        field_definitions = parsed_data.field_definitions
        for field_definition in field_definitions:
            # attrs is a named type
            field_definition = FieldDefinition(self, field_definition)
            # field definitions can be duplicated (they should be the same)
            self.__field_definition_lookup[field_definition.field_name] = field_definition

        # TODO: move to Portal.
        portal_definitions_lookup = parsed_data.relatedset_definitions
        for table_name, field_definitions in portal_definitions_lookup.items():
            portal = Portal(self, table_name)

            for field_definition in field_definitions:
                field_definition = FieldDefinition(self, field_definition, portal)

                # Add it to the layout there should be :: in it, so there won't be an collision
                # Used by FMLayer.get_definition()
                self.__field_definition_lookup[field_definition.field_name] = field_definition

                # Add it to the portal anyway, used in FieldContainer
                portal._add_field_definition(field_definition.field_name, field_definition)

            self._add_portal(portal.table_name, portal)

        self.__load_fmpxmllayout()

    @property
    def fms(self):
        return self.__fms

    @property
    def name(self):
        return self.__name

    @property
    def database_name(self):
        return self.__database_name

    def has_field_definition(self, field_name):
        return field_name in self.__field_definition_lookup

    def get_field_definition(self, field_name):
        """
        Args:
            field_name (str): Name of field.

        Returns:
            `FieldDefinition`: Field definition relating to this field.
        """
        return self.__field_definition_lookup[field_name]

    @property
    def field_names(self):
        return list(self.__field_definition_lookup)

    def get_valuelist(self, valuelist_name):
        return self.__valuelists[valuelist_name]

    def __load_fmpxmllayout(self):
        """
        Load the value lists (if any). This only happens when the layout
        is loaded. Each layout is only loaded once (by name).
        """
        from ..commands import Command, CommandContainer

        # The manual states that 'record_id' can be used as a
        # parameter, though there's no need here...
        record_id = None

        if record_id:
            # The manual (page 55) says you can do this...
            command_params = [
                Command('-db', self.__fms.db_name),
                Command('-lay', self.__name),
                Command('-recid', record_id),
                Command('-view'), ]
        else:
            # But as the layer is being read, only this is required...
            command_params = [
                Command('-db', self.__fms.db_name),
                Command('-lay', self.__name),
                Command('-view'), ]

        # ------------------------------------------------- read in the grammar
        query = CommandContainer(*command_params).as_query()
        xml_bytes = self.__fms._execute(query, xml_grammar='FMPXMLLAYOUT')
        assert xml_bytes

        from ..parsers import InfoGrammarParser

        parser = InfoGrammarParser()
        fmpxmllayout = parser.parse(xml_bytes)
        # ---------------------------------------- add the value lists (if any)
        for raw_field in fmpxmllayout.layout.raw_fields:
            # style_type = raw_field.style.type_
            valuelist_name = raw_field.style.valuelist_name
            if valuelist_name:
                field_name = raw_field.name
                field_definition = self.get_field_definition(field_name)
                field_definition._set_valuelist_name(valuelist_name)

        from ..structure import Valuelist

        for raw_valuelist in fmpxmllayout.raw_valuelists:
            name = raw_valuelist.name
            raw_values = raw_valuelist.raw_values

            self.__valuelists[name] = Valuelist(name, raw_values)

    @property
    def date_format(self):
        return self.__date_format

    @property
    def time_format(self):
        return self.__time_format

    @property
    def timestamp_format(self):
        return self.__timestamp_format

    def _add_portal(self, table_name, portal):
        self.__portals[table_name] = portal

    @property
    def portal_names(self):
        return list(self.__portals)
