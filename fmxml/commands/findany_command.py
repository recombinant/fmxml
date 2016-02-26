# -*- mode: python tab-width: 4 coding: utf-8 -*-
from .base_command import BaseCommand


class FindAnyCommand(BaseCommand):
    """
    –findany (Find random record) query commands
    """

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)

    def get_query(self):
        command_params = super().get_command_params()
        command_params['-findany'] = None
        return self.urlencode_query(command_params)
