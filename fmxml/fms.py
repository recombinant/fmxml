# -*- mode: python tab-width: 4 coding: utf-8 -*-
import logging

logging.basicConfig(level=logging.DEBUG)


class FileMakerServer:
    def __init__(self):
        self.log = logging.getLogger('FileMakerServer')
        self.log.info('FileMakerServer.__init__()')
