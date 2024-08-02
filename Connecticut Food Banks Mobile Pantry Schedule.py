from googleapiclient.discovery import build
import psycopg2
from datetime import datetime

# Configuration
API_KEY = '***'  # Replace with your Google API Key
CALENDAR_ID = 'ctfoodbank.events@gmail.com'  # Replace with your public calendar ID

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname='beacon',
    user='***',
    password='***',
    host="localhost",
    port='5432'
)
cur = conn.cursor()

cur.execute('''
DROP TABLE IF EXISTS connecticut_food_banks_mobile_pantry_schedule
''')

# Create table if not exists
cur.execute('''
CREATE TABLE IF NOT EXISTS connecticut_food_banks_mobile_pantry_schedule (
    id TEXT PRIMARY KEY,
    summary TEXT,
    start TIMESTAMP,
    "end" TIMESTAMP,
    description TEXT,
    location TEXT,
    creator TEXT
)
''')

# Create the Google Calendar service object
service = build('calendar', 'v3', developerKey=API_KEY)

# Fetch events from the public calendar
now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now,
                                       singleEvents=True, orderBy='startTime').execute()
events = events_result.get('items', [])

# Prepare data for PostgreSQL
for event in events:
    # Extract event details
    event_id = event.get('id')
    summary = event.get('summary', '')
    start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))
    end = event.get('end', {}).get('dateTime', event.get('end', {}).get('date', ''))
    description = event.get('description', '')
    location = event.get('location', '')
    creator = event.get('creator', {}).get('email', '')

    # Insert data into PostgreSQL
    cur.execute('''
    INSERT INTO connecticut_food_banks_mobile_pantry_schedule (id, summary, start, "end", description, location, creator)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO UPDATE SET
        summary = EXCLUDED.summary,
        start = EXCLUDED.start,
        "end" = EXCLUDED."end",
        description = EXCLUDED.description,
        location = EXCLUDED.location,
        creator = EXCLUDED.creator
    ''', (event_id, summary, start, end, description, location, creator))

# Commit the transaction and close the connection
conn.commit()
cur.close()
conn.close()

print("Data scraped and stored in PostgreSQL successfully")