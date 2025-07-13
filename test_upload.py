from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import pickle
# SCOPES Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Buat Flow OAuth
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json', SCOPES)


# Jalankan local server untuk login
creds = flow.run_local_server(port=0)

# Build Drive service
service = build('drive', 'v3', credentials=creds)


# Setelah flow sukses
with open('token.pkl', 'wb') as token:
    pickle.dump(creds, token)
# Upload 1 file test ke folder di My Drive
folder_id = '1P04NUThkyrXWz79y7BCNOxSUv05rJ9Pj'  # Folder di My Drive user

file_metadata = {
    'name': 'test_upload_oauth.txt',
    'parents': [folder_id]
}
media = MediaIoBaseUpload(io.BytesIO(b"Hello world from OAuth!"), mimetype='text/plain')

file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()

print("Upload berhasil:", file.get('id'))
print("Link:", f"https://drive.google.com/file/d/{file.get('id')}/view?usp=sharing")
