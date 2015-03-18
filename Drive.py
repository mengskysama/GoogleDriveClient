#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author:  Mengskysama

__VER__ = "0.1"

import httplib2
import traceback
import os
import time
import mimetypes

import Ulits
from Oauth import Oauth

from apiclient import errors
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from apiclient import errors


class Drive(object):

    def __init__(self, credentials):
        self.drive_service = self._build_service(credentials)
        self.__root_id = None

    def _build_service(self, credentials):
        http = httplib2.Http()
        http = credentials.authorize(http)
        drive_service = build('drive', 'v2', http=http)
        return drive_service

    def escape(self, s):
        return s.replace("'", "\\'")

    def files_get(self, id):
        #fileId=file_id
        print self.drive_service.files(id).get().execute()
    
    def retrieve_all_files(self, maxResults=1000, q=None):
        """
            Retrieve a list of File resources.
            https://developers.google.com/drive/v2/reference/files/list
        Returns:
            List of File resources.
        """
        result = []
        page_token = None
        while True:
            try:
                param = {}
                param['maxResults'] = maxResults
                if page_token is not None:
                    param['pageToken'] = page_token
                if q is not None:
                    param['q'] = q
                files = self.drive_service.files().list(**param).execute()
                result.extend(files['items'])
                page_token = files.get('nextPageToken')
                if page_token is None:
                    break
            except errors.HttpError, error:
                print 'An error occurred: %s' % error
                break
        return result
    
    def get_root_id(self):
        # I don't know how to get root_id so..
        if self.__root_id is None:
            TMP_FLODER = 'GoogleDriveCli_TMP_E364236B'
            q = "title = '%s'" % TMP_FLODER
            items = self.retrieve_all_files(q=q)
            if len(items) == 0:
                #Create floder and get parent id (root id)
                ret = self.insert_folder(TMP_FLODER)
                self.__root_id = ret[0]['parents'][0]['id']
            else:
                self.__root_id = items[0]['parents'][0]['id']
        return self.__root_id
        
    def get_path_id(self, path):
        #Can NOT identified the same name folder
        #Does NOT include trashed files
        lpath = path.strip('/').split('/')
        if len(lpath) == 1 and lpath[0] == '':
            # /
            return self.get_root_id()
        else:
            #get all title of path
            q = ''
            for title in lpath:
                if q != '':
                    q += 'or '
                q += "title = '%s' " % self.escape(title)
            q = "trashed = false and mimeType = 'application/vnd.google-apps.folder' and (" + q + ')'
            items = self.retrieve_all_files(q=q)
            # /f01/
            # /f01/f02/
            #  ^
            item = self._ls_path_is_root(items, lpath.pop(0))
            if len(lpath) == 0:
                # /f01/
                if item is None:
                    print 'path %s not found' % path
                    return None
                return item['id']
            for title in lpath:
                # /f01/f02/
                #      ^
                item = self._ls_path(items, item['id'], title)
                if item is None:
                    print 'path %s not found' % path
                    return None
            return item['id']
        
    def ls(self, path):
        #Can NOT identified the same name folder
        #Does NOT include trashed files
        """
        lpath = path.strip('/').split('/')
        if len(lpath) == 1 and lpath[0] == '':
            # /
            q = "trashed = false and '%s' in parents" % (self.get_root_id())
            items = self.retrieve_all_files(q=q)
            return self._ls_parents_is_root(items)
        else:
            #get all title of path
            q = ''
            for title in lpath:
                if q != '':
                    q += 'or '
                q += "title = '%s' " % self.escape(title)
            q = "trashed = false and mimeType = 'application/vnd.google-apps.folder' and (" + q + ')'
            items = self.retrieve_all_files(q=q)
            # /f01/
            # /f01/f02/
            #  ^
            item = self._ls_path_is_root(items, lpath.pop(0))
            if len(lpath) == 0:
                # /f01/
                q = "'%s' in parents" % item['id']
                return self.retrieve_all_files(q=q)
            for title in lpath:
                # /f01/f02/
                #      ^
                item = self._ls_path(items, item['id'], title)
                if item is None:
                    print 'path %s not found' % path
                    return None
            q = "'%s' in parents" % item['id']
            return self.retrieve_all_files(q=q)
        """
        id = self.get_path_id(path)
        if id is None:
            return None
        q = "trashed = false and '%s' in parents" % id
        return self.retrieve_all_files(q=q)
        
    
    def _ls_path_is_root(self, items, title):
        for item in items:
            if item['title'] == title:
                for parent in item['parents']:
                    if parent['isRoot'] is True:
                        return item

    def _ls_path(self, items, parent_id, title):
        for item in items:
            if item['title'] == title:
                for parent in item['parents']:
                    if parent['id'] == parent_id:
                        return item

    def _ls_parents_is_root(self, items):
        collects = []
        for item in items:
            for parent in item['parents']:
                if parent['isRoot'] is True:
                    collects.append(item)
                    break
        return collects
        
    def delete_file(self, file_id):
        """Permanently delete a file, skipping the trash.

        Args:
            file_id: ID of the file to delete.
        """
        try:
            self.drive_service.files().delete(fileId=file_id).execute()
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            
    def delete(self, del_path):
        #Delete is NOT Trash
        #Can NOT identified the same name folder
        #Can NOT delete trashed files
        """
            Args:
                save_path: file path in google drive
                file_path: local file path
                Eg.
                file_path              google drive
                /home/1        ---->   /home/1   file
                /home/1/        ---->  /home/1/  folder
        """
        if len(del_path) <= 1:
            return None
        
        is_folder = False
        #/home/1/
        if del_path[-1] == '/':
            is_folder = True
            del_path = del_path[:-1]
        #/home/1
        # ^
        del_path_0 = os.path.split(del_path)[0]
        del_path_1 = os.path.split(del_path)[1]
        id = self.get_path_id(del_path_0)
        if is_folder is True:
            q = "trashed = false and mimeType = 'application/vnd.google-apps.folder' and '%s' in parents and title = '%s'" % (id, del_path_1)
            items = self.retrieve_all_files(q=q)
            if len(items) == 0:
                print 'delete floder not found'
                return None
        else:
            q = "trashed = false and mimeType != 'application/vnd.google-apps.folder' and '%s' in parents and title = '%s'" % (id, del_path_1)
            items = self.retrieve_all_files(q=q)
            if len(items) == 0:
                print 'delete file not found'
                return None
        self.delete_file(items[0]['id'])
        
        
    def insert_folder(self, title, parent_id=None):
        body = {
            'title': title,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        if parent_id is not None:
            body['parents'] = [{'id': parent_id}]
        try:
            file = self.drive_service.files().insert(
                    body=body
                    ).execute()
            return file
        except errors.HttpError, error:
            print 'An error occured: %s' % error
            return None

    def insert_file(self, title, file_path, description='', parent_id=None, mime_type=None, print_info=True):
        """
            Insert new file.
            https://developers.google.com/drive/v2/reference/files/insert
        Args:
            service: Drive API service instance.
            title: Title of the file to insert, including the extension.
            description: Description of the file to insert.
            parent_id: Parent folder's ID.
            mime_type: MIME type of the file to insert. (None auto detect)
            file_path: file_path of the file to insert.
        Returns:
            Inserted file metadata if successful, None otherwise.
        """
        if mime_type is None:
            (mime_type, encoding) = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
        body = {
            'title': title,
            'description': description,
            'mimeType': mime_type
        }
        if parent_id is not None:
            body['parents'] = [{'id': parent_id}]
        try:
            if os.path.getsize(file_path) < 1024 * 1024:
                media_body = MediaFileUpload(file_path, mimetype=mime_type, resumable=False)
                response = self.drive_service.files().insert(
                        body=body,
                        media_body=media_body).execute()
            else:
                media_body = MediaFileUpload(file_path, mimetype=mime_type, chunksize=10240*1024, resumable=True)
                request = self.drive_service.files().insert(
                        body=body,
                        media_body=media_body)
                response = None
                
                while response is None:
                    if print_info is True:
                        begin = time.time()
                        status, response = request.next_chunk()
                        end = time.time()
                        speed = 10240 / (end - begin)
                        if status:
                            print "Upload %d%% complete. Speed: %s KB/s" % (int(status.progress() * 100), speed)
                return response
        except errors.HttpError, error:
            print 'An error occured: %s' % error
            raise Exception('insert file except')
    
    def upload_file(self, save_path, file_path, description='', dup_name=False):
        """
            Args:
                save_path: file path in google drive
                file_path: local file path
                Eg.
                save_path      file_path              google drive
                               /home/1.rar    ---->   /1.rar
                /              /home/1.rar    ---->   /1.rar
                /fd01/         /home/1.rar    ---->   /fd01/1.rar
                /fd01/2        /home/1.rar    ---->   /fd01/2
                dup_name: if false skip duplicate file (same name)
        """
        file_name = os.path.basename(file_path)
        if file_name == '':
            print '%s is not a file' % file_path
            return None
        save_name = os.path.basename(save_path)
        if save_name == '':
            save_path = os.path.join(save_path, file_name)
        save_name = os.path.basename(save_path)
        #Create folder
        lpath = save_path.strip('/').split('/')[:-1]
        parent_id = self.get_root_id()
        if len(lpath) == 1 and lpath[0] == '':
            pass
        else:
            # /f01/
            # /f01/f02/
            #  ^
            try:
                for title in lpath:
                    q = "trashed = false and mimeType = 'application/vnd.google-apps.folder' and title = '%s' and '%s' in parents" % (self.escape(title), parent_id)
                    items = self.retrieve_all_files(q=q)
                    if len(items) == 0:
                        #No exist create it
                        item = self.insert_folder(title, parent_id)
                        parent_id = item['id']
                    else:
                        parent_id = items[0]['id']
            except KeyboardInterrupt:
                raise
            except:
                #traceback.print_exec()
                #print 'An error occured: %s' % error
                #return None
                raise Exception('Create folder except')
        if dup_name is False:
            q = "trashed = false and title = '%s' and '%s' in parents" % (self.escape(save_name), parent_id)
            items = self.retrieve_all_files(q=q)
            if len(items) > 0:
                raise Exception('Duplicate file')
        #Create completed, begin upload
        return self.insert_file(save_name, file_path, description, parent_id)
        
    def upload_files(self, save_path, file_path, description=''):
        """
            Args:
                save_path: file path in google drive
                file_path: local file path
                Eg.
                save_path      file_path              google drive
                               /home/         ---->   error save_path error, must start with /
                /              /home/         ---->   /...
                /fd01/         /home/         ---->   /fd01/...
                /fd01/2        /home/         ---->   error save_path error, must end with /
                /fd01/2/       /home/         ---->   /fd01/2/...
                /fd01/2/       /home          ---->   /fd01/2/...
        """
        if save_path[0] != '/':
            print 'save_path error, must start with /'
            return None
        
        #make sure os.path.split work well
        if save_path[-1] != '/':
            print 'save_path error, must end with /'
            return None
        
        #make sure os.path.split work well
        file_path = Ulits.unixdir(file_path)
        if file_path[-1] != '/':
            file_path += '/'

        file_path = os.path.split(file_path)[0]
        files = Ulits.walkdir(file_path)
        #get each file save_path
        save_paths = map(lambda x: save_path[:-1] + Ulits.unixdir(x[len(file_path):]), files)
        
        for i in xrange(len(files)):
            try:
                print 'Upload %s' % files[i]
                self.upload_file(save_paths[i], files[i])
            except Exception, e:
                log = 'file %s upload failed.\nreason:%s' % (files[i], e)
                print log
            except KeyboardInterrupt:
                raise
            except:
                log = 'file %s upload failed.\nreason:%s' % (files[i], traceback.print_exec())
                print log

if __name__=="__main__":
    credentials = Oauth.Load()
    drive = Drive(credentials)
    #drive.ls('')
    #drive.ls('/')
    #drive.ls('/fd01')
    #drive.upload('/home/data/', '/root/The.Big.Bang.Theory.S08E18.720p.HDTV.X264-DIMENSION.mkv')
    #drive.upload_files('/GoogleDriveCli/', '/home/python/GoogleDriveCli/')
    drive.delete('/home/')
    #drive.delete('/GoogleDriveCli/')
    print drive.get_root_id()
    ls = drive.ls('/fd01')
    for i in ls:
        print i['title']