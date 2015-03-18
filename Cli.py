#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author:  Mengskysama

__VER__ = "0.1"

import traceback
import os
import time
import argparse

from Drive import Drive
from Oauth import Oauth


credentials = Oauth.Load()
if credentials is None:
    Oauth.cli_oauth()


parser = argparse.ArgumentParser(description="Google Drive Client Ver %s" % __VER__, epilog="")

parser.add_argument("--upload", help="upload a file to drive", metavar=('<file_path>', '<remote_path>'), nargs=2)
parser.add_argument("--uploads", help="upload all the files under the folder to drive", metavar=('<file_path>', '<remote_path>'), nargs=2)
parser.add_argument("--ls", help="show the list of path in drive", metavar="<remote_path>")
parser.add_argument("--delete", help="delete file or folder", metavar="<remote_path>")

args = parser.parse_args()

credentials = Oauth.Load()
drive = Drive(credentials)

while True:
    if args.upload is not None:
        drive.upload_file(args.upload[1], args.upload[0])
        break
    if args.uploads is not None:
        drive.upload_files(args.uploads[1], args.uploads[0])
        break
    if args.ls is not None:
        items = drive.ls(args.ls)
        if items:
            for item in items:
                filesize = '?'
                if 'fileSize' in item:
                    filesize = int(item['fileSize'])/(1024 * 1024.0)
                    filesize = '%sMB' % round(filesize, 2)
                print '%-30s %s'  % (item['title'], filesize)
        break
    if args.delete is not None:
        drive.delete(args.delete)
        break
    parser.print_help()
    exit(1)


