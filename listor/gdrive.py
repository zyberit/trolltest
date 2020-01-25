'''
Created on 5 okt. 2018

@author: HAPEAA03
'''

import io

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

class GDrive:
    mime_mappings = {"xlsx":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     "docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                     "pdf":"application/pdf",
                     "txt":"text/plain"}
    
    def __init__(self, credentials):
        creds = service_account.Credentials.from_service_account_info(credentials)
        self._gdrive_service_object = build('drive', 'v3', credentials=creds)
 
    def find_file(self,folder_id,file_name):
        query = "parents='"+folder_id+"' and name='"+file_name+"'"
        results = self._gdrive_service_object.files().list(q=query,pageSize=1000,fields="nextPageToken, files(id, name)").execute()
        return results.get('files', [])
    
    def write_file(self,file_name,parent_id,data):
        ext = file_name.split(".")[1]
        mimetype = self.mime_mappings[ext]
        media = MediaIoBaseUpload(io.BytesIO(data),mimetype)
        r = self.find_file(parent_id,file_name)
        results = 0
        if not r:
            file_metadata = {'name': file_name, 'parents':[parent_id]}
            results = self._gdrive_service_object.files().create(body=file_metadata,media_body=media,fields='id').execute()
        else:
            file_id = r[0]["id"]
            results = self._gdrive_service_object.files().update(fileId=file_id,media_body=media,fields='id').execute()
        return results
        
    def get_curr_users(self,folder_id):
        results = self._gdrive_service_object.permissions().list(fileId=folder_id,fields="permissions(emailAddress,id)").execute()
        users = set(u['emailAddress'].lower() for u in results.get('permissions', []))
        mappings = {u['emailAddress'].lower():u['id'] for u in results.get('permissions', [])}
        return users, mappings
     
    def add_user(self,user,folder_id,message=""):
        request_body = {"emailAddress":user, "role": "writer", "type": "user"}
        self._gdrive_service_object.permissions().create(fileId=folder_id, body=request_body, sendNotificationEmail=True, emailMessage=message).execute()
     
    def del_user(self,permid,folder_id):
        self._gdrive_service_object.permissions().delete(fileId=folder_id, permissionId=permid).execute()
