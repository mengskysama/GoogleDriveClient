#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author:  Mengskysama

import os
import platform


def walkdir(dir):
    lst_file = []
    for root,dirs,files in os.walk(dir):
        for filespath in files:
            lst_file.append(os.path.join(root,filespath))
    return lst_file

def unixdir(dir):
    if "Windows" == platform.system():
        return dir.replace('\\', '/')
    return dir
    