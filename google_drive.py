import os.path
import io
import oauth2client.client

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


CLIENT_SECRETS = "client_secrets.json"
TOKEN_FILE = "token.json"


def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, SCOPES)
            flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
            authorize_url = flow.step1_get_authorize_url()
            print("Go to the following link in your browser: " + authorize_url)
            code = input("Enter verification code: ").strip()
            creds = flow.step2_exchange(code)

            # Save the credentials for the next run
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
    return creds



def upload_file(drive_service, file_name, mime_type, title, description):
    media_body = MediaFileUpload(file_name, mimetype=mime_type, resumable=True)
    body = {
        "name": title,
        "description": description,
    }

    try:
        new_file = drive_service.files().create(body=body, media_body=media_body).execute()
        file_title = new_file.get("name")
        file_desc = new_file.get("description")
        if file_title == title and file_desc == description:
            print(f"File is uploaded \nTitle : {file_title}  \nDescription : {file_desc}")
    except HttpError as error:
        print(f"An error occurred: {error}")


def download_file(drive_service, file_id):
    try:
        request = drive_service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None
    return file.getvalue() if file else None


def download_folder(drive_service, folder_id, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    try:
        results = drive_service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name, mimeType)").execute()
        items = results.get('files', [])
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                download_folder(drive_service, item['id'], os.path.join(destination_folder, item['name']))
            else:
                content = download_file(drive_service, item['id']) #, item['name'])
                with open(os.path.join(destination_folder, item['name']), 'wb') as f:
                    f.write(content)
    except HttpError as error:
        print(f"An error occurred: {error}")


def get_folder_id_by_name(drive_service, folder_name):
    try:
        results = drive_service.files().list(q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'", fields="files(id)").execute()
        items = results.get('files', [])
        if items:
            return items[0]['id']
        else:
            print(f'Folder with name "{folder_name}" not found.')
            return None
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


def download_folder_by_name(drive_service, folder_name, destination_folder):
    folder_id = get_folder_id_by_name(drive_service, folder_name)
    if folder_id:
        download_folder(drive_service, folder_id, destination_folder)


def list_files(drive_service):
    try:
        results = drive_service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
            return
        print('Files:')
        for item in items:
            print(f'{item["name"]} ({item["id"]})')
    except HttpError as error:
        print(f'An error occurred: {error}')


def find_file(drive_service, file_name):
    try:
        results = drive_service.files().list(q=f"name='{file_name}'", fields="files(id, name, parents)").execute()
        items = results.get('files', [])
        if items:
            file_id = items[0]['id']
            return file_id
        else:
            return None
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

