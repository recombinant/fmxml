#
# coding: utf-8
#
# fmxml.fms
#
import logging
from urllib.parse import urlsplit, SplitResult, urlunsplit

import requests

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

# for -relatedsets.filter
FMS_RELATEDSETS_FILTER_LAYOUT = 'layout'
FMS_RELATEDSETS_FILTER_NONE = 'none'


class FileMakerServer:
    __slots__ = ('_log', '_prop_lookup', '_requests_session', '_layout_lookup',
                 '_hostspec', '_db_name', '_username', '_password',)

    def __init__(self,
                 hostspec,  # e.g. http://localhost
                 username,
                 password,
                 db=None):
        self._log = logging.getLogger(__name__)
        # self.log.info('FileMakerServer.__init__()')
        self._prop_lookup = {}
        self._layout_lookup = {}
        self._hostspec = None
        self._username = None
        self._password = None
        self._db_name = None
        self._requests_session = None

        self.hostspec = hostspec
        self.username = username
        self.password = password
        self.db_name = db or None

    def close(self):
        if self._requests_session is not None:
            self._requests_session.close()

    @property
    def log(self):
        return self._log

    def _get_db_name(self):
        return self._db_name

    def _set_db_name(self, db_name):
        self._db_name = db_name

    db_name = property(fget=_get_db_name, fset=_set_db_name)

    def _get_hostspec(self):
        return self._hostspec

    def _set_hostspec(self, hostspec):
        self._hostspec = hostspec

    hostspec = property(fget=_get_hostspec, fset=_set_hostspec)

    def _get_username(self):
        return self._username

    def _set_username(self, username):
        self._username = username

    username = property(fget=_get_username, fset=_set_username)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = password

    password = property(fget=_get_password, fset=_set_password)

    def find_record_by_id(self, layout_name, record_id):
        assert isinstance(layout_name, str)
        assert isinstance(record_id, int)
        assert record_id > 0

        command_object = self.create_find_records_command(layout_name)
        command_object.record_id = record_id
        command_result = command_object.execute()

        record_list = command_result.records
        if record_list:
            return record_list[0]
        else:
            self._log.info('Record "{}" not found in layout "{}".'.format(record_id, layout_name))
            return None

    def create_dup_record_command(self, layout_name, record_id=None):
        from .commands import DupCommand
        return DupCommand(self, layout_name, record_id)

    def create_delete_record_command(self, layout_name, record_id=None):
        from .commands import DeleteCommand
        return DeleteCommand(self, layout_name, record_id)

    def create_edit_record_command(self, layout_name, record_id=None, modification_id=None):
        from .commands import EditCommand
        return EditCommand(self, layout_name, record_id, modification_id)

    def create_find_records_command(self, layout_name):
        from .commands import FindCommand
        return FindCommand(self, layout_name)

    def create_findany_record_command(self, layout_name):
        from .commands import FindAnyCommand
        return FindAnyCommand(self, layout_name)

    def create_findquery_command(self, layout_name):
        from .commands import FindQueryCommand
        return FindQueryCommand(self, layout_name)

    def create_new_record_command(self, layout_name):
        from .commands import NewCommand
        # TODO: field container.
        return NewCommand(self, layout_name)

    def get_layout(self, layout_name):
        from .structure import Layout
        from .commands import CommandContainer, Command
        from .parsers import DataGrammarParser

        if layout_name in self._layout_lookup:
            return self._layout_lookup[layout_name]

        command_params = [
            Command('-db', self.db_name),
            Command('-lay', layout_name),
            Command('-view'),
        ]
        query = CommandContainer(*command_params).as_query()

        xml_bytes = self.execute_query(query)
        assert xml_bytes

        parser = DataGrammarParser()
        parsed_data = parser.parse(xml_bytes)
        layout = Layout(self, parsed_data)

        self._layout_lookup[layout_name] = layout
        return layout

    def get_db_names(self):
        from .commands import Command
        commands = [
            Command('-dbnames'),
        ]
        return self._get_names(commands)

    def get_layout_names(self):
        from .commands import Command
        commands = [
            Command('-db', self.db_name),
            Command('-layoutnames'),
        ]
        return self._get_names(commands)

    def get_script_names(self):
        from .commands import Command
        commands = [
            Command('-db', self.db_name),
            Command('-scriptnames'),
        ]
        return self._get_names(commands)

    def _get_names(self, commands):
        from .commands import CommandContainer
        from .parsers import DataGrammarParser

        query = CommandContainer(*commands).as_query()

        xml_bytes = self.execute_query(query)
        assert xml_bytes

        parser = DataGrammarParser()
        parsed_data = parser.parse(xml_bytes)

        # Get the names directly from the parsed data.
        names = (record.fields[0].data[0] for record in parsed_data.resultset.records)
        names = filter(bool, names)
        return list(names)

    def execute_query(self, query, xml_grammar='fmresultset'):
        """
        Args:
            query: Query part of url created elsewhere. 
            xml_grammar: One of the available XML grammars. 
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

        self._log.info(xml_url)

        resp = self.requests_session.get(url=xml_url, auth=(self.username, self.password))
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
        # dunder _requests_session is a variable. This is a function
        # that uses that variable.

        if self._requests_session is None:
            self._requests_session = requests.Session()
            # The username/password relates to this instance.
            if self.username:
                self._requests_session.auth = (self.username, self.password)

        return self._requests_session

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
        sr = SplitResult(scheme=sr1.scheme, netloc=sr1.netloc, path=sr2.path, query=sr2.query, fragment='')
        # Join together (correctly) for container_url.
        container_url = urlunsplit(sr)

        self._log.info(container_url)
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
        resp = self.requests_session.get(url=container_url, auth=(self.username, self.password))
        resp.raise_for_status()  # promulgate errors from the bowels of requests

        container_bytes = resp.content
        # ---------------------------------------------------------------------
        # TODO: store data in cache

        return container_bytes
