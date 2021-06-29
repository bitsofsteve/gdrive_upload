from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from tabulate import tabulate
import datetime


SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.file']

def get_gdrive_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # return Google Drive API service
    return build('drive', 'v3', credentials=creds)


def create_folder(folder):
    service = get_gdrive_service()
    folder_metadata = {
        "name": folder,
        "parents": [folder_id],
        "mimeType": "application/vnd.google-apps.folder"
    }
    file = service.files().create(body=folder_metadata,
                                  supportsAllDrives=True, fields="id").execute()
    parent_folder_id = file.get("id")
    print(
        f'Folder {folder_metadata["name"]} with Folder ID:, {parent_folder_id} has been created')
    return parent_folder_id


def create_csv_folder(folder):

    parents_folder_id = create_folder(folder)
    service = get_gdrive_service()
    folder_metadata = {
        "name": "CSVs",
        "parents": [parents_folder_id],
        "mimeType": "application/vnd.google-apps.folder"
    }
    file = service.files().create(body=folder_metadata,
                                  supportsAllDrives=True, fields="id").execute()
    csv_folder_id = file.get("id")
    print(
        f' CSV Folder {folder_metadata["name"]} with Folder ID:, {csv_folder_id} has been created')
    return csv_folder_id


def upload_files(file_name, parent_id, file_path):
      service = get_gdrive_service()

    file_metadata = {
        'name': file_name,
        'parents': [csv_folder_id]
    }
    media = MediaFileUpload(file_path,
                            mimetype='text/csv',
                            resumable=True)
    file = service.files().create(body=file_metadata, supportsAllDrives=True,
                                  media_body=media, fields='id').execute()
    file_id = file.get("id")
    print(f'{file_name} with id {file_id} was uploaded to the parent folder with id {csv_folder_id}')


if __name__ == "__main__":
    # get the week, plus 1 because we run it usually before the next week proper
    current_week = datetime.datetime.now().isocalendar()[1] + 1
    current_year = datetime.datetime.now().isocalendar()[0]
    folder_name = f'{current_year} - Week - {current_week}'

    csv_folder_id = create_csv_folder(folder_name)
    print(f'folder id of {csv_folder_id} stored')

    directory = r'files'

    for filename in os.listdir(directory):
        filename = filename
        filepath = os.path.join(directory, filename)
        upload_files(filename, csv_folder_id, filepath)
