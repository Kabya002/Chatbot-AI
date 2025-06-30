from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime

app = FastAPI()

# Enable CORS for local testing with Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Google Calendar credentials
def get_calendar_service():
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)
    return service

# Get upcoming events
@app.get("/available")
def get_availability(start: str = None, end: str = None):
    service = get_calendar_service()
    if not start:
        start = datetime.datetime.utcnow().isoformat() + "Z"
    if not end:
        end = (datetime.datetime.utcnow() + datetime.timedelta(days=30)).isoformat() + "Z"

    events_result = service.events().list(
        calendarId='primary', timeMin=start, timeMax=end,
        singleEvents=True, orderBy='startTime').execute()

    return {"events": events_result.get('items', [])}


# Book an event
@app.post("/book")
def book_event(title: str, start: str, end: str):
    service = get_calendar_service()
    event = {
        'summary': title,
        'start': {'dateTime': start, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end, 'timeZone': 'Asia/Kolkata'},
    }
    created = service.events().insert(calendarId='primary', body=event).execute()
    return created
