# -*- mode: python tab-width: 4 coding: utf-8 -*-
from collections import namedtuple, OrderedDict

from .base_command import BaseCommand
from .mixins import SortRulesMixin, FoundSetMixin, \
    ScriptsMixin, PreFindScriptsMixin, PreSortScriptsMixin

FindQuery = namedtuple('FindQuery', 'field_name test_value')


class FindRequestDefinition:
    def __init__(self, queries, omit=False):
        assert queries
        assert isinstance(queries, list)
        assert all(isinstance(query, FindQuery) for query in queries)

        self.queries = queries
        self.omit = omit


class FindQueryCommand(FoundSetMixin,
                       SortRulesMixin,
                       ScriptsMixin,
                       PreFindScriptsMixin,
                       PreSortScriptsMixin,
                       BaseCommand):
    __slots__ = ('__request_definitions',)

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)

        self.__request_definitions = []

    def add_request_definitions(self, request_definition1, request_definition2, *args):
        assert not self.__request_definitions
        assert isinstance(request_definition1, FindRequestDefinition)
        assert isinstance(request_definition2, FindRequestDefinition)
        assert all([isinstance(request, FindRequestDefinition) for request in args])

        self.__request_definitions.append(request_definition1)
        self.__request_definitions.append(request_definition2)
        for request_definition in args:
            self.__request_definitions.append(request_definition)

    def get_query(self):
        """
        Returns the URL query. Nothing to do with the FindQuery's query logic.
        """
        assert self.__request_definitions
        command_params = super().get_command_params()

        query_id = 1

        # List of requests e.g. ['(q1)', '!(q2), '(q3,q4)']
        request_list = []
        # For adding to command_params.
        params = OrderedDict()

        for rd in self.__request_definitions:
            query_list = []  # list of qN for this request

            for field_name, test_value in rd.queries:
                params['-q{}'.format(query_id)] = field_name
                params['-q{}.value'.format(query_id)] = test_value
                query_list.append('q{}'.format(query_id))
                query_id += 1

            exclamation = '!' if rd.omit else ''
            query_string = ','.join(query_list)  # e.g. q1,q2
            # e.g. !(q1,q2)
            request_string = '{}({})'.format(exclamation, query_string)
            request_list.append(request_string)

        request_declaration = ';'.join(request_list)

        command_params['-query'] = request_declaration

        # Request definitions in pairs of field_name + value.
        # e.g. {'-q1': 'typeofanimal', '-q1.value': 'Cat'}
        for k, v in params.items():
            command_params[k] = v

        command_params['-findquery'] = None
        return command_params.as_query()
