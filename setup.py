import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import schedule
import datetime
import time
import os


class MyDrive():
    def __init__(self):
        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)

    def list_files(self, page_size=10):
        # Call the Drive v3 API
        results = self.service.files().list(
            pageSize=page_size, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))

    def upload_file(self, filename, path):
        folder_id = "" #Google Drive FolderID 
        media = MediaFileUpload(f"{path}{filename}")

        response = self.service.files().list(
                                        q=f"name='{filename}' and parents='{folder_id}'",
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=None).execute()
        if len(response['files']) == 0:
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"A new file was created {file.get('id')}")

        else:
            for file in response.get('files', []):
                # Process change

                update_file = self.service.files().update(
                    fileId=file.get('id'),
                    media_body=media,
                ).execute()
                print(f'Updated File')


def main():
    path = "" #update this path
    files = os.listdir(path)
    my_drive = MyDrive()

    for item in files:
        try:
            my_drive.upload_file(item, path)
            file1 = open("log.txt","a")
            datetime_object = datetime.datetime.now()
            absolute_path = os.path.abspath(item)
            file1.write(str(datetime_object) + " Backup Successful " + str(absolute_path) + "\n")
            file1.close()
            
        except:
            file1 = open("log.txt","a")
            datetime_object = datetime.datetime.now()
            absolute_path = os.path.abspath(item)
            file1.write(str(datetime_object) + " Backup Failed " + str(absolute_path) + "\n")
            file1.close()


if __name__ == '__main__':
    schedule.every(30).seconds.do(main)
    while True:
        schedule.run_pending()
        time.sleep(0.5)