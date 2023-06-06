#!/usr/bin/env python
import os
import base64
import email
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = os.getenv('SCOPES').split(',')
REDIRECT_URI = os.getenv('REDIRECT_URI')
PORT = os.getenv('PORT')


# Set up the OAuth 2.0 authorization flow
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
flow.redirect_uri = REDIRECT_URI
creds = flow.run_local_server(port=PORT)

# Create a Gmail API service instance
service = build('gmail', 'v1', credentials=creds)

# Define the Gmail search query to retrieve the latest 10 emails
query = "in:inbox"
result = service.users().messages().list(userId='me', maxResults=1, q=query).execute()
messages = result.get('messages', [])

# Retrieve the data for each email message
for message in messages:
    msg = service.users().messages().get(userId='me', id=message['id']).execute()
    payload = msg['payload']
    headers = payload['headers']
    
    # Extract the message details
    for header in headers:
        if header['name'] == 'From':
            sender = header['value']
        elif header['name'] == 'To':
            recipient = header['value']
        elif header['name'] == 'Subject':
            subject = header['value']
        elif header['name'] == 'Date':
            date = header['value']
    
    # Extract the message body
    if 'parts' in payload:
        parts = payload['parts']
        data = parts[0]['body']['data']
    else:
        data = payload['body']['data']

    decoded_data = base64.urlsafe_b64decode(data.encode('UTF-8'))

    body = email.message_from_bytes(decoded_data).get_payload()
    
    message_dict = {
        "From": sender, 
        "To": recipient, 
        "Subject": subject, 
        "Date": date, 
        "Body": body
    }

    print(message_dict)
