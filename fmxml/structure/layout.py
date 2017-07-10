#
# coding: utf-8
#
# fmxml.structure.layout
#
from collections import OrderedDict

from . import field_definition as fd_module
from . import portal as portal_module
from . import valuelist as valuelist_module
from .. import commands as commands_module
from .. import parsers as parsers_module


class Layout:
    __slots__ = ('_fms',
                 '_name',
                 '_database_name',
                 '_date_format',
                 '_time_format',
                 '_timestamp_format',
                 '_field_definition_lookup',
                 '_valuelists',
                 '_portals',)

    def __init__(self, fms, parsed_data):

        self._fms = fms
        self._field_definition_lookup = OrderedDict()
        self._valuelists = {}
        self._portals = {}

        datasource = parsed_data.datasource
        self._name = datasource.layout
        self._database_name = datasource.database
        self._date_format = datasource.date_format
        self._time_format = datasource.time_format
        self._timestamp_format = datasource.timestamp_format

        field_definitions = parsed_data.field_definitions
        for field_definition in field_definitions:
            field_definition = fd_module.FieldDefinition(self, field_definition)
            # field definitions can be duplicated (they should be the same)
            self._field_definition_lookup[field_definition.field_name] = field_definition

        # TODO: move to Portal.
        portal_definitions_lookup = parsed_data.relatedset_definitions
        for table_name, field_definitions in portal_definitions_lookup.items():
            portal = portal_module.Portal(self, table_name)  # type: portal_module.Portal

            for field_definition in field_definitions:
                field_definition = fd_module.FieldDefinition(self, field_definition, portal)

                # Add it to the layout there should be :: in it, so there won't be an collision
                # Used by FMLayer.get_definition()
                self._field_definition_lookup[field_definition.field_name] = field_definition

                # Add it to the portal anyway, used in FieldContainer
                portal.add_field_definition_(field_definition.field_name, field_definition)

            self._add_portal(portal.table_name, portal)

        self._load_fmpxmllayout()

    @property
    def fms(self):
        return self._fms

    @property
    def name(self):
        return self._name

    @property
    def database_name(self):
        return self._database_name

    def has_field_definition(self, field_name):
        return field_name in self._field_definition_lookup

    def get_field_definition(self, field_name):
        """
        Args:
            field_name: Name of field.

        Returns:
            `FieldDefinition`: Field definition relating to this field.
        """
        return self._field_definition_lookup[field_name]

    @property
    def field_names(self):
        return list(self._field_definition_lookup)

    def get_valuelist(self, valuelist_name):
        return self._valuelists[valuelist_name]

    def _load_fmpxmllayout(self):
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
                commands_module.Command('-db', self._fms.db_name),
                commands_module.Command('-lay', self._name),
                commands_module.Command('-recid', record_id),
                commands_module.Command('-view'), ]
        else:
            # But as the layer is being read, only this is required...
            command_params = [
                commands_module.Command('-db', self._fms.db_name),
                commands_module.Command('-lay', self._name),
                commands_module.Command('-view'), ]

        # ------------------------------------------------- read in the grammar
        query = commands_module.CommandContainer(*command_params).as_query()
        xml_bytes = self._fms.execute_query(query, xml_grammar='FMPXMLLAYOUT')
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

            self._valuelists[name] = valuelist_module.Valuelist(name, raw_values)

    @property
    def date_format(self):
        return self._date_format

    @property
    def time_format(self):
        return self._time_format

    @property
    def timestamp_format(self):
        return self._timestamp_format

    def _add_portal(self, table_name, portal):
        self._portals[table_name] = portal

    @property
    def portal_names(self):
        return list(self._portals)
