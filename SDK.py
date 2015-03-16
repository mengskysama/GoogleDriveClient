#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author:  Mengskysama


class SDK():

    def __init__(self, oauth, config):
        self.oauth = oauth
        self.config = config

    @staticmethod
    def _requests(**kwargs):
        pass