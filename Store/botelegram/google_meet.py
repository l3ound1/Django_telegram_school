from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_credentials():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds

def create_google_meet_event(teacher_email, start_time_str, duration_minutes=30):
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    start_time = datetime.strptime(start_time_str, "%H:%M")
    now = datetime.now()
    event_start = datetime.combine(now.date(), start_time.time())
    event_end = event_start + timedelta(minutes=duration_minutes)

    event = {
        'summary': 'Google Meet Meeting',
        'description': 'A meeting created via API',
        'start': {
            'dateTime': event_start.isoformat(),
            'timeZone': 'Europe/Moscow',
        },
        'end': {
            'dateTime': event_end.isoformat(),
            'timeZone': 'Europe/Moscow',
        },

        'conferenceData': {
            'createRequest': {
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet',
                },
                'requestId': f'unique_request_{int(event_start.timestamp())}',
            },
        },
        "attendees": [
            {"email": teacher_email, "responseStatus": "accepted"}
        ],
        'guestsCanModify': True
    }

    created_event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()

    meet_link = created_event['conferenceData']['entryPoints'][0]['uri']
    return meet_link

