#
# coding: utf-8
#
# Stubs for fmxml.fms
#
from logging import Logger
from typing import List, Optional, Dict, Any

import requests

from .commands import command_container as command_container_module
from .commands import delete_command as delete_command_module
from .commands import dup_command as dup_command_module
from .commands import edit_command as edit_command_module
from .commands import find_command as find_command_module
from .commands import findany_command as findany_command_module
from .commands import findquery_command as findquery_command_module
from .commands import new_command as new_command_module
from .structure import layout as layout_module
from .structure import record as record_module

FMS_FIND_AND: str = ...
FMS_FIND_OR: str = ...

FMS_SORT_ASCEND: str = ...
FMS_SORT_DESCEND: str = ...

FMS_FIND_OP_EQ: str = ...
FMS_FIND_OP_NEQ: str = ...
FMS_FIND_OP_GT: str = ...
FMS_FIND_OP_GTE: str = ...
FMS_FIND_OP_LT: str = ...
FMS_FIND_OP_LTE: str = ...
FMS_FIND_OP_CN: str = ...
FMS_FIND_OP_BW: str = ...
FMS_FIND_OP_EW: str = ...

FMS_RELATEDSETS_FILTER_LAYOUT: str = ...
FMS_RELATEDSETS_FILTER_NONE: str = ...


class FileMakerServer:
    _log: Logger
    _prop_layout: Dict[str, Any]  # TODO: put correct type here
    _layout_lookup: Dict[str, layout_module.Layout]
    _hostspec: str
    _username: str
    _password: str
    _db_name: str
    _requests_session: requests.sessions.Session

    def __init__(self,
                 hostspec: str,
                 username: str,
                 password: str,
                 db: Optional[str] = None) \
            -> None:
        ...

    def close(self) -> None: ...

    @property
    def log(self) -> Logger: ...

    def _get_hostspec(self) -> Optional[str]: ...

    def _set_hostspec(self, hostspec: str) -> None: ...

    hostspec: Optional[str] = ...

    def _get_username(self) -> Optional[str]: ...

    def _set_username(self, username: str) -> None: ...

    username: Optional[str] = ...

    def _get_password(self) -> Optional[str]: ...

    def _set_password(self, password: str) -> None: ...

    password: Optional[str] = ...

    def _get_db_name(self) -> Optional[str]: ...

    def _set_db_name(self, db_name: str) -> None: ...

    db_name: Optional[str] = ...

    def find_record_by_id(self,
                          layout_name: str,
                          record_id: int) \
            -> List[record_module.Record]: ...

    def create_dup_record_command(self,
                                  layout_name: str,
                                  record_id: Optional[int] = ...) \
            -> dup_command_module.DupCommand: ...

    def create_delete_record_command(self,
                                     layout_name: str,
                                     record_id: Optional[int]) \
            -> delete_command_module.DeleteCommand: ...

    def create_edit_record_command(self,
                                   layout_name: str,
                                   record_id: Optional[int],
                                   modification_id: Optional[int] = None) \
            -> edit_command_module.EditCommand: ...

    def create_find_records_command(self,
                                    layout_name: str) \
            -> find_command_module.FindCommand: ...

    def create_findany_record_command(self,
                                      layout_name: str) \
            -> findany_command_module.FindAnyCommand: ...

    def create_findquery_command(self,
                                 layout_name: str) \
            -> findquery_command_module.FindQueryCommand: ...

    def create_new_record_command(self,
                                  layout_name: str) \
            -> new_command_module.NewCommand: ...

    def get_layout(self, layout_name: str) -> layout_module.Layout: ...

    def get_db_names(self) -> List[str]: ...

    def get_layout_names(self) -> List[str]: ...

    def get_script_names(self) -> List[str]: ...

    def _get_names(self, commands: List[command_container_module.Command]) -> List[str]: ...

    def execute_query(self, query: str, xml_grammar: str = ...) -> bytes: ...

    @property
    def requests_session(self) -> Optional[requests.sessions.Session]: ...

    def get_container_data_url(self, url_path: str) -> str: ...

    def get_container_data(self, url: str) -> bytes: ...
