#
# coding: utf-8
#
# fmxml.commands.findany_command
#
from .base_command import BaseCommand
from .mixins import RelatedsSetsMixin


class FindAnyCommand(RelatedsSetsMixin, BaseCommand):
    """
    –findany (Find random record) query commands
    """

    def get_query(self):
        command_params = super().get_command_params()
        command_params['-findany'] = None
        return command_params.as_query()
