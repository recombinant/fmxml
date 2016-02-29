# -*- mode: python tab-width: 4 coding: utf-8 -*-
from .base_command import BaseCommand
from .mixins import RelatedsSetsMixin


class FindAnyCommand(RelatedsSetsMixin, BaseCommand):
    """
    –findany (Find random record) query commands
    """
    __slots__ = ()

    def __init__(self, fms, layout_name):
        super().__init__(fms, layout_name)

    def get_query(self):
        command_params = super().get_command_params()
        command_params['-findany'] = None
        return command_params.as_query()
