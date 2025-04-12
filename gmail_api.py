from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64
import os

# Scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

def gmail_authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(subject, message_text, file_path):
    message = MIMEMultipart()
    message['to'] = ""
    message['from'] = ""
    message['subject'] = subject

    # Attach the email body
    message.attach(MIMEText(message_text, 'plain'))

    # Add file attachment
    if file_path:
        content_type, encoding = 'application/octet-stream', None
        main_type, sub_type = content_type.split('/', 1)

        with open(file_path, 'rb') as f:
            my_file = MIMEBase(main_type, sub_type)
            my_file.set_payload(f.read())

        encoders.encode_base64(my_file)
        my_file.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
        message.attach(my_file)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def create_draft(service, user_id, message_body):
    try:
        message = {'message': message_body}
        draft = service.users().drafts().create(userId=user_id, body=message).execute()
        print(f'Draft created: Draft ID - {draft["id"]}')
        return draft
    except Exception as error:
        print(f'An error occurred: {error}')
        return None
