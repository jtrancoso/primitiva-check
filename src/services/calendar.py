from datetime import datetime
import os
from googleapiclient.discovery import build

def create_calendar_event(creds, date_obj):
    ts = datetime.now().strftime("[%H:%M:%S]")
    calendar_id = os.getenv("CALENDAR_ID")
    try:
        service = build('calendar', 'v3', credentials=creds)
        date_str = date_obj.strftime('%Y-%m-%d')
        
        event = {
            'summary': '💰 Renovar Primitiva',
            'description': 'Toca renovar la primitiva.',
            'start': {'date': date_str},
            'end': {'date': date_str},
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60}, 
                    {'method': 'popup', 'minutes': 9 * 60}, 
                ],
            },
        }

        service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"{ts} 📆 Evento creado en el calendario: {calendar_id}")
        
    except Exception as e:
        print(f"{ts} ❌ Error creando evento en calendario: {e}")