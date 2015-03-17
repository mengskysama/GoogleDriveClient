#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author:  Mengskysama

__VER__ = "0.1"

import os
import traceback
import httplib2
import pprint
import pickle
#import Config

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow


# Copy your credentials from the console
CLIENT_ID = '665081966568.apps.googleusercontent.com'
CLIENT_SECRET = 'ckGVrYYQ_GE7O4rL80ozlEXR'

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


def cli_oauth(save=True):
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE,
                               redirect_uri=REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    print 'Go to the following link in your browser: ' + authorize_url
    code = raw_input('').strip()
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    Oauth.Store(credentials)


class Oauth(object):
    
    @staticmethod
    def _credentials_path():
        #path = os.path.expanduser(os.environ.get("HOME"))
        #auth_file = os.path.join(path, "credentials")
        #return auth_file
        return os.path.join(os.path.split(os.path.realpath(__file__))[0], 'credentials')

    @staticmethod
    def Store(credentials):
        #form https://github.com/tom-dignan/gdrive-cli/blob/master/gdrive-cli.py
        credentials_path = Oauth._credentials_path()
        pickle.dump(credentials, open(credentials_path, 'wb'))
    
    @staticmethod
    def Load():
        credentials_path = Oauth._credentials_path()
        if not os.path.isfile(credentials_path):
            print 'credentials_path file is not exists'
            return None
        try:
            return pickle.load(open(credentials_path, 'rb'))
        except:
            return None

#def test():
#    cli_oauth()