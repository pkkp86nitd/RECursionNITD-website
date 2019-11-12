from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import datefinder

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('../website/events/token.pickle'):
        with open('../website/events/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../website/events/client_secret3.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('../website/events/token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    print(creds)
    service = build('calendar', 'v3', credentials=creds)
    return service

def cal_list():   
    page_token = None
    service=main()
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            print (calendar_list_entry['summary'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
        
def create_event(event_):
    
    start_time = event_.start_time
    end_time =event_.end_time
    timezone='Asia/Kolkata'
    print(event_.start_time)
    event = {
        'summary': event_.title,
        'location': event_.location,
        'description': event_.description,
        'start': {
            'dateTime': start_time-timedelta(hours=5,minutes=30),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time-timedelta(hours=5,minutes=30),
            'timeZone': timezone,
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    print("Service")
    service=main()
    print(event['start'],event['end'])
    return service.events().insert(calendarId='primary', body=event).execute()   




        

# from googleapiclient.discovery import build
# from google.oauth2 import service_account

# SCOPES = ['https://www.googleapis.com/auth/calendar']
# SERVICE_ACCOUNT_FILE = '/path/to/service.json'
# credentials = service_account.Credentials.from_service_account_file(
#         'credentials.json', scopes=SCOPES)


# event = {
#   'summary': 'Google I/O 2015',
#   'location': '800 Howard St., San Francisco, CA 94103',
#   'description': 'A chance to hear more about Google\'s developer products.',
#   'start': {
#     'dateTime': '2015-05-28T09:00:00-07:00',
#     'timeZone': 'America/Los_Angeles',
#   },
#   'end': {
#     'dateTime': '2015-05-28T17:00:00-07:00',
#     'timeZone': 'America/Los_Angeles',
#   },
#   'recurrence': [
#     'RRULE:FREQ=DAILY;COUNT=2'
#   ],
# #   'attendees': [
# #     {'email': 'jayjeetchakraborty25@example.com'},
# #     {'email': '@.com'},
# #   ],
#   'reminders': {
#     'useDefault': False,
#     'overrides': [
#       {'method': 'email', 'minutes': 24 * 60},
#       {'method': 'popup', 'minutes': 10},
#     ],
#   },
# }

# service = build('calendar', 'v3', credentials=creds)
# event = service.events().insert(calendarId='primary', body=event).execute()
# print('Event created: %s' % (event.get('htmlLink')))