from apiclient import errors
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from apiclient import errors
import httplib2
import traceback
import os
import time
from Oauth import Oauth


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
        
    def ls(self, path):
        #Can NOT identified the same path and name folder
        #Does NOT include trashed files
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

    def insert_file(self, title, file_path, description='', parent_id=None, mime_type=None, print_speed=True, print_process=True):
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
        media_body = MediaFileUpload(file_path, mimetype=mime_type, chunksize=10240*1024, resumable=True)
        body = {
            'title': title,
            'description': description,
            'mimeType': mime_type
        }
        if parent_id is not None:
            body['parents'] = [{'id': parent_id}]

        request = self.drive_service.files().insert(
                body=body,
                media_body=media_body)
        response = None
        
        try:
            while response is None:
                if print_speed is True:
                    begin = time.time()
                    status, response = request.next_chunk()
                    end = time.time()
                    speed = 10240 / (end - begin)
                    print 'Speed: %s KB/s' % (speed)
                if print_process is True and status:
                    print "Upload %d%% complete." % int(status.progress() * 100)
            print response
        except errors.HttpError, error:
            print 'An error occured: %s' % error
            return None
    
    def upload(self, save_path, file_path, description=''):
        """
            Args:
                save_path: file path in google drive
                file_path: local file path
                Eg.
                save_path      file_path
                /fd01/         /home/1.rar    ---->   /fd01/1.rar
                /fd01/2        /home/1.rar    ---->   /fd01/2
        """
        
        save_name = os.path.basename(save_path)
        if save_name == '':
            file_name = os.path.basename(file_path)
            save_path = os.path.join(save_path, file_name)
        save_name = os.path.basename(save_path)
        #Create path
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
            except:
                traceback.print_exec()
                print 'An error occured: %s' % error
                return None
            
        #Create completed, begin upload
        self.insert_file(save_name, file_path, description, parent_id)
 


credentials = Oauth.Load()
drive = Drive(credentials)
drive.upload('/home/data/', '/root/The.Big.Bang.Theory.S08E18.720p.HDTV.X264-DIMENSION.mkv')
exit(1)


print drive.get_root_id()
drive.insert_file('The.Big.Bang.Theory.S08E18.720p.HDTV.X264-DIMENSION.mkv', '')
ls = drive.ls('/fd01')
for i in ls:
    print i['title']