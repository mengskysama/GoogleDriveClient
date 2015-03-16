#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author:  Mengskysama

__VER__ = "0.1"

import requests
import json
import os
import traceback

TIMEOUT = 30
PROXY = {'https': '127.0.0.1:8123'}
auth_url = 'https://accounts.google.com/o/oauth2/auth?scope=https://www.googleapis.com/auth/drive&re' \
           'direct_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code&client_id=665081966568.apps.googl' \
           'eusercontent.com&access_type=offline'
client_id = '665081966568.apps.googleusercontent.com'
client_secret = 'ckGVrYYQ_GE7O4rL80ozlEXR'


def cli_oauth(save=True):
    #step1 get auth code
    print 'goto get code:' + auth_url
    code = raw_input('code:')
    #step2 exchange
    d = {'code': code, 'client_id': client_id,
         'client_secret': client_secret, 'grant_type': 'authorization_code',
         'redirect_uri': ["urn:ietf:wg:oauth:2.0:oob","oob"]}
    r = requests.post('https://www.googleapis.com/oauth2/v3/token', data=d, proxies=PROXY, timeout=TIMEOUT)
    try:
        js = json.loads(r.text)
        if 'error' in js:
            print 'cli_oauth(): oath failed'
            print 'error:%s description:%s' % (js['error'], js['error_description'])
            return False
        print 'auth success!'
        print 'access_token', js['access_token']
        print 'refresh_token', js['refresh_token']
        Oauth.__refresh_token = js['refresh_token']
        Oauth.__access_token = js['access_token']
        if save is True:
            Oauth.save()
    except ValueError:
        print 'cli_oauth(): server return not json'
        print r.text
        return False
    except KeyError:
        print 'cli_oauth(): oath failed'
        print r.text
        return False
    except:
        print traceback.print_exc()
        return False
    return True


class Oauth(object):

    __refresh_token = None
    __access_token = None

    @staticmethod
    def _oath_path():
        #path = os.path.expanduser(os.environ.get("HOME"))
        #auth_file = os.path.join(path, "auth")
        #return auth_file
        return os.path.join(os.path.split(os.path.realpath(__file__))[0], 'auth')

    @staticmethod
    def save():
        open(Oauth._oath_path(), 'w').write(Oauth.__refresh_token)

    @staticmethod
    def load():
        auth_path = Oauth._oath_path()
        if not os.path.isfile(auth_path):
            print 'auth file is not exists'
            return False
        Oauth.__refresh_token = open(auth_path, 'r').read()
        return True

    @staticmethod
    def get_refresh_token():
        return Oauth.__refresh_token

    @staticmethod
    def get_access_token():
        return Oauth.__access_token

    @staticmethod
    def update_access_token():
        t = Oauth.get_refresh_token()
        if t is None:
            print 'update_access_token() Need refresh_token is None'
            return False
        d = {'refresh_token': t, 'client_id': client_id,
             'client_secret': client_secret, 'grant_type': 'refresh_token'}
        r = requests.post('https://www.googleapis.com/oauth2/v3/token', data=d, proxies=PROXY, timeout=TIMEOUT)
        try:
            js = json.loads(r.text)
            if 'error' in js:
                print 'update_access_token(): oath failed'
                print 'error:%s description:%s' % (js['error'], js['error_description'])
                return False
            print 'access_token success!'
            print 'access_token', js['access_token']
            Oauth.__access_token = js['access_token']
        except ValueError:
            print 'update_access_token(): server return not json'
            print r.text
            return False
        except KeyError:
            print 'update_access_token(): oath failed'
            print r.text
            return False
        except:
            print traceback.print_exc()
            return False
        return True


#cli_oauth(save=True)

Oauth.load()
Oauth.update_access_token()
print Oauth.get_refresh_token()