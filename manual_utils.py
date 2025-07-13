# manual_utils.py
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import io
import pickle
# === 1. Koneksi Service Account ===
def get_service_account_credentials():
    scope = [
        "https://www.googleapis.com/auth/drive",
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive.file"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), scope)
    return creds

# === 2. Upload satu file ke Google Drive ===
def upload_to_drive_oauth(file_storage, folder_id):
    # Load creds dari file
    with open('token.pkl', 'rb') as token:
        creds = pickle.load(token)

    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': file_storage.filename,
        'parents': [folder_id]
    }

    media = MediaIoBaseUpload(file_storage.stream, mimetype=file_storage.mimetype)

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    # Buat link share
    service.permissions().create(
        fileId=file['id'],
        body={'role': 'reader', 'type': 'anyone'}
    ).execute()

    link = f"https://drive.google.com/file/d/{file['id']}/view?usp=sharing"
    return link

