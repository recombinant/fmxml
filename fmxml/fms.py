# -*- mode: python tab-width: 4 coding: utf-8 -*-
import logging

# Logical operators for FindCommand
from urllib.parse import urlsplit, SplitResult, urlunsplit

import requests

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

# for -relatedsets.filter
FMS_RELATEDSETS_FILTER_LAYOUT = 'layout'
FMS_RELATEDSETS_FILTER_NONE = 'none'


class FileMakerServer:
    __slots__ = ('__log', '__prop_lookup', '__requests_session', '__layout_names',
                 '__hostspec', '__db_name', '__username', '__password',)

    def __init__(self,
                 hostspec='http://localhost',
                 username='user',
                 password='password',
                 db=None,
                 log_level=logging.WARNING):
        logging.basicConfig(level=log_level)
        self.__log = logging.getLogger('FileMakerServer')
        # self.log.info('FileMakerServer.__init__()')
        self.__prop_lookup = {}
        self.__layout_names = {}
        self.__requests_session = None

        self.set_db_name(db or None)
        self.set_hostspec(hostspec)
        self.set_username(username)
        self.set_password(password)

    def close(self):
        if self.__requests_session is not None:
            self.__requests_session.close()

    @property
    def log(self):
        return self.__log

    @property
    def db_name(self):
        return self.__db_name

    @property
    def hostspec(self):
        return self.__hostspec

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    def set_db_name(self, db_name):
        self.__db_name = db_name

    def set_hostspec(self, hostspec):
        self.__hostspec = hostspec

    def set_username(self, username):
        self.__username = username

    def set_password(self, password):
        self.__password = password

    def find_record_by_id(self, layout_name, record_id):
        assert isinstance(layout_name, str)
        assert isinstance(record_id, int)
        assert record_id > 0

        command_object = self.create_find_records_command(layout_name)
        command_object.set_record_id(record_id)
        command_result = command_object.execute()

        record_list = command_result.records
        if record_list:
            return record_list[0]
        else:
            self.__log.info('Record "{}" not found in layout "{}".'.format(record_id, layout_name))
            return None

    def create_dup_record_command(self, layout_name, record_id=None):
        from fmxml.commands import DupCommand
        return DupCommand(self, layout_name, record_id)

    def create_delete_record_command(self, layout_name, record_id=None):
        from fmxml.commands import DeleteCommand
        return DeleteCommand(self, layout_name, record_id)

    def create_edit_record_command(self, layout_name, record_id=None, modification_id=None):
        from fmxml.commands import EditCommand
        return EditCommand(self, layout_name, record_id, modification_id)

    def create_find_records_command(self, layout_name):
        from fmxml.commands import FindCommand
        return FindCommand(self, layout_name)

    def create_findany_record_command(self, layout_name):
        from fmxml.commands import FindAnyCommand
        return FindAnyCommand(self, layout_name)

    def create_findquery_command(self, layout_name):
        from fmxml.commands import FindQueryCommand
        return FindQueryCommand(self, layout_name)

    def create_new_record_command(self, layout_name):
        from fmxml.commands import NewCommand
        # TODO: field container.
        return NewCommand(self, layout_name)

    def get_layout(self, layout_name):
        from fmxml.structure import Layout
        from fmxml.commands import CommandContainer, Command
        from fmxml.parsers import DataGrammarParser

        if layout_name in self.__layout_names:
            return self.__layout_names[layout_name]

        command_params = [
            Command('-db', self.db_name),
            Command('-lay', layout_name),
            Command('-view'),
        ]
        query = CommandContainer(*command_params).as_query()

        xml_bytes = self._execute(query)
        assert xml_bytes

        parser = DataGrammarParser()
        parsed_data = parser.parse(xml_bytes)
        layout = Layout(self, parsed_data)

        self.__layout_names[layout_name] = layout
        return layout

    def get_db_names(self):
        from fmxml.commands import Command
        commands = [
            Command('-dbnames'),
        ]
        return self.__get_names(commands)

    def get_layout_names(self):
        from fmxml.commands import Command
        commands = [
            Command('-db', self.db_name),
            Command('-layoutnames'),
        ]
        return self.__get_names(commands)

    def get_script_names(self):
        from fmxml.commands import Command
        commands = [
            Command('-db', self.db_name),
            Command('-scriptnames'),
        ]
        return self.__get_names(commands)

    def __get_names(self, commands):
        from fmxml.commands import CommandContainer, Command
        from fmxml.parsers import DataGrammarParser

        query = CommandContainer(*commands).as_query()

        xml_bytes = self._execute(query)
        assert xml_bytes

        parser = DataGrammarParser()
        parsed_data = parser.parse(xml_bytes)

        # Get the names directly from the parsed data.
        names = (record.fields[0].data[0] for record in parsed_data.resultset.records)
        names = filter(bool, names)
        return list(names)

    def _execute(self, query, xml_grammar='fmresultset'):
        """
        Args:
            query (str): Query part of url created elsewhere.
            xml_grammar (str): One of the available XML grammars.

        Returns:
            bytes: XML result.
        """
        assert query
        assert isinstance(query, str)
        assert xml_grammar
        assert isinstance(xml_grammar, str)

        path = '/fmi/xml/{}.xml'.format(xml_grammar)
        hostspec = self.hostspec

        sr = urlsplit(hostspec)
        sr = SplitResult(scheme=sr.scheme, netloc=sr.netloc, path=path, query=query, fragment='')
        # Join together (correctly) for xml_url.
        xml_url = urlunsplit(sr)

        self.__log.info(xml_url)

        resp = self.requests_session.get(url=xml_url)
        resp.raise_for_status()  # promulgate errors from the bowels of requests

        xml_bytes = resp.content

        return xml_bytes

    @property
    def requests_session(self):
        """
        Returns:
          request.Session: Session object. Makes repeat connects much
            faster.
        """
        # dunder __requests_session is a variable. This is a function
        # that uses that variable.

        if self.__requests_session is None:
            self.__requests_session = requests.Session()
            # The username/password relates to this instance.
            if self.username:
                self.__requests_session.auth = \
                    (self.username, self.password)

        return self.__requests_session

    def get_container_data_url(self, url_path):
        """
            url = fms.get_container_data_url(record.get_field_value('Cover Image'))

            returns

            /fmi/xml/cnt/FL-cover.jpg?-db=FMPHP_Sample&-lay=Form%20View&-recid=6&-field=Cover%20Image(1)
        """
        assert isinstance(url_path, str)
        assert url_path.lower().startswith('/fmi/xml/cnt')

        hostspec = self.hostspec
        # ----------------------------------------------------- reconstruct url
        sr1 = urlsplit(hostspec)
        sr2 = urlsplit(url_path)
        sr = SplitResult(scheme=sr1.scheme,
                         netloc=sr1.netloc,
                         path=sr2.path,
                         query=sr2.query,
                         fragment='')
        # Join together (correctly) for container_url.
        container_url = urlunsplit(sr)

        self.__log.info(container_url)
        # ---------------------------------------------------------------------
        return container_url

    def get_container_data(self, url):
        """
        Returns the data for the specified container field.
        Pass in a URL string that represents the URL for the container
        field contents. For example, get the image data from a container field
        named ``'Cover Image'``::

            container_bytes = fms.get_container_data(record.get_field_value('Cover Image'))

        In the above example the ``container_bytes`` will be a jpeg. This can be used
        in a web page by converting to base64 and embedding in the <IMG> tag::

            container_data = b64encode(container_bytes).decode('ascii', 'strict')
            image_data = 'data:image/jpg;base64,{}'.format(container_data)

        In a *jinja2* template this could then be used::

            <IMG src="{{ image_data }}">

        .. warning::

            Undefined behaviour if remote container field.

        Args:
          url (str): URL of the container field contents to get.
        Returns:
          bytes: Raw field data
        """
        assert isinstance(url, str)
        assert url.lower().startswith('/fmi/xml/cnt')

        container_url = self.get_container_data_url(url)
        # TODO: retrieve data from cache

        # --------------------------------------------------- retrieve the data
        resp = self.requests_session.get(url=container_url)
        resp.raise_for_status()  # promulgate errors from the bowels of requests

        container_bytes = resp.content
        # ---------------------------------------------------------------------
        # TODO: store data in cache

        return container_bytes
